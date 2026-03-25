import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.orchestration import AgentRun, OrchestrationRun
from app.models.task import Task
from app.models.task_plan import TaskPlan
from app.models.task_progress import TaskProgressUpdate
from app.models.task_status import TaskStatus
from app.services.agents import AgentContext, build_default_agents
from app.services.artifact_storage import get_artifact_storage
from app.models.artifact import GeneratedArtifact
from app.services.task_service import TaskService


class OrchestrationService:
    @staticmethod
    def _persist_text_artifact(db: Session, task: Task, artifact_type: str, file_name: str, content: str, content_type: str) -> None:
        storage = get_artifact_storage()
        stored = storage.save_text(task_id=task.id, artifact_type=artifact_type, file_name=file_name, content=content)
        db.add(
            GeneratedArtifact(
                task_id=task.id,
                artifact_type=artifact_type,
                file_name=file_name,
                storage_backend=stored.backend,
                storage_key=stored.key,
                content_type=content_type,
                file_size=stored.size_bytes,
            )
        )

    @staticmethod
    def run(db: Session, task: Task) -> None:
        orchestration_run = OrchestrationRun(task_id=task.id, status="running")
        db.add(orchestration_run)
        db.commit()
        db.refresh(orchestration_run)

        context = AgentContext(task_id=task.id, title=task.title, user_prompt=task.user_prompt)
        previous_outputs: dict[str, dict] = {}

        TaskService.update_status(db, task, TaskStatus.planning, "Orchestrator started planner agent")

        for sequence, agent in enumerate(build_default_agents(), start=1):
            agent_run = AgentRun(
                orchestration_run_id=orchestration_run.id,
                task_id=task.id,
                agent_name=agent.name,
                sequence=sequence,
                status="running",
                started_at=datetime.now(timezone.utc),
            )
            orchestration_run.current_agent = agent.name
            db.add(agent_run)
            db.commit()
            try:
                result = agent.run(context, previous_outputs)
                previous_outputs[agent.name] = result.payload
                agent_run.status = "completed"
                agent_run.output_payload = json.dumps({"summary": result.summary, "data": result.payload}, indent=2)
                agent_run.completed_at = datetime.now(timezone.utc)

                TaskService.update_status(
                    db,
                    task,
                    TaskStatus.planning if agent.name == "planner" else (
                        TaskStatus.generating if agent.name in {"coder", "tester"} else TaskStatus.reviewing
                    ),
                    f"{agent.name.title()} agent completed",
                )
            except Exception as exc:
                agent_run.status = "failed"
                agent_run.error_payload = json.dumps({"error": str(exc), "agent": agent.name})
                agent_run.completed_at = datetime.now(timezone.utc)
                orchestration_run.status = "failed"
                orchestration_run.completed_at = datetime.now(timezone.utc)
                task.error_message = f"Agent {agent.name} failed"
                db.add(TaskProgressUpdate(task_id=task.id, status=TaskStatus.failed.value, message=task.error_message))
                TaskService.update_status(db, task, TaskStatus.failed, task.error_message)
                raise
            finally:
                db.add(agent_run)
                db.add(orchestration_run)
                db.commit()

        planner_payload = previous_outputs.get("planner", {})
        task.planner_status = "completed"
        task.planner_source = planner_payload.get("source", "fallback")
        db.query(TaskPlan).filter(TaskPlan.task_id == task.id).delete()
        for step in planner_payload.get("steps", []):
            db.add(
                TaskPlan(
                    task_id=task.id,
                    step_number=step["step_number"],
                    title=step["title"],
                    description=step["description"],
                )
            )

        OrchestrationService._persist_text_artifact(
            db,
            task,
            "plan",
            "execution-plan.json",
            json.dumps(planner_payload, indent=2),
            "application/json",
        )
        OrchestrationService._persist_text_artifact(
            db,
            task,
            "summary",
            "generation-summary.md",
            previous_outputs.get("reviewer", {}).get("summary", "No review summary."),
            "text/markdown",
        )
        OrchestrationService._persist_text_artifact(
            db,
            task,
            "deployment",
            "deployment-checklist.json",
            json.dumps(previous_outputs.get("deployer", {}), indent=2),
            "application/json",
        )

        orchestration_run.status = "completed"
        orchestration_run.current_agent = None
        orchestration_run.completed_at = datetime.now(timezone.utc)
        db.add(orchestration_run)
        db.commit()

        TaskService.update_status(db, task, TaskStatus.completed, "All orchestration agents completed")

import json

from sqlalchemy.orm import Session

from app.models.artifact import GeneratedArtifact
from app.models.task import Task
from app.models.task_plan import TaskPlan
from app.models.task_progress import TaskProgressUpdate
from app.models.task_status import TaskStatus
from app.services.artifact_storage import get_artifact_storage
from app.services.planner_factory import get_planner_service
from app.services.task_service import TaskService


class GenerationPipeline:
    @staticmethod
    def add_progress_update(db: Session, task: Task, status: TaskStatus, message: str) -> None:
        TaskService.update_status(db, task, status, message)

    @staticmethod
    def _persist_artifact(
        db: Session,
        *,
        task_id: int,
        artifact_type: str,
        file_name: str,
        content: str,
        content_type: str,
    ) -> None:
        storage = get_artifact_storage()
        stored = storage.save_text(task_id=task_id, artifact_type=artifact_type, file_name=file_name, content=content)
        db.add(
            GeneratedArtifact(
                task_id=task_id,
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
        task.planner_status = "running"
        db.commit()

        GenerationPipeline.add_progress_update(db, task, TaskStatus.planning, "Building an execution plan")

        planner_result = get_planner_service().generate_plan(task.user_prompt)
        task.planner_status = "completed"
        task.planner_source = planner_result.source
        db.query(TaskPlan).filter(TaskPlan.task_id == task.id).delete()
        for step in planner_result.plan.steps:
            db.add(
                TaskPlan(
                    task_id=task.id,
                    step_number=step.step_number,
                    title=step.title,
                    description=step.description,
                )
            )
        db.add(
            TaskProgressUpdate(
                task_id=task.id,
                status=TaskStatus.planning.value,
                message=f"Execution plan generated via {planner_result.source}",
            )
        )
        db.commit()

        GenerationPipeline.add_progress_update(db, task, TaskStatus.generating, "Generating API scaffolding artifacts")

        GenerationPipeline._persist_artifact(
            db,
            task_id=task.id,
            artifact_type="plan",
            file_name="execution-plan.json",
            content=planner_result.plan.model_dump_json(indent=2),
            content_type="application/json",
        )
        GenerationPipeline._persist_artifact(
            db,
            task_id=task.id,
            artifact_type="summary",
            file_name="generation-summary.md",
            content="Mock generation completed asynchronously by worker.",
            content_type="text/markdown",
        )
        GenerationPipeline._persist_artifact(
            db,
            task_id=task.id,
            artifact_type="review",
            file_name="review-report.log",
            content=json.dumps({"status": "ok", "notes": ["Pipeline completed", "Fallback scaffold generated"]}, indent=2),
            content_type="application/json",
        )
        db.commit()

        GenerationPipeline.add_progress_update(db, task, TaskStatus.reviewing, "Reviewing generated assets")
        GenerationPipeline.add_progress_update(db, task, TaskStatus.completed, "Generation finished successfully")

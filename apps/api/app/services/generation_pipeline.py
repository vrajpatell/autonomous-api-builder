from sqlalchemy.orm import Session

from app.models.artifact import GeneratedArtifact
from app.models.task import Task
from app.models.task_plan import TaskPlan
from app.models.task_progress import TaskProgressUpdate
from app.models.task_status import TaskStatus
from app.services.planner_factory import get_planner_service
from app.services.task_service import TaskService


class GenerationPipeline:
    @staticmethod
    def add_progress_update(db: Session, task: Task, status: TaskStatus, message: str) -> None:
        TaskService.update_status(db, task, status, message)

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
        db.add(
            GeneratedArtifact(
                task_id=task.id,
                artifact_type="summary",
                file_name="generation-summary.md",
                content="Mock generation completed asynchronously by worker.",
            )
        )
        db.commit()

        GenerationPipeline.add_progress_update(db, task, TaskStatus.reviewing, "Reviewing generated assets")
        GenerationPipeline.add_progress_update(db, task, TaskStatus.completed, "Generation finished successfully")

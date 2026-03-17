from sqlalchemy.orm import Session

from app.models.artifact import GeneratedArtifact
from app.models.task import Task
from app.models.task_plan import TaskPlan
from app.models.task_progress import TaskProgressUpdate
from app.models.task_status import TaskStatus


class GenerationPipeline:
    PLAN_STEPS = [
        ("Analyze requirements", "Parse the prompt and extract architecture, stack, and constraints."),
        ("Design system architecture", "Define backend modules, data models, and API contracts."),
        ("Generate implementation scaffolding", "Prepare directories, initial services, and integration points."),
        ("Validate and test", "Run baseline tests and static checks to verify generated outputs."),
        ("Prepare deployment bundle", "Create Docker, CI/CD, and deployment configuration artifacts."),
    ]

    @staticmethod
    def add_progress_update(db: Session, task: Task, status: TaskStatus, message: str) -> None:
        task.status = status.value
        db.add(TaskProgressUpdate(task_id=task.id, status=status.value, message=message))
        db.commit()
        db.refresh(task)

    @staticmethod
    def run(db: Session, task: Task) -> None:
        GenerationPipeline.add_progress_update(db, task, TaskStatus.planning, "Building an execution plan")

        db.query(TaskPlan).filter(TaskPlan.task_id == task.id).delete()
        for index, (title, description) in enumerate(GenerationPipeline.PLAN_STEPS, start=1):
            db.add(TaskPlan(task_id=task.id, step_number=index, title=title, description=description))
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

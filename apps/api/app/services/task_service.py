from sqlalchemy.orm import Session, selectinload

from app.models.task import Task
from app.models.task_plan import TaskPlan
from app.schemas.task import TaskCreate


class TaskService:
    """Business logic for task creation and retrieval."""

    @staticmethod
    def create_task(db: Session, payload: TaskCreate) -> Task:
        task = Task(title=payload.title, user_prompt=payload.user_prompt, status="planning")
        db.add(task)
        db.flush()

        plan_steps = [
            ("Analyze requirements", "Parse the prompt and extract architecture, stack, and constraints."),
            ("Design system architecture", "Define backend modules, data models, and API contracts."),
            ("Generate implementation scaffolding", "Prepare directories, initial services, and integration points."),
            ("Validate and test", "Run baseline tests and static checks to verify generated outputs."),
            ("Prepare deployment bundle", "Create Docker, CI/CD, and deployment configuration artifacts."),
        ]

        for idx, (title, description) in enumerate(plan_steps, start=1):
            db.add(TaskPlan(task_id=task.id, step_number=idx, title=title, description=description))

        task.status = "planned"
        db.commit()
        db.refresh(task)
        return TaskService.get_task(db, task.id)

    @staticmethod
    def list_tasks(db: Session) -> list[Task]:
        return (
            db.query(Task)
            .options(selectinload(Task.plans), selectinload(Task.artifacts))
            .order_by(Task.created_at.desc())
            .all()
        )

    @staticmethod
    def get_task(db: Session, task_id: int) -> Task | None:
        return (
            db.query(Task)
            .options(selectinload(Task.plans), selectinload(Task.artifacts))
            .filter(Task.id == task_id)
            .first()
        )

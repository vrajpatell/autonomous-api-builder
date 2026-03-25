from app.domain.exceptions import ValidationDomainError
from app.models.task_status import TaskStatus

TITLE_MIN_LENGTH = 3
TITLE_MAX_LENGTH = 120
PROMPT_MIN_LENGTH = 10
PROMPT_MAX_LENGTH = 4000
STATUS_MESSAGE_MAX_LENGTH = 1000


class TaskDomainRules:
    @staticmethod
    def _validate_required_text(value: str, *, field_name: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValidationDomainError(f"{field_name} cannot be empty or whitespace", details={"field": field_name})
        return normalized

    @staticmethod
    def validate_create_payload(*, title: str, user_prompt: str) -> tuple[str, str]:
        normalized_title = TaskDomainRules._validate_required_text(title, field_name="title")
        normalized_prompt = TaskDomainRules._validate_required_text(user_prompt, field_name="user_prompt")

        if not (TITLE_MIN_LENGTH <= len(normalized_title) <= TITLE_MAX_LENGTH):
            raise ValidationDomainError(
                f"title length must be between {TITLE_MIN_LENGTH} and {TITLE_MAX_LENGTH} characters",
                details={"field": "title"},
            )
        if not (PROMPT_MIN_LENGTH <= len(normalized_prompt) <= PROMPT_MAX_LENGTH):
            raise ValidationDomainError(
                f"user_prompt length must be between {PROMPT_MIN_LENGTH} and {PROMPT_MAX_LENGTH} characters",
                details={"field": "user_prompt"},
            )

        return normalized_title, normalized_prompt

    @staticmethod
    def validate_status_update(*, status: TaskStatus, message: str | None) -> str | None:
        if status not in TaskStatus:
            raise ValidationDomainError("status is not an allowed enum value", details={"field": "status"})

        if message is None:
            return None

        normalized_message = message.strip()
        if not normalized_message:
            raise ValidationDomainError(
                "message cannot be empty or whitespace when provided",
                details={"field": "message"},
            )
        if len(normalized_message) > STATUS_MESSAGE_MAX_LENGTH:
            raise ValidationDomainError(
                f"message length must be less than or equal to {STATUS_MESSAGE_MAX_LENGTH}",
                details={"field": "message"},
            )
        return normalized_message

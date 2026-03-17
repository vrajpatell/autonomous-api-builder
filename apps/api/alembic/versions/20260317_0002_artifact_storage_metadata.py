"""artifact storage metadata

Revision ID: 20260317_0002
Revises: 20260317_0001
Create Date: 2026-03-17 00:15:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260317_0002"
down_revision: Union[str, None] = "20260317_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("generated_artifacts", sa.Column("storage_backend", sa.String(length=50), nullable=True))
    op.add_column("generated_artifacts", sa.Column("storage_key", sa.String(length=1024), nullable=True))
    op.add_column("generated_artifacts", sa.Column("content_type", sa.String(length=255), nullable=True))
    op.add_column("generated_artifacts", sa.Column("file_size", sa.Integer(), nullable=True))

    op.execute("UPDATE generated_artifacts SET storage_backend='local', storage_key=file_name, content_type='text/plain', file_size=length(content)")

    op.alter_column("generated_artifacts", "storage_backend", nullable=False)
    op.alter_column("generated_artifacts", "storage_key", nullable=False)
    op.alter_column("generated_artifacts", "content_type", nullable=False)
    op.alter_column("generated_artifacts", "file_size", nullable=False)
    op.alter_column("generated_artifacts", "content", existing_type=sa.Text(), nullable=True)


def downgrade() -> None:
    op.alter_column("generated_artifacts", "content", existing_type=sa.Text(), nullable=False)
    op.drop_column("generated_artifacts", "file_size")
    op.drop_column("generated_artifacts", "content_type")
    op.drop_column("generated_artifacts", "storage_key")
    op.drop_column("generated_artifacts", "storage_backend")

"""add agent orchestration tables

Revision ID: 20260325_0003
Revises: 20260317_0002
Create Date: 2026-03-25 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260325_0003"
down_revision: Union[str, None] = "20260317_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "orchestration_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("current_agent", sa.String(length=50), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_orchestration_runs_id"), "orchestration_runs", ["id"], unique=False)
    op.create_index(op.f("ix_orchestration_runs_task_id"), "orchestration_runs", ["task_id"], unique=False)

    op.create_table(
        "agent_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("orchestration_run_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("agent_name", sa.String(length=50), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("output_payload", sa.Text(), nullable=True),
        sa.Column("error_payload", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["orchestration_run_id"], ["orchestration_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_runs_id"), "agent_runs", ["id"], unique=False)
    op.create_index(op.f("ix_agent_runs_orchestration_run_id"), "agent_runs", ["orchestration_run_id"], unique=False)
    op.create_index(op.f("ix_agent_runs_task_id"), "agent_runs", ["task_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_agent_runs_task_id"), table_name="agent_runs")
    op.drop_index(op.f("ix_agent_runs_orchestration_run_id"), table_name="agent_runs")
    op.drop_index(op.f("ix_agent_runs_id"), table_name="agent_runs")
    op.drop_table("agent_runs")

    op.drop_index(op.f("ix_orchestration_runs_task_id"), table_name="orchestration_runs")
    op.drop_index(op.f("ix_orchestration_runs_id"), table_name="orchestration_runs")
    op.drop_table("orchestration_runs")

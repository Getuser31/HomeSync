"""add_cascade_delete_on_houses

Revision ID: 7ec4f67379f9
Revises: cefc3fd67439
Create Date: 2026-03-24 15:46:13.112574

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '7ec4f67379f9'
down_revision: Union[str, Sequence[str], None] = 'cefc3fd67439'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('tasks_house_id_fkey', 'tasks', type_='foreignkey')
    op.create_foreign_key('tasks_house_id_fkey', 'tasks', 'houses', ['house_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('house_users_house_id_fkey', 'house_users', type_='foreignkey')
    op.create_foreign_key('house_users_house_id_fkey', 'house_users', 'houses', ['house_id'], ['id'],
                          ondelete='CASCADE')

    op.drop_constraint('role_house_users_house_id_fkey', 'role_house_users', type_='foreignkey')
    op.create_foreign_key('role_house_users_house_id_fkey', 'role_house_users', 'houses', ['house_id'], ['id'],
                          ondelete='CASCADE')

    op.drop_constraint('task_lives_task_id_fkey', 'task_lives', type_='foreignkey')
    op.create_foreign_key('task_lives_task_id_fkey', 'task_lives', 'tasks', ['task_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('task_completions_task_life_id_fkey', 'task_completions', type_='foreignkey')
    op.create_foreign_key('task_completions_task_life_id_fkey', 'task_completions', 'task_lives', ['task_life_id'],
                          ['id'], ondelete='CASCADE')


def downgrade() -> None:
    op.drop_constraint('tasks_house_id_fkey', 'tasks', type_='foreignkey')
    op.create_foreign_key('tasks_house_id_fkey', 'tasks', 'houses', ['house_id'], ['id'])

    op.drop_constraint('house_users_house_id_fkey', 'house_users', type_='foreignkey')
    op.create_foreign_key('house_users_house_id_fkey', 'house_users', 'houses', ['house_id'], ['id'])

    op.drop_constraint('role_house_users_house_id_fkey', 'role_house_users', type_='foreignkey')
    op.create_foreign_key('role_house_users_house_id_fkey', 'role_house_users', 'houses', ['house_id'], ['id'])

    op.drop_constraint('task_lives_task_id_fkey', 'task_lives', type_='foreignkey')
    op.create_foreign_key('task_lives_task_id_fkey', 'task_lives', 'tasks', ['task_id'], ['id'])

    op.drop_constraint('task_completions_task_life_id_fkey', 'task_completions', type_='foreignkey')
    op.create_foreign_key('task_completions_task_life_id_fkey', 'task_completions', 'task_lives', ['task_life_id'],
                          ['id'])

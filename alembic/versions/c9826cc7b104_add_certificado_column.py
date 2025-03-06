"""add_certificado_column

Revision ID: c9826cc7b104
Revises: 620cdcf3d1b5
Create Date: 2025-02-23 19:10:47.678366

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9826cc7b104'
down_revision: Union[str, None] = '620cdcf3d1b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

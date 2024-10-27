"""-

Revision ID: 614f9b818f02
Revises: 74dd440d690f
Create Date: 2024-10-27 10:16:20.434811

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '614f9b818f02'
down_revision = '74dd440d690f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('admins', schema=None) as batch_op:
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(length=150),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('admins', schema=None) as batch_op:
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(length=150),
               nullable=False)

    # ### end Alembic commands ###
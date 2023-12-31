"""Adicionando campos porte, agressivo, obs, pelagem

Revision ID: c11855de79ad
Revises: 56bc9cb8d350
Create Date: 2023-11-23 11:49:13.094849

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c11855de79ad'
down_revision = '56bc9cb8d350'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('animal', schema=None) as batch_op:
        batch_op.alter_column('porte',
               existing_type=mysql.VARCHAR(length=10),
               type_=sa.String(length=20),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('animal', schema=None) as batch_op:
        batch_op.alter_column('porte',
               existing_type=sa.String(length=20),
               type_=mysql.VARCHAR(length=10),
               existing_nullable=True)

    # ### end Alembic commands ###

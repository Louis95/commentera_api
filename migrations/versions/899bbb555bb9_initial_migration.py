"""initial migration

Revision ID: 899bbb555bb9
Revises: 
Create Date: 2023-08-22 01:26:42.846595

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '899bbb555bb9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('customer_id', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('badges',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('badge_name', sa.String(), nullable=True),
    sa.Column('user_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_badges_badge_name'), 'badges', ['badge_name'], unique=False)
    op.create_index(op.f('ix_badges_id'), 'badges', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_badges_id'), table_name='badges')
    op.drop_index(op.f('ix_badges_badge_name'), table_name='badges')
    op.drop_table('badges')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
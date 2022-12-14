"""empty message

Revision ID: c46974723883
Revises: b695ac8a79d5
Create Date: 2022-08-03 03:53:50.650503

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c46974723883'
down_revision = 'c58d1023f2db'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('show')
    op.create_table('show',
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['venue_id'], ['venue.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('artist_id', 'venue_id', 'start_time')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('show')
    # ### end Alembic commands ###

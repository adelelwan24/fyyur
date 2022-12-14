"""empty message

Revision ID: c58d1023f2db
Revises: c15b649324f7
Create Date: 2022-08-01 17:28:56.869302

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c58d1023f2db'
down_revision = 'c15b649324f7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('seeking_venues', sa.Boolean(), nullable=True))
    op.drop_column('artist', 'looking_for_venues')
    op.add_column('venue', sa.Column('genres', sa.String(length=120), nullable=True))
    op.add_column('venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.drop_column('venue', 'looking_for_talent')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('looking_for_talent', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('venue', 'seeking_talent')
    op.drop_column('venue', 'genres')
    op.add_column('artist', sa.Column('looking_for_venues', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('artist', 'seeking_venues')
    # ### end Alembic commands ###

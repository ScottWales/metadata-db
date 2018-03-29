"""Autogenerate model

Revision ID: 8e4e31afc0a2
Revises: 78ead7c923ed
Create Date: 2018-03-29 19:58:09.530793

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e4e31afc0a2'
down_revision = '78ead7c923ed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('attribute',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(), nullable=True),
    sa.Column('value', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key', 'value')
    )
    op.create_table('collection',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('last_crawled', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('metadata',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sha256', sa.String(), nullable=True),
    sa.Column('mtime', sa.Integer(), nullable=True),
    sa.Column('size', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('sha256')
    )
    op.create_table('dimension',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('meta_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('size', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['meta_id'], ['metadata.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('meta_to_attr',
    sa.Column('meta_id', sa.Integer(), nullable=True),
    sa.Column('attr_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['attr_id'], ['attribute.id'], ),
    sa.ForeignKeyConstraint(['meta_id'], ['metadata.id'], )
    )
    op.create_table('path',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('meta_id', sa.Integer(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('basename', sa.Text(), nullable=True),
    sa.Column('mtime', sa.Integer(), nullable=True),
    sa.Column('uid', sa.Integer(), nullable=True),
    sa.Column('gid', sa.Integer(), nullable=True),
    sa.Column('size', sa.Integer(), nullable=True),
    sa.Column('last_seen', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['meta_id'], ['metadata.id'], ),
    sa.ForeignKeyConstraint(['parent_id'], ['path.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('variable',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('meta_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('type', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['meta_id'], ['metadata.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('collection_root_path',
    sa.Column('path_id', sa.Integer(), nullable=True),
    sa.Column('coll_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['coll_id'], ['collection.id'], ),
    sa.ForeignKeyConstraint(['path_id'], ['path.id'], )
    )
    op.create_table('path_to_collection',
    sa.Column('path_id', sa.Integer(), nullable=True),
    sa.Column('coll_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['coll_id'], ['collection.id'], ),
    sa.ForeignKeyConstraint(['path_id'], ['path.id'], )
    )
    op.create_table('var_to_attr',
    sa.Column('var_id', sa.Integer(), nullable=True),
    sa.Column('attr_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['attr_id'], ['attribute.id'], ),
    sa.ForeignKeyConstraint(['var_id'], ['variable.id'], )
    )
    op.create_table('var_to_dim',
    sa.Column('var_id', sa.Integer(), nullable=True),
    sa.Column('dim_id', sa.Integer(), nullable=True),
    sa.Column('ndim', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['dim_id'], ['dimension.id'], ),
    sa.ForeignKeyConstraint(['var_id'], ['variable.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('var_to_dim')
    op.drop_table('var_to_attr')
    op.drop_table('path_to_collection')
    op.drop_table('collection_root_path')
    op.drop_table('variable')
    op.drop_table('path')
    op.drop_table('meta_to_attr')
    op.drop_table('dimension')
    op.drop_table('metadata')
    op.drop_table('collection')
    op.drop_table('attribute')
    # ### end Alembic commands ###

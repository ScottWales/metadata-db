"""Add unique constraints

Revision ID: 988b5a1a2c47
Revises: 7ae41e19e0be
Create Date: 2018-04-05 11:12:40.380332

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '988b5a1a2c47'
down_revision = '7ae41e19e0be'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('collection_root_path') as batch_op:
        batch_op.create_unique_constraint(
            'coll_root_uniq', ['path_id', 'coll_id'])
    with op.batch_alter_table('meta_to_attr') as batch_op:
        batch_op.create_unique_constraint(
            'meta_to_attr_uniq',  ['meta_id', 'attr_id'])
    with op.batch_alter_table('path_to_collection') as batch_op:
        batch_op.create_unique_constraint(
            'path_to_coll_uniq',  ['path_id', 'coll_id'])
    with op.batch_alter_table('var_to_attr') as batch_op:
        batch_op.create_unique_constraint(
            'var_to_attr_uniq',  ['var_id', 'attr_id'])
    with op.batch_alter_table('var_to_dim') as batch_op:
        batch_op.create_unique_constraint(
            'var_to_dim_uniq',  ['var_id', 'dim_id'])


def downgrade():
    with op.batch_alter_table('collection_root_path') as batch_op:
        batch_op.drop_constraint('coll_root_uniq',  type_='unique')
    with op.batch_alter_table('meta_to_attr') as batch_op:
        batch_op.drop_constraint('meta_to_attr_uniq',   type_='unique')
    with op.batch_alter_table('path_to_collection') as batch_op:
        batch_op.drop_constraint('path_to_coll_uniq',   type_='unique')
    with op.batch_alter_table('var_to_attr') as batch_op:
        batch_op.drop_constraint('var_to_attr_uniq',   type_='unique')
    with op.batch_alter_table('var_to_dim') as batch_op:
        batch_op.drop_constraint('var_to_dim_uniq',   type_='unique')

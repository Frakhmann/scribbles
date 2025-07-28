from alembic import op
import sqlalchemy as sa

revision = 'cbc4475001f'
down_revision = '700a6b1725a9'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('likes', sa.Column('comment_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_likes_comment_id', 'likes', 'comments', ['comment_id'], ['id'], ondelete='CASCADE')
    op.create_unique_constraint('unique_user_comment_like', 'likes', ['user_id', 'comment_id'])

def downgrade():
    op.drop_constraint('unique_user_comment_like', 'likes', type_='unique')
    op.drop_constraint('fk_likes_comment_id', 'likes', type_='foreignkey')
    op.drop_column('likes', 'comment_id')

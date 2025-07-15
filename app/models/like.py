from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from app.db.base_class import Base

class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=True)
    comment_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="unique_user_post_like"),
        UniqueConstraint("user_id", "comment_id", name="unique_user_comment_like"),
    )
    
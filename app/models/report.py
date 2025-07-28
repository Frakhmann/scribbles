from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, backref
from app.db.base_class import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    reason = Column(String(200), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    post = relationship(
        "Post",
        backref=backref("reports", passive_deletes=True)
    )
    user = relationship("User")

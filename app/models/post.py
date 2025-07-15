from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)

    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    media_url = Column(String, nullable=True)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="posts")
    section = relationship("Section", back_populates="posts")
    university = relationship("University", back_populates="posts")

    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan", passive_deletes=True)
    likes = relationship("Like", backref="post", cascade="all, delete-orphan", passive_deletes=True)
    notifications = relationship("Notification", back_populates="post", cascade="all, delete-orphan", passive_deletes=True)

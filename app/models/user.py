from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from sqlalchemy import DateTime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String)
    nickname = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    activation_token = Column(String, nullable=True)
    activation_token_expiry = Column(DateTime, nullable=True)

    university_id = Column(Integer, ForeignKey("universities.id"), nullable=True)
    university = relationship("University", backref="users")

    # 🔄 связь с постами
    posts = relationship("Post", back_populates="user")

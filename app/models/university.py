from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class University(Base):
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    email_domain = Column(String, unique=True, nullable=False)
    image_url = Column(String, nullable=True) 

    posts = relationship("Post", back_populates="university")

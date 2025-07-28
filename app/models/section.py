from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)

    university = relationship("University", backref="sections")
    posts = relationship("Post", back_populates="section")

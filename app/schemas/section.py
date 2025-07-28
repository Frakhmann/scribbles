from pydantic import BaseModel

class SectionBase(BaseModel):
    name: str
    university_id: int

class SectionCreate(SectionBase):
    pass

class SectionRead(SectionBase):
    id: int

    class Config:
        from_attributes = True

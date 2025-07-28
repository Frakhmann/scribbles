from pydantic import BaseModel

class UniversityBase(BaseModel):
    name: str
    domain: str

class UniversityCreate(UniversityBase):
    pass

class UniversityRead(UniversityBase):
    id: int

    class Config:
        from_attributes = True

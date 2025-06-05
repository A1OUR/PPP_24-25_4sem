# models.py
from pydantic import BaseModel
from typing import List, Optional

# Teachers
class TeacherCreate(BaseModel):
    name: str

class TeacherResponse(TeacherCreate):
    id: int
    courses: Optional[List["CourseResponse"]] = []

    class Config:
        orm_mode = True

# Courses
class CourseCreate(BaseModel):
    name: str
    student_count: int
    teacher_id: int

class CourseResponse(CourseCreate):
    id: int

    class Config:
        orm_mode = True

# Разрешаем циклические ссылки
TeacherResponse.update_forward_refs()
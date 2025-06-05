# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import Base, engine, SessionLocal
from models import TeacherCreate, TeacherResponse, CourseCreate, CourseResponse
from database import TeacherDB, CourseDB

app = FastAPI()


@app.get("/ping")
def ping():
    return {"status": "ok"}

# Создание таблиц в БД
Base.metadata.create_all(bind=engine)

# Зависимость для подключения к БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ========== TEACHERS ==========
@app.get("/teachers", response_model=List[TeacherResponse], status_code=status.HTTP_200_OK)
def get_teachers(db: Session = Depends(get_db)):
    return db.query(TeacherDB).all()

@app.post("/teachers", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
def create_teacher(teacher: TeacherCreate, db: Session = Depends(get_db)):
    db_teacher = TeacherDB(**teacher.dict())
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

@app.get("/teachers/{id}/courses", response_model=List[CourseResponse], status_code=status.HTTP_200_OK)
def get_teacher_courses(id: int, db: Session = Depends(get_db)):
    teacher = db.query(TeacherDB).filter(TeacherDB.id == id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Преподаватель не найден")
    return teacher.courses

@app.delete("/teachers/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher(id: int, db: Session = Depends(get_db)):
    teacher = db.query(TeacherDB).filter(TeacherDB.id == id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Преподаватель не найден")
    db.delete(teacher)
    db.commit()
    return

# ========== COURSES ==========
@app.get("/courses", response_model=List[CourseResponse], status_code=status.HTTP_200_OK)
def get_courses(db: Session = Depends(get_db)):
    return db.query(CourseDB).all()

@app.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    teacher = db.query(TeacherDB).filter(TeacherDB.id == course.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Преподаватель не найден")
    db_course = CourseDB(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@app.delete("/courses/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(id: int, db: Session = Depends(get_db)):
    course = db.query(CourseDB).filter(CourseDB.id == id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    db.delete(course)
    db.commit()
    return
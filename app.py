from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from database import SessionLocal, engine
from models import Base, User, Task

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
def home():
    return {"message": "Task Manager Running"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(
        request,
        "register.html"
    )
    
@app.post("/register")
def register_user(
    username: str = Form(...),
    password: str = Form(...)
):
    db = SessionLocal()

    user = User(
        username=username,
        password=password
    )

    db.add(user)
    db.commit()

    db.close()

    return RedirectResponse(
        url="/register",
        status_code=303
    )
    
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html"
    )
    
@app.post("/login")
def login_user(
    username: str = Form(...),
    password: str = Form(...)
):
    db = SessionLocal()

    user = db.query(User).filter(
        User.username == username,
        User.password == password
    ).first()

    db.close()

    if user:
        return RedirectResponse(
            url="/dashboard",
            status_code=303
        )

    return {
        "message": "Invalid Username or Password"
    }
    
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):

    db = SessionLocal()

    tasks = db.query(Task).all()

    total_tasks = len(tasks)

    completed_tasks = len(
        [task for task in tasks if task.completed]
    )

    pending_tasks = total_tasks - completed_tasks

    db.close()

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "tasks": tasks,
            "total": total_tasks,
            "completed": completed_tasks,
            "pending": pending_tasks
        }
    )


@app.post("/add-task")
def add_task(
    title: str = Form(...)
):
    db = SessionLocal()

    task = Task(
        title=title,
        completed=False,
        owner_id=1
    )

    db.add(task)

    db.commit()

    db.close()

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )
    
@app.get("/delete-task/{task_id}")
def delete_task(task_id: int):

    db = SessionLocal()

    task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if task:
        db.delete(task)
        db.commit()

    db.close()

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )
    
@app.get("/complete-task/{task_id}")
def complete_task(task_id: int):

    db = SessionLocal()

    task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if task:
        task.completed = True
        db.commit()

    db.close()

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )
    
@app.get("/logout")
def logout():
    return RedirectResponse(
        url="/login",
        status_code=303
    )
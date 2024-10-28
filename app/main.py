from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app import models, schemas
from app.database import get_db
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/hi')
def hi():
    return {"message": "Hi"}


@app.get('/hello/{name}')
def hello(name:str):
    return {"message": f"Hello {name} welcome to Fast API Framework."}



@app.get('/employees', response_model=list[schemas.Employee])
def employees_list(skip:int = 0, limit:int = 10, db:Session = Depends(get_db)):
    employees_data = db.execute(select(models.Employee).order_by(models.Employee.emp_id).offset(skip).limit(limit)).scalars().all()
    return employees_data


@app.post('/employees', response_model=schemas.Employee)
def create_employee(data:schemas.Employee, db:Session = Depends(get_db)):
    emp_data = models.Employee(**data.model_dump())
    db.add(emp_data)
    db.commit()
    db.refresh(emp_data)
    return emp_data


@app.get('/employee/{emp_id}', response_model=schemas.Employee)
def employee_details(emp_id:int, db:Session = Depends(get_db)):
    emp_data = db.get(models.Employee, emp_id)
    if emp_data is None:
        raise HTTPException(status_code=404, detail="Employee not found.")
    return emp_data


@app.put('/employeeupdate/{emp_id}', response_model=schemas.Employee)
def employee_update(emp_id:int, data:schemas.EmployeeUpdate, db:Session = Depends(get_db)):
    emp_data = db.get(models.Employee, emp_id)
    if emp_data is None:
        raise HTTPException(status_code=404, detail="Employee not found.")

    for key, val in data.model_dump(exclude_none=True).items():
        setattr(emp_data, key, val)
    db.commit()
    db.refresh(emp_data)
    return emp_data


@app.delete('/employeedelete/{emp_id}')
def employee_delete(emp_id:int, db:Session = Depends(get_db)):
    emp_data = db.get(models.Employee, emp_id)
    db.delete(emp_data)
    db.commit()
    return {"message": f"{emp_data.emp_name} Employee was deleted successfully"}
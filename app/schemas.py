from pydantic import BaseModel, PositiveFloat


class Employee(BaseModel):

    emp_id: int
    emp_name: str
    emp_role: str
    emp_salary: PositiveFloat


class EmployeeUpdate(BaseModel):
    emp_role: str | None = None
    emp_salary: PositiveFloat | None = None

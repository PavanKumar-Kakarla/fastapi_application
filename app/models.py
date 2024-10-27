from sqlalchemy.orm import DeclarativeBase, Mapped, MappedColumn


class Base(DeclarativeBase):
    pass


class Employee(Base):
    __tablename__ = 'employees'

    emp_id: Mapped[int] = MappedColumn(primary_key=True, index=True)
    emp_name: Mapped[str] = MappedColumn(nullable=False)
    emp_role: Mapped[str] = MappedColumn(nullable=True)
    emp_salary: Mapped[float] = MappedColumn(server_default='0')





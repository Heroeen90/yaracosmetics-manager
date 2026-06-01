from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    Text
)
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///yara.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# =========================
# PRODUCTS
# =========================
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)

    category = Column(String)

    supplier = Column(String)

    purchase_price = Column(Float, default=0)

    sale_price = Column(Float, default=0)

    quantity = Column(Integer, default=0)

    min_quantity = Column(Integer, default=3)

    image = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================
# SALES
# =========================
class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)

    product_name = Column(String)

    quantity = Column(Integer)

    sale_price = Column(Float)

    total = Column(Float)

    sale_date = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================
# PURCHASES
# =========================
class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True)

    product_name = Column(String)

    quantity = Column(Integer)

    purchase_price = Column(Float)

    total = Column(Float)

    supplier = Column(String)

    purchase_date = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================
# DEBTS
# =========================
class Debt(Base):
    __tablename__ = "debts"

    id = Column(Integer, primary_key=True)

    customer_name = Column(String)

    amount = Column(Float)

    paid_amount = Column(Float, default=0)

    status = Column(String, default="غير مسدد")

    note = Column(Text)

    debt_date = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================
# EXPENSES
# =========================
class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True)

    category = Column(String)

    amount = Column(Float)

    note = Column(Text)

    expense_date = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================
# SALARIES
# =========================
class Salary(Base):
    __tablename__ = "salaries"

    id = Column(Integer, primary_key=True)

    employee_name = Column(String)

    amount = Column(Float)

    note = Column(Text)

    salary_date = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================
# SUPPLIERS
# =========================
class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True)

    name = Column(String)

    phone = Column(String)

    note = Column(Text)


# =========================
# SETTINGS
# =========================
class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)

    key = Column(String)

    value = Column(String)


def create_database():
    Base.metadata.create_all(bind=engine)

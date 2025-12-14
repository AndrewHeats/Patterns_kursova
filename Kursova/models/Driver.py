from sqlalchemy import Column, Integer, String

from models.base import Base


class Driver(Base):
    __tablename__ = 'drivers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    license_number = Column(String)
    experience = Column(Integer)
    medical_checks = Column(String)  # Use 'State' pattern values: "Passed", "Not Passed", etc.

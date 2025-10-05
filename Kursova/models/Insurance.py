from sqlalchemy import Column, Integer, String, Float, ForeignKey

from models.base import Base


class Insurance(Base):
    __tablename__ = 'insurance'
    id = Column(Integer, primary_key=True)
    policy_number = Column(String)
    expiry_date = Column(String)  # можна змінити на Date
    cost = Column(Float)
    car_id = Column(Integer, ForeignKey('cars.id'))

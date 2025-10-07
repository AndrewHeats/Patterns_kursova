from sqlalchemy import Column, Integer, String, Float, ForeignKey

from models.base import Base


class FuelCost(Base):
    __tablename__ = 'fuelcosts'
    id = Column(Integer, primary_key=True)
    date = Column(String)
    type = Column(String)
    cost = Column(Float)
    car_id = Column(Integer, ForeignKey('cars.id'))

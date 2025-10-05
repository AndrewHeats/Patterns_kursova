from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey

from models.base import Base


class Trip(Base):
    __tablename__ = 'trips'
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    route = Column(String)
    distance = Column(Float)
    car_id = Column(Integer, ForeignKey('cars.id'))
    driver_id = Column(Integer, ForeignKey('drivers.id'))

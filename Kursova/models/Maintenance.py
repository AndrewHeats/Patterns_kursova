from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey

from models.base import Base


class Maintenance(Base):
    __tablename__ = 'maintenance'
    id = Column(Integer, primary_key=True)
    date = Column(String)
    type = Column(String)
    cost = Column(Float)
    done = Column(Boolean)
    car_id = Column(Integer, ForeignKey('cars.id'))

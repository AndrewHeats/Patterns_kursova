from sqlalchemy import Column, Integer, String, ForeignKey

from models.base import Base


class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    date = Column(String)
    type = Column(String)
    message = Column(String)
    car_id = Column(Integer, ForeignKey('cars.id'))
    driver_id = Column(Integer, ForeignKey('drivers.id'))

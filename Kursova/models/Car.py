from sqlalchemy import Column, Integer, String

from models.base import Base


class Car(Base):
    __tablename__ = 'cars'
    id = Column(Integer, primary_key=True)
    brand = Column(String)
    model = Column(String)
    year = Column(Integer)
    vin = Column(String)
    technical_state = Column(String)

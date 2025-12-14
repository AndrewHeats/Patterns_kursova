from sqlalchemy import Column, Integer, String
from models.base import Base


class FleetManager(Base):
    __tablename__ = 'fleet_managers'
    id = Column(Integer, primary_key=True)
    name = Column(String)

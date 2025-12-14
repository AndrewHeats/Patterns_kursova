from sqlalchemy import Column, Integer, String

from models.base import Base


class Report(Base):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True)
    start_date = Column(String)
    end_date = Column(String)
    type = Column(String)
    data = Column(String)

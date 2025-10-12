import datetime
import random

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.Car import Car
from models.Driver import Driver
from models.FuelCost import FuelCost
from models.Insurance import Insurance
from models.Maintenance import Maintenance
from models.Notification import Notification
from models.Report import Report
from models.Trip import Trip
from models.base import Base

engine = create_engine('sqlite:///fleet.db')
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


def seed_database():
    session = Session()
    session.query(Notification).delete()
    session.query(Report).delete()
    session.query(Insurance).delete()
    session.query(Maintenance).delete()
    session.query(FuelCost).delete()
    session.query(Trip).delete()
    session.query(Driver).delete()
    session.query(Car).delete()
    session.commit()

    today = datetime.date.today()

    for i in range(1, 11):
        session.add(Car(id=i, brand=f"Brand{i}", model=f"Model{i}", year=random.randint(2000, 2025),
                        vin=f"VIN{random.randint(0, 99999):05d}", technical_state="OK"))
        session.add(Driver(id=i, name=f"Driver{i}", license_number=f"L{random.randint(0, 99999):05d}", experience=5 + i,
                           medical_checks="Passed"))
        session.add(
            Trip(id=i, date=today, route=f"Route {i}", distance=random.randint(1, 1000), car_id=random.randint(1, 11),
                 driver_id=random.randint(1, 11)))
        session.add(FuelCost(id=i, date=today, type="Petrol", cost=random.randint(50, 1000), car_id=random.randint(1, 11)))
        session.add(Maintenance(id=i, date=today, type="TO", cost=random.randint(100, 10000), done=False, car_id=random.randint(1, 11)))
        expiry = today + datetime.timedelta(days=30 * i)
        session.add(Insurance(id=i, policy_number=f"Policy{i}", expiry_date=expiry, cost=50, car_id=i))


    session.commit()
    session.close()
    print("Database seeded with sample data.")


if __name__ == "__main__":
    seed_database()

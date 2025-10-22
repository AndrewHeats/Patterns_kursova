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

    session.add(Car(id=1, brand=f"Toyota", model=f"Corolla", year=random.randint(2000, 2025),
                    vin=f"VIN{random.randint(0, 99999):05d}", technical_state="OK"))
    session.add(Car(id=2, brand=f"Mercedes", model=f"Benz", year=random.randint(2000, 2025),
                    vin=f"VIN{random.randint(0, 99999):05d}", technical_state="OK"))
    session.add(Car(id=3, brand=f"Scoda", model=f"Octavia", year=random.randint(2000, 2025),
                    vin=f"VIN{random.randint(0, 99999):05d}", technical_state="OK"))
    session.add(Car(id=4, brand=f"Toyota", model=f"Land Cruiser", year=random.randint(2000, 2025),
                    vin=f"VIN{random.randint(0, 99999):05d}", technical_state="OK"))
    session.add(Car(id=5, brand=f"Opel", model=f"Astra", year=random.randint(2000, 2025),
                    vin=f"VIN{random.randint(0, 99999):05d}", technical_state="OK"))
    session.add(Car(id=6, brand=f"Lanos", model=f"Deo", year=random.randint(2000, 2025),
                    vin=f"VIN{random.randint(0, 99999):05d}", technical_state="OK"))
    session.add(Car(id=7, brand=f"Toyota", model=f"Corolla", year=random.randint(2000, 2025),
                    vin=f"VIN{random.randint(0, 99999):05d}", technical_state="OK"))
    session.add(Car(id=8, brand=f"Mitsubisi", model=f"Pagero", year=random.randint(2000, 2025),
                    vin=f"VIN{random.randint(0, 99999):05d}", technical_state="OK"))
    session.add(Car(id=9, brand=f"Hyundai", model=f"Sonata", year=random.randint(2000, 2025),
                    vin=f"VIN{random.randint(0, 99999):05d}", technical_state="OK"))
    session.add(Car(id=10, brand=f"Honda", model=f"Civic", year=random.randint(2000, 2025),
                    vin=f"VIN{random.randint(0, 99999):05d}", technical_state="OK"))

    session.add(Driver(id=1, name=f"Petro Shchur", license_number=f"L{random.randint(0, 99999):05d}", experience=6,
                       medical_checks="Passed"))
    session.add(Driver(id=2, name=f"Ivan Kolomyja", license_number=f"L{random.randint(0, 99999):05d}", experience=8,
                       medical_checks="Passed"))
    session.add(
        Driver(id=3, name=f"Oleksandr Halytskyy", license_number=f"L{random.randint(0, 99999):05d}", experience=10,
               medical_checks="Passed"))
    session.add(Driver(id=4, name=f"Pavlo Kordola", license_number=f"L{random.randint(0, 99999):05d}", experience=5,
                       medical_checks="Passed"))
    session.add(Driver(id=5, name=f"Stepan Pidhayets", license_number=f"L{random.randint(0, 99999):05d}", experience=1,
                       medical_checks="Passed"))
    session.add(Driver(id=6, name=f"Sofiya Zayets", license_number=f"L{random.randint(0, 99999):05d}", experience=4,
                       medical_checks="Passed"))
    session.add(Driver(id=7, name=f"Daryna Mandaryna", license_number=f"L{random.randint(0, 99999):05d}", experience=15,
                       medical_checks="Passed"))
    session.add(Driver(id=8, name=f"Andrii Perun", license_number=f"L{random.randint(0, 99999):05d}", experience=22,
                       medical_checks="Passed"))
    session.add(Driver(id=9, name=f"Oleg Kos", license_number=f"L{random.randint(0, 99999):05d}", experience=16,
                       medical_checks="Passed"))
    session.add(Driver(id=10, name=f"Eduard Ivanenko", license_number=f"L{random.randint(0, 99999):05d}", experience=3,
                       medical_checks="Passed"))

    session.add(
        Trip(id=1, date=today, route=f"Kyiv-Lviv", distance=556, car_id=random.randint(1, 10),
             driver_id=random.randint(1, 10)))
    session.add(
        Trip(id=2, date=today, route=f"Rivne-Lviv", distance=315, car_id=random.randint(1, 10),
             driver_id=random.randint(1, 10)))
    session.add(
        Trip(id=3, date=today, route=f"Kyiv-Kramatorsk", distance=225, car_id=random.randint(1, 10),
             driver_id=random.randint(1, 10)))
    session.add(
        Trip(id=4, date=today, route=f"Ternopil-Ratne", distance=480, car_id=random.randint(1, 10),
             driver_id=random.randint(1, 10)))
    session.add(
        Trip(id=5, date=today, route=f"Poltava-Lviv", distance=1112, car_id=random.randint(1, 10),
             driver_id=random.randint(1, 10)))
    session.add(
        Trip(id=6, date=today, route=f"Kyiv-Dnipro", distance=356, car_id=random.randint(1, 10),
             driver_id=random.randint(1, 10)))
    session.add(
        Trip(id=7, date=today, route=f"Uzhorod-Ternopil", distance=682, car_id=random.randint(1, 10),
             driver_id=random.randint(1, 10)))
    session.add(
        Trip(id=8, date=today, route=f"Briukhovychi-Lviv", distance=5, car_id=random.randint(1, 10),
             driver_id=random.randint(1, 10)))
    session.add(
        Trip(id=9, date=today, route=f"Ratne-Lutsk", distance=82, car_id=random.randint(1, 10),
             driver_id=random.randint(1, 10)))
    session.add(
        Trip(id=10, date=today, route=f"Khmelnytskyy-Cherkasy", distance=432, car_id=random.randint(1, 10),
             driver_id=random.randint(1, 10)))

    for i in range(1,11):
        session.add(
            FuelCost(id=i, date=today, type="Petrol", cost=random.randint(50, 1000), car_id=random.randint(1, 11)))
        session.add(Maintenance(id=i, date=today, type="TO", cost=random.randint(100, 10000), done=False,
                                car_id=random.randint(1, 11)))
        expiry = today + datetime.timedelta(days=30 * i)
        session.add(Insurance(id=i, policy_number=f"Policy{i}", expiry_date=expiry, cost=50, car_id=i))

    session.commit()
    session.close()
    print("Database seeded with sample data.")


if __name__ == "__main__":
    seed_database()

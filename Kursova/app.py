from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.Car import Car
from models.Driver import Driver
from models.base import Base


def main():
    # Підключення до SQLite (або до іншої БД)
    engine = create_engine('sqlite:///fleet.db', echo=True)
    Base.metadata.create_all(engine)  # створює всі таблиці

    Session = sessionmaker(bind=engine)
    session = Session()

    # Додаємо автомобіль в БД
    car1 = Car(id=1, brand="Toyota", model="Corolla", year=2020, vin="JH4DA9340LS123456", technical_state="добрий")
    session.add(car1)

    # Додаємо водія
    driver1 = Driver(id=1, name="Іван Іванов", license_number="A12345", experience=10, medical_checks="пройдено")
    session.add(driver1)

    session.commit()

    # Читаємо дані з БД
    all_cars = session.query(Car).all()
    for car in all_cars:
        print(car.brand, car.model)


if __name__ == "__main__":
    main()

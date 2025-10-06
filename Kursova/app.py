from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.Car import Car
from models.Driver import Driver
from models.Trip import Trip
from models.FuelCost import FuelCost
from models.Maintenance import Maintenance
from models.Insurance import Insurance
from models.Notification import Notification
from models.Report import Report
from controllers.CarController import car_bp
from controllers.DriverController import driver_bp
from controllers.TripController import trip_bp
from controllers.FuelCostController import fuel_bp
from controllers.MaintenanceController import maintenance_bp
from controllers.InsuranceController import ins_bp
from controllers.NotificationController import notif_bp
from controllers.ReportController import report_bp
from controllers.FleetManagerController import fleetmanager_bp
import datetime

app = Flask(__name__)
app.register_blueprint(car_bp)
app.register_blueprint(driver_bp)
app.register_blueprint(trip_bp)
app.register_blueprint(fuel_bp)
app.register_blueprint(maintenance_bp)
app.register_blueprint(ins_bp)
app.register_blueprint(notif_bp)
app.register_blueprint(report_bp)
app.register_blueprint(fleetmanager_bp)

engine = create_engine('sqlite:///fleet.db')
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

def seed_database():
    session = Session()
    # Видаляємо всі записи
    session.query(Notification).delete()
    session.query(Report).delete()
    session.query(Insurance).delete()
    session.query(Maintenance).delete()
    session.query(FuelCost).delete()
    session.query(Trip).delete()
    session.query(Driver).delete()
    session.query(Car).delete()
    session.commit()

    # Додаємо 10 Car
    for i in range(1, 11):
        car = Car(id=i, brand=f"Brand{i}", model=f"Model{i}", year=2010+i, vin=f"VIN{i:05d}", technical_state="OK")
        session.add(car)

    # Додаємо 10 Driver
    for i in range(1, 11):
        driver = Driver(id=i, name=f"Driver{i}", license_number=f"L{i:05d}", experience=5+i, medical_checks="Passed")
        session.add(driver)

    # Додаємо 10 Trip
    for i in range(1, 11):
        trip = Trip(
            id=i,
            date=datetime.date.today(),  # <- об'єкт дати, а не рядок
            route=f"Route {i}",
            distance=10 * i,
            car_id=i,
            driver_id=i
        )
        session.add(trip)

    # Додаємо 10 FuelCost
    for i in range(1, 11):
        fuel = FuelCost(id=i, date=str(datetime.date.today()), type="Petrol", cost=100+i*10, car_id=i)
        session.add(fuel)

    # Додаємо 10 Maintenance
    for i in range(1, 11):
        maintenance = Maintenance(id=i, date=str(datetime.date.today()), type="TO", cost=200+i*20, done=False, car_id=i)
        session.add(maintenance)

    # Додаємо 10 Insurance
    for i in range(1, 11):
        expiry = datetime.date.today() + datetime.timedelta(days=30*i)
        insurance = Insurance(id=i, policy_number=f"Policy{i}", expiry_date=str(expiry), cost=50, car_id=i)
        session.add(insurance)

    # Додаємо 10 Notification
    for i in range(1, 11):
        notif = Notification(id=i, date=str(datetime.date.today()), type="Info", message=f"Notification {i}", car_id=i, driver_id=i)
        session.add(notif)

    # Додаємо 10 Report
    for i in range(1, 11):
        start = datetime.date.today() - datetime.timedelta(days=30)
        end = datetime.date.today()
        report = Report(id=i, start_date=str(start), end_date=str(end), type="CarsPark", data=f"Report data {i}")
        session.add(report)

    session.commit()
    session.close()
    print("Database seeded with sample data.")

if __name__ == "__main__":
    seed_database()
    app.run(debug=True)

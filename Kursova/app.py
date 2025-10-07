from flask import Flask, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime

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

app = Flask(__name__)

app.register_blueprint(car_bp, url_prefix="/cars")
app.register_blueprint(driver_bp, url_prefix="/drivers")
app.register_blueprint(trip_bp, url_prefix="/trips")
app.register_blueprint(fuel_bp, url_prefix="/fuelcosts")
app.register_blueprint(maintenance_bp, url_prefix="/maintenances")
app.register_blueprint(ins_bp, url_prefix="/insurances")
app.register_blueprint(notif_bp, url_prefix="/notifications")
app.register_blueprint(report_bp, url_prefix="/reports")
app.register_blueprint(fleetmanager_bp, url_prefix="/fleetmanager")

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
        session.add(Car(id=i, brand=f"Brand{i}", model=f"Model{i}", year=2010 + i, vin=f"VIN{i:05d}", technical_state="OK"))
        session.add(Driver(id=i, name=f"Driver{i}", license_number=f"L{i:05d}", experience=5 + i, medical_checks="Passed"))
        session.add(Trip(id=i, date=today, route=f"Route {i}", distance=10 * i, car_id=i, driver_id=i))
        session.add(FuelCost(id=i, date=today, type="Petrol", cost=100 + i * 10, car_id=i))
        session.add(Maintenance(id=i, date=today, type="TO", cost=200 + i * 20, done=False, car_id=i))
        expiry = today + datetime.timedelta(days=30 * i)
        session.add(Insurance(id=i, policy_number=f"Policy{i}", expiry_date=expiry, cost=50, car_id=i))
        session.add(Notification(id=i, date=today, type="Info", message=f"Notification {i}", car_id=i, driver_id=i))
        start = today - datetime.timedelta(days=30)
        end = today
        session.add(Report(id=i, start_date=start, end_date=end, type="CarsPark", data=f"Report data {i}"))

    session.commit()
    session.close()
    print("Database seeded with sample data.")

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    seed_database()
    app.run(debug=True)

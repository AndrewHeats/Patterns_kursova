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

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

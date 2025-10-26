import datetime
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.Trip import Trip
from models.Car import Car
from models.Driver import Driver
from models.Maintenance import Maintenance
from models.FuelCost import FuelCost
from controllers.Observer import FleetManagerObserver

trip_bp = Blueprint('trip', __name__)
engine = create_engine('sqlite:///fleet.db')
Session = sessionmaker(bind=engine)

@trip_bp.route('/')
def list_trips():
    session = Session()
    trips = session.query(Trip).all()
    session.close()
    return render_template('trips/trips.html', trips=trips)

@trip_bp.route('/add', methods=['GET', 'POST'])
def add_trip():
    session = Session()
    observer = FleetManagerObserver(session)
    cars = session.query(Car).all()
    drivers = session.query(Driver).all()
    if request.method == 'POST':
        data = request.form
        trip_date = datetime.datetime.strptime(data['date'], "%Y-%m-%d").date()
        car_id = int(data['car_id'])
        driver_id = int(data['driver_id'])
        car = session.query(Car).filter_by(id=car_id).first()
        driver = session.query(Driver).filter_by(id=driver_id).first()
        if car and car.technical_state == "Broke":
            observer.update({
                'type': "CarBrokeTripBlocked",
                'message': f"Автомобіль #{car.id} зламаний — поїздку неможливо створити!",
                'car_id': car.id,
                'driver_id': driver.id
            })
            html = render_template('trips/trips_add.html', cars=cars, drivers=drivers,
                                   error="Автомобіль зламаний — поїздку неможливо створити!")
            session.close()
            return html
        if driver and driver.medical_checks == "Not Passed":
            observer.update({
                'type': "MedicalCheckFailed",
                'message': f"Водій #{driver.id} не пройшов медогляд!",
                'car_id': car.id,
                'driver_id': driver.id
            })
            html = render_template('trips/trips_add.html', cars=cars, drivers=drivers,
                                   error="Водій не пройшов медогляд — поїздка неможлива.")
            session.close()
            return html
        active_maint = session.query(Maintenance).filter(
            Maintenance.car_id == car_id,
            Maintenance.done == False,
            Maintenance.date <= trip_date
        ).first()
        if active_maint:
            observer.update({
                'type': "MaintenanceConflict",
                'message': f"Авто #{car_id} має незавершене ТО від {active_maint.date}!",
                'car_id': car_id,
                'driver_id': driver_id
            })
            html = render_template('trips/trips_add.html', cars=cars, drivers=drivers,
                                   error="Автомобіль має незавершене ТО — поїздку неможливо!")
            session.close()
            return html
        conflict_trip = session.query(Trip).filter(
            Trip.date == trip_date,
            ((Trip.car_id == car_id) | (Trip.driver_id == driver_id))
        ).first()
        if conflict_trip:
            observer.update({
                'type': "TripConflict",
                'message': f"Авто #{car_id} або водій #{driver_id} вже мають поїздку на {trip_date}!",
                'car_id': car_id,
                'driver_id': driver_id
            })
            html = render_template('trips/trips_add.html', cars=cars, drivers=drivers,
                                   error="Цього дня водій або авто вже зайняті!")
            session.close()
            return html
        trip = Trip(
            date=trip_date,
            route=data['route'],
            distance=float(data['distance']),
            car_id=car_id,
            driver_id=driver_id
        )
        session.add(trip)
        session.commit()
        fuelcost = FuelCost(
            date=trip.date,
            type="Petrol",
            cost=round(trip.distance/100*2.3*58.11, 2),
            car_id=trip.car_id
        )
        session.add(fuelcost)
        session.commit()
        session.close()
        return redirect(url_for('trip.list_trips'))
    session.close()
    return render_template('trips/trips_add.html', cars=cars, drivers=drivers)

@trip_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_trip(id):
    session = Session()
    observer = FleetManagerObserver(session)
    trip = session.query(Trip).filter_by(id=id).first()
    cars = session.query(Car).all()
    drivers = session.query(Driver).all()
    if not trip:
        session.close()
        return "Поїздку не знайдено", 404
    if request.method == 'POST':
        data = request.form
        trip.date = datetime.datetime.strptime(data['date'], "%Y-%m-%d").date()
        trip.route = data['route']
        trip.distance = float(data['distance'])
        trip.car_id = int(data['car_id'])
        trip.driver_id = int(data['driver_id'])
        session.commit()
        session.close()
        return redirect(url_for('trip.list_trips'))
    session.close()
    return render_template('trips/trips_edit.html', trip=trip, cars=cars, drivers=drivers)

@trip_bp.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_trip_view(id):
    session = Session()
    trip = session.query(Trip).filter_by(id=id).first()
    if not trip:
        session.close()
        return "Поїздка не знайдена", 404
    if request.method == 'POST':
        session.delete(trip)
        session.commit()
        session.close()
        return redirect(url_for('trip.list_trips'))
    session.close()
    return render_template('trips/trips_delete.html', trip=trip)

@trip_bp.route('/api', methods=['GET'])
def api_get_trips():
    session = Session()
    trips = session.query(Trip).all()
    data = [{
        "id": t.id, "date": t.date.isoformat(), "route": t.route,
        "distance": t.distance, "car_id": t.car_id, "driver_id": t.driver_id
    } for t in trips]
    session.close()
    return jsonify(data)

@trip_bp.route('/api', methods=['POST'])
def api_add_trip():
    session = Session()
    data = request.json
    trip = Trip(
        date=datetime.datetime.strptime(data['date'], "%Y-%m-%d").date(),
        route=data['route'],
        distance=data['distance'],
        car_id=data['car_id'],
        driver_id=data['driver_id']
    )
    session.add(trip)
    session.commit()
    fuelcost = FuelCost(
        date=trip.date,
        type="Trip fuel cost",
        cost=0.0,
        car_id=trip.car_id
    )
    session.add(fuelcost)
    session.commit()
    session.close()
    return jsonify({'message': 'Поїздку створено'}), 201

@trip_bp.route('/api/<int:id>', methods=['PUT'])
def api_update_trip(id):
    session = Session()
    trip = session.query(Trip).filter_by(id=id).first()
    if not trip:
        session.close()
        return jsonify({'error': 'Поїздку не знайдено'}), 404
    data = request.json
    trip.date = datetime.datetime.strptime(data['date'], "%Y-%m-%d").date()
    trip.route = data['route']
    trip.distance = data['distance']
    trip.car_id = data['car_id']
    trip.driver_id = data['driver_id']
    session.commit()
    session.close()
    return jsonify({'message': 'Поїздку оновлено'})

@trip_bp.route('/api/<int:id>', methods=['DELETE'])
def api_delete_trip(id):
    session = Session()
    trip = session.query(Trip).filter_by(id=id).first()
    if not trip:
        session.close()
        return jsonify({'error': 'Поїздку не знайдено'}), 404
    session.delete(trip)
    session.commit()
    session.close()
    return jsonify({'message': 'Поїздку видалено'})

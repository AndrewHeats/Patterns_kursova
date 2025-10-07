import datetime
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.Trip import Trip
from models.Car import Car
from models.Driver import Driver

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
    cars = session.query(Car).all()
    drivers = session.query(Driver).all()
    if request.method == 'POST':
        data = request.form
        trip = Trip(
            date=datetime.datetime.strptime(data['date'], "%Y-%m-%d").date(),
            route=data['route'],
            distance=float(data['distance']),
            car_id=int(data['car_id']),
            driver_id=int(data['driver_id'])
        )
        session.add(trip)
        session.commit()
        session.close()
        return redirect(url_for('trip.list_trips'))
    session.close()
    return render_template('trips/trips_add.html', cars=cars, drivers=drivers)

@trip_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_trip(id):
    session = Session()
    trip = session.query(Trip).filter_by(id=id).first()
    cars = session.query(Car).all()
    drivers = session.query(Driver).all()
    if not trip:
        session.close()
        return "Поїздка не знайдена", 404
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
def delete_trip(id):
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

# API: додати поїздку
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
    session.close()
    return jsonify({'message': 'Запис додано'}), 201

# API: отримати всі поїздки
@trip_bp.route('/api', methods=['GET'])
def api_get_trips():
    session = Session()
    trips = session.query(Trip).all()
    results = []
    for t in trips:
        results.append({
            "id": t.id,
            "date": t.date.isoformat(),
            "route": t.route,
            "distance": t.distance,
            "car_id": t.car_id,
            "driver_id": t.driver_id
        })
    session.close()
    return jsonify(results)

# API: оновити поїздку
@trip_bp.route('/api/<int:id>', methods=['PUT'])
def api_update_trip(id):
    session = Session()
    trip = session.query(Trip).filter_by(id=id).first()
    if not trip:
        session.close()
        return jsonify({'error': 'Поїздка не знайдена'}), 404
    data = request.json
    trip.date = datetime.datetime.strptime(data['date'], "%Y-%m-%d").date()
    trip.route = data['route']
    trip.distance = data['distance']
    trip.car_id = data['car_id']
    trip.driver_id = data['driver_id']
    session.commit()
    session.close()
    return jsonify({'message': 'Запис оновлено'})

# API: видалити поїздку
@trip_bp.route('/api/<int:id>', methods=['DELETE'])
def api_delete_trip(id):
    session = Session()
    trip = session.query(Trip).filter_by(id=id).first()
    if not trip:
        session.close()
        return jsonify({'error': 'Поїздка не знайдена'}), 404
    session.delete(trip)
    session.commit()
    session.close()
    return jsonify({'message': 'Запис видалено'})

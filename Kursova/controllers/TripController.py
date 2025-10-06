from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.Car import Car
from models.Driver import Driver
from models.Trip import Trip

trip_bp = Blueprint('trip', __name__)
engine = create_engine('sqlite:///fleet.db')
Session = sessionmaker(bind=engine)


@trip_bp.route('/trips', methods=['POST'])
def start_trip():
    session = Session()
    data = request.json
    car = session.query(Car).filter_by(id=data['car_id']).first()
    driver = session.query(Driver).filter_by(id=data['driver_id']).first()
    if car.technical_state != "добрий":
        session.close()
        return jsonify({'error': 'Авто не готове до виїзду!'}), 400
    if driver.medical_checks != "пройдено":
        session.close()
        return jsonify({'error': 'У водія не пройдено медогляд!'}), 400
    trip = Trip(**data)
    session.add(trip)
    session.commit()
    session.close()
    return jsonify({'message': 'Поїздка розпочата'}), 201


@trip_bp.route('/trips', methods=['GET'])
def get_trips():
    session = Session()
    trips = session.query(Trip).all()
    result = [{"id": t.id, "date": t.date, "route": t.route, "distance": t.distance, "car_id": t.car_id,
               "driver_id": t.driver_id} for t in trips]
    session.close()
    return jsonify(result)


@trip_bp.route('/trips/<int:id>', methods=['PUT'])
def update_trip(id):
    session = Session()
    trip = session.query(Trip).filter_by(id=id).first()
    if not trip:
        session.close()
        return jsonify({'error': 'Поїздка не знайдена'}), 404
    for key, value in request.json.items():
        setattr(trip, key, value)
    session.commit()
    session.close()
    return jsonify({'message': 'Поїздка оновлена'})


@trip_bp.route('/trips/<int:id>', methods=['DELETE'])
def delete_trip(id):
    session = Session()
    trip = session.query(Trip).filter_by(id=id).first()
    if not trip:
        session.close()
        return jsonify({'error': 'Поїздка не знайдена'}), 404
    session.delete(trip)
    session.commit()
    session.close()
    return jsonify({'message': 'Поїздка видалена'})

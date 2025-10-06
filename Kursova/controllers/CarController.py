import datetime

from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.Car import Car
from models.Notification import Notification

car_bp = Blueprint('car', __name__)
engine = create_engine('sqlite:///fleet.db')
Session = sessionmaker(bind=engine)


@car_bp.route('/cars', methods=['POST'])
def add_car():
    session = Session()
    data = request.json
    exists = session.query(Car).filter_by(vin=data['vin']).first()
    if exists:
        session.close()
        return jsonify({'error': 'Авто з таким VIN вже зареєстровано!'}), 400
    car = Car(**data)
    session.add(car)
    session.commit()
    session.close()
    return jsonify({'message': 'Авто додано!'}), 201


@car_bp.route('/cars', methods=['GET'])
def get_cars():
    session = Session()
    cars = session.query(Car).all()
    result = [{"id": c.id, "brand": c.brand, "model": c.model, "year": c.year, "vin": c.vin,
               "technical_state": c.technical_state} for c in cars]
    session.close()
    return jsonify(result)


@car_bp.route('/cars/<int:id>', methods=['PUT'])
def update_car(id):
    session = Session()
    car = session.query(Car).filter_by(id=id).first()
    if not car:
        session.close()
        return jsonify({'error': 'Автомобіль не знайдено'}), 404
    prev_state = car.technical_state
    for key, value in request.json.items():
        setattr(car, key, value)
    session.commit()
    # Якщо авто стало "Broke"
    if prev_state != "Broke" and car.technical_state == "Broke":
        notification = Notification(
            date=datetime.date.today().isoformat(),
            type="CarBroke",
            message=f"Автомобіль #{car.id} перейшов у стан Broke",
            car_id=car.id)
        session.add(notification)
        session.commit()
    session.close()
    return jsonify({'message': 'Автомобіль оновлено'})


@car_bp.route('/cars/<int:id>', methods=['DELETE'])
def delete_car(id):
    session = Session()
    car = session.query(Car).filter_by(id=id).first()
    if not car:
        session.close()
        return jsonify({'error': 'Автомобіль не знайдено'}), 404
    session.delete(car)
    session.commit()
    session.close()
    return jsonify({'message': 'Автомобіль видалено'})

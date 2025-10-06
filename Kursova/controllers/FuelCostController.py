from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.Car import Car
from models.FuelCost import FuelCost

fuel_bp = Blueprint('fuel', __name__)
engine = create_engine('sqlite:///fleet.db')
Session = sessionmaker(bind=engine)


@fuel_bp.route('/fuel', methods=['POST'])
def add_fuel_cost():
    session = Session()
    data = request.json
    car = session.query(Car).filter_by(id=data['car_id']).first()
    if not car:
        session.close()
        return jsonify({'error': 'Авто не знайдено'}), 400
    fuel = FuelCost(**data)
    session.add(fuel)
    session.commit()
    session.close()
    return jsonify({'message': 'Витрати на паливо додано'}), 201


@fuel_bp.route('/fuel', methods=['GET'])
def get_fuel_costs():
    session = Session()
    costs = session.query(FuelCost).all()
    result = [{"id": f.id, "date": f.date, "type": f.type, "cost": f.cost, "car_id": f.car_id} for f in costs]
    session.close()
    return jsonify(result)


@fuel_bp.route('/fuel/<int:id>', methods=['PUT'])
def update_fuel_cost(id):
    session = Session()
    fuel = session.query(FuelCost).filter_by(id=id).first()
    if not fuel:
        session.close()
        return jsonify({'error': 'Запис не знайдено'}), 404
    for key, value in request.json.items():
        setattr(fuel, key, value)
    session.commit()
    session.close()
    return jsonify({'message': 'Витрати на паливо оновлено'})


@fuel_bp.route('/fuel/<int:id>', methods=['DELETE'])
def delete_fuel_cost(id):
    session = Session()
    fuel = session.query(FuelCost).filter_by(id=id).first()
    if not fuel:
        session.close()
        return jsonify({'error': 'Запис не знайдено'}), 404
    session.delete(fuel)
    session.commit()
    session.close()
    return jsonify({'message': 'Витрати на паливо видалено'})

import datetime
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.FuelCost import FuelCost
from models.Car import Car

fuel_bp = Blueprint('fuel', __name__)
engine = create_engine('sqlite:///fleet.db')
Session = sessionmaker(bind=engine)

@fuel_bp.route('/')
def list_fuelcosts():
    session = Session()
    fuelcosts = session.query(FuelCost).all()
    session.close()
    return render_template('fuelcosts/fuelcosts.html', fuelcosts=fuelcosts)

@fuel_bp.route('/add', methods=['GET', 'POST'])
def add_fuelcost_view():
    session = Session()
    cars = session.query(Car).all()
    if request.method == 'POST':
        data = request.form
        fuelcost = FuelCost(
            date=datetime.datetime.strptime(data['date'], "%Y-%m-%d").date(),
            type=data['type'],
            cost=float(data['cost']),
            car_id=int(data['car_id'])
        )
        session.add(fuelcost)
        session.commit()
        session.close()
        return redirect(url_for('fuel.list_fuelcosts'))
    session.close()
    return render_template('fuelcosts/fuelcosts_add.html', cars=cars)

@fuel_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_fuelcost(id):
    session = Session()
    fuelcost = session.query(FuelCost).filter_by(id=id).first()
    cars = session.query(Car).all()
    if not fuelcost:
        session.close()
        return "Запис не знайдено", 404
    if request.method == 'POST':
        data = request.form
        fuelcost.date = datetime.datetime.strptime(data['date'], "%Y-%m-%d").date()
        fuelcost.type = data['type']
        fuelcost.cost = float(data['cost'])
        fuelcost.car_id = int(data['car_id'])
        session.commit()
        session.close()
        return redirect(url_for('fuel.list_fuelcosts'))
    session.close()
    return render_template('fuelcosts/fuelcosts_edit.html', fuel=fuelcost, cars=cars)

@fuel_bp.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_fuelcost_view(id):
    session = Session()
    fuelcost = session.query(FuelCost).filter_by(id=id).first()
    if not fuelcost:
        session.close()
        return "Запис не знайдено", 404
    if request.method == 'POST':
        session.delete(fuelcost)
        session.commit()
        session.close()
        return redirect(url_for('fuel.list_fuelcosts'))
    session.close()
    return render_template('fuelcosts/fuelcosts_delete.html', fuel=fuelcost)

# API

@fuel_bp.route('/api', methods=['POST'])
def api_add_fuelcost():
    session = Session()
    data = request.json
    fuelcost = FuelCost(
        date=datetime.datetime.strptime(data['date'], "%Y-%m-%d").date(),
        type=data['type'],
        cost=data['cost'],
        car_id=data['car_id']
    )
    session.add(fuelcost)
    session.commit()
    session.close()
    return jsonify({'message': 'Витрати на паливо додано'}), 201

@fuel_bp.route('/api', methods=['GET'])
def api_get_fuelcosts():
    session = Session()
    costs = session.query(FuelCost).all()
    result = [{
        "id": c.id,
        "date": c.date.isoformat(),
        "type": c.type,
        "cost": c.cost,
        "car_id": c.car_id
    } for c in costs]
    session.close()
    return jsonify(result)

@fuel_bp.route('/api/<int:id>', methods=['PUT'])
def api_update_fuelcost(id):
    session = Session()
    fuel = session.query(FuelCost).filter_by(id=id).first()
    if not fuel:
        session.close()
        return jsonify({'error': 'Запис не знайдено'}), 404
    data = request.json
    fuel.date = datetime.datetime.strptime(data['date'], "%Y-%m-%d").date()
    fuel.type = data['type']
    fuel.cost = data['cost']
    fuel.car_id = data['car_id']
    session.commit()
    session.close()
    return jsonify({'message': 'Витрати оновлено'})

@fuel_bp.route('/api/<int:id>', methods=['DELETE'])
def api_delete_fuelcost(id):
    session = Session()
    fuel = session.query(FuelCost).filter_by(id=id).first()
    if not fuel:
        session.close()
        return jsonify({'error': 'Запис не знайдено'}), 404
    session.delete(fuel)
    session.commit()
    session.close()
    return jsonify({'message': 'Витрати видалено'})


from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.Car import Car
from controllers.Observer import FleetManagerObserver
from controllers.MaintenanceController import create_maintenance_for_broken_car


car_bp = Blueprint('car', __name__)
engine = create_engine('sqlite:///fleet.db')
Session = sessionmaker(bind=engine)

@car_bp.route('/')
def list_cars():
    session = Session()
    cars = session.query(Car).all()
    session.close()
    return render_template('cars/cars.html', cars=cars)

@car_bp.route('/add', methods=['GET', 'POST'])
def add_car_view():
    session = Session()
    observer = FleetManagerObserver(session)
    if request.method == 'POST':
        data = request.form
        if session.query(Car).filter_by(vin=data['vin']).first():
            session.close()
            return render_template('cars/cars_add.html', error="Авто з таким VIN вже існує!")

        car = Car(
            brand=data['brand'], model=data['model'],
            year=int(data['year']), vin=data['vin'],
            technical_state=data['technical_state']
        )
        session.add(car)
        session.commit()

        if car.technical_state == "Broke":
            observer.update({
                'type': 'CarBroke',
                'message': f'Автомобіль #{car.id} у стані Broke',
                'car_id': car.id
            })
            create_maintenance_for_broken_car(car.id, session)

        session.close()
        return redirect(url_for('car.list_cars'))
    session.close()
    return render_template('cars/cars_add.html')

@car_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_car(id):
    session = Session()
    observer = FleetManagerObserver(session)
    car = session.query(Car).filter_by(id=id).first()
    if not car:
        session.close()
        return "Авто не знайдено", 404
    if request.method == 'POST':
        data = request.form
        old_state = car.technical_state
        car.brand = data['brand']
        car.model = data['model']
        car.year = int(data['year'])
        car.vin = data['vin']
        car.technical_state = data['technical_state']
        session.commit()

        if old_state != "Broke" and car.technical_state == "Broke":
            observer.update({
                'type': "CarBroke",
                'message': f'Автомобіль #{car.id} перейшов у стан Broke',
                'car_id': car.id
            })
            create_maintenance_for_broken_car(car.id, session)

        session.close()
        return redirect(url_for('car.list_cars'))
    session.close()
    return render_template('cars/cars_edit.html', car=car)

@car_bp.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_car_view(id):
    session = Session()
    car = session.query(Car).filter_by(id=id).first()
    if not car:
        session.close()
        return "Авто не знайдено", 404
    if request.method == 'POST':
        session.delete(car)
        session.commit()
        session.close()
        return redirect(url_for('car.list_cars'))
    session.close()
    return render_template('cars/cars_delete.html', car=car)


# ---------- API ----------
@car_bp.route('/api', methods=['POST'])
def api_add_car():
    session = Session()
    data = request.json
    car = Car(**data)
    session.add(car)
    session.commit()
    session.close()
    return jsonify({'message': 'Авто створено'}), 201

@car_bp.route('/api', methods=['GET'])
def api_get_cars():
    session = Session()
    cars = session.query(Car).all()
    result = [{
        "id": c.id, "brand": c.brand, "model": c.model,
        "year": c.year, "vin": c.vin,
        "technical_state": c.technical_state
    } for c in cars]
    session.close()
    return jsonify(result)

@car_bp.route('/api/<int:id>', methods=['PUT'])
def api_update_car(id):
    session = Session()
    car = session.query(Car).filter_by(id=id).first()
    if not car:
        session.close()
        return jsonify({'error': 'Авто не знайдено'}), 404
    for k, v in request.json.items():
        setattr(car, k, v)
    session.commit()
    session.close()
    return jsonify({'message': 'Оновлено'})

@car_bp.route('/api/<int:id>', methods=['DELETE'])
def api_delete_car(id):
    session = Session()
    car = session.query(Car).filter_by(id=id).first()
    if not car:
        session.close()
        return jsonify({'error': 'Авто не знайдено'}), 404
    session.delete(car)
    session.commit()
    session.close()
    return jsonify({'message': 'Видалено'})

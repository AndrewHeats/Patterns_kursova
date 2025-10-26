
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.Driver import Driver
from controllers.Observer import FleetManagerObserver


driver_bp = Blueprint('driver', __name__)
engine = create_engine('sqlite:///fleet.db')
Session = sessionmaker(bind=engine)

@driver_bp.route('/')
def list_drivers():
    session = Session()
    drivers = session.query(Driver).all()
    session.close()
    return render_template('drivers/drivers.html', drivers=drivers)

@driver_bp.route('/add', methods=['GET', 'POST'])
def add_driver_view():
    session = Session()
    observer = FleetManagerObserver(session)
    if request.method == 'POST':
        data = request.form
        if session.query(Driver).filter_by(license_number=data['license_number']).first():
            session.close()
            return render_template('drivers/drivers_add.html', error="Водій із такою ліцензією вже існує!")

        driver = Driver(
            name=data['name'],
            license_number=data['license_number'],
            experience=int(data['experience']),
            medical_checks=data.get('medical_checks', 'Passed')
        )
        session.add(driver)
        session.commit()
        session.close()
        return redirect(url_for('driver.list_drivers'))
    session.close()
    return render_template('drivers/drivers_add.html')

@driver_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_driver(id):
    session = Session()
    observer = FleetManagerObserver(session)
    driver = session.query(Driver).filter_by(id=id).first()
    if not driver:
        session.close()
        return "Водій не знайдений", 404
    if request.method == 'POST':
        data = request.form
        old_check = driver.medical_checks
        driver.name = data['name']
        driver.license_number = data['license_number']
        driver.experience = int(data['experience'])
        driver.medical_checks = data.get('medical_checks', 'Passed')
        session.commit()

        if old_check == "Passed" and driver.medical_checks != "Passed":
            observer.update({
                'type': 'DriverMedical',
                'message': f'У водія #{driver.id} не пройдений медогляд!',
                'driver_id': driver.id
            })

        session.close()
        return redirect(url_for('driver.list_drivers'))
    session.close()
    return render_template('drivers/drivers_edit.html', driver=driver)

@driver_bp.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_driver(id):
    session = Session()
    driver = session.query(Driver).filter_by(id=id).first()
    if not driver:
        session.close()
        return "Водій не знайдений", 404
    if request.method == 'POST':
        session.delete(driver)
        session.commit()
        session.close()
        return redirect(url_for('driver.list_drivers'))
    session.close()
    return render_template('drivers/drivers_delete.html', driver=driver)


# API: отримати всіх водіїв
@driver_bp.route('/api', methods=['GET'])
def api_get_drivers():
    session = Session()
    drivers = session.query(Driver).all()
    result = [{
        "id": d.id, "name": d.name,
        "license_number": d.license_number,
        "experience": d.experience,
        "medical_checks": d.medical_checks
    } for d in drivers]
    session.close()
    return jsonify(result)

# API: додати водія
@driver_bp.route('/api', methods=['POST'])
def api_add_driver():
    session = Session()
    data = request.json
    driver = Driver(**data)
    session.add(driver)
    session.commit()
    session.close()
    return jsonify({'message': 'Водій доданий'}), 201

# API: оновити водія
@driver_bp.route('/api/<int:id>', methods=['PUT'])
def api_update_driver(id):
    session = Session()
    driver = session.query(Driver).filter_by(id=id).first()
    if not driver:
        session.close()
        return jsonify({'error': 'Водій не знайдений'}), 404
    for k, v in request.json.items():
        setattr(driver, k, v)
    session.commit()
    session.close()
    return jsonify({'message': 'Оновлено'})

# API: видалити водія
@driver_bp.route('/api/<int:id>', methods=['DELETE'])
def api_delete_driver(id):
    session = Session()
    driver = session.query(Driver).filter_by(id=id).first()
    if not driver:
        session.close()
        return jsonify({'error': 'Не знайдено'}), 404
    session.delete(driver)
    session.commit()
    session.close()
    return jsonify({'message': 'Видалено'})

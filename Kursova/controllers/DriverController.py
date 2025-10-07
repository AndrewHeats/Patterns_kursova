import datetime
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.Driver import Driver
from models.Notification import Notification

driver_bp = Blueprint('driver', __name__)
engine = create_engine('sqlite:///fleet.db')
Session = sessionmaker(bind=engine)

# View: список водіїв
@driver_bp.route('/')
def list_drivers():
    session = Session()
    drivers = session.query(Driver).all()
    session.close()
    return render_template('drivers/drivers.html', drivers=drivers)

# View: форма додавання водія
@driver_bp.route('/add', methods=['GET', 'POST'])
def add_driver_view():
    session = Session()
    if request.method == 'POST':
        data = request.form
        exists = session.query(Driver).filter_by(license_number=data['license_number']).first()
        if exists:
            session.close()
            return render_template('drivers/drivers_add.html', error="Водій із такою ліцензією вже існує!")
        new_driver = Driver(
            name=data['name'],
            license_number=data['license_number'],
            experience=int(data['experience']),
            medical_checks=data['medical_checks']
        )
        session.add(new_driver)
        session.commit()
        session.close()
        return redirect(url_for('driver.list_drivers'))
    session.close()
    return render_template('drivers/drivers_add.html')

# View: форма редагування водія
@driver_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_driver(id):
    session = Session()
    driver = session.query(Driver).filter_by(id=id).first()
    if not driver:
        session.close()
        return "Водій не знайдений", 404
    if request.method == 'POST':
        data = request.form
        old_medical = driver.medical_checks
        driver.name = data['name']
        driver.license_number = data['license_number']
        driver.experience = int(data['experience'])
        driver.medical_checks = data['medical_checks']
        session.commit()
        if old_medical == "Passed" and driver.medical_checks != "Passed":
            notif = Notification(
                date=datetime.date.today(),
                type="DriverMedical",
                message=f"У водія #{driver.id} не пройдений медогляд!",
                driver_id=driver.id
            )
            session.add(notif)
            session.commit()
        session.close()
        return redirect(url_for('driver.list_drivers'))
    session.close()
    return render_template('drivers/drivers_edit.html', driver=driver)

# View: видалення водія
@driver_bp.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_driver_view(id):
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

# API: створити водія
@driver_bp.route('/api', methods=['POST'])
def api_add_driver():
    session = Session()
    data = request.json
    exists = session.query(Driver).filter_by(license_number=data['license_number']).first()
    if exists:
        session.close()
        return jsonify({'error': 'Водій із такою ліцензією вже існує!'}), 400
    driver = Driver(**data)
    session.add(driver)
    session.commit()
    session.close()
    return jsonify({'message': 'Водій доданий'}), 201

# API: отримати всіх водіїв
@driver_bp.route('/api', methods=['GET'])
def api_get_drivers():
    session = Session()
    drivers = session.query(Driver).all()
    result = [{"id": d.id, "name": d.name, "license_number": d.license_number,
               "experience": d.experience, "medical_checks": d.medical_checks} for d in drivers]
    session.close()
    return jsonify(result)

# API: оновити водія
@driver_bp.route('/api/<int:id>', methods=['PUT'])
def api_update_driver(id):
    session = Session()
    driver = session.query(Driver).filter_by(id=id).first()
    if not driver:
        session.close()
        return jsonify({'error': 'Водій не знайдений!'}), 404
    prev_med = driver.medical_checks
    for key, value in request.json.items():
        setattr(driver, key, value)
    session.commit()
    if prev_med == "Passed" and driver.medical_checks != "Passed":
        notif = Notification(
            date=datetime.date.today().isoformat(),
            type="DriverMedical",
            message=f"У водія #{driver.id} не пройдений медогляд!",
            driver_id=driver.id)
        session.add(notif)
        session.commit()
    session.close()
    return jsonify({'message': 'Водій оновлений'})

# API: видалити водія
@driver_bp.route('/api/<int:id>', methods=['DELETE'])
def api_delete_driver(id):
    session = Session()
    driver = session.query(Driver).filter_by(id=id).first()
    if not driver:
        session.close()
        return jsonify({'error': 'Водій не знайдений!'}), 404
    session.delete(driver)
    session.commit()
    session.close()
    return jsonify({'message': 'Водій видалений'})

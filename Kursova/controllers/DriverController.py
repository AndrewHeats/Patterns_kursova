import datetime

from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.Driver import Driver
from models.Notification import Notification

driver_bp = Blueprint('driver', __name__)
engine = create_engine('sqlite:///fleet.db')
Session = sessionmaker(bind=engine)


@driver_bp.route('/drivers', methods=['POST'])
def add_driver():
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


@driver_bp.route('/drivers', methods=['GET'])
def get_drivers():
    session = Session()
    drivers = session.query(Driver).all()
    result = [{"id": d.id, "name": d.name, "license_number": d.license_number, "experience": d.experience,
               "medical_checks": d.medical_checks} for d in drivers]
    session.close()
    return jsonify(result)


@driver_bp.route('/drivers/<int:id>', methods=['PUT'])
def update_driver(id):
    session = Session()
    driver = session.query(Driver).filter_by(id=id).first()
    if not driver:
        session.close()
        return jsonify({'error': 'Водій не знайдений!'}), 404
    prev_med = driver.medical_checks
    for key, value in request.json.items():
        setattr(driver, key, value)
    session.commit()
    # Якщо медогляд не "пройдено"
    if prev_med == "пройдено" and driver.medical_checks != "пройдено":
        notif = Notification(
            date=datetime.date.today().isoformat(),
            type="DriverMedical",
            message=f"У водія #{driver.id} не пройдений медогляд!",
            driver_id=driver.id
        )
        session.add(notif)
        session.commit()
    session.close()
    return jsonify({'message': 'Водій оновлений'})


@driver_bp.route('/drivers/<int:id>', methods=['DELETE'])
def delete_driver(id):
    session = Session()
    driver = session.query(Driver).filter_by(id=id).first()
    if not driver:
        session.close()
        return jsonify({'error': 'Водій не знайдений!'}), 404
    session.delete(driver)
    session.commit()
    session.close()
    return jsonify({'message': 'Водій видалений'})

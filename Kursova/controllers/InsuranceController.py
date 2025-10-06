import datetime

from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.Car import Car
from models.Insurance import Insurance
from models.Notification import Notification

ins_bp = Blueprint('ins', __name__)
engine = create_engine('sqlite:///fleet.db')
Session = sessionmaker(bind=engine)


@ins_bp.route('/insurance', methods=['POST'])
def add_insurance():
    session = Session()
    data = request.json
    car = session.query(Car).filter_by(id=data['car_id']).first()
    if not car:
        session.close()
        return jsonify({'error': 'Авто не знайдено'}), 400
    ins = Insurance(
        policy_number=data['policy_number'],
        expiry_date=data['expiry_date'],
        cost=50,
        car_id=car.id
    )
    session.add(ins)
    session.commit()
    expiry = datetime.datetime.strptime(ins.expiry_date, "%Y-%m-%d").date()
    if expiry <= datetime.date.today():
        notif = Notification(
            date=datetime.date.today().isoformat(),
            type="InsuranceExpired",
            message=f"Страховка авто #{car.id} завершилась або завершується сьогодні!",
            car_id=car.id
        )
        session.add(notif)
        session.commit()
    session.close()
    return jsonify({'message': 'Страховку створено'}), 201


@ins_bp.route('/insurance', methods=['GET'])
def get_insurances():
    session = Session()
    ins = session.query(Insurance).all()
    result = [
        {"id": i.id, "policy_number": i.policy_number, "expiry_date": i.expiry_date, "cost": i.cost, "car_id": i.car_id}
        for i in ins]
    session.close()
    return jsonify(result)


@ins_bp.route('/insurance/<int:id>', methods=['PUT'])
def update_insurance(id):
    session = Session()
    ins = session.query(Insurance).filter_by(id=id).first()
    if not ins:
        session.close()
        return jsonify({'error': 'Страхування не знайдено'}), 404
    for key, value in request.json.items():
        setattr(ins, key, value)
    session.commit()
    session.close()
    return jsonify({'message': 'Страхування оновлено'})


@ins_bp.route('/insurance/<int:id>', methods=['DELETE'])
def delete_insurance(id):
    session = Session()
    ins = session.query(Insurance).filter_by(id=id).first()
    if not ins:
        session.close()
        return jsonify({'error': 'Страхування не знайдено'}), 404
    session.delete(ins)
    session.commit()
    session.close()
    return jsonify({'message': 'Страхування видалено'})

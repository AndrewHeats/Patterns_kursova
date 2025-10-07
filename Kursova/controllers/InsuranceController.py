import datetime
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.Insurance import Insurance
from models.Car import Car
from models.Notification import Notification

ins_bp = Blueprint('insurance', __name__)
engine = create_engine('sqlite:///fleet.db')
Session = sessionmaker(bind=engine)

# View: список страховок
@ins_bp.route('/')
def list_insurances():
    session = Session()
    insurances = session.query(Insurance).all()
    session.close()
    return render_template('insurances/insurances.html', insurances=insurances)

# View: додати страховку
@ins_bp.route('/add', methods=['GET', 'POST'])
def add_insurance_view():
    session = Session()
    cars = session.query(Car).all()
    if request.method == 'POST':
        data = request.form
        expiry_date = datetime.datetime.strptime(data['expiry_date'], "%Y-%m-%d").date()
        insurance = Insurance(
            policy_number=data['policy_number'],
            expiry_date=expiry_date,
            cost=float(data['cost']),
            car_id=int(data['car_id'])
        )
        session.add(insurance)
        session.commit()
        if expiry_date <= datetime.date.today():
            notif = Notification(
                date=datetime.date.today(),
                type="InsuranceExpired",
                message=f"Страховка авто #{insurance.car_id} завершилась або завершується!",
                car_id=insurance.car_id
            )
            session.add(notif)
            session.commit()
        session.close()
        return redirect(url_for('insurance.list_insurances'))
    session.close()
    return render_template('insurances/insurances_add.html', cars=cars)

# View: редагувати страховку
@ins_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_insurance(id):
    session = Session()
    insurance = session.query(Insurance).filter_by(id=id).first()
    cars = session.query(Car).all()
    if not insurance:
        session.close()
        return "Страховка не знайдена", 404
    if request.method == 'POST':
        data = request.form
        expiry_date = datetime.datetime.strptime(data['expiry_date'], "%Y-%m-%d").date()
        insurance.policy_number = data['policy_number']
        insurance.expiry_date = expiry_date
        insurance.cost = float(data['cost'])
        insurance.car_id = int(data['car_id'])
        session.commit()
        session.close()
        return redirect(url_for('insurance.list_insurances'))
    session.close()
    return render_template('insurances/insurances_edit.html', insurance=insurance, cars=cars)

# View: видалити страховку
@ins_bp.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_insurance_view(id):
    session = Session()
    insurance = session.query(Insurance).filter_by(id=id).first()
    if not insurance:
        session.close()
        return "Страховка не знайдена", 404
    if request.method == 'POST':
        session.delete(insurance)
        session.commit()
        session.close()
        return redirect(url_for('insurance.list_insurances'))
    session.close()
    return render_template('insurances/insurances_delete.html', insurance=insurance)

# API: додати страховку
@ins_bp.route('/api', methods=['POST'])
def api_add_insurance():
    session = Session()
    data = request.json
    expiry_date = datetime.datetime.strptime(data['expiry_date'], "%Y-%m-%d").date()
    insurance = Insurance(
        policy_number=data['policy_number'],
        expiry_date=expiry_date,
        cost=data['cost'],
        car_id=data['car_id']
    )
    session.add(insurance)
    session.commit()
    session.close()
    return jsonify({'message': 'Страховка додана'}), 201

# API: отримати всі страховки
@ins_bp.route('/api', methods=['GET'])
def api_get_insurances():
    session = Session()
    insurances = session.query(Insurance).all()
    result = [{
        "id": ins.id,
        "policy_number": ins.policy_number,
        "expiry_date": ins.expiry_date.isoformat(),
        "cost": ins.cost,
        "car_id": ins.car_id
    } for ins in insurances]
    session.close()
    return jsonify(result)

# API: оновити страховку
@ins_bp.route('/api/<int:id>', methods=['PUT'])
def api_update_insurance(id):
    session = Session()
    insurance = session.query(Insurance).filter_by(id=id).first()
    if not insurance:
        session.close()
        return jsonify({'error': 'Страховка не знайдена'}), 404
    data = request.json
    insurance.policy_number = data['policy_number']
    insurance.expiry_date = datetime.datetime.strptime(data['expiry_date'], "%Y-%m-%d").date()
    insurance.cost = data['cost']
    insurance.car_id = data['car_id']
    session.commit()
    session.close()
    return jsonify({'message': 'Страховка оновлена'})

# API: видалити страховку
@ins_bp.route('/api/<int:id>', methods=['DELETE'])
def api_delete_insurance(id):
    session = Session()
    insurance = session.query(Insurance).filter_by(id=id).first()
    if not insurance:
        session.close()
        return jsonify({'error': 'Страховка не знайдена'}), 404
    session.delete(insurance)
    session.commit()
    session.close()
    return jsonify({'message': 'Страховка видалена'})

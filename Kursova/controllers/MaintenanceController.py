import datetime
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.Maintenance import Maintenance
from models.Car import Car
from models.Notification import Notification

maintenance_bp = Blueprint('maintenance', __name__)
engine = create_engine('sqlite:///fleet.db')
Session = sessionmaker(bind=engine)

@maintenance_bp.route('/')
def list_maintenances():
    session = Session()
    maintenances = session.query(Maintenance).all()
    session.close()
    return render_template('maintenances/maintenances.html', maintenances=maintenances)

@maintenance_bp.route('/add', methods=['GET', 'POST'])
def add_maintenance_view():
    session = Session()
    cars = session.query(Car).all()
    if request.method == 'POST':
        data = request.form
        maintenance = Maintenance(
            date=datetime.datetime.strptime(data['date'], "%Y-%m-%d").date(),
            type=data['type'],
            cost=float(data['cost']),
            done=(data.get('done', 'false').lower() == 'true'),
            car_id=int(data['car_id'])
        )
        session.add(maintenance)
        session.commit()
        notif = Notification(
            date=datetime.date.today(),
            type="Maintenance",
            message=f"Заплановано ТО {maintenance.type} для авто {maintenance.car_id}",
            car_id=maintenance.car_id
        )
        session.add(notif)
        session.commit()
        session.close()
        return redirect(url_for('maintenance.list_maintenances'))
    session.close()
    return render_template('maintenances/maintenances_add.html', cars=cars)

@maintenance_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_maintenance(id):
    session = Session()
    maintenance = session.query(Maintenance).filter_by(id=id).first()
    cars = session.query(Car).all()
    if not maintenance:
        session.close()
        return "ТО не знайдено", 404
    if request.method == 'POST':
        data = request.form
        maintenance.date = datetime.datetime.strptime(data['date'], "%Y-%m-%d").date()
        maintenance.type = data['type']
        maintenance.cost = float(data['cost'])
        maintenance.done = (data.get('done', 'false').lower() == 'true')
        maintenance.car_id = int(data['car_id'])
        session.commit()
        session.close()
        return redirect(url_for('maintenance.list_maintenances'))
    session.close()
    return render_template('maintenances/maintenances_edit.html', maintenance=maintenance, cars=cars)

@maintenance_bp.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_maintenance_view(id):
    session = Session()
    maintenance = session.query(Maintenance).filter_by(id=id).first()
    if not maintenance:
        session.close()
        return "ТО не знайдено", 404
    if request.method == 'POST':
        session.delete(maintenance)
        session.commit()
        session.close()
        return redirect(url_for('maintenance.list_maintenances'))
    session.close()
    return render_template('maintenances/maintenances_delete.html', maintenance=maintenance)

# API: додати ТО
@maintenance_bp.route('/api', methods=['POST'])
def api_add_maintenance():
    session = Session()
    data = request.json
    maintenance = Maintenance(
        date=datetime.datetime.strptime(data['date'], "%Y-%m-%d").date(),
        type=data['type'],
        cost=data['cost'],
        done=data['done'],
        car_id=data['car_id']
    )
    session.add(maintenance)
    session.commit()
    session.close()
    return jsonify({'message': 'ТО додано'}), 201

# API: отримати всі ТО
@maintenance_bp.route('/api', methods=['GET'])
def api_get_maintenances():
    session = Session()
    maints = session.query(Maintenance).all()
    result = [{
        "id": m.id,
        "date": m.date.isoformat(),
        "type": m.type,
        "cost": m.cost,
        "done": m.done,
        "car_id": m.car_id
    } for m in maints]
    session.close()
    return jsonify(result)

# API: оновити ТО
@maintenance_bp.route('/api/<int:id>', methods=['PUT'])
def api_update_maintenance(id):
    session = Session()
    maintenance = session.query(Maintenance).filter_by(id=id).first()
    if not maintenance:
        session.close()
        return jsonify({'error': 'ТО не знайдено'}), 404
    data = request.json
    maintenance.date = datetime.datetime.strptime(data['date'], "%Y-%m-%d").date()
    maintenance.type = data['type']
    maintenance.cost = data['cost']
    maintenance.done = data['done']
    maintenance.car_id = data['car_id']
    session.commit()
    session.close()
    return jsonify({'message': 'ТО оновлено'})

# API: видалити ТО
@maintenance_bp.route('/api/<int:id>', methods=['DELETE'])
def api_delete_maintenance(id):
    session = Session()
    maintenance = session.query(Maintenance).filter_by(id=id).first()
    if not maintenance:
        session.close()
        return jsonify({'error': 'ТО не знайдено'}), 404
    session.delete(maintenance)
    session.commit()
    session.close()
    return jsonify({'message': 'ТО видалено'})

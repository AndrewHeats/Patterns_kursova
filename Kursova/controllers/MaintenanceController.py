import datetime

from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.Maintenance import Maintenance
from models.Notification import Notification

maintenance_bp = Blueprint('maintenance', __name__)
engine = create_engine('sqlite:///fleet.db')
Session = sessionmaker(bind=engine)


@maintenance_bp.route('/maintenance', methods=['POST'])
def plan_maintenance():
    session = Session()
    data = request.json
    maintenance = Maintenance(**data)
    session.add(maintenance)
    session.commit()
    notif = Notification(
        date=str(datetime.date.today()),
        type="ТО",
        message=f"Заплановано ТО {maintenance.type} для авто id={maintenance.car_id}",
        car_id=maintenance.car_id
    )
    session.add(notif)
    session.commit()
    session.close()
    return jsonify({'message': 'ТО заплановано, повідомлення надіслано'}), 201


@maintenance_bp.route('/maintenance', methods=['GET'])
def get_maintenance():
    session = Session()
    maints = session.query(Maintenance).all()
    result = [{"id": m.id, "date": m.date, "type": m.type, "cost": m.cost, "done": m.done, "car_id": m.car_id} for m in
              maints]
    session.close()
    return jsonify(result)


@maintenance_bp.route('/maintenance/<int:id>', methods=['PUT'])
def update_maintenance(id):
    session = Session()
    maintenance = session.query(Maintenance).filter_by(id=id).first()
    if not maintenance:
        session.close()
        return jsonify({'error': 'ТО не знайдено'}), 404
    for key, value in request.json.items():
        setattr(maintenance, key, value)
    session.commit()
    session.close()
    return jsonify({'message': 'ТО оновлено'})


@maintenance_bp.route('/maintenance/<int:id>', methods=['DELETE'])
def delete_maintenance(id):
    session = Session()
    maintenance = session.query(Maintenance).filter_by(id=id).first()
    if not maintenance:
        session.close()
        return jsonify({'error': 'ТО не знайдено'}), 404
    session.delete(maintenance)
    session.commit()
    session.close()
    return jsonify({'message': 'ТО видалено'})

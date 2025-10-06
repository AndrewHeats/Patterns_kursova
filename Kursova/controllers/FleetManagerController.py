from flask import Blueprint, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.Notification import Notification

fleetmanager_bp = Blueprint('fm', __name__)
engine = create_engine('sqlite:///fleet.db')
Session = sessionmaker(bind=engine)


@fleetmanager_bp.route('/fleet/notifications', methods=['GET'])
def get_all_notifications():
    session = Session()
    nots = session.query(Notification).all()
    result = [
        {"id": n.id, "date": n.date, "type": n.type, "message": n.message, "car_id": n.car_id, "driver_id": n.driver_id}
        for n in nots]
    session.close()
    return jsonify(result)

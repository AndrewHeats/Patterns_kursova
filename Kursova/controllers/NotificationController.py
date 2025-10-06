from flask import Blueprint, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.Notification import Notification

notif_bp = Blueprint('notif', __name__)
engine = create_engine('sqlite:///fleet.db')
Session = sessionmaker(bind=engine)


@notif_bp.route('/notifications', methods=['GET'])
def get_notifications():
    session = Session()
    notifs = session.query(Notification).all()
    result = [
        {"id": n.id, "date": n.date, "type": n.type, "message": n.message, "car_id": n.car_id, "driver_id": n.driver_id}
        for n in notifs]
    session.close()
    return jsonify(result)

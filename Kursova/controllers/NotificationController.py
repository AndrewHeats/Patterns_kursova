from flask import Blueprint, render_template, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.Notification import Notification

notif_bp = Blueprint('notif', __name__)
engine = create_engine('sqlite:///fleet.db')
Session = sessionmaker(bind=engine)

# View: список сповіщень
@notif_bp.route('/')
def list_notifications():
    session = Session()
    # Читаємо параметри з URL
    notif_type = request.args.get('type', default=None)
    date_from = request.args.get('from', default=None)
    date_to = request.args.get('to', default=None)

    query = session.query(Notification)

    if notif_type and notif_type != '' and notif_type != 'Інші':
        query = query.filter(Notification.type == notif_type)
    elif notif_type == 'Інші':
        known_types = ['CarBroke', 'TripConflict', 'Maintenance', 'MaintenanceConflict', 'DriverMedical']
        query = query.filter(~Notification.type.in_(known_types))

    if date_from:
        query = query.filter(Notification.date >= date_from)
    if date_to:
        query = query.filter(Notification.date <= date_to)

    notifications = query.order_by(Notification.date.desc()).all()

    session.close()

    # Передаємо у шаблон для збереження стану фільтра
    return render_template('notifications/notifications.html',
                           notifications=notifications,
                           notif_type=notif_type,
                           date_from=date_from,
                           date_to=date_to)

# API: отримати всі сповіщення
@notif_bp.route('/api', methods=['GET'])
def api_get_notifications():
    session = Session()
    notifs = session.query(Notification).all()
    result = [{
        "id": n.id, "date": n.date.isoformat(), "type": n.type,
        "message": n.message, "car_id": n.car_id, "driver_id": n.driver_id
    } for n in notifs]
    session.close()
    return jsonify(result)

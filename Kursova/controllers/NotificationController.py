import datetime
from flask import Blueprint, jsonify, render_template, request, redirect, url_for
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
    notifications = session.query(Notification).all()
    session.close()
    return render_template('notifications/notifications.html', notifications=notifications)

# View: додати сповіщення (опціонально)
@notif_bp.route('/add', methods=['GET', 'POST'])
def add_notification_view():
    if request.method == 'POST':
        session = Session()
        data = request.form
        notification = Notification(
            date=datetime.datetime.strptime(data['date'], "%Y-%m-%d").date(),
            type=data['type'],
            message=data['message'],
            car_id=int(data['car_id']) if data.get('car_id') else None,
            driver_id=int(data['driver_id']) if data.get('driver_id') else None
        )
        session.add(notification)
        session.commit()
        session.close()
        return redirect(url_for('notif.list_notifications'))
    return render_template('notifications/notifications_add.html')

# View: видалити сповіщення
@notif_bp.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_notification_view(id):
    session = Session()
    notif = session.query(Notification).filter_by(id=id).first()
    if not notif:
        session.close()
        return "Сповіщення не знайдено", 404
    if request.method == 'POST':
        session.delete(notif)
        session.commit()
        session.close()
        return redirect(url_for('notif.list_notifications'))
    session.close()
    return render_template('notifications/notifications_delete.html', notification=notif)

# API: отримати всі сповіщення
@notif_bp.route('/api', methods=['GET'])
def api_get_notifications():
    session = Session()
    notifications = session.query(Notification).all()
    result = []
    for n in notifications:
        result.append({
            "id": n.id,
            "date": n.date.isoformat(),
            "type": n.type,
            "message": n.message,
            "car_id": n.car_id,
            "driver_id": n.driver_id
        })
    session.close()
    return jsonify(result)

# API: створити сповіщення
@notif_bp.route('/api', methods=['POST'])
def api_add_notification():
    session = Session()
    data = request.json
    notification = Notification(
        date=datetime.datetime.strptime(data['date'], "%Y-%m-%d").date(),
        type=data['type'],
        message=data['message'],
        car_id=data.get('car_id'),
        driver_id=data.get('driver_id')
    )
    session.add(notification)
    session.commit()
    session.close()
    return jsonify({'message': 'Сповіщення створено'}), 201

# API: видалити сповіщення
@notif_bp.route('/api/<int:id>', methods=['DELETE'])
def api_delete_notification(id):
    session = Session()
    notification = session.query(Notification).filter_by(id=id).first()
    if not notification:
        session.close()
        return jsonify({'error': 'Сповіщення не знайдено'}), 404
    session.delete(notification)
    session.commit()
    session.close()
    return jsonify({'message': 'Сповіщення видалено'})

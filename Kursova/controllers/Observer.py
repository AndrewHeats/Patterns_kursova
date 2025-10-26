import datetime


class Observer:
    def update(self, notification_data):
        pass


class FleetManagerObserver(Observer):
    def __init__(self, session):
        self.session = session

    def update(self, notification_data):
        from models.Notification import Notification

        notif = Notification(
            date=notification_data.get('date', None) or datetime.date.today(),
            type=notification_data['type'],
            message=notification_data['message'],
            car_id=notification_data.get('car_id'),
            driver_id=notification_data.get('driver_id')
        )
        self.session.add(notif)
        self.session.commit()
        print(f"FleetManager отримав сповіщення: {notif.type} - {notif.message}")

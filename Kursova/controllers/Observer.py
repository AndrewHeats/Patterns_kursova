class Observer:
    def update(self, notification):
        pass


class FleetManagerObserver(Observer):
    def update(self, notification):
        print(f"FleetManager отримав сповіщення: {notification.type} - {notification.message}")

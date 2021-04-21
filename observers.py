class Observer:
    def notify(self, instance):
        raise Exception("Not implemented")


class SubtensorInterfaceObserver(Observer):
    def __init__(self):
        pass

    def notify(self, instance):
        pass


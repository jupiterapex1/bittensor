from loguru import logger




class Observer:
    def notify(self, instance):
        raise Exception("Not implemented")


class SubtensorInterfaceObserver(Observer):
    def __init__(self, if_factory , network : str):
        self.factory = if_factory
        self.network = network

    def notify(self, instance):
        client = instance.get_client()

        if not client:
            logger.debug("No client defined for interface")
            return

        # if not instance.protocol.is_connected:
        #     logger.error("still Connected")

        self.__change_interface(client)

    def __change_interface(self, client):
        interface = self.factory.get_by_network(network=self.network)
        client.set_interface(interface)




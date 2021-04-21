import asyncio

from loguru import logger
from munch import Munch
import random

from bittensor.observers import SubtensorInterfaceObserver
from bittensor.substrate import SubstrateWSInterface
from bittensor.subtensor import Subtensor


class SubtensorEndpointFactory:
    # Hardcoded entry point nodes.
    def __init__(self):

        self.endpoints = {
            "akira": [
                'fermi.akira.bittensor.com:9944',
                'copernicus.akira.bittensor.com:9944',
                'buys.akira.bittensor.com:9944',
                'nobel.akira.bittensor.com:9944',
                'mendeleev.akira.bittensor.com:9944',
                'rontgen.akira.bittensor.com:9944',
                'feynman.akira.bittensor.com:9944',
                'bunsen.akira.bittensor.com:9944',
                'berkeley.akira.bittensor.com:9944',
                'huygens.akira.bittensor.com:9944',
            ],
            "kusanagi": [
                'fermi.kusanagi.bittensor.com:9944',
                'copernicus.kusanagi.bittensor.com:9944',
                'buys.kusanagi.bittensor.com:9944',
                'nobel.kusanagi.bittensor.com:9944',
                'mendeleev.kusanagi.bittensor.com:9944',
                'rontgen.kusanagi.bittensor.com:9944',
                'feynman.kusanagi.bittensor.com:9944',
                'bunsen.kusanagi.bittensor.com:9944',
                'berkeley.kusanagi.bittensor.com:9944',
                'huygens.kusanagi.bittensor.com:9944',
            ],
            "boltzmann": [
                'feynman.boltzmann.bittensor.com:9944',
            ],
            "local": [
                '127.0.0.1:9944'
            ]}



    def get(self, network, blacklist):
        if network not in self.endpoints:
            logger.error("[!] network [{}] not in endpoints list", network)
            return None

        endpoints = self.endpoints[network]
        endpoint_available = [item for item in endpoints if item not in blacklist]
        if len(endpoint_available) == 0:
            return None

        return random.choice(endpoint_available)



class SubtensorInterfaceFactory:
    def __init__(self, endpoint_factory : SubtensorEndpointFactory):
        self.__endpoint_factory = endpoint_factory
        self.__attempted_endpoints = []
        self.__custom_type_registry = {
            "runtime_id": 2,
            "types": {
                "NeuronMetadataOf": {
                    "type": "struct",
                    "type_mapping": [["ip", "u128"], ["port", "u16"], ["ip_type", "u8"], ["uid", "u64"],
                                     ["modality", "u8"], ["hotkey", "AccountId"], ["coldkey", "AccountId"]]
                }
            }
        }


    def get_by_endpoint(self, endpoint : str):
        interface =  self.__get_interface(endpoint)

        # We're not attaching an observer here, because a single endpoint does not have an alternative
        # To reconnect to
        return interface

    def get_by_network(self, network: str):
        interface = None

        while interface is None:
            endpoint = self.__endpoint_factory.get(network=network, blacklist=self.__attempted_endpoints)
            if endpoint is None:
                # We have exhausted the list of available endpoint, break away
                self.__display_no_more_endpoints_message(network)
                self.__connection_error_message()
                return None
            else:
                self.__attempted_endpoints.append(endpoint)
                interface = self.__get_interface(endpoint)

        # At this point, all endpoints have been tested, and we have a valid, connected interface
        # Attach an observer that is able to detect disconnections and init a new connection
        self.__attach_observer(interface, network)

        return interface

    def __attach_observer(self, interface : SubstrateWSInterface, network : str):
        observer = SubtensorInterfaceObserver(self, network)
        interface.add_observer(observer)


    def __get_interface(self, endpoint):
        interface = SubstrateWSInterface(
            address_type=42,
            type_registry_preset='substrate-node-template',
            type_registry=self.__custom_type_registry,
        )

        loop = asyncio.get_event_loop()
        loop.set_debug(enabled=True)

        if loop.run_until_complete(interface.async_connect(endpoint, timeout=5)):
            self.__display_success_message(endpoint)
            return interface
        else:  # Timeout occured
            self.__display_timeout_message(endpoint)
            return None


    ''' Error message helper functions '''

    def __display_no_more_endpoints_message(self, network):
        logger.log('USER-CRITICAL', "No more endpoints available for subtensor.network: {}, attempted: {}".format(
            network, self.__attempted_endpoints))

    def __display_timeout_message(self, endpoint):
        logger.log('USER-CRITICAL', "Error while connecting to the chain endpoint {}".format(endpoint))

    def __display_success_message(self, endpoint):
        logger.log('USER-SUCCESS', "Successfully connected to endpoint: {}".format(endpoint))


    def __connection_error_message(self):
            print('''
    Check that your internet connection is working and the chain endpoints are available: {}
    The subtensor.network should likely be one of the following choices:
        -- local - (your locally running node)
        -- akira - (testnet)
        -- kusanagi - (mainnet)
    Or you may set the endpoint manually using the --subtensor.chain_endpoint flag 
    To run a local node (See: docs/running_a_validator.md) \n
                                  '''.format(self.__attempted_endpoints))


class SubtensorClientFactory:
    def __init__(self, interface_factory: SubtensorInterfaceFactory):
        self.__interface_factory = interface_factory

    def create_by_config(self, config : 'Munch'):
        if config.subtensor.chain_endpoint:
            return self.create_by_endpoint(config.subtensor.chain_endpoint)
        elif config.subtensor.network:
            return self.create_by_network(config.subtensor.network)
        else:
            logger.error("[!] Invalid subtensor config. chain_endpoint and network not defined")
            return None

    def create_by_network(self, network: str):
        interface =  self.__interface_factory.get_by_network(network)
        return self.__build_client(interface)

    def create_by_endpoint(self, endpoint: str):
        interface =  self.__interface_factory.get_by_endpoint(endpoint)
        return self.__build_client(interface)

    def create_default(self):
        config = Subtensor.default_config()
        return self.create_by_config(config)




    def __build_client(self, interface : SubstrateWSInterface):
        client = Subtensor(interface)
        interface.set_client(client)
        return client








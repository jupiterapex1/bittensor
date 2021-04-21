from loguru import logger
from munch import Munch
from numpy.random import random

from bittensor.substrate import SubstrateWSInterface
from bittensor.subtensor import Subtensor


class SubtensorEndpointFactory:
    # Hardcoded entry point nodes.
    def __init__(self):

        self.endpoints = {
            "akira": [
                '104.248.52.148:9944',
                '142.93.194.110:9944',
                '162.243.175.73:9944',
                '165.227.92.237:9944',
                '167.172.141.223:9944',
                '174.138.32.166:9944',
                '206.189.194.236:9944',
                '68.183.130.145:9944',
                '68.183.140.221:9944',
                '68.183.140.251:9944'
            ],
            "kusanagi": [
                '142.93.203.149:9944',
                '157.230.11.1:9944',
                '157.230.11.116:9944',
                '157.230.11.31:9944',
                '157.230.11.36:9944',
                '157.230.11.53:9944',
                '157.230.3.108:9944',
                '159.65.236.189:9944',
                '165.227.81.42:9944',
                '206.189.207.173:9944'
            ],
            "boltzmann": [
                'feynman.boltzmann.bittensor.com:9944',
                '157.230.223.68:9944'
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
        return self.__get_interface(endpoint)

    def get_by_network(self, network: str):
        blacklist = []
        interface = None

        while interface is None:
            endpoint = self.__endpoint_factory.get(network=network, blacklist=blacklist)
            if endpoint is None:
                # We have exhausted the list of available endpoint, break away
                self.__display_no_more_endpoints_message(network)
                self.__connection_error_message()
                return None
            else:
                self.__attempted_endpoints.append(endpoint)
                interface = self.__get_interface(endpoint)

            # At this point, all endpoints have been tested, and we have a valid, connected interface
            return interface


    def __get_interface(self, endpoint):
        interface = SubstrateWSInterface(
            address_type=42,
            type_registry_preset='substrate-node-template',
            type_registry=self.__custom_type_registry,
        )

        if await interface.async_connect(endpoint, timeout=5):
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

    def get_for_config(self, config : 'Munch'):
        if config.subtensor.chain_endpoint:
            return self.get_for_endpoint(config.subtensor.chain_endpoint)
        elif config.subtensor.network:
            return self.get_for_network(config.subtensor.network)
        else:
            logger.error("[!] Invalid subtensor config. chain_endpoint and network not defined")
            return None

    def get_for_network(self, network: str):
        return self.__interface_factory.get_by_network(network)

    def get_for_endpoint(self, endpoint: str):
        return self.__interface_factory.get_by_endpoint(endpoint)

    def get_default(self):
        config = Subtensor.default_config()
        return self.get_for_config(config)







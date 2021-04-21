from bittensor.factories import SubtensorEndpointFactory, SubtensorInterfaceFactory, SubtensorClientFactory

endpointfactory = SubtensorEndpointFactory()
subtensorinterfacefactory = SubtensorInterfaceFactory(endpointfactory)
clientFactory = SubtensorClientFactory(subtensorinterfacefactory)

# client = clientFactory.get_for_network("akira")
# client = clientFactory.get_default()
client = clientFactory.get_for_endpoint("feynman.boltzmann.bittensor.com:9944")

print(client)

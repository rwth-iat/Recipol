import asyncio
from asyncua import Client

async def get_opcua_namespaces(opc_url):
    async with Client(opc_url) as client:
        namespace_array = await client.get_namespace_array()  # Asynchrone Methode!
        for index, namespace in enumerate(namespace_array):
            print(f"Namespace Index {index}: {namespace}")

# OPC UA Server URL
opc_url = "opc.tcp://your-opc-server:4840";

# Asynchrone Methode ausführen
asyncio.run(get_opcua_namespaces(opc_url))
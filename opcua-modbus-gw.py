from pymodbus.client import ModbusTcpClient
from asyncua import Client, ua
import asyncio
import argparse
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("modbus_opcua_integration")

def read_modbus_registers(client, address, count):
    result = client.read_holding_registers(address, count)
    if result.isError():
        log.error(f"Error reading Modbus registers: {result}")
        return []
    log.info(f"Read Modbus registers: {result.registers}")
    return result.registers

async def write_opcua_variable(opcua_client, node_id, value):
    node = opcua_client.get_node(node_id)
    await node.write_value(value)

async def read_opcua_variable(opcua_client, node_id):
    node = opcua_client.get_node(node_id)
    value = await node.read_value()
    return value

async def write_modbus_register(client, address, value):
    result = client.write_register(address, value)
    if result.isError():
        log.error(f"Error writing to Modbus register: {result}")
    else:
        log.info(f"Written value {value} to Modbus address {address}")

class OPCUASubscriptionHandler:
    def __init__(self, modbus_client, start_address):
        self.modbus_client = modbus_client
        self.start_address = start_address

    async def datachange_notification(self, node, val, data):
        log.info(f"Data change event: {node} = {val}")
        address_offset = int(node.nodeid.Identifier) - 2003  # Adjust offset based on node id
        if 0 <= address_offset < 4:
            await write_modbus_register(self.modbus_client, self.start_address + address_offset, int(val))

async def main(modbus_server_host, modbus_server_port, opc_ua_server_url, start_address, register_count):
    modbus_client = ModbusTcpClient(modbus_server_host, port=modbus_server_port)
    opcua_client = Client(opc_ua_server_url)

    try:
        modbus_client.connect()
        await opcua_client.connect()

        # Read Modbus registers and initialize OPC UA server
        registers = read_modbus_registers(modbus_client, start_address, register_count)
        if len(registers) >= 4:
            await write_opcua_variable(opcua_client, "ns=2;i=2003", registers[0])
            await write_opcua_variable(opcua_client, "ns=2;i=2004", registers[1])
            await write_opcua_variable(opcua_client, "ns=2;i=2005", registers[2])
            await write_opcua_variable(opcua_client, "ns=2;i=2006", registers[3])

        # Set up subscription to monitor OPC UA variables
        subscription = await opcua_client.create_subscription(100, OPCUASubscriptionHandler(modbus_client, start_address))
        handles = []
        handles.append(await subscription.subscribe_data_change(opcua_client.get_node("ns=2;i=2003")))
        handles.append(await subscription.subscribe_data_change(opcua_client.get_node("ns=2;i=2004")))
        handles.append(await subscription.subscribe_data_change(opcua_client.get_node("ns=2;i=2005")))
        handles.append(await subscription.subscribe_data_change(opcua_client.get_node("ns=2;i=2006")))

        try:
            while True:
                await asyncio.sleep(1)
        finally:
            for handle in handles:
                await subscription.unsubscribe(handle)
            await subscription.delete()

    finally:
        modbus_client.close()
        await opcua_client.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Modbus to OPC UA Integration Script')
    parser.add_argument('--modbus-server-host', type=str, default='localhost', help='Modbus server host')
    parser.add_argument('--modbus-server-port', type=int, default=5020, help='Modbus server port')
    parser.add_argument('--opc-ua-server-url', type=str, default="opc.tcp://localhost:4840/freeopcua/server/", help='OPC UA server URL')
    parser.add_argument('--start-address', type=int, default=0, help='Starting address for reading Modbus registers')
    parser.add_argument('--register-count', type=int, default=4, help='Number of Modbus registers to read')
    
    args = parser.parse_args()

    asyncio.run(main(args.modbus_server_host, args.modbus_server_port, args.opc_ua_server_url, args.start_address, args.register_count))

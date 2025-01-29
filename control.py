import asyncio

from asyncua import Client, ua

import time

url = "opc.tcp://192.168.0.10:4840"
namespace = "urn:BeckhoffAutomation:Ua:PLC1"


async def main():

    print(f"Connecting to {url} ...")
    async with Client(url=url) as client:
        # Find the namespace index
        nsidx = await client.get_namespace_index(namespace)
        #print(f"Namespace Index for '{namespace}': {nsidx}")

        # check state of dosing
        node = client.get_node("ns=4;s=GVL_MTP.Dosing.StateCur")
        val = await node.read_value()
        if val == 131072:
            # Reset
            node = client.get_node("ns=4;s=GVL_MTP.Dosing.CommandExt")
            dv = ua.DataValue(ua.Variant([2], ua.VariantType.UInt32))
            await node.set_data_value(dv)
        # Turn off operator mode
        node = client.get_node("ns=4;s=GVL_MTP.Dosing.StateOffOp")
        dv = ua.DataValue(ua.Variant([True], ua.VariantType.Boolean))
        await node.set_data_value(dv)
        time.sleep(1)
        # Start automatic mode
        node = client.get_node("ns=4;s=GVL_MTP.Dosing.StateAutOp")
        dv = ua.DataValue(ua.Variant([True], ua.VariantType.Boolean))
        await node.set_data_value(dv)
        # Set procedure value VExt
        node = client.get_node("ns=4;s=GVL_MTP.Dosing.Param_Dosing_Duration.VExt")
        dv = ua.DataValue(ua.Variant([7], ua.VariantType.Int32))
        await node.set_data_value(dv)
        # Set procedure
        node = client.get_node("ns=4;s=GVL_MTP.Dosing.ProcedureExt")
        dv = ua.DataValue(ua.Variant([2], ua.VariantType.UInt32))
        await node.set_data_value(dv)
        # Apply parameter changes
        node = client.get_node("ns=4;s=GVL_MTP.Dosing.ProcParamApplyExt")
        dv = ua.DataValue(ua.Variant([True], ua.VariantType.Boolean))
        await node.set_data_value(dv)
        # Start procedure
        node = client.get_node("ns=4;s=GVL_MTP.Dosing.CommandExt")
        dv = ua.DataValue(ua.Variant([4], ua.VariantType.UInt32))
        await node.set_data_value(dv)
        # read current state
        node = client.get_node("ns=4;s=GVL_MTP.Dosing.StateCur")
        val = await node.read_value()
        while (val != 131072):
            val = await node.read_value()
        # Reset
        node = client.get_node("ns=4;s=GVL_MTP.Dosing.CommandExt")
        dv = ua.DataValue(ua.Variant([2], ua.VariantType.UInt32))
        await node.set_data_value(dv)

        node = client.get_node("ns=4;s=GVL_MTP.Stirring.StateCur")
        val = await node.read_value()
        if val == 131072:
            # Reset
            node = client.get_node("ns=4;s=GVL_MTP.Stirring.CommandExt")
            dv = ua.DataValue(ua.Variant([2], ua.VariantType.UInt32))
            await node.set_data_value(dv)
        # Turn off operator mode
        node = client.get_node("ns=4;s=GVL_MTP.Stirring.StateOffOp")
        dv = ua.DataValue(ua.Variant([True], ua.VariantType.Boolean))
        await node.set_data_value(dv)
        time.sleep(1)
        # Start automatic mode
        node = client.get_node("ns=4;s=GVL_MTP.Stirring.StateAutOp")
        dv = ua.DataValue(ua.Variant([True], ua.VariantType.Boolean))
        await node.set_data_value(dv)
        # Set procedure value VExt
        node = client.get_node("ns=4;s=GVL_MTP.Stirring.Param_Stirring_Duration.VExt")
        dv = ua.DataValue(ua.Variant([5], ua.VariantType.Int32))
        await node.set_data_value(dv)
        # Set procedure
        node = client.get_node("ns=4;s=GVL_MTP.Stirring.ProcedureExt")
        dv = ua.DataValue(ua.Variant([2], ua.VariantType.UInt32))
        await node.set_data_value(dv)
        # Apply parameter changes
        node = client.get_node("ns=4;s=GVL_MTP.Stirring.ProcParamApplyExt")
        dv = ua.DataValue(ua.Variant([True], ua.VariantType.Boolean))
        await node.set_data_value(dv)
        # Start procedure
        node = client.get_node("ns=4;s=GVL_MTP.Stirring.CommandExt")
        dv = ua.DataValue(ua.Variant([4], ua.VariantType.UInt32))
        await node.set_data_value(dv)
        # read current state
        node = client.get_node("ns=4;s=GVL_MTP.Stirring.StateCur")
        val = await node.read_value()
        while (val != 131072):
            val = await node.read_value()
        # Reset
        node = client.get_node("ns=4;s=GVL_MTP.Stirring.CommandExt")
        dv = ua.DataValue(ua.Variant([2], ua.VariantType.UInt32))
        await node.set_data_value(dv)
        # val = await node.read_value()
        # print(f"Current State: {val}")

        # new_value = value - 50
        # print(f"Setting value of MyVariable to {new_value} ...")
        # await var.write_value(new_value)

        # # Calling a method
        # res = await client.nodes.objects.call_method(f"{nsidx}:ServerMethod", 5)
        # print(f"Calling ServerMethod returned {res}")


if __name__ == "__main__":
    asyncio.run(main())
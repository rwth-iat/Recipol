import asyncio

from asyncua import Client, ua

import time

import orchestration as oc

### static variables
url = "opc.tcp://192.168.0.10:4840"
namespace = "urn:BeckhoffAutomation:Ua:PLC1"
proc = oc.procedure

async def main():

    print(f"Connecting to {url} ...")
    async with Client(url=url) as client:
        # Find the namespace index
        # nsidx = await client.get_namespace_index(namespace)
        nsid, nsidx = await client.get_namespace_array()
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
    matFlag = True
    # preliminary check for material requirements
    for p in proc:
        if type(p) is list:
            if type(p[0]) is dict:
                # step in a parallel function
                pass
        else:
            if type(p) is dict:
                # simple step
                for r in p['bml'].reqs:
                    if "Material" in r.const:
                        # check by operator
                        material = r.const[r.const.rfind("=")+1:]
                        ack = input(f"Step {p['bml'].name} only allows {material}. Please ensure that only {material} is used. Press 'y' to continue, press any other key to terminate.")
                        if ack.lower() == "y":
                            continue
                        else:
                            matFlag = False
                            break
    if matFlag:
        for p in proc:
            if type(p) is list:
                if type(p[0]) is dict:
                    # step in a parallel function
                    pass
                else:
                    # transition in a parallel function
                    pass
            else:
                if type(p) is dict:
                    # simple step
                    if p['mtp'] is None:
                        # either initial or end step
                        continue
                    else:
                        # fetch opc url if different from current url
                        if p['mtp'].url != url:
                            url = p['mtp'].url




    asyncio.run(main())

### main

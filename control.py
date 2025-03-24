import asyncio
from asyncua import Client, ua
import time
import orchestration as oc
from typing import Any
import mtpparser as mtp

### static variables
url = "opc.tcp://192.168.0.10:4840"
namespace = "urn:BeckhoffAutomation:Ua:PLC1"
#proc = oc.procedure
#print(proc)
pea = mtp.mtps[0]

def getUaType(dtype:str) -> ua.VariantType:
    match(dtype):
        case "DWORD":
            return ua.VariantType.UInt32
        case "STRING":
            return ua.VariantType.String
        case "BOOL":
            return ua.VariantType.Boolean
        case "BYTE":
            return ua.VariantType.Byte
        case "REAL":
            return ua.VariantType.Int32
        case "INT":
            return ua.VariantType.Int16

async def getNamespace(opcurl:str) -> str:
    async with Client(url=opcurl) as client:
            ns = None
            res = await client.get_namespace_array()
            nsarray = [entry for entry in res if entry.startswith("urn")]
            print("Following namespaces detected:")
            for i in range(len(nsarray)):
                print(f"{i}: {nsarray[i]}")
            while ns is None:
                ns = input("Please enter the number of the namespace to be used.")
                if not ns.isdecimal():
                    print("Not a valid number.")
                    ns = None 
            return ns
    
async def writeNodeValue(opcurl:str, nsIndex:str, nodeAddress:str, value:Any, variantType:ua.VariantType) -> None:
    async with Client(url=opcurl) as client:
        node = client.get_node(f"ns={nsIndex};s={nodeAddress}")
        dv = ua.DataValue(ua.Variant([value], variantType))
        await node.set_data_value(dv)

async def readNodeValue(opcurl:str, nsIndex:str, nodeAddress:str) -> Any:
    async with Client(url=opcurl) as client:
        node = client.get_node(f"ns={nsIndex};s={nodeAddress}")
        val = await node.read_value()
        return val
    
def changeParameterValue(opcurl:str, mode:str, nsIndex:str, param:mtp.Instance, value:Any) -> None:
    if mode == "op":
        # set value in operator mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=param.paramElem['VOp']['ID'], value=value, variantType=ua.VariantType.Int32))
        # apply parameter changes
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=param.paramElem['ProcParamApplyOp']['ID'], value=True, variantType=ua.VariantType.Boolean))
    elif mode == "aut":
        # set value in automatic mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=param.paramElem['VExt']['ID'], value=value, variantType=ua.VariantType.Int32))
        # apply parameter changes
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=param.paramElem['ProcParamApplyExt']['ID'], value=True, variantType=ua.VariantType.Boolean))

def setProcedure(opcurl:str, mode:str, nsIndex:str, service:mtp.Service, procId:int) -> None:
    if mode == "op":
        # set value in operator mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['ProcedureOp']['ID'], value=procId, variantType=ua.VariantType.UInt32))
        # apply parameter changes
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['ProcParamApplyOp']['ID'], value=procId, variantType=ua.VariantType.Boolean))
    elif mode == "aut":
        # set value in automatic mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['ProcedureExt']['ID'], value=procId, variantType=ua.VariantType.UInt32))
        # apply parameter changes
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['ProcParamApplyExt']['ID'], value=procId, variantType=ua.VariantType.Boolean))

def startService(opcurl:str, mode:str, nsIndex:str, service:mtp.Service) -> None:
    if mode == "op":
        # run service in operator mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandOp']['ID'], value=4, variantType=ua.VariantType.UInt32))
    elif mode == "aut":
        # run service in automatic mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandExt']['ID'], value=4, variantType=ua.VariantType.UInt32))

def resetService(opcurl:str, mode:str, nsIndex:str, service:mtp.Service) -> None:
    if mode == "op":
        # run service in operator mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandOp']['ID'], value=2, variantType=ua.VariantType.UInt32))
    elif mode == "aut":
        # run service in automatic mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandExt']['ID'], value=2, variantType=ua.VariantType.UInt32))

def stopService(opcurl:str, mode:str, nsIndex:str, service:mtp.Service) -> None:
    if mode == "op":
        # run service in operator mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandOp']['ID'], value=8, variantType=ua.VariantType.UInt32))
    elif mode == "aut":
        # run service in automatic mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandExt']['ID'], value=8, variantType=ua.VariantType.UInt32))

def holdService(opcurl:str, mode:str, nsIndex:str, service:mtp.Service) -> None:
    if mode == "op":
        # run service in operator mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandOp']['ID'], value=16, variantType=ua.VariantType.UInt32))
    elif mode == "aut":
        # run service in automatic mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandExt']['ID'], value=16, variantType=ua.VariantType.UInt32))

def unholdService(opcurl:str, mode:str, nsIndex:str, service:mtp.Service) -> None:
    if mode == "op":
        # run service in operator mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandOp']['ID'], value=32, variantType=ua.VariantType.UInt32))
    elif mode == "aut":
        # run service in automatic mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandExt']['ID'], value=32, variantType=ua.VariantType.UInt32))

def pauseService(opcurl:str, mode:str, nsIndex:str, service:mtp.Service) -> None:
    if mode == "op":
        # run service in operator mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandOp']['ID'], value=64, variantType=ua.VariantType.UInt32))
    elif mode == "aut":
        # run service in automatic mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandExt']['ID'], value=64, variantType=ua.VariantType.UInt32))

def resumeService(opcurl:str, mode:str, nsIndex:str, service:mtp.Service) -> None:
    if mode == "op":
        # run service in operator mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandOp']['ID'], value=128, variantType=ua.VariantType.UInt32))
    elif mode == "aut":
        # run service in automatic mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandExt']['ID'], value=128, variantType=ua.VariantType.UInt32))

def abortService(opcurl:str, mode:str, nsIndex:str, service:mtp.Service) -> None:
    if mode == "op":
        # run service in operator mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandOp']['ID'], value=256, variantType=ua.VariantType.UInt32))
    elif mode == "aut":
        # run service in automatic mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandExt']['ID'], value=256, variantType=ua.VariantType.UInt32))

def restartService(opcurl:str, mode:str, nsIndex:str, service:mtp.Service) -> None:
    if mode == "op":
        # run service in operator mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandOp']['ID'], value=512, variantType=ua.VariantType.UInt32))
    elif mode == "aut":
        # run service in automatic mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandExt']['ID'], value=512, variantType=ua.VariantType.UInt32))

def completeService(opcurl:str, mode:str, nsIndex:str, service:mtp.Service) -> None:
    if mode == "op":
        # run service in operator mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandOp']['ID'], value=1024, variantType=ua.VariantType.UInt32))
    elif mode == "aut":
        # run service in automatic mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandExt']['ID'], value=1024, variantType=ua.VariantType.UInt32))

def setOperationMode(opcurl:str, mode:str, nsIndex:str, service:mtp.Service) -> None:
    if mode == "op":
        # set operation mode to operator
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['StateOpOp']['ID'], value=True, variantType=ua.VariantType.Boolean))
    elif mode == "aut":
        # set operation mode to automatic
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['StateAutOp']['ID'], value=True, variantType=ua.VariantType.Boolean))

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

### main
if __name__ == "__main__":
    # matFlag = True
    # # preliminary check for material requirements
    # for p in proc:
    #     if type(p) is list:
    #         if type(p[0]) is dict:
    #             # step in a parallel function
    #             pass
    #     else:
    #         if type(p) is dict:
    #             # simple step
    #             for r in p['bml'].reqs:
    #                 if "Material" in r.const:
    #                     # check by operator
    #                     material = r.const[r.const.rfind("=")+1:]
    #                     ack = input(f"Step {p['bml'].name} only allows {material}. Please ensure that only {material} is used. Press 'y' to continue, press any other key to terminate.")
    #                     if ack.lower() == "y":
    #                         continue
    #                     else:
    #                         matFlag = False
    #                         break
    # if matFlag:
    #     for p in proc:
    #         if type(p) is list:
    #             if type(p[0]) is dict:
    #                 # step in a parallel function
    #                 pass
    #             else:
    #                 # transition in a parallel function
    #                 pass
    #         else:
    #             if type(p) is dict:
    #                 # simple step
    #                 if p['mtp'] is None:
    #                     # either initial or end step
    #                     continue
    #                 else:
    #                     # fetch opc url if different from current url
    #                     if p['mtp'].url != url:
    #                         url = p['mtp'].url
    # asyncio.run(main())


    service = pea.getService(id="7d5ec92e-5c19-4171-b21b-c17513ddf526")
    print(asyncio.run(readNodeValue(url, 4, service.paramElem['ProcedureOp']['ID'])))
    #print(asyncio.run(writeNodeValue(url, 4, service.paramElem['ProcedureOp']['ID'], 2, ua.VariantType.UInt32)))
    setProcedure(url, "op", 4, service, 0)
    print(asyncio.run(readNodeValue(url, 4, service.paramElem['ProcedureOp']['ID'])))
import asyncio
from asyncua import Client, ua
import time
import orchestration as oc
from typing import Any
import mtpparser as mtp
import csv
import b2mmlparser as bml
import sequenz as seq
import os.path

### global variables
#url = "opc.tcp://192.168.0.10:4840"
url = ""
ns = ""
#namespace = "urn:BeckhoffAutomation:Ua:PLC1"
#pea = mtp.mtps[1]                        

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
        
def getStateByEncoding(code:int) -> str:
    match(code):
        case 1:
            return "Not used"
        case 2:
            return  "Not used"
        case 4:
            return "Stopped"
        case 8:
            return "Starting"
        case 16:
            return "Idle"
        case 32:
            return "Paused"
        case 64:
            return "Execute"
        case 128:
            return "Stopping"
        case 256:
            return "Aborting"
        case 512:
            return "Aborted"
        case 1024:
            return "Holding"
        case 2048:
            return "Held"
        case 4096:
            return "Unholding"
        case 8192:
            return "Pausing"
        case 16384:
            return "Resuming"
        case 32768:
            return "Resetting"
        case 65536:
            return "Completing"
        case 131072:
            return "Completed"
        case _:
            return "Illegal state"

async def getNamespaceId(opcurl:str, ns:str) -> int:
    client = Client(url=opcurl)
    async with client:
        nsid = await client.get_namespace_index(uri=ns)
        return nsid

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
            nsid = await client.get_namespace_index(uri=nsarray[int(ns)])
            return nsid
    
# async def getVariantType(opcurl:str, nsIndex:str, nodeAddress:str):
#     async with Client(url=url) as client:
#         node = client.get_node(f'ns={nsIndex};s={nodeAddress}')
#         val = await node.read_data_type_as_variant_type()
#         return val
    
async def writeNodeValue(opcurl:str, nsIndex:str, nodeAddress:str, value:Any) -> None:
    async with Client(url=opcurl) as client:
        node = client.get_node(f"ns={nsIndex};s={nodeAddress}")
        variantType = await node.read_data_type_as_variant_type()
        dv = ua.DataValue(ua.Variant(value, variantType))
        await node.set_data_value(dv)

async def readNodeValue(opcurl:str, nsIndex:str, nodeAddress:str) -> Any:
    async with Client(url=opcurl) as client:
        node = client.get_node(f"ns={nsIndex};s={nodeAddress}")
        val = await node.read_value()
        return val
    
def changeParameterValue(opcurl:str, mode:str, nsIndex:str, service:mtp.Service, param:mtp.Instance, value:Any) -> None:
    if mode == "op":
        # set source to operator mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=param.paramElem['StateOpOp']['ID'], value=1))
        # set value in operator mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=param.paramElem['VOp']['ID'], value=value))
        # apply parameter changes
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=param.paramElem['ApplyOp']['ID'], value=1))
    elif mode == "aut":
        # set source to automatic mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=param.paramElem['StateAutOp']['ID'], value=1))
        # set value in automatic mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=param.paramElem['VExt']['ID'], value=value))
        # apply parameter changes
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=param.paramElem['ApplyExt']['ID'], value=1))

def setProcedure(opcurl:str, mode:str, nsIndex:str, service:mtp.Service, procId:int) -> None:
    if mode == "op":
        # set value in operator mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['ProcedureOp']['ID'], value=procId))
        # apply parameter changes
        #asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['ProcParamApplyOp']['ID'], value=1))
    elif mode == "aut":
        # set value in automatic mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['ProcedureExt']['ID'], value=procId))
        # apply parameter changes
        #asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['ProcParamApplyExt']['ID'], value=1))

def startService(opcurl:str, mode:str, nsIndex:str, service:mtp.Service) -> None:
    if mode == "op":
        # run service in operator mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandOp']['ID'], value=4))
    elif mode == "aut":
        # run service in automatic mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandExt']['ID'], value=4))

def resetService(opcurl:str, mode:str, nsIndex:str, service:mtp.Service) -> None:
    if mode == "op":
        # run service in operator mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandOp']['ID'], value=2))
    elif mode == "aut":
        # run service in automatic mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandExt']['ID'], value=2))

def stopService(opcurl:str, mode:str, nsIndex:str, service:mtp.Service) -> None:
    if mode == "op":
        # run service in operator mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandOp']['ID'], value=8))
    elif mode == "aut":
        # run service in automatic mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandExt']['ID'], value=8))

def holdService(opcurl:str, mode:str, nsIndex:str, service:mtp.Service) -> None:
    if mode == "op":
        # run service in operator mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandOp']['ID'], value=16))
    elif mode == "aut":
        # run service in automatic mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandExt']['ID'], value=16))

def unholdService(opcurl:str, mode:str, nsIndex:str, service:mtp.Service) -> None:
    if mode == "op":
        # run service in operator mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandOp']['ID'], value=32))
    elif mode == "aut":
        # run service in automatic mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandExt']['ID'], value=32))

def pauseService(opcurl:str, mode:str, nsIndex:str, service:mtp.Service) -> None:
    if mode == "op":
        # run service in operator mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandOp']['ID'], value=64))
    elif mode == "aut":
        # run service in automatic mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandExt']['ID'], value=64))

def resumeService(opcurl:str, mode:str, nsIndex:str, service:mtp.Service) -> None:
    if mode == "op":
        # run service in operator mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandOp']['ID'], value=128))
    elif mode == "aut":
        # run service in automatic mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandExt']['ID'], value=128))

def abortService(opcurl:str, mode:str, nsIndex:str, service:mtp.Service) -> None:
    if mode == "op":
        # run service in operator mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandOp']['ID'], value=256))
    elif mode == "aut":
        # run service in automatic mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandExt']['ID'], value=256))

def restartService(opcurl:str, mode:str, nsIndex:str, service:mtp.Service) -> None:
    if mode == "op":
        # run service in operator mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandOp']['ID'], value=512))
    elif mode == "aut":
        # run service in automatic mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandExt']['ID'], value=512))

def completeService(opcurl:str, mode:str, nsIndex:str, service:mtp.Service) -> None:
    if mode == "op":
        # run service in operator mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandOp']['ID'], value=1024))
    elif mode == "aut":
        # run service in automatic mode
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['CommandExt']['ID'], value=1024))

def setOperationMode(opcurl:str, mode:str, nsIndex:str, service:mtp.Service) -> None:
    if mode == "op":
        # set operation mode to operator
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['StateOpOp']['ID'], value=1))
    elif mode == "aut":
        # set operation mode to automatic
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['StateAutOp']['ID'], value=1))
        # set source to external
        asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['SrcExtOp']['ID'], value=1))

def setOSLevel(opcurl:str, nsIndex:str, service:mtp.Service) -> None:
    # set os level to 1
    asyncio.run(writeNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['OSLevel']['ID'], value=1))

def checkAutomaticMode(opcurl:str, nsIndex:str, service:mtp.Service) -> bool:
    # return the value
    return asyncio.run(readNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['StateAutAct']['ID']))

def checkOperatorMode(opcurl:str, nsIndex:str, service:mtp.Service) -> bool:
    # return the value
    return asyncio.run(readNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['StateOpAct']['ID']))

def checkCurrentState(opcurl:str, nsIndex:str, service:mtp.Service) -> int:
    # return the value
    return asyncio.run(readNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=service.paramElem['StateCur']['ID']))

def readSensorValue(opcurl:str, nsIndex:str, sensor:mtp.Instance) -> Any:
    # get the value of the sensor
    if sensor.paramElem["V"]["ID"] is not None:
        value = asyncio.run(readNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=sensor.paramElem["V"]["ID"]))
    elif sensor.paramElem["VOut"]["ID"] is not None:
        value = asyncio.run(readNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=sensor.paramElem["VOut"]["ID"]))
    elif sensor.paramElem["Pos"]["ID"] is not None:
        value = asyncio.run(readNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=sensor.paramElem["Pos"]["ID"]))
    elif sensor.paramElem["Ctrl"]["ID"] is not None:
        value = asyncio.run(readNodeValue(opcurl=opcurl, nsIndex=nsIndex, nodeAddress=sensor.paramElem["Ctrl"]["ID"]))

    return value

def statusMonitoring(peas:list[mtp.Pea], url:str, idx:str) -> list[dict]:
    # gives an overview of the statuses of the services, sensors and actuators of the current pea
    statuses = [{"Name": "Time", "Value": time.localtime()}]

    for pea in peas:
        url = pea.url
        if pea.nsid != None:
            idx = pea.nsid
        else:
            idx = pea.nsid = asyncio.run(getNamespaceId(url, pea.ns))
        for s in pea.servs:
            s: mtp.Service
            statuses.append({"Name": f"{pea.name}_{s.name}", "ID": s.refid, "Value": getStateByEncoding(code=checkCurrentState(opcurl=url, nsIndex=idx, service=s))})

        for sa in pea.sensacts:
            sa: mtp.Instance
            if sa.paramElem["V"]["ID"] is not None:
                statuses.append({"Name": f"{pea.name}_{sa.name}", "ID": sa.id, "Value": asyncio.run(readNodeValue(opcurl=url, nsIndex=idx, nodeAddress=sa.paramElem["V"]["ID"]))})
            elif sa.paramElem["VOut"]["ID"] is not None:
                statuses.append({"Name": f"{pea.name}_{sa.name}", "ID": sa.id, "Value": asyncio.run(readNodeValue(opcurl=url, nsIndex=idx, nodeAddress=sa.paramElem["VOut"]["ID"]))})
            elif sa.paramElem["Pos"]["ID"] is not None:
                statuses.append({"Name": f"{pea.name}_{sa.name}", "ID": sa.id, "Value": asyncio.run(readNodeValue(opcurl=url, nsIndex=idx, nodeAddress=sa.paramElem["Pos"]["ID"]))})
            elif sa.paramElem["Ctrl"]["ID"] is not None:
                statuses.append({"Name": f"{pea.name}_{sa.name}", "ID": sa.id, "Value": asyncio.run(readNodeValue(opcurl=url, nsIndex=idx, nodeAddress=sa.paramElem["Ctrl"]["ID"]))})
            elif sa.paramElem["FwdCtrl"]["ID"] is not None:
                fwdval = asyncio.run(readNodeValue(opcurl=url, nsIndex=idx, nodeAddress=sa.paramElem["FwdCtrl"]["ID"]))
                revval = asyncio.run(readNodeValue(opcurl=url, nsIndex=idx, nodeAddress=sa.paramElem["RevCtrl"]["ID"]))
                if fwdval == True or fwdval == 1:
                    statuses.append({"Name": f"{pea.name}_{sa.name}", "ID": sa.id, "Value": "1"})
                elif revval == True or revval == 1:
                    statuses.append({"Name": f"{pea.name}_{sa.name}", "ID": sa.id, "Value": "-1"})
                else:
                    statuses.append({"Name": f"{pea.name}_{sa.name}", "ID": sa.id, "Value": "0"})

    return statuses

def main(proc:list[dict[bml.Element, mtp.Pea, mtp.Procedure, list[mtp.Instance]]], mtps:list[mtp.Pea]):
    # initial flags
    matFlag = True
    firstStepFlag = True

    # create filename with current timestamp
    filename = f"Datahistory\\log_{time.strftime('%d-%m-%Y_%H-%M-%S')}.csv"

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
                        r:  bml.Requirement
                        # check by operator
                        material = r.const[r.const.rfind("=")+1:]
                        ack = input(f"Step {p['bml'].name} only allows {material}. Please ensure that only {material} is used. Press 'y' to continue, press any other key to terminate.")
                        if ack.lower() == "y":
                            continue
                        else:
                            matFlag = False
                            return
    # create list of headers
    headers:list[str] = ["Time"]
    for m in mtps:
        for s in m.servs:
            s: mtp.Service
            headers.append(f"{m.name}_{s.name}")
        for sa in m.sensacts:
            sa: mtp.Instance
            headers.append(f"{m.name}_{sa.name}")
    
    if matFlag:
        for p in proc:
            if type(p) is list:
                if type(p[0]) is dict:
                    # To Do: step in a parallel function
                    pass
                else:
                    # To Do: transition in a parallel function
                    pass
            else:
                # draw sequence diagram
                seq.drawSequenceDiagram(p, proc)

                # execute step
                if type(p) is dict:
                    # simple step
                    if p['inst'] is None:
                        # either initial or end step
                        continue
                    else:
                        # fetch service, procedure and parameters
                        global url
                        global ns
                        if url != p['mtp'].url:
                            url = p['mtp'].url
                            ns = p['mtp'].ns
                            if p["mtp"].nsid is None:
                                p["mtp"].nsid = asyncio.run(getNamespaceId(opcurl=url, ns=ns))
                            nsid = p["mtp"].nsid
                            #ns = asyncio.run(getNamespace(opcurl=url))
                        service:mtp.Service = p['mtp'].getService(p['inst'].serviceId)
                        procedure:mtp.Procedure = p['inst']
                        params:list[mtp.Instance] = p['params']

                        # set service to automatic mode
                        setOperationMode(opcurl=url, mode="aut", nsIndex=nsid, service=service)
                        # check if mode has been set
                        while(True):
                            if checkAutomaticMode(opcurl=url, nsIndex=nsid, service=service):
                                break
                        
                        # set procedure
                        setProcedure(opcurl=url, mode="aut", nsIndex=nsid, service=service, procId=procedure.procId)

                        # set paramaters
                        for par in params:
                            changeParameterValue(opcurl=url, mode="aut", nsIndex=nsid, service=service, param=par[0], value=int(par[1]))

                        # check current State
                        currState = checkCurrentState(opcurl=url, nsIndex=nsid, service=service)

                        if currState == 16:
                            # idle, start service
                            startService(opcurl=url, mode="aut", nsIndex=nsid, service=service)
                        elif currState == 131072:
                            # completed, reset and start
                            resetService(opcurl=url, mode="aut", nsIndex=nsid, service=service)
                            startService(opcurl=url, mode="aut", nsIndex=nsid, service=service)
                        elif currState == 512:
                            # aborted, abort
                            return
                        elif currState == 4:
                            # stopped, abort
                            return
                        
                        # short sleep
                        time.sleep(0.5)

                        # status monitoring
                        statuses = statusMonitoring(peas=mtps, url=url, idx=nsid)
                        
                        with open(filename, 'a', newline='') as csvfile:
                            writer = csv.writer(csvfile)
                            if firstStepFlag == True:
                                writer.writerow(headers)
                                firstStepFlag = False
                            rowToWrite = []
                            for head in headers:
                                for s in statuses:
                                    if s["Name"] == head:
                                        if head == "Time":
                                            rowToWrite.append(time.asctime(s["Value"]))
                                        else:
                                            rowToWrite.append(s["Value"])
                                        break
                                else:
                                    rowToWrite.append("NaN")
                            writer.writerow(rowToWrite)
                else:
                    # simple transition
                    # fetch keyword, instance, operator and value
                    if type(p) is tuple:
                        cond:str = p[0].cond
                    else:
                        cond: str = p.cond
                    if cond != "True":
                        if "AND" in cond or "OR" in cond or "NOT" in cond:
                            # To do 
                            pass
                        else:
                            kw = cond[:cond.find(" ")]
                            cond = cond[cond.find(" ")+1:]
                            inst = cond[:cond.find(" ")]
                            cond = cond[cond.find(" ")+1:]
                            op = cond[:cond.find(" ")]
                            cond = cond[cond.find(" ")+1:]
                            value = cond
                    else:
                        kw = cond

                    # check condition
                    if kw == "True":
                        # move on
                        pass
                    elif kw == "Level":
                        # get sensor instance
                        sens = p[1].getInstanceByName(inst)
                        # get sensor value
                        sensval = readSensorValue(url, nsid, sens)
                        match(op):
                            case ">=":
                                while(sensval < float(value)):
                                    sensval = readSensorValue(url, nsid, sens)
                            case ">":
                                while(sensval <= float(value)):
                                    sensval = readSensorValue(url, nsid, sens)
                            case "==":
                                while(sensval != float(value)):
                                    sensval = readSensorValue(url, nsid, sens)
                            case "<=":
                                while(sensval > float(value)):
                                    sensval = readSensorValue(url, nsid, sens)
                            case "<":
                                while(sensval >= float(value)):
                                    sensval = readSensorValue(url, nsid, sens)
                        if procedure.compl:
                            # procedure is self completing, stop service
                            stopService(url, "aut", nsid, service)
                        else:
                            # complete service
                            completeService(url, "aut", nsid, service)
                        while True:
                            state = checkCurrentState(opcurl=url, nsIndex=nsid, service=service)
                            if state == 131072 or state == 4:
                                break
                        # reset service
                        resetService(url, "aut", nsid, service)
                    elif kw == "Temp":
                        # to do
                        # get sensor instance
                        sens = p[1].getInstanceByName(inst)
                        # get sensor value
                        sensval = readSensorValue(url, nsid, sens)
                        match(op):
                            case ">=":
                                while(sensval < float(value)):
                                    sensval = readSensorValue(url, nsid, sens)
                            case ">":
                                while(sensval <= float(value)):
                                    sensval = readSensorValue(url, nsid, sens)
                            case "==":
                                while(sensval != float(value)):
                                    sensval = readSensorValue(url, nsid, sens)
                            case "<=":
                                while(sensval > float(value)):
                                    sensval = readSensorValue(url, nsid, sens)
                            case "<":
                                while(sensval >= float(value)):
                                    sensval = readSensorValue(url, nsid, sens)
                        if procedure.compl:
                            # procedure is self completing, stop service
                            stopService(url, "aut", nsid, service)
                        else:
                            # complete service
                            completeService(url, "aut", nsid, service)
                        while True:
                            state = checkCurrentState(opcurl=url, nsIndex=nsid, service=service)
                            if state == 131072 or state == 4:
                                break
                        # reset service
                        resetService(url, "aut", nsid, service)
                    elif kw == "Material":
                        # already checked, move on
                        pass
                    elif kw == "Step":
                        # fetch the step
                        step = next(s for s in proc if type(s) is dict and s['bml'].name == inst)
                        service = step['mtp'].getService(step['inst'].serviceId)
                        
                        # check step state
                        if value == "Idle":
                            while(True):
                                if checkCurrentState(opcurl=url, nsIndex=nsid, service=service) == 16:
                                    break
                        elif value == "Paused":
                            while(True):
                                if checkCurrentState(opcurl=url, nsIndex=nsid, service=service) == 32:
                                    break
                        elif value == "Held":
                            while(True):
                                if checkCurrentState(opcurl=url, nsIndex=nsid, service=service) == 2048:
                                    break
                        elif value == "Completed":
                            while(True):
                                if checkCurrentState(opcurl=url, nsIndex=nsid, service=service) == 131072:
                                    break
                                elif checkCurrentState(opcurl=url, nsIndex=nsid, service=service) == 4:
                                    # user check
                                    inp = input(f"Step {step.name} has STOPPED. Reset? y/n")
                                    if inp.lower() == "y":
                                        resetService(opcurl=url, mode="aut", nsIndex=nsid, service=service)
                                    return
                                elif checkCurrentState(opcurl=url, nsIndex=nsid, service=service) == 512:
                                    # user check
                                    inp = input(f"Step {step.name} has ABORTED. Reset? y/n")
                                    if inp.lower() == "y":
                                        resetService(opcurl=url, mode="aut", nsIndex=nsid, service=service)
                                    return
                            # reset state
                            resetService(opcurl=url, mode="aut", nsIndex=nsid, service=service)

                            # set all parameters to default
                            params = []
                            # for par in step['inst'].params:
                            #     changeParameterValue(opcurl=url, mode="aut", nsIndex=nsid, service=service, param=par, value=int(par.default))
                            for par in params:
                                changeParameterValue(opcurl=url, mode="aut", nsIndex=nsid, service=service, param=par, value=int(par.default))
                        elif value == "Stopped":
                            while(True):
                                if checkCurrentState(opcurl=url, nsIndex=nsid, service=service) == 4:
                                    break
                        elif value == "Aborted":
                            while(True):
                                if checkCurrentState(opcurl=url, nsIndex=nsid, service=service) == 512:
                                    break
    
### main
if __name__ == "__main__":
    # service = pea.getService(id="8c361264-6ceb-4825-9b55-3b404b33fd5f")
    # proc = service.procs[2]
    # param = proc.params[0]
    # url = "opc.tcp://192.168.0.20:4840"
    
    #setOperationMode(opcurl=url, mode="aut", nsIndex=3, service=service)
    # changeParameterValue(opcurl=url, mode="aut", nsIndex=7, service=service, param=param, value=5)
    #setProcedure(opcurl=url, mode="op", nsIndex=3, service=service, procId=proc.procId)
    # startService(opcurl=url, mode="op", nsIndex=3, service=service)

    # setOperationMode(opcurl=url, mode="aut", nsIndex=3, service=service)
    # resetService(opcurl=url, mode="aut", nsIndex=3, service=service)

    # setOperationMode(opcurl=url, mode="aut", nsIndex=4, service=service)
    # changeParameterValue(opcurl=url, mode="aut", nsIndex=4, service=service, param=param, value=5)
    # setProcedure(opcurl=url, mode="aut", nsIndex=4, service=service, procId=2)
    # startService(opcurl=url, mode="aut", nsIndex=4, service=service)
    # resetService(opcurl=url, mode="aut", nsIndex=4, service=service)
    
    mtps:list[mtp.Pea] = mtp.getMtps()

    procedure = oc.getProcedure()

    # operator sequence check
    print("\n" * 3)
    ack = input("Please enter 'y' if you want to continue with the above procedure, press any other key to stop: ")

    if ack.lower() == "y":
        main(procedure, mtps)
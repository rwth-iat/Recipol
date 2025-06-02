import b2mmlparser as bml
import mtpparser as mtp

procedure = []

### start main
def getProcedure() -> list[dict]:
    sortedList = bml.main()
    mtps = mtp.getMtps()
    thisMtp = None
    for elem in sortedList:
        # iterate over elements in list
        if type(elem) is not list:
            if elem.getType() == "Step":
                elemId:str = elem.getId()
                if ":" in elemId:
                    elemId = elemId[elemId.rfind(":")+1:]
                # map to mtp instance
                for m in mtps:
                    thisMtp = m
                    mInst = m.getProcedure(procId=elemId)
                    if mInst is not None:
                        break
                else:
                    if not (elem.getRecipeElementType() == "Begin" or elem.getRecipeElementType() == "End"):
                        raise RuntimeError(f"Could not find the element {elem.getName()}. Please ensure that the corresponding MTP has been imported.")
                    
                # check for params
                params = []
                bmlparams = elem.getParameter()
                if len(bmlparams) > 0:
                    # fetch corresponding parameter
                    for p in bmlparams:
                        if ":" in p.id:
                            pid = p.id[p.id.rfind(":")+1:]
                        mParam = mInst.getParameter(pid)
                        if mParam is None:
                            raise RuntimeError(f"Invalid parameter ID {p.id}.")
                        else:
                            if p.unit.isdecimal():
                                if int(p.unit) != mParam.unitval and mParam.unitval != 1998:
                                    raise RuntimeError(f"Invalid unit for parameter {mParam.name}. Expected {mParam.unitval}, received {p.unit}.")
                            elif p.unit.lower() != mParam.unit.lower() and mParam.unit != "Maßeinheit nicht bekannt":
                                raise RuntimeError(f"Invalid unit for parameter {mParam.name}. Expected {mParam.unit}, received {p.unit}.")
                            if float(p.value) < mParam.min or float(p.value) > mParam.max:
                                raise RuntimeError(f"Invalid value for parameter {mParam.name}. The value has to be within {mParam.min,mParam.max}")
                            params.append((mParam, p.value))                        
                
                # add tuple
                if elemId == "Init" or elemId == "End":
                    procedure.append({'bml':elem, 'mtp':None, 'inst':mInst, 'params':params})
                else:
                    procedure.append({'bml': elem, 'mtp': thisMtp, 'inst': mInst, 'params': params})
            else:
                # sensor value
                cond = elem.cond
                if not cond.startswith("Step") and not cond.startswith("True"):
                    kw = cond[:cond.find(" ")]
                    cond = cond[cond.find(" ")+1:]
                    instName = cond[:cond.find(" ")]
                    # find instance
                    if thisMtp is not None:
                        inst = thisMtp.getInstanceByName(instName)
                        if inst is None:
                            # check other mtps
                            for m in mtps:
                                if m == thisMtp:
                                    continue
                                else:
                                    inst = m.getInstanceByName(instName)
                                    if inst is not None:
                                        break
                    procedure.append((elem, thisMtp))

                else:
                    # we don't have to match transitions to anything, simpy add
                    procedure.append(elem)
        else:
            # create sublist
            sl = []
            # iterate over items
            for e in elem:
                if e.getType() == "Step":
                    elemId:str = elem.getId()
                    if ":" in elemId:
                        elemId = elemId[elemId.rfind(":")+1:]
                    for m in mtp.mtps:
                        thisMtp = m
                        mInst = m.getProcedure(id=elemId)
                        if mInst is not None:
                            break
                    
                    if e.getName() == "Init" or e.getName() == "End of Procedure":
                        sl.append({'bml':e, 'mtp':None, 'inst':mInst})
                    else:
                        sl.append({'bml': e, 'mtp': thisMtp, 'inst': mInst})
                else:
                    # we don't have to match transitions to anything, simpy add
                    sl.append(e)
            # add sublist to procedure
            procedure.append(sl)

    # user check before continuation
    i = 0
    for p in procedure:
        if i == 0:
            print("     _ _    ")
            i += 1
        if type(p) is list:
            if type(p[0]) is dict:
                print("     |")
                print("  _______")
                print(" |       |")
                print(" |       |")
                print(" |_______|")
        else:
            if type(p) is dict:
                name = p['bml'].getName()
                namelen = len(name)
                print("  ____|____")
                print(" |         |")
                while namelen > 0:
                    print(f" | {name[:7]: <7} |")
                    name = name[7:]
                    namelen = namelen -7
                print(" |_________|")
                print("     _|_")
            else:
                print(f"    |___| - {p.getCond()}")

    ## for debugging only
    # for p in procedure:
    #     if type(p) is list:
    #         for pp in p:
    #             if type(pp) is dict:
    #                 if pp['inst'] is not None:
    #                     print(f"BML: {pp['bml'].getName()}, MTP: {pp['mtp'].name}")
    #                 else:
    #                     print(f"BML: {pp['bml'].getName()}, None")
    #             else:
    #                 print(f"TRANS: {pp.getName()}")
    #     else:
    #         if type(p) is dict:
    #             if p['mtp'] is not None:
    #                 print(f"BML: {p['bml'].getName()}, MTP: {p['mtp'].name}")
    #             else:
    #                 print(f"BML: {p['bml'].getName()}, None")
    #         elif type(p) is tuple:
    #             print(f"TRANS: {p[0].getName()}, MTP: {p[1].name}")
    #         else:
    #             print(f"TRANS: {p.getName()}")

    return procedure

if __name__ == "__main__":
    proc = getProcedure()
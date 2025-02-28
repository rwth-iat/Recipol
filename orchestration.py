import b2mmlparser as bml
import mtpparser as mtp

procedure = []

### start main
for elem in bml.sortedList:
    # iterate over elements in list
    if type(elem) is not list:
        if elem.getType() == "Step":
            elemId:str = elem.getId()
            if ":" in elemId:
                elemId = elemId[elemId.rfind(":")+1:]
            # map to mtp instance
            for m in mtp.mtps:
                mInst = m.getProcedure(id=elemId)
                if mInst is not None:
                    break
            else:
                if not (elem.getRecipeElementType() == "Begin" or elem.getRecipeElementType() == "End"):
                    raise RuntimeError(f"Could not find the element {elem.getName()}. Please ensure that the corresponding MTP has been imported.")
                
            # check for params
            params = elem.getParameter()
            if len(params) > 0:
                # fetch corresponding parameter
                for p in params:
                    if ":" in p.id:
                        pid = p.id[p.id.rfind(":")+1:]
                    mParam = mInst.getParameter(pid)
                    if mParam is None:
                        raise RuntimeError(f"Invalid parameter ID {p.id}.")
                    else:
                        if p.unit.lower() != mParam.unit.lower():
                            raise RuntimeError(f"Invalid unit for parameter {mParam.name}. Expected {mParam.unit}, received {p.unit}.")
                        elif float(p.value) < mParam.min or float(p.value) > mParam.max:
                            raise RuntimeError(f"Invalid value for parameter {mParam.name}. The value has to be within {mParam.min,mParam.max}")
            
            # add tuple
            procedure.append({'bml': elem, 'mtp': mInst})
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
                    mInst = m.getInstance(instId=elemId)
                    if mInst is not None:
                        break
                
                sl.append({'bml': e, 'mtp': mInst})
            else:
                # we don't have to match transitions to anything, simpy add
                sl.append(e)
        # add sublist to procedure
        procedure.append(sl)

# user check before continuation
for p in procedure:
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

print("\n" * 3)
ack = input("Please press 'y' if you want to continue with the above procedure, press any other key to stop: ")

# for p in procedure:
#     if type(p) is list:
#         for pp in p:
#             if type(pp) is dict:
#                 if pp['mtp'] is not None:
#                     print(f"BML: {pp['bml'].getName()}, MTP: {pp['mtp'].getName()}")
#                 else:
#                     print(f"BML: {pp['bml'].getName()}, None")
#             else:
#                 print(f"TRANS: {pp.getName()}")
#     else:
#         if type(p) is dict:
#             if p['mtp'] is not None:
#                 print(f"BML: {p['bml'].getName()}, MTP: {p['mtp'].getName()}")
#             else:
#                 print(f"BML: {p['bml'].getName()}, None")
#         else:
#             print(f"TRANS: {p.getName()}")
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
                mInst = m.getInstance(instId=elemId)
                if mInst is not None:
                    break
            else:
                if not (elem.getRecipeElementType() == "Begin" or elem.getRecipeElementType() == "End"):
                    raise RuntimeError(f"Could not find the element {elem.getName()}. Please ensure that the corresponding MTP has been imported.")                    
            
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

for p in procedure:
    if type(p) is list:
        for pp in p:
            if type(pp) is dict:
                if pp['mtp'] is not None:
                    print(f"BML: {pp['bml'].getName()}, MTP: {pp['mtp'].getName()}")
                else:
                    print(f"BML: {pp['bml'].getName()}, None")
            else:
                print(f"TRANS: {pp.getName()}")
    else:
        if type(p) is dict:
            if p['mtp'] is not None:
                print(f"BML: {p['bml'].getName()}, MTP: {p['mtp'].getName()}")
            else:
                print(f"BML: {p['bml'].getName()}, None")
        else:
            print(f"TRANS: {p.getName()}")
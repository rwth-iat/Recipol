import b2mmlparser as bml
import mtpparser as mtp

procedure = []

### start main
for elem in bml.sortedList:
    # iterate over elements in list
    if type(elem) is not list:
        if elem.getType() == "Step":
            # map to mtp instance
            for m in mtp.mtps:
                mInst = m.getInstance(instId=elem.getId())
                if mInst is not None:
                    break
            
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
                for m in mtp.mtps:
                    mInst = m.getInstance(instId=e.getId())
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
                    print(f"BML: {pp['bml'].getId()}, MTP: {pp['mtp'].getName()}")
                else:
                    print(f"BML: {pp['bml'].getId()}, None")
            else:
                print(f"TRANS: {pp.getId()}")
    else:
        if type(p) is dict:
            if p['mtp'] is not None:
                print(f"BML: {p['bml'].getId()}, MTP: {p['mtp'].getName()}")
            else:
                print(f"BML: {p['bml'].getId()}, None")
        else:
            print(f"TRANS: {p.getId()}")
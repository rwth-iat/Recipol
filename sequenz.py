from b2mmlparser import Element

### start main
def drawSequenceDiagram(currElem:Element, proc:list) -> None:
    i = 0
    for p in proc:
        if i == 0:
            print("      _ _    ")
            i += 1
        if p == currElem:
            # current step or transition
            if type(p) is dict:
                # draw step
                name = p["bml"].name
                namelen = len(name)
                print("   ____|____")
                print(" ||         ||")
                while namelen > 0:
                    print(f" || {name[:7]: <7} ||")
                    name = name[7:]
                    namelen = namelen -7
                print(" ||_________||")
                print("      _|_")
            else:
                # draw transition
                print(f"    ||___|| - {p.getCond()}")
        else:
            # any other step or transition
            if type(p) is dict:
                # draw step
                name = p['bml'].getName()
                namelen = len(name)
                print("   ____|____")
                print("  |         |")
                while namelen > 0:
                    print(f"  | {name[:7]: <7} |")
                    name = name[7:]
                    namelen = namelen -7
                print("  |_________|")
                print("      _|_")
            else:
                # draw transition
                print(f"     |___| - {p.getCond()}")
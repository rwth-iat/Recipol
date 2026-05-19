from .b2mmlparser import Element


def _iter_proc_items(proc: list):
    for p in proc:
        if isinstance(p, list):
            for sub in p:
                yield sub
        else:
            yield p


### start main
def drawSequenceDiagram(currElem, proc: list) -> None:
    i = 0
    for p in _iter_proc_items(proc):
        if i == 0:
            print("      _ _    ")
            i += 1

        is_current = False
        if isinstance(currElem, dict) and isinstance(p, dict):
            is_current = p is currElem
        elif isinstance(currElem, Element):
            if isinstance(p, dict):
                is_current = p.get("bml") is currElem
            elif isinstance(p, tuple):
                is_current = p[0] is currElem
            else:
                is_current = p is currElem

        if is_current:
            # current step or transition
            if isinstance(p, dict):
                # draw step
                name = p["bml"].name
                namelen = len(name)
                print("   ____|____")
                print(" ||         ||")
                while namelen > 0:
                    print(f" || {name[:7]: <7} ||")
                    name = name[7:]
                    namelen = namelen - 7
                print(" ||_________||")
                print("      _|_")
            else:
                # draw transition
                elem = p[0] if isinstance(p, tuple) else p
                print(f"    ||___|| - {elem.getCond()}")
        else:
            # any other step or transition
            if isinstance(p, dict):
                # draw step
                name = p['bml'].getName()
                namelen = len(name)
                print("   ____|____")
                print("  |         |")
                while namelen > 0:
                    print(f"  | {name[:7]: <7} |")
                    name = name[7:]
                    namelen = namelen - 7
                print("  |_________|")
                print("      _|_")
            else:
                # draw transition
                elem = p[0] if isinstance(p, tuple) else p
                print(f"     |___| - {elem.getCond()}")

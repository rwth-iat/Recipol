from defusedxml.ElementTree import parse

### static variables
TESTMTP1 = r"Artefakte\HC10_manifest.aml"
TESTMTP2 = r"Artefakte\HC30_manifest.aml"
TESTMTPS = [TESTMTP1, TESTMTP2]
NAMESPACE = "{http://www.dke.de/CAEX}"

### classes
class Instance:
    def __init__(self, name, id):
        self.name = name # name of the instance
        self.id = id # ID of the instance
        self.refid = None # refID of the instance
        self.min = None # minimal value of the instance
        self.max = None # maximal value of the instance
        self.unit = None # unit of the instance

    def __str__(self):
        descr = f"NAME: {self.name}, ID={self.id}"
        descr += f"\n    Min: {self.min}, Max: {self.max}, Unit: {self.unit}"
        return descr
    
    def addRefId(self, refId: str):
        """Adds a refID to the instance"""
        self.refid = refId
    
    def addMin(self, minVal:float):
        """Adds a low limit value"""
        self.min = minVal

    def addMax(self, maxVal:float):
        """Adds a high limit value"""
        self.max = maxVal

    def addUnit(self, unit:str):
        """Adds a unit"""
        self.unit = unit

    def getName(self) -> str:
        """Returns the name of the instance"""
        return self.name

class Procedure:
    def __init__(self, name:str, id:str):
        self.name = name # name of the procedure
        self.id = id # id of the procedure
        self.params = [] # list of parameters of the procedure
        self.compl = None # flag that says if procedure is self completing or not

    def __str__(self):
        descr = f"NAME: {self.name}, ID: {self.id}"
        descr += f"\n   Parameter: {self.params}"
        descr += f"\n   Self Completing: {self.compl}"
        return descr
    
    def addParameter(self, param:Instance) -> None:
        """Adds a parameter to the procedure"""
        self.params.append(param)

    def setSelfCompleting(self, complFlag:bool) -> None:
        """Sets the self completing flag of the procedure"""
        self.compl = complFlag

class Mtp:
    def __init__(self):
        self.name = "" # name of the mtp 
        self.insts = [] # list of instances
        self.procs = [] # list of procedures

    def __str__(self):
        descr = f"{self.name}\nInstances:"
        for i in self.insts:
            descr += f"\n    {i}"
        descr += f"\nProcedures:"
        for p in self.procs:
            descr += f"\n   {p}"
        return descr

    def nameMtp(self, name:str) -> None:
        """Adds a name to the mtp"""
        self.name = name

    def addInstance(self, inst:Instance) -> None:
        """Adds an instance to the mtp"""
        self.insts.append(inst)

    def hasInstance(self, instId:str) -> bool:
        """Returns true if an instance with the given id exists, otherwise false"""
        for i in self.insts:
            if i.id == instId or i.refid == instId:
                return True
            
        return False
    
    def getInstance(self, instId:str) -> Instance | None:
        """Returns the instance with the given id"""
        for i in self.insts:
            if i.id == instId or i.refid == instId:
                return i
            
        return None

    def addProcedure(self, proc:Procedure) -> None:
        """Adds a procedure to the mtp."""
        self.procs.append(proc)

### functions
def getUnit(unitNr: int) -> str:
    """Returns the unit corresponding to the identifier"""
    match unitNr:
        case 1000:
            return "kelvin"
        case 1001:
            return "degree Celsius"
        case 1002:
            return "degree Fahrenheit"
        case 1005:
            return "degree"
        case 1006:
            return "minute"
        case 1007:
            return "second"
        case 1010:
            return "metre"
        case 1013:
            return "millimetre"
        case 1018:
            return "foot"
        case 1023:
            return "square metre"
        case 1038:
            return "litre"
        case 1041:
            return "hectolitre"
        case 1054:
            return "second"
        case 1058:
            return "minute"
        case 1059:
            return "hour"
        case 1060:
            return "day"
        case 1061:
            return "metre per second"
        case 1077:
            return "hertz"
        case 1081:
            return "kilohertz"
        case 1082:
            return "per second"
        case 1083:
            return "per minute"
        case 1088:
            return "kilogram"
        case 1092:
            return "tonne"
        case 1100:
            return "gram per cubic centimetre"
        case 1105:
            return "gram per litre"
        case 1120:
            return "newton"
        case 1123:
            return "millinewton"
        case 1130:
            return "pascal"
        case 1133:
            return "kilopascal"
        case 1137:
            return "bar"
        case 1138:
            return "millibar"
        case 1149:
            return "millimetre water column"
        case 1175:
            return "watt hour"
        case 1179:
            return "kilowatt hour"
        case 1181:
            return "kilocalorie"
        case 1190:
            return "kilowatt"
        case 1209: 
            return "ampere"
        case 1211:
            return "milliampere"
        case 1221:
            return "ampere hour"
        case 1240:
            return "volt"
        case 1342: 
            return "per cent"
        case 1349:
            return "cubic metre per hour"
        case 1353:
            return "litre per hour"
        case 1384:
            return "mole"
        case 1422:
            return "pH value"

### start main

mtps:list[Mtp] = []

# parse mtp files
for file in TESTMTPS:
    tree = parse(file)
    root = tree.getroot()

    # create mtp object
    mtp = Mtp()
    mtps.append(mtp)

    # parse mtp
    for child in root:
        if child.tag == f"{NAMESPACE}InstanceHierarchy" and child.get("Name") == "ModuleTypePackage":
            # fetch name of mtp
            mtp.nameMtp(name=child.find(f"{NAMESPACE}InternalElement").get("Name"))

            for gchild in child.iter(f"{NAMESPACE}InternalElement"):
                if gchild.get("Name") == "CommunicationSet" or gchild.get("Name") == "Communication":
                    for node in gchild:
                        if node.get("Name") == "InstanceList" or node.get("Name") == "Instances":
                            # parse instances
                            for instNode in node.iter(f"{NAMESPACE}InternalElement"):
                                if instNode.get("Name") == "InstanceList" or instNode.get("Name") == "Instances":
                                    continue
                                inst = Instance(name=instNode.get("Name"), id=instNode.get("ID"))

                                for attrNode in instNode.iter(f"{NAMESPACE}Attribute"):
                                    if attrNode.get("Name") == "RefID":
                                        inst.addRefId(attrNode.findtext(f"{NAMESPACE}Value"))
                                    elif attrNode.get("Name") == "VMin":
                                        inst.addMin(float(attrNode.findtext(f"{NAMESPACE}DefaultValue")))
                                    elif attrNode.get("Name") == "VMax":
                                        inst.addMax(float(attrNode.findtext(f"{NAMESPACE}DefaultValue")))
                                    elif attrNode.get("Name") == "VUnit":
                                        unitId = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        inst.addUnit(getUnit(int(unitId)))

                                # add instance to mtp
                                mtp.addInstance(inst)

        elif child.tag == f"{NAMESPACE}InstanceHierarchy" and child.get("Name") == "Services":
            for gchild in child:
                if gchild.tag == f"{NAMESPACE}InternalElement":
                    servName = gchild.get("Name") # name of the service
                    servId = gchild.get("ID") # id of the service
                    procCount = 0 # number of procedures under service

                    # get procedures
                    for ggchild in gchild:
                        if ggchild.tag == f"{NAMESPACE}InternalElement":
                            procName = ggchild.get("Name") # name of the procedure
                            procId = ggchild.get("ID") # id of the procedure
                            proc = Procedure(name=procName, id=procId)
                            procCount += 1

                            # add the procedure to the mtp's procedures
                            mtp.addProcedure(proc)

                            for paramNode in ggchild:
                                if paramNode.tag == f"{NAMESPACE}InternalElement":
                                    for refNode in paramNode.iter(f"{NAMESPACE}Attribute"):
                                        if refNode.get("Name") == "RefID" and mtp.hasInstance(refNode.findtext(f"{NAMESPACE}Value")):
                                            # get the instance the procedure refers to 
                                            procParam = mtp.getInstance(refNode.findtext(f"{NAMESPACE}Value"))

                                            # add the instance to the procedure's params
                                            proc.addParameter(procParam)
                                elif paramNode.tag == f"{NAMESPACE}Attribute" and paramNode.get("Name") == "IsSelfCompleting":
                                    proc.setSelfCompleting(paramNode.findtext(f"{NAMESPACE}Value"))


                    if procCount == 0:
                        # no procedures, add the service instead
                        mtp.addProcedure(Procedure(name=servName, id=servId))

for m in mtps:
    print(m)
from defusedxml.ElementTree import parse

### static variables
TESTMTP = r"Artefakte\manifest.aml"
NAMESPACE = "{http://www.dke.de/CAEX}"

### classes
class Instance:
    def __init__(self, name, id):
        self.name = name # name of the instance
        self.id = id # refID of the instance
        self.min = None # minimal value of the instance
        self.max = None # maximal value of the instance
        self.unit = None # unit of the instance

    def __str__(self):
        descr = f"NAME: {self.name}, ID={self.id}"
        descr += f"\n    Min: {self.min}, Max: {self.max}, Unit: {self.unit}"
        return descr
    
    def addMin(self, minVal:int):
        """Adds a low limit value"""
        self.min = minVal

    def addMax(self, maxVal:int):
        """Adds a high limit value"""
        self.max = maxVal

    def addUnit(self, unit:str):
        """Adds a unit"""
        self.unit = unit

class Mtp:
    def __init__(self):
        self.name = "" # name of the mtp 
        self.insts = [] # list of instances

    def __str__(self):
        descr = f"{self.name}\nInstances:"
        for i in self.insts:
            descr += f"\n    {i}"
        return descr

    def nameMtp(self, name:str) -> None:
        """Adds a name to the mtp"""
        self.name = name

    def addInstance(self, inst:Instance) -> None:
        """Adds an instance to the mtp"""
        self.insts.append(inst)

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

# parse mtp file
tree = parse(TESTMTP)
root = tree.getroot()

# create mtp object
mtp = Mtp()

# parse mtp
for child in root:
    if child.tag == f"{NAMESPACE}InstanceHierarchy" and child.get("Name") == "ModuleTypePackage":
        # fetch name of mtp
        mtp.nameMtp(name=child.find(f"{NAMESPACE}InternalElement").get("Name"))

        for gchild in child.iter(f"{NAMESPACE}InternalElement"):
            if gchild.get("Name") == "CommunicationSet":
                for node in gchild:
                    if node.get("Name") == "InstanceList":
                        # parse instances
                        for instNode in node.iter(f"{NAMESPACE}InternalElement"):
                            if instNode.get("Name") == "InstanceList":
                                continue
                            inst = Instance(name=instNode.get("Name"), id=instNode.get("ID"))

                            for attrNode in instNode.iter(f"{NAMESPACE}Attribute"):
                                if attrNode.get("Name") == "VMin":
                                    inst.addMin(int(attrNode.findtext(f"{NAMESPACE}DefaultValue")))
                                elif attrNode.get("Name") == "VMax":
                                    inst.addMax(int(attrNode.findtext(f"{NAMESPACE}DefaultValue")))
                                elif attrNode.get("Name") == "VUnit":
                                    unitId = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                    inst.addUnit(getUnit(int(unitId)))

                            # add instance to mtp
                            mtp.addInstance(inst)

print(mtp)
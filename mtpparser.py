from defusedxml.ElementTree import parse

### static variables
TESTMTP1 = r"Artefakte\HC10_2025-04-25.aml"
TESTMTP2 = r"Artefakte\HC20HC40_2025-05-07.aml"
#TESTMTP3 = r"Artefakte\HC30_manifest_new.aml"
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
        self.default = None # default value of the instance
        self.unit = None # unit of the instance
        self.unitval: int = None # numerical identifier of the unit of the instance
        self.paramElem = {'WQC': {'Type': 'BYTE', 'ID': None, 'Default': None},
                          'OSLevel': {'Type': 'BYTE', 'ID': None, 'Default': None},
                          'CommandInfo': {'Type': 'DWORD', 'ID': None, 'Default': None},
                          'CommandOp': {'Type': 'DWORD', 'ID': None, 'Default': None},
                          'CommandInt': {'Type': 'DWORD', 'ID': None, 'Default': None},
                          'CommandExt': {'Type': 'DWORD', 'ID': None, 'Default': None},
                          'ProcedureOp': {'Type': 'DWORD', 'ID': None, 'Default': None},
                          'ProcedureInt': {'Type': 'DWORD', 'ID': None, 'Default': None},
                          'ProcedureExt': {'Type': 'BYTE', 'ID': None, 'Default': None},
                          'StateCur': {'Type': 'DWORD', 'ID': None, 'Default': None},
                          'CommandEn': {'Type': 'DWORD', 'ID': None, 'Default': None},
                          'ProcedureCur': {'Type': 'DWORD', 'ID': None, 'Default': None},
                          'ProcedureReq': {'Type': 'DWORD', 'ID': None, 'Default': None},
                          'Pos': {'Type': 'REAL', 'ID': None, 'Default': None},
                          'PosTextID': {'Type': 'DWORD', 'ID': None, 'Default': None},
                          'InteractQuestionID': {'Type': 'DWORD', 'ID': None, 'Default': None},
                          'InteractAnswerID': {'Type': 'DWORD', 'ID': None, 'Default': None},
                          'InteractAddInfo': {'Type': 'STRING', 'ID': None, 'Default': None},
                          'OSLevel': {'Type': 'BYTE', 'ID': None, 'Default': None},
                          'ApplyEn': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'ApplyExt': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'ApplyOp': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'ApplyInt': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'Sync': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'StateChannel': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'StateOffAut': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'StateOpAut': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'StateAutAut': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'StateOffOp': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'StateOpOp': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'StateAutOp': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'StateOpAct': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'StateAutAct': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'StateOffAct': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'SrcChannel': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'SrcExtAut': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'SrcIntAut': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'SrcIntOp': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'SrcExtOp': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'SrcIntAct': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'SrcExtAct': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'ProcParamApplyEn': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'ProcParamApplyExt': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'ProcParamApplyOp': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'ProcParamApplyInt': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'ConfigParamApplyEn': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'ConfigParamApplyExt': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'ConfigParamApplyOp': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'ConfigParamApplyInt': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'ReportValueFreeze': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'Ctrl': {'Type': 'REAL', 'ID': None, 'Default': None},
                          'FwdCtrl': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'RevCtrl': {'Type': 'BOOL', 'ID': None, 'Default': None},
                          'V': {'Type': 'REAL', 'ID': None, 'Default': None},
                          'VExt': {'Type': 'REAL', 'ID': None, 'Default': None},
                          'VOp': {'Type': 'REAL', 'ID': None, 'Default': None},
                          'VInt': {'Type': 'REAL', 'ID': None, 'Default': None},
                          'VReq': {'Type': 'REAL', 'ID': None, 'Default': None},
                          'VOut': {'Type': 'REAL', 'ID': None, 'Default': None},
                          'VFbk': {'Type': 'REAL', 'ID': None, 'Default': None},
                          'VSclMin': {'Type': 'REAL', 'ID': None, 'Default': None},
                          'VSclMax': {'Type': 'REAL', 'ID': None, 'Default': None},
                          'VUnit': {'Type': 'INT', 'ID': None, 'Default': None},
                          'VMin': {'Type': 'REAL', 'ID': None, 'Default': None},
                          'VMax': {'Type': 'REAL', 'ID': None, 'Default': None}}

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
        self.procId = None # procedure ID
        self.serviceId = None # id of the service the procedure is under

    def __str__(self):
        descr = f"NAME: {self.name}, ID: {self.id}"
        descr += f"\n   Parameter: {self.params}"
        descr += f"\n   Self Completing: {self.compl}"
        return descr

    def addParameter(self, param:Instance) -> None:
        """Adds a parameter to the procedure"""
        self.params.append(param)

    def getParameter(self, id:str) -> Instance:
        """Returns the specified parameter"""
        for p in self.params:
            if p.id == id:
                return p

        return None

    def setSelfCompleting(self, complFlag:bool) -> None:
        """Sets the self completing flag of the procedure"""
        self.compl = complFlag

class Service:
    def __init__(self):
        self.name = "" # name of the service
        self.id = "" # id of the service
        self.refid = "" # refid of the service
        self.paramElem = {} # param elems of the service
        self.procs = [] # the procedures under the service

    def __str__(self):
        return f"Name: {self.name}, ID: {self.id}, RefID: {self.refid}\nparamElem: {self.paramElem}\nProcedures: {self.procs}"

class Port:
    def __init__(self):
        self.name:str = "" # name of the port
        self.x:int = 0 # x coordinate of the port
        self.y:int = 0 # y coordinate of the port
        self.connectId = "" # ID of the connector of the port

class VisualObject:
    def __init__(self):
        self.name:str = "" # name of the visual object
        self.refId:str = "" # refId of the visual object
        self.refInst:Instance = None # the instance the visual object represents
        self.width:int = 0 # width of the visual object
        self.height:int = 0 # height of the visual object
        self.x:int = 0 # x coordinate of the visual object
        self.y:int = 0 # y coordinate of the visual object
        self.zindex:int = 0 # zindex of the visual object
        self.rotation:int = 0 # rotation of the visual object
        self.eClassVer:str = "" # eClass Version of the visual object
        self.eClassClass:str = "" # eClass Classification Class of the visual object
        self.eClassIRDI:str = "" # eClass IRDI of the visual object
        self.ports:list[Port] = [] # list of ports the visual object has

class Junction:
    def __init__(self):
        self.name:str = "" # name of the topology object
        self.x:int = 0 # x coordinate of the topology object
        self.y:int = 0 # y coordinate of the topology object
        self.zindex:int = 0 # z index of the topology object
        self.ports:list[Port] = [] # list of ports the topology object has

class Source:
    def __init__(self):
        self.name:str = "" # name of the source object
        self.x:int = 0 # x coordinate of the source object
        self.y:int = 0 # y coordinate of the source object
        self.termId:str = "" # term ID of the source object
        self.zindex:int = 0 # z index of the source object
        self.ports:list[Port] = [] # list of ports the source object has

class Sink:
    def __init__(self):
        self.name:str = "" # name of the sink object
        self.x:int = 0 # x coordinate of the sink object
        self.y:int = 0 # y coordinate of the sink object
        self.termId:str = "" # term ID of the sink object
        self.zindex:int = 0 # z index of the sink object
        self.ports:list[Port] = [] # list of ports the sink object has

class Pipe:
    def __init__(self):
        self.name:str = "" # name of the pipe
        self.direct:bool = False # whether the pipe is directed or not
        self.ep:str = "" # the edge path of the pipe
        self.zindex:int = 0 # the z index of the pipe
        self.ports:list[Port] = [] # list of ports of the pipe

class Line:
    def __init__(self):
        self.type:str = "" # the type of the line, either Function or Measurement
        self.name:str = "" # name of the line
        self.ep:str = "" # the edge path of the line
        self.zindex:int = 0 # the z index of the line
        self.ports:list[Port] = [] # list of ports of the line

class HMI:
    def __init__(self):
        self.type:str = "" # type of the HMI instance, either 'Service' or 'RI'
        self.width:int = 0 # width of the HMI instance
        self.height:int = 0 # height of the HMI instance
        self.hierarchy:str = "" # hierarchy level of the HMI instance
        self.visuals:list[VisualObject] = [] # list of visual objects of the HMI instance
        self.juncts:list[Junction] = [] # list of junction objects of the HMI instance
        self.srcs:list[Source] = [] # list of source objects of the HMI instance
        self.sinks:list[Sink] = [] # list of sink objects of the HMI instance
        self.pipes:list[Pipe] = [] # list of pipes of the HMI instance
        self.lines:list[Line] = [] # list of function lines of the HMI instance
        self.links:list[tuple[str,str]] = [] # list of internal links consisting of the refIds of both connection sides

class Pea:
    def __init__(self):
        self.name = "" # name of the mtp
        self.insts:list[Instance] = [] # list of instances
        self.sensacts = [] # list of sensors and actuators
        self.procs = [] # list of procedures
        self.servs = [] # list of services
        self.url = "" # address of the opc ua server
        self.ns = "" # namespace of the opc ua server
        self.nsid = None # index of the opc namespace
        self.hmis:list[HMI] = [] # list of the hmi representation(s) of the PEA

    def __str__(self):
        descr = f"{self.name}\nInstances:"
        for i in self.insts:
            descr += f"\n    {i}"
        descr += f"\nServices:"
        for p in self.servs:
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

    def getInstance(self, instId:str) -> Instance:
        """Returns the instance with the given id"""
        for i in self.insts:
            if i.id == instId or i.refid == instId:
                return i

        return None

    def getInstanceByName(self, instName:str) -> Instance:
        """Returns the instance with the given name"""
        for i in self.insts:
            if i.name == instName:
                return i
        
        return None

    def addService(self, serv:Service) -> None:
        """Adds a procedure to the mtp."""
        self.servs.append(serv)

    def hasService(self, servId:str) -> bool:
        """Returns true if the mtp has the corresponding service."""
        for s in self.servs:
            if s.id == servId or s.refid == servId:
                return True
        return False

    def addUrl(self, url:str) -> None:
        """Adds an opc ua server url to the mtp"""
        self.url = url

    def getUrl(self) -> str:
        """Returns the url of the opc ua server"""
        return self.url

    def getService(self, id:str) -> Service:
        """Returns the service with the specified id"""
        for s in self.servs:
            if s.id == id:
                return s

        return None

    def getProcedure(self, procId:str) -> Procedure:
        """Returns the procedure with the specified id"""
        for p in self.procs:
            if p.id == procId:
                return p
        return None

    def hasProcedure(self, procId:str) -> bool:
        """Returns true if mtp has specified procedure."""
        for p in self.procs:
            if p.id == procId:
                return True
        return False

    def hasParameter(self, paramId:str) -> bool:
        """Returns true if there is a parameter with the specified id."""
        for p in self.procs:
            for param in p.params:
                if param.id == paramId:
                    return True
        return False

### functions
def getUnit(unitNr: int) -> str:
    """Returns the unit corresponding to the identifier"""
    match unitNr:
        case 1000:
            return "Kelvin"
        case 1001:
            return "Grad Celsius"
        case 1002:
            return "Grad Fahrenheit"
        case 1003:
            return "Grad Rankine"
        case 1004:
            return "Radiant"
        case 1005:
            return "Grad"
        case 1006:
            return "Minute"
        case 1007:
            return "Sekunde"
        case 1008:
            return "Gon"
        case 1009:
            return "Umdrehung"
        case 1010:
            return "Meter"
        case 1011:
            return "Kilometer"
        case 1012:
            return "Zentimeter"
        case 1013:
            return "Millimeter"
        case 1014:
            return "Mikrometer"
        case 1015:
            return "Nanometer"
        case 1016:
            return "Picometer"
        case 1017:
            return "Angstrom"
        case 1018:
            return "Fuß"
        case 1019:
            return "Zoll"
        case 1020:
            return "Yard"
        case 1021:
            return "Meile"
        case 1022:
            return "Nautische Meile"
        case 1023:
            return "Quadratmeter"
        case 1024:
            return "Quadratkilometer"
        case 1025:
            return "Quadratzentimeter"
        case 1026:
            return "Quadratdezimeter"
        case 1027:
            return "Quadratmillimeter"
        case 1028:
            return "Ar"
        case 1029:
            return "Hektar"
        case 1030:
            return "Quadratzoll"
        case 1031:
            return "Quadratfuß"
        case 1032:
            return "Quadratyard"
        case 1033:
            return "Quadratmeile"
        case 1034:
            return "Kubikmeter"
        case 1035:
            return "Kubikdezimeter"
        case 1036:
            return "Kubikzentimeter"
        case 1037:
            return "Kubikmillimeter"
        case 1038:
            return "Liter"
        case 1039:
            return "Zentiliter"
        case 1040:
            return "Milliliter"
        case 1041:
            return "Hektoliter"
        case 1042:
            return "Kubikzoll"
        case 1043:
            return "Kubikfuß"
        case 1044:
            return "Kubikyard"
        case 1045:
            return "Kubikmeile"
        case 1046:
            return "Pint"
        case 1047:
            return "Quart"
        case 1048:
            return "US-Gallonen"
        case 1049:
            return "Imperial Gallonen"
        case 1050:
            return "Bushel"
        case 1051:
            return "Barrel"
        case 1052:
            return "Barrel flüssig"
        case 1053:
            return "Normkubikfuß"
        case 1054:
            return "Sekunde"
        case 1055:
            return "Kilosekunde"
        case 1056:
            return "Millisekunde"
        case 1057:
            return "Mikrosekunde"
        case 1058:
            return "Minute"
        case 1059:
            return "Stunde"
        case 1060:
            return "Tag"
        case 1061:
            return "Meter pro Sekunde"
        case 1062:
            return "Millimeter pro Sekunde"
        case 1063:
            return "Meter pro Stunde"
        case 1064:
            return "Kilometer pro Stunde"
        case 1065:
            return "Knoten"
        case 1066:
            return "Zoll pro Sekunde"
        case 1067:
            return "Fuß pro Sekunde"
        case 1068:
            return "Yard pro Sekunde"
        case 1069:
            return "Zoll pro Minute"
        case 1070:
            return "Fuß pro Minute"
        case 1071:
            return "Yard pro Minute"
        case 1072:
            return "Zoll pro Stunde"
        case 1073:
            return "Fuß pro Stunde"
        case 1074:
            return "Yard pro Stunde"
        case 1075:
            return "Meilen pro Stunde"
        case 1076:
            return "Meter pro Quadratsekunde"
        case 1077:
            return "Hertz"
        case 1078:
            return "Terahertz"
        case 1079:
            return "Gigahertz"
        case 1080:
            return "Megahertz"
        case 1081:
            return "Kilohertz"
        case 1082:
            return "Pro Sekunde"
        case 1083:
            return "Pro Minute"
        case 1084:
            return "Umdrehungen pro Sekunde"
        case 1085:
            return "Umdrehungen pro Minute"
        case 1086:
            return "Radiant pro Sekunde"
        case 1087:
            return "Pro Quadratsekunden"
        case 1088:
            return "Kilogramm"
        case 1089:
            return "Gramm"
        case 1090:
            return "Milligramm"
        case 1091:
            return "Megagramm"
        case 1092:
            return "Metrische Tonne"
        case 1093:
            return "Unze"
        case 1094:
            return "Pfund"
        case 1095:
            return "US-Tonne"
        case 1096:
            return "Britische Tonne"
        case 1097:
            return "Kilogramm pro Kubikmeter"
        case 1098:
            return "Megagramm pro Kubikmeter"
        case 1099:
            return "Kilogramm pro Kubikdezimeter"
        case 1100:
            return "Gramm pro Kubikzentimeter"
        case 1101:
            return "Gramm pro Kubikmeter"
        case 1102:
            return "Metrische Tonne pro Kubikmeter"
        case 1103:
            return "Kilogramm pro Liter"
        case 1104:
            return "Gramm pro Milliliter"
        case 1105:
            return "Gramm pro Liter"
        case 1106:
            return "Pfund pro Kubikzoll"
        case 1107:
            return "Pfund pro Kubikfuß"
        case 1108:
            return "Pfund pro US-Gallonen"
        case 1109:
            return "US-Tonnen pro Kubikyard"
        case 1110:
            return "Grad Twaddell"
        case 1111:
            return "Grad Baumé (schwer)"
        case 1112:
            return "Grad Baumé (leicht)"
        case 1113:
            return "Grad API"
        case 1114:
            return "Specific gravity units"
        case 1115:
            return "Kilogramm pro Meter"
        case 1116:
            return "Milligramm pro Meter"
        case 1117:
            return "Tex"
        case 1118:
            return "Kilogramm mal Quadratmeter"
        case 1119:
            return "Kilogramm mal Meter pro Sekunde"
        case 1120:
            return "Newton"
        case 1121:
            return "Meganewton"
        case 1122:
            return "Kilonewton"
        case 1123:
            return "Millinewton"
        case 1124:
            return "Mikronewton"
        case 1125:
            return "Kilogramm mal Quadratmeter pro Sekunde"
        case 1126:
            return "Newton mal Meter"
        case 1127:
            return "Meganewton mal Meter"
        case 1128:
            return "Kilonewton mal Meter"
        case 1129:
            return "Millinewton mal Meter"
        case 1130:
            return "Pascal"
        case 1131:
            return "Gigapascal"
        case 1132:
            return "Megapascal"
        case 1133:
            return "Kilopascal"
        case 1134:
            return "Millipascal"
        case 1135:
            return "Mikropascal"
        case 1136:
            return "Hektopascal"
        case 1137:
            return "Bar"
        case 1138:
            return "Millibar"
        case 1139:
            return "Torr"
        case 1140:
            return "Atmosphären"
        case 1141:
            return "Pfund pro Quadratzoll"
        case 1142:
            return "Pfund pro quadratinch (absolut)"
        case 1143:
            return "Pfund pro quadratinch (gauge)"
        case 1144:
            return "Gramm pro Quadratzentimeter"
        case 1145:
            return "Kilogramm pro Quadratzentimeter"
        case 1146:
            return "Zoll Wassersäule"
        case 1147:
            return "Zoll Wassersäule bei 4 Grad Celsius"
        case 1148:
            return "Zoll Wassersäule bei 68 Grad Fahrenheit"
        case 1149:
            return "Millimeter Wassersäule"
        case 1150:
            return "Millimeter Wassersäule bei 4 Grad Celsius"
        case 1151:
            return "Millimeter Wassersäule bei 68 Grad Fahrenheit"
        case 1152:
            return "Fuß Wassersäule"
        case 1153:
            return "Fuß Wassersäule bei 4 Grad Celsius"
        case 1154:
            return "Fuß Wassersäule bei 68 Grad Fahrenheit"
        case 1155:
            return "Zoll Quecksilbersäule"
        case 1156:
            return "Zoll Quecksilbersäule bei 0 Grad Celsius"
        case 1157:
            return "Millimeter Quecksilbersäule"
        case 1158:
            return "Millimeter Quecksilbersäule bei 0 Grad Celsius"
        case 1159:
            return "Pascalsekunde"
        case 1160:
            return "Quadratmeter pro Sekunde"
        case 1161:
            return "Poise"
        case 1162:
            return "Zentipoise"
        case 1163:
            return "Stokes"
        case 1164:
            return "Zentistokes"
        case 1165:
            return "Newton pro Meter"
        case 1166:
            return "Millinewton pro Meter"
        case 1167:
            return "Joule"
        case 1168:
            return "Exajoule"
        case 1169:
            return "Petajoule"
        case 1170:
            return "Terajoule"
        case 1171:
            return "Gigajoule"
        case 1172:
            return "Megajoule"
        case 1173:
            return "Kilojoule"
        case 1174:
            return "Millijoule"
        case 1175:
            return "Wattstunde"
        case 1176:
            return "Terawattstunde"
        case 1177:
            return "Gigawattstunde"
        case 1178:
            return "Megawattstunde"
        case 1179:
            return "Kilowattstunde"
        case 1180:
            return "Kalorie (thermochemisch)"
        case 1181:
            return "Kilokalorie (thermochemisch)"
        case 1182:
            return "Megakalorie (thermochemisch)"
        case 1183:
            return "British thermal unit"
        case 1184:
            return "Decatherm"
        case 1185:
            return "Fuß mal Pfund"
        case 1186:
            return "Watt"
        case 1187:
            return "Terawatt"
        case 1188:
            return "Gigawatt"
        case 1189:
            return "Megawatt"
        case 1190:
            return "Kilowatt"
        case 1191:
            return "Milliwatt"
        case 1192:
            return "Mikrowatt"
        case 1193:
            return "Nanowatt"
        case 1194:
            return "Picowatt"
        case 1195:
            return "Megakalorie pro Stunde"
        case 1196:
            return "Megajoule pro Stunde"
        case 1197:
            return "Britische thermische Einheit pro Stunde"
        case 1198:
            return "Pferdestärke"
        case 1199:
            return "Watt pro Meter mal Kelvin"
        case 1200:
            return "Watt pro Quadratmeter mal Kelvin"
        case 1201:
            return "Quadratmeter mal Kelvin pro Watt"
        case 1202:
            return "Joule pro Kelvin"
        case 1203:
            return "Kilojoule pro Kelvin"
        case 1204:
            return "Joule pro Kilogramm mal Kelvin"
        case 1205:
            return "Kilojoule pro Kilogramm mal Kelvin"
        case 1206:
            return "Joule pro Kilogramm"
        case 1207:
            return "Megajoule pro Kilogramm"
        case 1208:
            return "Kilojoule pro Kilogramm"
        case 1209:
            return "Ampere"
        case 1210:
            return "Kiloampere"
        case 1211:
            return "Milliampere"
        case 1212:
            return "Mikroampere"
        case 1213:
            return "Nanoampere"
        case 1214:
            return "Picoampere"
        case 1215:
            return "Coulomb"
        case 1216:
            return "Megacoulomb"
        case 1217:
            return "Kilocoulomb"
        case 1218:
            return "Mikrocoulomb"
        case 1219:
            return "Nanocoulomb"
        case 1220:
            return "Picocoulomb"
        case 1221:
            return "Amperestunde"
        case 1222:
            return "Coulomb pro Kubikmeter"
        case 1223:
            return "Coulomb pro Kubikmillimeter"
        case 1224:
            return "Coulomb pro Kubikzentimeter"
        case 1225:
            return "Kilocoulomb pro Kubikmeter"
        case 1226:
            return "Millicoulomb pro Kubikmeter"
        case 1227:
            return "Mikrocoulomb pro Kubikmeter"
        case 1228:
            return "Coulomb pro Quadratmeter"
        case 1229:
            return "Coulomb pro Quadratmillimeter"
        case 1230:
            return "Coulomb pro Quadratzentimeter"
        case 1231:
            return "Kilocoulomb pro Quadratmeter"
        case 1232:
            return "Millicoulomb pro Quadratmeter"
        case 1233:
            return "Mikrocoulomb pro Quadratmeter"
        case 1234:
            return "Volt pro Meter"
        case 1235:
            return "Megavolt pro Meter"
        case 1236:
            return "Kilovolt pro Meter"
        case 1237:
            return "Volt pro Zentimeter"
        case 1238:
            return "Millivolt pro Meter"
        case 1239:
            return "Mikrovolt pro Meter"
        case 1240:
            return "Volt"
        case 1241:
            return "Megavolt"
        case 1242:
            return "Kilovolt"
        case 1243:
            return "Millivolt"
        case 1244:
            return "Mikrovolt"
        case 1245:
            return "Farad"
        case 1246:
            return "Millifarad"
        case 1247:
            return "Mikrofarad"
        case 1248:
            return "Nanofarad"
        case 1249:
            return "Picofarad"
        case 1250:
            return "Farad pro Meter"
        case 1251:
            return "Mikrofarad pro Meter"
        case 1252:
            return "Nanofarad pro Meter"
        case 1253:
            return "Picofarad pro Meter"
        case 1254:
            return "Coulomb mal Meter"
        case 1255:
            return "Ampere pro Quadratmeter"
        case 1256:
            return "Megaampere pro Quadratmeter"
        case 1257:
            return "Ampere pro Quadratzentimeter"
        case 1258:
            return "Kiloampere pro Quadratmeter"
        case 1259:
            return "Ampere pro Meter"
        case 1260:
            return "Kiloampere pro Meter"
        case 1261:
            return "Ampere pro Zentimeter"
        case 1262:
            return "Tesla"
        case 1263:
            return "Millitesla"
        case 1264:
            return "Mikrotesla"
        case 1265:
            return "Nanotesla"
        case 1266:
            return "Weber"
        case 1267:
            return "Milliweber"
        case 1268:
            return "Weber pro Meter"
        case 1269:
            return "Kiloweber pro Meter"
        case 1270:
            return "Henry"
        case 1271:
            return "Millihenry"
        case 1272:
            return "Mikrohenry"
        case 1273:
            return "Nanohenry"
        case 1274:
            return "Picohenry"
        case 1275:
            return "Henry pro Meter"
        case 1276:
            return "Mikrohenry pro Meter"
        case 1277:
            return "Nanohenry pro Meter"
        case 1278:
            return "Ampere mal Quadratmeter"
        case 1279:
            return "Newton mal Quadratmeter pro Ampere"
        case 1280:
            return "Weber mal Meter"
        case 1281:
            return "Ohm"
        case 1282:
            return "GigaOhm"
        case 1283:
            return "MegaOhm"
        case 1284:
            return "KiloOhm"
        case 1285:
            return "MilliOhm"
        case 1286:
            return "MikroOhm"
        case 1287:
            return "Siemens"
        case 1288:
            return "Kilosiemens"
        case 1289:
            return "Millisiemens"
        case 1290:
            return "Mikrosiemens"
        case 1291:
            return "Ohm mal Meter"
        case 1292:
            return "GigaOhm mal Meter"
        case 1293:
            return "MegaOhm mal Meter"
        case 1294:
            return "KiloOhm mal Meter"
        case 1295:
            return "Ohm mal Zentimeter"
        case 1296:
            return "MilliOhm mal Meter"
        case 1297:
            return "MikroOhm mal Meter"
        case 1298:
            return "NanoOhm mal Meter"
        case 1299:
            return "Siemens pro Meter"
        case 1300:
            return "Megasiemens pro Meter"
        case 1301:
            return "Kilosiemens pro Meter"
        case 1302:
            return "Millisiemens pro Zentimeter"
        case 1303:
            return "Mikrosiemens pro Millimeter"
        case 1304:
            return "Pro Henry"
        case 1305:
            return "Steradiant"
        case 1306:
            return "Watt pro Steradiant"
        case 1307:
            return "Watt pro Steradiant mal Quadratmeter"
        case 1308:
            return "Watt pro Quadratmeter"
        case 1309:
            return "Lumen"
        case 1310:
            return "Lumensekunde"
        case 1311:
            return "Lumenstunde"
        case 1312:
            return "Lumen pro Quadratmeter"
        case 1313:
            return "Lumen pro Watt"
        case 1314:
            return "Lux"
        case 1315:
            return "Luxsekunde"
        case 1316:
            return "Candela"
        case 1317:
            return "Candela pro Quadratmeter"
        case 1318:
            return "Gramm pro Sekunde"
        case 1319:
            return "Gramm pro Minute"
        case 1320:
            return "Gramm pro Stunde"
        case 1321:
            return "Gramm pro Tag"
        case 1322:
            return "Kilogramm pro Sekunde"
        case 1323:
            return "Kilogramm pro Minute"
        case 1324:
            return "Kilogramm pro Stunde"
        case 1325:
            return "Kilogramm pro Tag"
        case 1326:
            return "Metrische Tonne pro Sekunde"
        case 1327:
            return "Metrische Tonne pro Minute"
        case 1328:
            return "Metrische Tonne pro Stunde"
        case 1329:
            return "Metrische Tonne pro Tag"
        case 1330:
            return "Pfund pro Sekunde"
        case 1331:
            return "Pfund pro Minute"
        case 1332:
            return "Pfund pro Stunde"
        case 1333:
            return "Pfund pro Tag"
        case 1334:
            return "US-Tonnen pro Sekunde"
        case 1335:
            return "US-Tonnen pro Minute"
        case 1336:
            return "US-Tonnen pro Stunde"
        case 1337:
            return "US-Tonnen pro Tag"
        case 1338:
            return "Britische Tonnen pro Sekunde"
        case 1339:
            return "Britische Tonnen pro Minute"
        case 1340:
            return "Britische Tonnen pro Stunde"
        case 1341:
            return "Britische Tonnen pro Tag"
        case 1342:
            return "Prozent"
        case 1343:
            return "Prozent Feststoffe pro Gewichtseinheit"
        case 1344:
            return "Prozent Feststoffe pro Volumeneinheit"
        case 1345:
            return "Prozent Dampfqualität"
        case 1346:
            return "Grad plato"
        case 1347:
            return "Kubikmeter pro Sekunde"
        case 1348:
            return "Kubikmeter pro Minute"
        case 1349:
            return "Kubikmeter pro Stunde"
        case 1350:
            return "Kubikmeter pro Tag"
        case 1351:
            return "Liter pro Sekunde"
        case 1352:
            return "Liter pro Minute"
        case 1353:
            return "Liter pro Stunde"
        case 1354:
            return "Liter pro Tag"
        case 1355:
            return "Megaliter pro Tag"
        case 1356:
            return "Kubikfuß pro Sekunde"
        case 1357:
            return "Kubikfuß pro Minute"
        case 1358:
            return "Kubikfuß pro Stunde"
        case 1359:
            return "Kubikfuß pro Tag"
        case 1360:
            return "Standard Kubikfuß pro Minute"
        case 1361:
            return "Standard Kubikfuß pro Stunde"
        case 1362:
            return "US-Gallonen pro Sekunde"
        case 1363:
            return "US-Gallonen pro Minute"
        case 1364:
            return "US-Gallonen pro Stunde"
        case 1365:
            return "US-Gallonen pro Tag"
        case 1366:
            return "Mega US-Gallonen pro Tag"
        case 1367:
            return "Imperial Gallonen pro Sekunde"
        case 1368:
            return "Imperial Gallonen pro Minute"
        case 1369:
            return "Imperial Gallonen pro Stunde"
        case 1370:
            return "Imperial Gallonen pro Tag"
        case 1371:
            return "Barrel pro Sekunde"
        case 1372:
            return "Barrel pro Minute"
        case 1373:
            return "Barrel pro Stunde"
        case 1374:
            return "Barrel pro Tag"
        case 1375:
            return "Watt pro Quadratmeter"
        case 1376:
            return "Milliwatt pro Quadratmeter"
        case 1377:
            return "Mikrowatt pro Quadratmeter"
        case 1378:
            return "Picowatt pro Quadratmeter"
        case 1379:
            return "Pascalsekunde pro Kubikmeter"
        case 1380:
            return "Newtonsekunde pro Meter"
        case 1381:
            return "Pascalsekunde pro Meter"
        case 1382:
            return "Bel"
        case 1383:
            return "Dezibel"
        case 1384:
            return "Mol"
        case 1385:
            return "Kilomol"
        case 1386:
            return "Millimol"
        case 1387:
            return "Mikromol"
        case 1388:
            return "Kilogramm pro Mol"
        case 1389:
            return "Gramm pro Mol"
        case 1390:
            return "Kubikmeter pro Mol"
        case 1391:
            return "Kubikdezimeter pro Mol"
        case 1392:
            return "Kubikzentimeter pro Mol"
        case 1393:
            return "Liter pro Mol"
        case 1394:
            return "Joule pro Mol"
        case 1395:
            return "Kilojoule pro Mol"
        case 1396:
            return "Joule pro Mol mal Kelvin"
        case 1397:
            return "Mol pro Kubikmeter"
        case 1398:
            return "Mol pro Kubikdezimeter"
        case 1399:
            return "Mol pro Liter"
        case 1400:
            return "Mol pro Kilogramm"
        case 1401:
            return "Millimol pro Kilogramm"
        case 1402:
            return "Becquerel"
        case 1403:
            return "Megabecquerel"
        case 1404:
            return "Kilobecquerel"
        case 1405:
            return "Becquerel pro Kilogramm"
        case 1406:
            return "Kilobecquerel pro Kilogramm"
        case 1407:
            return "Megabecquerel pro Kilogramm"
        case 1408:
            return "Grau"
        case 1409:
            return "Milligray"
        case 1410:
            return "Rad"
        case 1411:
            return "Sievert"
        case 1412:
            return "Millisievert"
        case 1413:
            return "Rem"
        case 1414:
            return "Coulomb pro Kilogramm"
        case 1415:
            return "Millicoulomb pro Kilogramm"
        case 1416:
            return "Röntgen"
        case 1417:
            return "Magnetische Energiedichte"
        case 1418:
            return ""
        case 1419:
            return "Kubikmeter pro Coulomb"
        case 1420:
            return "Volt pro Kelvin"
        case 1421:
            return "Millivolt pro Kelvin"
        case 1422:
            return "pH-Wert"
        case 1423:
            return "Teile pro Million"
        case 1424:
            return "Teile pro Milliarde"
        case 1425:
            return "Teile pro Billion"
        case 1426:
            return "Grad Brix"
        case 1427:
            return "Grad Balling"
        case 1428:
            return "Proof per volume"
        case 1429:
            return "Proof per mass"
        case 1430:
            return "Pfund pro Imperial Gallone"
        case 1431:
            return "Kilokalorie pro Sekunde"
        case 1432:
            return "Kilokalorie pro Minute"
        case 1433:
            return "Kilokalorie pro Stunde"
        case 1434:
            return "Kilokalorie pro Tag"
        case 1435:
            return "Megakalorie pro Sekunde"
        case 1436:
            return "Megakalorie pro Minute"
        case 1437:
            return "Megakalorie pro Tag"
        case 1438:
            return "Kilojoule pro Sekunde"
        case 1439:
            return "Kilojoule pro Minute"
        case 1440:
            return "Kilojoule pro Stunde"
        case 1441:
            return "Kilojoule pro Tag"
        case 1442:
            return "Megajoule pro Sekunde"
        case 1443:
            return "Megajoule pro Minute"
        case 1444:
            return "Megajoule pro Tag"
        case 1445:
            return "Britische thermische Einheit pro Sekunde"
        case 1446:
            return "Britische thermische Einheit pro Minute"
        case 1447:
            return "Britische thermische Einheit pro Tag"
        case 1448:
            return "Mikro US-Gallone pro Sekunde"
        case 1449:
            return "Milli US-Gallone pro Sekunde"
        case 1450:
            return "Kilo US-Gallone pro Sekunde"
        case 1451:
            return "Mega US-Gallone pro Sekunde"
        case 1452:
            return "Mikro US-Gallone pro Minute"
        case 1453:
            return "Milli US-Gallone pro Minute"
        case 1454:
            return "Kilo US-Gallone pro Minute"
        case 1455:
            return "Mega US-Gallone pro Minute"
        case 1456:
            return "Mikro US-Gallone pro Stunde"
        case 1457:
            return "Milli US-Gallone pro Stunde"
        case 1458:
            return "Kilo US-Gallone pro Stunde"
        case 1459:
            return "Mega US-Gallone pro Stunde"
        case 1460:
            return "Mikro US-Gallone pro Tag"
        case 1461:
            return "Milli US-Gallone pro Tag"
        case 1462:
            return "Kilo US-Gallone pro Tag"
        case 1463:
            return "Mikro Imperial Gallone pro Sekunde"
        case 1464:
            return "Milli Imperial Gallone pro Sekunde"
        case 1465:
            return "Kilo Imperial Gallone pro Sekunde"
        case 1466:
            return "Mega Imperial Gallone pro Sekunde"
        case 1467:
            return "Mikro Imperial Gallone pro Minute"
        case 1468:
            return "Milli Imperial Gallone pro Minute"
        case 1469:
            return "Kilo Imperial Gallone pro Minute"
        case 1470:
            return "Mega Imperial Gallone pro Minute"
        case 1471:
            return "Mikro Imperial Gallone pro Stunde"
        case 1472:
            return "Milli Imperial Gallone pro Stunde"
        case 1473:
            return "Kilo Imperial Gallone pro Stunde"
        case 1474:
            return "Mega Imperial Gallone pro Stunde"
        case 1475:
            return "Mikro Imperial Gallone pro Tag"
        case 1476:
            return "Milli Imperial Gallone pro Tag"
        case 1477:
            return "Kilo Imperial Gallone pro Tag"
        case 1478:
            return "Mega Imperial Gallone pro Tag"
        case 1479:
            return "Mikrobarrel pro Sekunde"
        case 1480:
            return "Millibarrel pro Sekunde"
        case 1481:
            return "Kilobarrel pro Sekunde"
        case 1482:
            return "Megabarrel pro Sekunde"
        case 1483:
            return "Mikrobarrel pro Minute"
        case 1484:
            return "Millibarrel pro Minute"
        case 1485:
            return "Kilobarrel pro Minute"
        case 1486:
            return "Megabarrel pro Minute"
        case 1487:
            return "Mikrobarrel pro Stunde"
        case 1488:
            return "Millibarrel pro Stunde"
        case 1489:
            return "Kilobarrel pro Stunde"
        case 1490:
            return "Megabarrel pro Stunde"
        case 1491:
            return "Mikrobarrel pro Tag"
        case 1492:
            return "Millibarrel pro Tag"
        case 1493:
            return "Kilobarrel pro Tag"
        case 1494:
            return "Megabarrel pro Tag"
        case 1495:
            return "Kubikmikrometer pro Sekunde"
        case 1496:
            return "Kubikmillimeter pro Sekunde"
        case 1497:
            return "Kubikkilometer pro Sekunde"
        case 1498:
            return "Kubikmegameter pro Sekunde"
        case 1499:
            return "Kubikmikrometer pro Minute"
        case 1500:
            return "Kubikmillimeter pro Minute"
        case 1501:
            return "Kubikkilometer pro Minute"
        case 1502:
            return "Kubikmegameter pro Minute"
        case 1503:
            return "Kubikmikrometer pro Stunde"
        case 1504:
            return "Kubikmillimeter pro Stunde"
        case 1505:
            return "Kubikkilometer pro Stunde"
        case 1506:
            return "Kubikmegameter pro Stunde"
        case 1507:
            return "Kubikmikrometer pro Tag"
        case 1508:
            return "Kubikmillimeter pro Tag"
        case 1509:
            return "Kubikkilometer pro Tag"
        case 1510:
            return "Kubikmegameter pro Tag"
        case 1511:
            return "Kubikzentimeter pro Sekunde"
        case 1512:
            return "Kubikzentimeter pro Minute"
        case 1513:
            return "Kubikzentimeter pro Stunde"
        case 1514:
            return "Kubikzentimeter pro Tag"
        case 1515:
            return "Kilokalorie pro Kilogramm"
        case 1516:
            return "Britische thermische Einheit pro Pfund"
        case 1517:
            return "Kiloliter"
        case 1518:
            return "Kiloliter pro Minute"
        case 1519:
            return "Kiloliter pro Stunde"
        case 1520:
            return "Kiloliter pro Tag"
        case 1551:
            return "Siemens pro Zentimeter"
        case 1552:
            return "Mikrosiemens pro Zentimeter"
        case 1553:
            return "Millisiemens pro Meter"
        case 1554:
            return "Mikrosiemens pro Meter"
        case 1555:
            return "Megaohm Zentimeter"
        case 1556:
            return "Kiloohm Zentimeter"
        case 1557:
            return "Gewichtprozent"
        case 1558:
            return "Milligramm pro Liter"
        case 1559:
            return "Mikogramm pro Liter"
        case 1560:
            return "-"
        case 1561:
            return "-"
        case 1562:
            return "Volumenprozent"
        case 1563:
            return "Milliliter pro Minute"
        case 1564:
            return "Milligramm pro Kubikzentimeter"
        case 1565:
            return "Milligramm pro Liter"
        case 1566:
            return "Milligramm pro Kubikmeter"
        case 1567:
            return "Karat"
        case 1568:
            return "Pfund (troy or apothecary)"
        case 1569:
            return "Unze (troy or apothecary)"
        case 1570:
            return "Unze (U.S. fluid)"
        case 1571:
            return "Kubikzentimeter"
        case 1572:
            return "acre foot"
        case 1573:
            return "Kubikmeter"
        case 1574:
            return "Liter"
        case 1575:
            return "Standard Kubikmeter"
        case 1576:
            return "Standard Liter"
        case 1577:
            return "Milliliter pro Sekunde"
        case 1578:
            return "Milliliter pro Stunde"
        case 1579:
            return "Milliliter pro Tag"
        case 1580:
            return "acre foot pro Sekunde"
        case 1581:
            return "acre foot pro Minute"
        case 1582:
            return "acre foot pro Stunde"
        case 1583:
            return "acre foot pro Tag"
        case 1584:
            return "Unze pro Sekunde"
        case 1585:
            return "Unze pro Minute"
        case 1586:
            return "Unze pro Stunde"
        case 1587:
            return "Unze pro Tag"
        case 1588:
            return "Standardkubikmeter pro Sekunde"
        case 1589:
            return "Standardkubikmeter pro Minute"
        case 1590:
            return "Standardkubikmeter pro Stunde"
        case 1591:
            return "Standardkubikmeter pro Tag"
        case 1592:
            return "Standardliter pro Sekunde"
        case 1593:
            return "Standardliter pro Minute"
        case 1594:
            return "Standardliter pro Stunde"
        case 1595:
            return "Standardliter pro Tag"
        case 1596:
            return "Standardkubikmeter pro Sekunde"
        case 1597:
            return "Standardkubikmeter pro Minute"
        case 1598:
            return "Standardkubikmeter pro Stunde"
        case 1599:
            return "Standardkubikmeter pro Tag"
        case 1600:
            return "Standardliter pro Sekunde"
        case 1601:
            return "Standardliter pro Minute"
        case 1602:
            return "Standardliter pro Stunde"
        case 1603:
            return "Standardliter pro Tag"
        case 1604:
            return "Standardkubikfuß pro Sekuknde"
        case 1605:
            return "Standardkubikfuß pro Tag"
        case 1606:
            return "Unze pro Sekunde"
        case 1607:
            return "Unze pro Minute"
        case 1608:
            return "Unze pro Stunde"
        case 1609:
            return "Unze pro Tag"
        case 1610:
            return "Pascal (absolut)"
        case 1611:
            return "Pascal (gauge)"
        case 1612:
            return "Gigapascal (absolut)"
        case 1613:
            return "Gigapascal (Gauge)"
        case 1614:
            return "Megapascal (absolut)"
        case 1615:
            return "Megapascal (Gauge)"
        case 1616:
            return "Kilopascal (absolut)"
        case 1617:
            return "Kilopascal (Gauge)"
        case 1618:
            return "Millipascal (absolut)"
        case 1619:
            return "Millipascal (Gauge)"
        case 1620:
            return "Micropascal (absolut)"
        case 1621:
            return "Micropascal (Gauge)"
        case 1622:
            return "Hektopascal (absolut)"
        case 1623:
            return "Hektopascal (Gauge)"
        case 1624:
            return ""
        case 1625:
            return ""
        case 1626:
            return ""
        case 1627:
            return ""
        case 1628:
            return "Standarddichte bei 4°C"
        case 1629:
            return "Standarddichte bei 15°C"
        case 1630:
            return "Standarddichte bei 20°C"
        case 1631:
            return "Metrische Pferdestärken"
        case 1632:
            return "Teile pro Billion"
        case 1633:
            return "Hektoliter pro Sekunde"
        case 1634:
            return "Hektoliter pro Minute"
        case 1635:
            return "Hektoliter pro Stunde"
        case 1636:
            return "Hektoliter pro Tag"
        case 1637:
            return "Barrel (US flüssig) pro Sekunde"
        case 1638:
            return "Barrel (US flüssig) pro Minute"
        case 1639:
            return "Barrel (US flüssig) pro Stunde"
        case 1640:
            return "Barrel (US flüssig) pro Tag"
        case 1641:
            return "Barrel (U.S. federal)"
        case 1642:
            return "Barrel (U.S. federal) pro Sekunde"
        case 1643:
            return "Barrel (U.S. federal) pro Minute"
        case 1644:
            return "Barrel (U.S. federal) pro Stunde"
        case 1645:
            return "Barrel (U.S. federal) pro Tag"
        case 1998:
            return "Maßeinheit nicht bekannt"
        case 1999:
            return "spezial"


### start main
def getMtps() -> list[Pea]:
    mtps:list[Pea] = []

    # parse mtp files
    for file in TESTMTPS:
        tree = parse(file)
        root = tree.getroot()

        # create mtp object
        mtp = Pea()
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
                                    if (instNode.get("Name") == "InstanceList" or 
                                        instNode.get("Name") == "Instances" or
                                        instNode.get("RefBaseSystemUnitPath") == "MTPDataObjectSUCLib/DataAssembly/PeaElement/PeaInformationLabel" or
                                        instNode.get("RefBaseSystemUnitPath") == "MTPDataObjectSUCLib/DataAssembly/PeaElement/WebServerUrlInfo" or
                                        instNode.get("RefBaseSystemUnitPath") == "MTPDataObjectSUCLib/DataAssembly/ServiceElement/ProcedureHealthView"):
                                        continue
                                    inst = Instance(name=instNode.get("Name"), id=instNode.get("ID"))

                                    for attrNode in instNode.iter(f"{NAMESPACE}Attribute"):
                                        if attrNode.get("Name") == "RefID":
                                            inst.addRefId(attrNode.findtext(f"{NAMESPACE}Value"))
                                        elif attrNode.get("Name") == "WQC":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['WQC']['ID'] = id
                                            inst.paramElem['WQC']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "OSLevel":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['OSLevel']['ID'] = id
                                            inst.paramElem['OSLevel']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "CommandInfo":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['CommandInfo']['ID'] = id
                                            inst.paramElem['CommandInfo']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "CommandOp":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['CommandOp']['ID'] = id
                                            inst.paramElem['CommandOp']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "CommandInt":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['CommandInt']['ID'] = id
                                            inst.paramElem['CommandInt']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "CommandExt":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['CommandExt']['ID'] = id
                                            inst.paramElem['CommandExt']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ProcedureOp":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ProcedureOp']['ID'] = id
                                            inst.paramElem['ProcedureOp']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ProcedureInt":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ProcedureInt']['ID'] = id
                                            inst.paramElem['ProcedureInt']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ProcedureExt":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ProcedureExt']['ID'] = id
                                            inst.paramElem['ProcedureExt']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "StateCur":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['StateCur']['ID'] = id
                                            inst.paramElem['StateCur']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "CommandEn":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['CommandEn']['ID'] = id
                                            inst.paramElem['CommandEn']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ProcedureCur":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ProcedureCur']['ID'] = id
                                            inst.paramElem['ProcedureCur']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ProcedureReq":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ProcedureReq']['ID'] = id
                                            inst.paramElem['ProcedureReq']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "PosTextID":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['PosTextID']['ID'] = id
                                            inst.paramElem['PosTextID']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "InteractQuestionID":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['InteractQuestionID']['ID'] = id
                                            inst.paramElem['InteractQuestionID']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "InteractAnswerID":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['InteractAnswerID']['ID'] = id
                                            inst.paramElem['InteractAnswerID']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "InteractAddInfo":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['InteractAddInfo']['ID'] = id
                                            inst.paramElem['InteractAddInfo']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "StateChannel":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['StateChannel']['ID'] = id
                                            inst.paramElem['StateChannel']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "StateOffAut":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['StateOffAut']['ID'] = id
                                            inst.paramElem['StateOffAut']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "StateOpAut":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['StateOpAut']['ID'] = id
                                            inst.paramElem['StateOpAut']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "StateAutAut":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['StateAutAut']['ID'] = id
                                            inst.paramElem['StateAutAut']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "StateOffOp":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['StateOffOp']['ID'] = id
                                            inst.paramElem['StateOffOp']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "StateOpOp":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['StateOpOp']['ID'] = id
                                            inst.paramElem['StateOpOp']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "StateAutOp":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['StateAutOp']['ID'] = id
                                            inst.paramElem['StateAutOp']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "StateOpAct":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['StateOpAct']['ID'] = id
                                            inst.paramElem['StateOpAct']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "StateAutAct":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['StateAutAct']['ID'] = id
                                            inst.paramElem['StateAutAct']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "StateOffAct":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['StateOffAct']['ID'] = id
                                            inst.paramElem['StateOffAct']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "SrcChannel":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['SrcChannel']['ID'] = id
                                            inst.paramElem['SrcChannel']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "SrcExtAut":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['SrcExtAut']['ID'] = id
                                            inst.paramElem['SrcExtAut']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "SrcIntAut":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['SrcIntAut']['ID'] = id
                                            inst.paramElem['SrcIntAut']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "SrcExtOp":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['SrcExtOp']['ID'] = id
                                            inst.paramElem['SrcExtOp']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "SrcIntOp":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['SrcIntOp']['ID'] = id
                                            inst.paramElem['SrcIntOp']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "SrcIntAct":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['SrcIntAct']['ID'] = id
                                            inst.paramElem['SrcIntAct']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "SrcExtAct":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['SrcExtAct']['ID'] = id
                                            inst.paramElem['SrcExtAct']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ProcParamApplyEn":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ProcParamApplyEn']['ID'] = id
                                            inst.paramElem['ProcParamApplyEn']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ProcParamApplyExt":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ProcParamApplyExt']['ID'] = id
                                            inst.paramElem['ProcParamApplyExt']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ProcParamApplyOp":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ProcParamApplyOp']['ID'] = id
                                            inst.paramElem['ProcParamApplyOp']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ProcParamApplyInt":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ProcParamApplyInt']['ID'] = id
                                            inst.paramElem['ProcParamApplyInt']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ConfigParamApplyEn":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ConfigParamApplyEn']['ID'] = id
                                            inst.paramElem['ConfigParamApplyEn']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ConfigParamApplyExt":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ConfigParamApplyExt']['ID'] = id
                                            inst.paramElem['ConfigParamApplyExt']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ConfigParamApplyOp":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ConfigParamApplyOp']['ID'] = id
                                            inst.paramElem['ConfigParamApplyOp']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ConfigParamApplyInt":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ConfigParamApplyInt']['ID'] = id
                                            inst.paramElem['ConfigParamApplyInt']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ReportValueFreeze":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ReportValueFreeze']['ID'] = id
                                            inst.paramElem['ReportValueFreeze']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ApplyEn":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ApplyEn']['ID'] = id
                                            inst.paramElem['ApplyEn']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ApplyExt":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ApplyExt']['ID'] = id
                                            inst.paramElem['ApplyExt']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ApplyOp":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ApplyOp']['ID'] = id
                                            inst.paramElem['ApplyOp']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ApplyInt":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ApplyInt']['ID'] = id
                                            inst.paramElem['ApplyInt']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "Sync":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['Sync']['ID'] = id
                                            inst.paramElem['Sync']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "VExt":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['VExt']['ID'] = id
                                            inst.paramElem['VExt']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "VInt":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['VInt']['ID'] = id
                                            inst.paramElem['VInt']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "VOp":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['VOp']['ID'] = id
                                            inst.paramElem['VOp']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "VReq":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['VReq']['ID'] = id
                                            inst.paramElem['VReq']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                            inst.default = float(attrNode.findtext(f"{NAMESPACE}DefaultValue"))
                                        elif attrNode.get("Name") == "VFbk":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['VFbk']['ID'] = id
                                            inst.paramElem['VFbk']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "VOut":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['VOut']['ID'] = id
                                            inst.paramElem['VOut']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "V":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['V']['ID'] = id
                                            inst.paramElem['V']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "Pos":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['Pos']['ID'] = id
                                            inst.paramElem['Pos']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "Ctrl":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['Ctrl']['ID'] = id
                                            inst.paramElem['Ctrl']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "FwdCtrl":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['FwdCtrl']['ID'] = id
                                            inst.paramElem['FwdCtrl']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "RevCtrl":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['RevCtrl']['ID'] = id
                                            inst.paramElem['RevCtrl']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "VSclMin":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['VSclMin']['ID'] = id
                                            inst.paramElem['VSclMin']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "VSclMax":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['VSclMax']['ID'] = id
                                            inst.paramElem['VSclMax']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "VMin":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['VMin']['ID'] = id
                                            inst.paramElem['VMin']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                            inst.addMin(float(attrNode.findtext(f"{NAMESPACE}DefaultValue")))
                                        elif attrNode.get("Name") == "VMax":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['VMax']['ID'] = id
                                            inst.paramElem['VMax']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                            inst.addMax(float(attrNode.findtext(f"{NAMESPACE}DefaultValue")))
                                        elif attrNode.get("Name") == "VUnit":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['VUnit']['ID'] = id
                                            inst.paramElem['VUnit']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                            unitId = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                            inst.unitval = int(unitId)
                                            inst.addUnit(getUnit(int(unitId)))

                                    # add instance to mtp
                                    mtp.addInstance(inst)
                            elif node.get("Name") == "SourceList" or node.get("Name") == "Sources":
                                # parse url
                                mtp.addUrl(url=node.findtext(f".//*[@Name='Endpoint']/{NAMESPACE}Value"))
                                # parse namespace
                                mtp.ns = node.findtext(f".//*[@Name='Namespace']/{NAMESPACE}Value")

            elif child.tag == f"{NAMESPACE}InstanceHierarchy" and child.get("Name") == "Services":
                for gchild in child:
                    if gchild.tag == f"{NAMESPACE}InternalElement":
                        keys = ['CommandEn',
                                'CommandExt',
                                'CommandInt',
                                'CommandOp',
                                'ConfigParamApplyEn',
                                'ConfigParamApplyExt',
                                'ConfigParamApplyInt',
                                'ConfigParamApplyOp',
                                'InteractAddInfo',
                                'InteractAnswerID',
                                'InteractQuestionID',
                                'OSLevel',
                                'PosTextID',
                                'ProcParamApplyEn',
                                'ProcParamApplyExt',
                                'ProcParamApplyInt',
                                'ProcParamApplyOp',
                                'ProcedureCur',
                                'ProcedureExt',
                                'ProcedureInt',
                                'ProcedureOp',
                                'ProcedureReq',
                                'ReportValueFreeze',
                                'SrcChannel',
                                'SrcExtAct',
                                'SrcExtAut',
                                'SrcExtOp',
                                'SrcIntAct',
                                'SrcIntAut',
                                'SrcIntOp',
                                'StateAutAct',
                                'StateAutAut',
                                'StateAutOp',
                                'StateChannel',
                                'StateCur',
                                'StateOffAct',
                                'StateOffAut',
                                'StateOffOp',
                                'StateOpAct',
                                'StateOpAut',
                                'StateOpOp']

                        inst = mtp.getInstance(instId=gchild.findtext(f"./{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}Value"))
                        serv = Service()
                        serv.name = gchild.get("Name") # name of the service
                        serv.id = gchild.get("ID") # id of the service
                        serv.refid = gchild.findtext(f"./{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}Value")
                        for key in keys:
                            serv.paramElem[key] = inst.paramElem[key]
                        mtp.addService(serv)

                        # get procedures
                        for ggchild in gchild:
                            if ggchild.tag == f"{NAMESPACE}InternalElement":
                                procName = ggchild.get("Name") # name of the procedure
                                procId = ggchild.findtext(f"./{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}Value") # id of the procedure
                                proc = Procedure(name=procName, id=procId)
                                serv.procs.append(proc)
                                mtp.procs.append(proc)
                                proc.serviceId = serv.id

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
                                    elif paramNode.tag == f"{NAMESPACE}Attribute" and paramNode.get("Name") == "ProcedureID":
                                        proc.procId = int(paramNode.findtext(f"{NAMESPACE}Value"))

            elif child.tag == f"{NAMESPACE}InstanceHierarchy" and child.get("Name") == "HMI":
                # parse HMI Information for HC10/HC2040
                children = child.findall(".//*[@RefBaseSystemUnitPath='MTPHMISUCLib/Picture']")
                if len(children) == 1:
                    # HC2040
                    # create HMI instance
                    hmi = HMI()
                    # set type to RI because HC2040 doesn't support services
                    hmi.type = "RI"
                    # set width, height and hierarchy level
                    for gchild in children[0]:
                        if gchild.tag == f"{NAMESPACE}Attribute":
                            # width
                            if gchild.get("Name") == "Width":
                                if int(gchild.findtext(f"{NAMESPACE}Value")) is not None:
                                    hmi.width = int(gchild.findtext(f"{NAMESPACE}Value"))
                                elif int(gchild.findtext(f"{NAMESPACE}DefaultValue")) is not None:
                                    hmi.width = int(gchild.findtext(f"{NAMESPACE}DefaultValue"))
                            # height
                            elif gchild.get("Name") == "Height":
                                if int(gchild.findtext(f"{NAMESPACE}Value")) is not None:
                                    hmi.height = int(gchild.findtext(f"{NAMESPACE}Value"))
                                elif int(gchild.findtext(f"{NAMESPACE}DefaultValue")) is not None:
                                    hmi.height = int(gchild.findtext(f"{NAMESPACE}DefaultValue"))
                            # hierarchy level
                            elif gchild.get("Name") == "HierarchyLevel":
                                if gchild.findtext(f"{NAMESPACE}Value") is not None:
                                    hmi.hierarchy = gchild.findtext(f"{NAMESPACE}Value")
                                elif gchild.findtext(f"{NAMESPACE}DefaultValue") is not None:
                                    hmi.hierarchy = gchild.findtext(f"{NAMESPACE}DefaultValue")
                        elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/VisualObject":
                            # add visual objects
                            visObj = VisualObject()
                            visObj.name = gchild.get("Name")
                            # width
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}Value") is not None:
                                visObj.width = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}DefaultValue") is not None:
                                visObj.width = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}DefaultValue")
                            # height
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}Value") is not None:
                                visObj.height = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}DefaultValue") is not None:
                                visObj.height = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}DefaultValue")
                            # x coordinate
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                visObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                visObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                            # y coordinate
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                visObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                visObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                            # z index
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value") is not None:
                                visObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue") is not None:
                                visObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue")
                            # rotation
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}Value") is not None:
                                visObj.rotation = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}DefaultValue") is not None:
                                visObj.rotation = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}DefaultValue")
                            # eClass Version
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}Value") is not None:
                                visObj.eClassVer = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}DefaultValue") is not None:
                                visObj.eClassVer = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}DefaultValue")
                            # eClass Classification Class
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}Value") is not None:
                                visObj.eClassClass = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}DefaultValue") is not None:
                                visObj.eClassClass = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}DefaultValue")
                            # eClass IRDI
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}Value") is not None:
                                visObj.eClassIRDI = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}DefaultValue") is not None:
                                visObj.eClassIRDI = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}DefaultValue")
                            # refId
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}Value") is not None:
                                visObj.refId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}DefaultValue") is not None:
                                visObj.refId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}DefaultValue")
                            # refInstance
                            visObj.refInst = mtp.getInstance(instId=visObj.refId)

                            # find nodes that have port information
                            portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                            for pn in portNodes:
                                # create port
                                port = Port()
                                port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                port.name = pn.get("Name")
                                # x coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                # y coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")

                                visObj.ports.append(port)
                            hmi.visuals.append(visObj)
                        elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/TopologyObject/Junction":
                            # add junction objects
                            junc = Junction()
                            junc.name = gchild.get("Name")
                            # x coordinate
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                junc.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                junc.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                            # y coordinate
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                junc.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                junc.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")

                            # find nodes that have port information
                            portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                            for pn in portNodes:
                                # create port
                                port = Port()
                                port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                port.name = pn.get("Name")
                                # x coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                # y coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                
                                junc.ports.append(port)
                            hmi.juncts.append(junc)
                        elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/TopologyObject/Termination/Sink":
                            # add sink objects
                            sinkObj = Sink()
                            sinkObj.name = gchild.get("Name")
                            # x coordinate
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                sinkObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                sinkObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                            # y coordinate
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                sinkObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                sinkObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                            # term ID
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}Value") is not None:
                                sinkObj.termId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}DefaultValue") is not None:
                                sinkObj.termId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}DefaultValue")
                            
                            # find nodes that have port information
                            portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                            for pn in portNodes:
                                # create port
                                port = Port()
                                port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                port.name = pn.get("Name")
                                # x coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                # y coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                
                                sinkObj.ports.append(port)
                            hmi.sinks.append(sinkObj)
                        elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/TopologyObject/Termination/Source":
                            # add source objects
                            sourceObj = Source()
                            sourceObj.name = gchild.get("Name")
                            # x coordinate
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                sourceObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                sourceObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                            # y coordinate
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                sourceObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                sourceObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                            # term ID
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}Value") is not None:
                                sourceObj.termId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}DefaultValue") is not None:
                                sourceObj.termId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}DefaultValue")
                            
                            # find nodes that have port information
                            portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                            for pn in portNodes:
                                # create port
                                port = Port()
                                port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                port.name = pn.get("Name")
                                # x coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                # y coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                
                                sourceObj.ports.append(port)
                            hmi.srcs.append(sourceObj)
                        elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/Connection/Pipe":
                            # add pipe objects
                            pipeObj = Pipe()
                            pipeObj.name = gchild.get("Name")
                            # directed flag
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Directed']/{NAMESPACE}Value") is not None:
                                pipeObj.direct = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Directed']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Directed']/{NAMESPACE}DefaultValue") is not None:
                                pipeObj.direct = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Directed']/{NAMESPACE}DefaultValue")
                            # edge path
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value") is not None:
                                pipeObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue") is not None:
                                pipeObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue")
                            
                            # find nodes that have port information
                            portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                            for pn in portNodes:
                                # create port
                                port = Port()
                                port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                port.name = pn.get("Name")
                                # x coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                # y coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                
                                pipeObj.ports.append(port)
                            hmi.pipes.append(pipeObj)
                        elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/Connection/FunctionLine":
                            # add function line objects
                            functlinObj = Line()
                            functlinObj.type = "Function Line"
                            functlinObj.name = gchild.get("Name")
                            # edge path
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value") is not None:
                                functlinObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue") is not None:
                                functlinObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue")
                            
                            # find nodes that have port information
                            portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/LogicalPort']")
                            for pn in portNodes:
                                # create port
                                port = Port()
                                port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                port.name = pn.get("Name")
                                # x coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                # y coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                
                                functlinObj.ports.append(port)
                            hmi.lines.append(functlinObj)
                        elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/Connection/MeasurementLine":
                            # add measurement line objects
                            measLinObj = Line()
                            measLinObj.type = "Measurement Line"
                            measLinObj.name = gchild.get("Name")
                            # edge path
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value") is not None:
                                measLinObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue") is not None:
                                measLinObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue")
                            
                            # find nodes that have port information
                            portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/MeasurementPoint']")
                            for pn in portNodes:
                                # create port
                                port = Port()
                                port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                port.name = pn.get("Name")
                                # x coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                # y coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                
                                measLinObj.ports.append(port)
                            hmi.lines.append(measLinObj)
                        elif gchild.tag == f"{NAMESPACE}InternalLink":
                            # side A
                            sideA = gchild.get("RefPartnerSideA")
                            # side B
                            sideB = gchild.get("RefPartnerSideB")
                            hmi.links.append((sideA, sideB))

                    mtp.hmis.append(hmi)
                else:
                    # HC10
                    for hminode in children:
                        # create hmi instance
                        hmi = HMI()
                        if hminode.get("Name") == "Services":
                            # set type to service
                            hmi.type = "Service"
                            for gchild in hminode:
                                if gchild.tag == f"{NAMESPACE}Attribute":
                                    if gchild.get("Name") == "Width":
                                        if int(gchild.findtext(f"{NAMESPACE}Value")) is not None:
                                            hmi.width = int(gchild.findtext(f"{NAMESPACE}Value"))
                                        elif int(gchild.findtext(f"{NAMESPACE}DefaultValue")) is not None:
                                            hmi.width = int(gchild.findtext(f"{NAMESPACE}DefaultValue"))
                                    elif gchild.get("Name") == "Height":
                                        if int(gchild.findtext(f"{NAMESPACE}Value")) is not None:
                                            hmi.height = int(gchild.findtext(f"{NAMESPACE}Value"))
                                        elif int(gchild.findtext(f"{NAMESPACE}DefaultValue")) is not None:
                                            hmi.height = int(gchild.findtext(f"{NAMESPACE}DefaultValue"))
                                    elif gchild.get("Name") == "HierarchyLevel":
                                        if gchild.findtext(f"{NAMESPACE}Value") is not None:
                                            hmi.hierarchy = gchild.findtext(f"{NAMESPACE}Value")
                                        elif gchild.findtext(f"{NAMESPACE}DefaultValue") is not None:
                                            hmi.hierarchy = gchild.findtext(f"{NAMESPACE}DefaultValue")
                                elif gchild.tag == f"{NAMESPACE}InternalElement":
                                    # add visual object
                                    visObj = VisualObject()
                                    visObj.name = gchild.get("Name")
                                    visObj.refId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}Value")
                                    visObj.refInst = mtp.getInstance(visObj.refId)
                                    visObj.width = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}Value")
                                    visObj.height = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}Value")
                                    visObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                    visObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                    visObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value")
                                    visObj.rotation = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}Value")
                                    visObj.eClassVer = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}Value")
                                    visObj.eClassClass = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}Value")
                                    visObj.eClassIRDI = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}Value")
                                    hmi.visuals.append(visObj)

                            mtp.hmis.append(hmi)
                        elif hminode.get("Name") == "RI_Fliessbild":
                            # set type to ri
                            hmi.type = "RI"
                            for gchild in hminode:
                                if gchild.tag == f"{NAMESPACE}Attribute":
                                    if gchild.get("Name") == "Width":
                                        if int(gchild.findtext(f"{NAMESPACE}Value")) is not None:
                                            hmi.width = int(gchild.findtext(f"{NAMESPACE}Value"))
                                        elif int(gchild.findtext(f"{NAMESPACE}DefaultValue")) is not None:
                                            hmi.width = int(gchild.findtext(f"{NAMESPACE}DefaultValue"))
                                    elif gchild.get("Name") == "Height":
                                        if int(gchild.findtext(f"{NAMESPACE}Value")) is not None:
                                            hmi.height = int(gchild.findtext(f"{NAMESPACE}Value"))
                                        elif int(gchild.findtext(f"{NAMESPACE}DefaultValue")) is not None:
                                            hmi.height = int(gchild.findtext(f"{NAMESPACE}DefaultValue"))
                                    elif gchild.get("Name") == "HierarchyLevel":
                                        if gchild.findtext(f"{NAMESPACE}Value") is not None:
                                            hmi.hierarchy = gchild.findtext(f"{NAMESPACE}Value")
                                        elif gchild.findtext(f"{NAMESPACE}DefaultValue") is not None:
                                            hmi.hierarchy = gchild.findtext(f"{NAMESPACE}DefaultValue")
                                elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/TopologyObject/Termination/Sink":
                                    # add sink objects
                                    sinkObj = Sink()
                                    sinkObj.name = gchild.get("Name")
                                    # x coordinate
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                        sinkObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                        sinkObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                    # y coordinate
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                        sinkObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                        sinkObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                    # term ID
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}Value") is not None:
                                        sinkObj.termId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}DefaultValue") is not None:
                                        sinkObj.termId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}DefaultValue")
                                    
                                    # find nodes that have port information
                                    portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                                    for pn in portNodes:
                                        # create port
                                        port = Port()
                                        port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                        port.name = pn.get("Name")
                                        # x coordinate
                                        if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                            port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                        elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                            port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                        # y coordinate
                                        if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                            port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                        elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                            port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                        
                                        sinkObj.ports.append(port)
                                    hmi.sinks.append(sinkObj)
                                elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/TopologyObject/Junction":
                                    # add junction objects
                                    junc = Junction()
                                    junc.name = gchild.get("Name")
                                    # x coordinate
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                        junc.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                        junc.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                    # y coordinate
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                        junc.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                        junc.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")

                                    # find nodes that have port information
                                    portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                                    for pn in portNodes:
                                        # create port
                                        port = Port()
                                        port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                        port.name = pn.get("Name")
                                        # x coordinate
                                        if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                            port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                        elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                            port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                        # y coordinate
                                        if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                            port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                        elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                            port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                        
                                        junc.ports.append(port)
                                    hmi.juncts.append(junc)
                                elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/Connection/MeasurementLine":
                                    # add measurement line objects
                                    measLinObj = Line()
                                    measLinObj.type = "Measurement Line"
                                    measLinObj.name = gchild.get("Name")
                                    # edge path
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value") is not None:
                                        measLinObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue") is not None:
                                        measLinObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue")
                                    
                                    # find nodes that have port information
                                    portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/MeasurementPoint']")
                                    for pn in portNodes:
                                        # create port
                                        port = Port()
                                        port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                        port.name = pn.get("Name")
                                        # x coordinate
                                        if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                            port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                        elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                            port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                        # y coordinate
                                        if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                            port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                        elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                            port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                        
                                        measLinObj.ports.append(port)
                                    hmi.lines.append(measLinObj)
                                elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/Connection/FunctionLine":
                                    # add function line objects
                                    functlinObj = Line()
                                    functlinObj.type = "Function Line"
                                    functlinObj.name = gchild.get("Name")
                                    # edge path
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value") is not None:
                                        functlinObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue") is not None:
                                        functlinObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue")
                                    
                                    # find nodes that have port information
                                    portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/LogicalPort']")
                                    for pn in portNodes:
                                        # create port
                                        port = Port()
                                        port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                        port.name = pn.get("Name")
                                        # x coordinate
                                        if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                            port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                        elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                            port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                        # y coordinate
                                        if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                            port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                        elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                            port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                        
                                        functlinObj.ports.append(port)
                                    hmi.lines.append(functlinObj)
                                elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/Connection/Pipe":
                                    # add pipe objects
                                    pipeObj = Pipe()
                                    pipeObj.name = gchild.get("Name")
                                    # directed flag
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Directed']/{NAMESPACE}Value") is not None:
                                        pipeObj.direct = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Directed']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Directed']/{NAMESPACE}DefaultValue") is not None:
                                        pipeObj.direct = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Directed']/{NAMESPACE}DefaultValue")
                                    # edge path
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value") is not None:
                                        pipeObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue") is not None:
                                        pipeObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue")
                                    
                                    # find nodes that have port information
                                    portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                                    for pn in portNodes:
                                        # create port
                                        port = Port()
                                        port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                        port.name = pn.get("Name")
                                        # x coordinate
                                        if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                            port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                        elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                            port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                        # y coordinate
                                        if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                            port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                        elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                            port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                        
                                        pipeObj.ports.append(port)
                                    hmi.pipes.append(pipeObj)
                                elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/VisualObject":
                                    # add visual objects
                                    visObj = VisualObject()
                                    visObj.name = gchild.get("Name")
                                    # width
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}Value") is not None:
                                        visObj.width = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}DefaultValue") is not None:
                                        visObj.width = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}DefaultValue")
                                    # height
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}Value") is not None:
                                        visObj.height = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}DefaultValue") is not None:
                                        visObj.height = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}DefaultValue")
                                    # x coordinate
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                        visObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                        visObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                    # y coordinate
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                        visObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                        visObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                    # z index
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value") is not None:
                                        visObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue") is not None:
                                        visObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue")
                                    # rotation
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}Value") is not None:
                                        visObj.rotation = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}DefaultValue") is not None:
                                        visObj.rotation = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}DefaultValue")
                                    # eClass Version
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}Value") is not None:
                                        visObj.eClassVer = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}DefaultValue") is not None:
                                        visObj.eClassVer = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}DefaultValue")
                                    # eClass Classification Class
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}Value") is not None:
                                        visObj.eClassClass = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}DefaultValue") is not None:
                                        visObj.eClassClass = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}DefaultValue")
                                    # eClass IRDI
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}Value") is not None:
                                        visObj.eClassIRDI = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}DefaultValue") is not None:
                                        visObj.eClassIRDI = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}DefaultValue")
                                    # refId
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}Value") is not None:
                                        visObj.refId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}DefaultValue") is not None:
                                        visObj.refId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}DefaultValue")
                                    # refInstance
                                    visObj.refInst = mtp.getInstance(instId=visObj.refId)
                                    
                                    # find nodes that have port information
                                    portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                                    for pn in portNodes:
                                        # create port
                                        port = Port()
                                        port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                        port.name = pn.get("Name")
                                        # x coordinate
                                        if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                            port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                        elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                            port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                        # y coordinate
                                        if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                            port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                        elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                            port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                        
                                        visObj.ports.append(port)
                                    hmi.visuals.append(visObj)
                                elif gchild.tag == f"{NAMESPACE}InternalLink":
                                    sideA = gchild.get("RefPartnerSideA")
                                    sideB = gchild.get("RefPartnerSideB")
                                    hmi.links.append((sideA, sideB))

                            mtp.hmis.append(hmi)
            elif child.tag == f"{NAMESPACE}InstanceHierarchy" and child.get("Name") == "Pictures":
                # parse HMI Information for HC30
                hminode = child.find(f".//*[@RefBaseSystemUnitPath='MTPHMISUCLib/Picture'][@Name='{mtp.name}']")
                # create hmi
                hmi = HMI()
                # set type to RI because HC30 doesn't support services
                hmi.type = "RI"
                for gchild in hminode:
                    if gchild.tag == f"{NAMESPACE}Attribute":
                        if gchild.get("Name") == "Width":
                            if int(gchild.findtext(f"{NAMESPACE}Value")) is not None:
                                hmi.width = int(gchild.findtext(f"{NAMESPACE}Value"))
                            elif int(gchild.findtext(f"{NAMESPACE}DefaultValue")) is not None:
                                hmi.width = int(gchild.findtext(f"{NAMESPACE}DefaultValue"))
                        elif gchild.get("Name") == "Height":
                            if int(gchild.findtext(f"{NAMESPACE}Value")) is not None:
                                hmi.height = int(gchild.findtext(f"{NAMESPACE}Value"))
                            elif int(gchild.findtext(f"{NAMESPACE}DefaultValue")) is not None:
                                hmi.height = int(gchild.findtext(f"{NAMESPACE}DefaultValue"))
                        elif gchild.get("Name") == "HierarchyLevel":
                            if gchild.findtext(f"{NAMESPACE}Value") is not None:
                                hmi.hierarchy = gchild.findtext(f"{NAMESPACE}Value")
                            elif gchild.findtext(f"{NAMESPACE}DefaultValue") is not None:
                                hmi.hierarchy = gchild.findtext(f"{NAMESPACE}DefaultValue")
                    elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/Connection/MeasurementLine":
                        # add measurement line objects
                        measLinObj = Line()
                        measLinObj.type = "Measurement Line"
                        measLinObj.name = gchild.get("Name")
                        # edge path
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value") is not None:
                            measLinObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue") is not None:
                            measLinObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue")
                        # z index
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value") is not None:
                            measLinObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue") is not None:
                            measLinObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue")
                        
                        # find nodes that have port information
                        portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/MeasurementPoint']")
                        for pn in portNodes:
                            # create port
                            port = Port()
                            port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                            port.name = pn.get("Name")
                            # x coordinate
                            if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                            elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                            # y coordinate
                            if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                            elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                            
                            measLinObj.ports.append(port)
                        hmi.lines.append(measLinObj)
                    elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/Connection/Pipe":
                        # add pipe objects
                        pipeObj = Pipe()
                        pipeObj.name = gchild.get("Name")
                        # directed flag
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Directed']/{NAMESPACE}Value") is not None:
                            pipeObj.direct = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Directed']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Directed']/{NAMESPACE}DefaultValue") is not None:
                            pipeObj.direct = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Directed']/{NAMESPACE}DefaultValue")
                        # edge path
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value") is not None:
                            pipeObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue") is not None:
                            pipeObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue")
                        # z Index
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value") is not None:
                            pipeObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue") is not None:
                            pipeObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue")
                        
                        # find nodes that have port information
                        portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                        for pn in portNodes:
                            # create port
                            port = Port()
                            port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                            port.name = pn.get("Name")
                            # x coordinate
                            if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                            elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                            # y coordinate
                            if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                            elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                            
                            pipeObj.ports.append(port)
                        hmi.pipes.append(pipeObj)
                    elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/VisualObject":
                        # add visual objects
                        visObj = VisualObject()
                        visObj.name = gchild.get("Name")
                        # width
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}Value") is not None:
                            visObj.width = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}DefaultValue") is not None:
                            visObj.width = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}DefaultValue")
                        # height
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}Value") is not None:
                            visObj.height = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}DefaultValue") is not None:
                            visObj.height = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}DefaultValue")
                        # x coordinate
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                            visObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                            visObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                        # y coordinate
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                            visObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                            visObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                        # z index
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value") is not None:
                            visObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue") is not None:
                            visObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue")
                        # rotation
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}Value") is not None:
                            visObj.rotation = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}DefaultValue") is not None:
                            visObj.rotation = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}DefaultValue")
                        # eClass Version
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}Value") is not None:
                            visObj.eClassVer = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}DefaultValue") is not None:
                            visObj.eClassVer = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}DefaultValue")
                        # eClass Classification Class
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}Value") is not None:
                            visObj.eClassClass = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}DefaultValue") is not None:
                            visObj.eClassClass = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}DefaultValue")
                        # eClass IRDI
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}Value") is not None:
                            visObj.eClassIRDI = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}DefaultValue") is not None:
                            visObj.eClassIRDI = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}DefaultValue")
                        # refId
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}Value") is not None:
                            visObj.refId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}DefaultValue") is not None:
                            visObj.refId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}DefaultValue")
                        # refInstance
                        visObj.refInst = mtp.getInstance(instId=visObj.refId)

                        # find nodes that have port information
                        portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                        for pn in portNodes:
                            # create port
                            port = Port()
                            port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                            port.name = pn.get("Name")
                            # x coordinate
                            if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                            elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                            # y coordinate
                            if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                            elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")

                            visObj.ports.append(port)
                        hmi.visuals.append(visObj)
                    elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/TopologyObject/Termination/Source":
                        # add source objects
                        sourceObj = Source()
                        sourceObj.name = gchild.get("Name")
                        # x coordinate
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                            sourceObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                            sourceObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                        # y coordinate
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                            sourceObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                            sourceObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                        # z index
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value") is not None:
                            sourceObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue") is not None:
                            sourceObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue")
                        # term ID
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}Value") is not None:
                            sourceObj.termId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}DefaultValue") is not None:
                            sourceObj.termId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}DefaultValue")
                        
                        # find nodes that have port information
                        portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                        for pn in portNodes:
                            # create port
                            port = Port()
                            port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                            port.name = pn.get("Name")
                            # x coordinate
                            if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                            elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                            # y coordinate
                            if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                            elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                            
                            sourceObj.ports.append(port)
                        hmi.srcs.append(sourceObj)
                    elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/TopologyObject/Termination/Sink":
                        # add sink objects
                        sinkObj = Sink()
                        sinkObj.name = gchild.get("Name")
                        # x coordinate
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                            sinkObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                            sinkObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                        # y coordinate
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                            sinkObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                            sinkObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                        # z index
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value") is not None:
                            sinkObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue") is not None:
                            sinkObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue")
                        # term ID
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}Value") is not None:
                            sinkObj.termId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}DefaultValue") is not None:
                            sinkObj.termId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}DefaultValue")
                        
                        # find nodes that have port information
                        portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                        for pn in portNodes:
                            # create port
                            port = Port()
                            port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                            port.name = pn.get("Name")
                            # x coordinate
                            if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                            elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                            # y coordinate
                            if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                            elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                            
                            sinkObj.ports.append(port)
                        hmi.sinks.append(sinkObj)
                    elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/TopologyObject/Junction":
                            # add junction objects
                            junc = Junction()
                            junc.name = gchild.get("Name")
                            # x coordinate
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                junc.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                junc.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                            # y coordinate
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                junc.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                junc.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                            # z index
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value") is not None:
                                junc.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue") is not None:
                                junc.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue")

                            # find nodes that have port information
                            portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                            for pn in portNodes:
                                # create port
                                port = Port()
                                port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                port.name = pn.get("Name")
                                # x coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                # y coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                
                                junc.ports.append(port)
                            hmi.juncts.append(junc)

                mtp.hmis.append(hmi)
        # get sensors and actuators
        for i in mtp.insts:
            if not (mtp.hasParameter(i.id) or mtp.hasProcedure(i.id) or mtp.hasService(i.id) or i.name == "PeaInforamtionLabel"):
                mtp.sensacts.append(i)

    ## debugging only
    # for m in mtps:
    #     print(m.name)
    #     for s in m.servs:
    #         print(s.name, s.id)
    #         for p in s.procs:
    #             print("  ", p.name, p.id)
    #             for pa in p.params:
    #                 print("    ", pa.name, pa.id, pa.default, pa.unit)
    #         print("\n")

    ## debugging only
    # print("Services: ")
    # for s in mtp.servs:
    #     print(s.name)
    # print("\n", "Procedures: ")
    # for p in mtp.procs:
    #     print(p.name)
    # print("\n", "Sensors and Actuators: ")
    # for sa in mtp.sensacts:
    #     if sa.paramElem["V"]["ID"] is not None:
    #         print(sa.name, sa.paramElem["V"]["ID"])
    #     elif sa.paramElem["VOut"]["ID"] is not None:
    #         print(sa.name, sa.paramElem["VOut"]["ID"])
    #     elif sa.paramElem["Pos"]["ID"] is not None:
    #         print(sa.name, sa.paramElem["Pos"]["ID"])
    #     elif sa.paramElem["Ctrl"]["ID"] is not None:
    #         print(sa.name, sa.paramElem["Ctrl"]["ID"])

    return mtps

if __name__ == "__main__":
    getMtps()
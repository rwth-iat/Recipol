"""Domain models for MTP parser."""

class Instance:
    def __init__(self, name, id):
        self.name = name # name of the instance
        self.id = id # ID of the instance
        # Full AML path (e.g. ".../ProcessValueOut") used to classify parameter nodes in UI.
        self.ref_base_system_unit_path = None
        # Derived short type from path tail (e.g. ProcessValueOut).
        self.parameter_type = None
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

    def addRefBaseSystemUnitPath(self, path: str):
        """Store RefBaseSystemUnitPath and derive UI-friendly parameter type."""
        self.ref_base_system_unit_path = path
        if path:
            self.parameter_type = path.rsplit("/", 1)[-1]
        else:
            self.parameter_type = None

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
        self.source_file = "" # source AML file path

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


### imports
from __future__ import annotations

from defusedxml.ElementTree import parse
import xmlschema


### static variables
TESTXML10 = r"Artefakte\Wabe10_Grundrezept.xml"
#TESTXML20 = r""
TESTXML30 = r"Artefakte\Wabe30_Grundrezept.xml"
SCHEMA = r"Schemas\AllSchemas.xsd"
NAMESPACE = "{http://www.mesa.org/xml/B2MML}"

### classes
class Requirement:
    def __init__(self, id:str = "", const:str = ""):
        self.id = id # unique identifier of the requirement
        self.const = const # constraint of the requirement

    def __str__(self):
        return f"ID: {self.id}, CONSTRAINT: {self.const}"

    def nameRequirement(self, id:str):
        """Adds a unique identifier to the requirement."""
        
        if self.id != "":
            print("Cannot change id of existing requirement.")
        else:
            self.id = id

    def addConstraint(self, const:str):
        """Adds a constraint to the requirement."""
        
        if self.const != "":
            print("Cannot overwrite existing constraint of requirement.")
        else:
            self.const = const

class Parameter:
    def __init__(self, id:str = "", value:str = "", dtype:str = "", unit:str = ""):
        self.id = id # unique identifier of the parameter
        self.value = value # value of the paraemter
        self.dtype = dtype # datatype of the parameter
        self.unit = unit # measurement unit of the parameter

    def __str__(self):
        return f"ID: {self.id}, DATATYPE: {self.dtype}, VALUE: {self.value} {self.unit}"
    
    def nameParameter(self, id:str):
        """Adds a unique identifier to the parameter."""

        if self.id != "":
            print("Cannot change id of existing requirement.")
        else:
            self.id = id

    def addValue(self, value:str):
        """Adds a value to the parameter."""

        self.value = value

    def addDataType(self, dtype:str):
        """Adds a datatype to the parameter."""
        
        self.dtype = dtype

    def addUnit(self, unit:str):
        """Adds a unit of measurement to the parameter."""

        self.unit = unit

class Procedure:
    def __init__(self, id:str):
        self.id = id # the id of the procedure
        self.params = [] # the list of parameters of the procedure

    def __str__(self):
        return self.id

    def addParameter(self, param:Parameter):
        """Adds a parameter to the procedure"""

        self.params.append(param)

class Resource:
    def __init__(self, id:str):
        self.id = id # the id of the resource
        self.skills = [] # the procedures of the resource

    def __str__(self):
        return f"ID: {self.id}, Procedures: {','.join(s.id for s in self.skills)}"
    
    def addProcedure(self, proc:Procedure):
        """Adds a procedure to the resource"""

        self.skills.append(proc)

class Element:
    def __init__(self, etype:str, id:str):
        if etype == "Step":
            self.acts = [] # procedures executing during the step
            self.reqs = [] # requirements associated with the procedures
            self.init = False # whether initial step or not
            self.res = None # the resource that executes this step's procedures
            self.params = [] # parameters for the procedure
            self.cond = None # condition only for transitions
        else:
            self.acts = None # procedures only for steps
            self.reqs = None # requirements only for steps
            self.init = None # transition cannot be initial element
            self.res = None # resources only for steps
            self.params = None # parameters only for steps
            self.cond = None # condition of the transition

        self.etype = etype
        self.id = id
        self.name = None
        self.retype = None
        self.preds = [] # the element(s) that precedes this element
        self.posts = [] # the element(s) that follow this element

    def __str__(self):
        if self.init:
            descr = f"Initial {self.etype} {self.name}:\n"
        else:
            descr = f"{self.etype} {self.name}:\n"

        descr += f"    Predecessors: {','.join(p.name for p in self.preds)}\n"

        if self.etype == "Step":
            descr += f"    Requirements: {','.join(r.id for r in self.reqs)}\n"
            descr += f"    Procedures: {','.join(a.id for a in self.acts)}\n"
            descr += f"    Parameters: {','.join(p.id for p in self.params)}\n"
            descr += f"    Resource: {self.res}\n"
        else:
            descr += f"    Condition: {self.cond}\n"

        descr += f"    Successors: {','.join(p.name for p in self.posts)}\n"

        return descr

    def getId(self) -> str:
        """Returns the id of the element"""
        return self.id
    
    def setName(self, name:str) -> None:
        """Gives a name to the element"""
        self.name = name
    
    def getName(self) -> str:
        """Returns the name of the element"""
        return self.name

    def setRecipeElementType(self, type:str) -> None:
        """Adds a RecipeElementType to the element"""
        self.retype = type

    def getRecipeElementType(self) -> str:
        """Returns the RecipeElementType"""
        return self.retype

    def addPred(self, pred:Element):
        """Adds a predecessor to the list of preds"""
        self.preds.append(pred)

    def getPred(self) -> Element | list[Element]:
        """Returns the preceding element(s)"""
        return self.preds

    def addPost(self, post:Element):
        """Adds a sucessor to the list of posts"""
        self.posts.append(post)

    def getPost(self) -> Element | list[Element]:
        """Returns the following element(s)"""
        return self.posts

    def changeId(self, id:str):
        """Replaces the element ID (Step/Transition) with the RecipeElementID"""
        self.id = id

    def addCond(self, cond:str):
        """Adds a condition to the transition"""
        self.cond = cond

    def getCond(self) -> str:
        """Returns the condition of the transition"""
        return self.cond

    def getType(self) -> str | None:
        """Returns the type of the element"""
        return self.etype
    
    def setType(self, etype:str):
        """Sets the type of the element"""
        self.etype = etype

    def setInit(self):
        """Sets the element as initial element"""
        self.init = True

    def isInit(self) -> bool:
        """Returns the value of the init"""
        return self.init

    def addResource(self, res:Resource):
        """Adds a resource to the element"""
        self.res = res

    def addRequirement(self, req:Requirement):
        """Adds a requirement to the element's requirements"""
        self.reqs.append(req)

    def addParameter(self, param:Parameter):
        """Adds a parameter to the element's parameters"""
        self.params.append(param)

    def getParameter(self) -> list[Parameter]:
        """Returns the parameter of the element"""
        return self.params

    def addProcedure(self, proc:Procedure):
        """Adds a procedure to the element's procedures"""
        self.acts.append(proc)

class Bml:
    def __init__(self):
        self.reqs:list[Requirement] = [] # list of requirements of the b2mml file
        self.params:list[Parameter] = [] # list of parameters of the b2mml file
        self.elems:list[Element] = [] # list of elements of the b2mml file
        self.res:list[Resource] = [] # list of resources of the b2mml file

    def __str__(self):
        descr = "Requirements:\n"

        for req in self.reqs:
            descr += f"{str(req)}\n"

        descr += "\nParameters:\n"

        for param in self.params:
            descr += f"{str(param)}\n"

        descr += "\nResources:\n"

        for res in self.res:
            descr += f"{str(res)}\n"

        descr += "\n"

        for elem in self.elems:
            descr += f"{str(elem)}\n"

        return descr

    def addRequirement(self, req:Requirement):
        """Adds a requirement to the bml instance."""
        
        self.reqs.append(req)

    def addParameter(self, param:Parameter):
        """Adds a parameter to the bml instance."""

        self.params.append(param)

    def getElement(self, eID:str) -> Element | None:
        """Returns the element if it exists, otherwise None."""
        for e in self.elems:
            if e.id == eID:
                return e
            
        return None

    def addElement(self, elem:Element):
        """Adds an element to the bml's list of elements"""
        self.elems.append(elem)

    def getInitialElement(self) -> Element:
        """Returns the initial element"""
        for e in self.elems:
            if e.isInit():
                return e
            
        raise RuntimeError("No initial step has been declared.")

    def getResource(self, rID:str) -> Resource | None:
        """Returns the resource if it exists, otherwise None."""
        for r in self.res:
            if r.id == rID:
                return r
            
        return None
    
    def addResource(self, res:Resource):
        """Adds a resource to the bml's list of resources"""
        self.res.append(res)

    def getRequirement(self, reqId) -> Requirement | None:
        """Returns the requirement if it exists, otherwise None."""
        for r in self.reqs:
            if r.id == reqId:
                return r
            
        return None
    
    def getParameter(self, paramId) -> Parameter | None:
        """Returns the parameter if it exists, otherwise None."""
        for p in self.params:
            if p.id == paramId:
                return p
            
        return None

### functions
def parseMasterRecipe(node):
    for child in node:
        if child.tag == f"{NAMESPACE}EquipmentRequirement":
            # create requirement object
            req = Requirement()

            # fetch information about requirement
            for gchild in child:
                if gchild.tag == f"{NAMESPACE}ID":
                    req.nameRequirement(gchild.text)
                elif gchild.tag == f"{NAMESPACE}Constraint":
                    req.addConstraint(gchild.findtext(f"{NAMESPACE}Condition"))

            # add requirement to bml's requirements
            bml.addRequirement(req)

        elif child.tag == f"{NAMESPACE}Formula":
            for gchild in child:
                if gchild.tag == f"{NAMESPACE}Parameter":
                    # create parameter object
                    param = Parameter()

                    # fetch information about parameter
                    param.nameParameter(gchild.findtext(f"{NAMESPACE}ID"))
                    param.addValue(gchild.find(f"{NAMESPACE}Value").findtext(f"{NAMESPACE}ValueString"))
                    param.addDataType(gchild.find(f"{NAMESPACE}Value").findtext(f"{NAMESPACE}DataType"))
                    param.addUnit(gchild.find(f"{NAMESPACE}Value").findtext(f"{NAMESPACE}UnitOfMeasure"))

                    # add parameter to bml's parameters
                    bml.addParameter(param)

        elif child.tag == f"{NAMESPACE}ProcedureLogic":
            for gchild in child:
                if gchild.tag == f"{NAMESPACE}Link" and gchild.findtext(f"{NAMESPACE}LinkType") == "ControlLink":
                    # To Do: build structure
                    fromId = gchild.find(f"{NAMESPACE}FromID").findtext(f"{NAMESPACE}FromIDValue")
                    fromType = gchild.find(f"{NAMESPACE}FromID").findtext(f"{NAMESPACE}FromType")
                    toId = gchild.find(f"{NAMESPACE}ToID").findtext(f"{NAMESPACE}ToIDValue")
                    toType = gchild.find(f"{NAMESPACE}ToID").findtext(f"{NAMESPACE}ToType")

                    fromElem = bml.getElement(fromId)
                    toElem = bml.getElement(toId)

                    if fromElem is None:
                        # element doesn't exist yet, create it
                        if fromType == "Step" or fromType == "Transition":
                            fromElem = Element(etype=fromType, id=fromId)
                        else:
                            # To Do: add parallel divergence and convergence structure
                            pass
                        
                        bml.addElement(fromElem)
                    elif fromElem.getType() is None:
                        fromElem.setType(fromType)

                    if toElem is None:
                        # element doesn't exist yet, create it
                        if toType == "Step" or toType == "Transition":
                            toElem = Element(etype=toType, id=toId)
                        else:
                            # To Do: add parallel divergence and convergence structure
                            pass
                        
                        bml.addElement(toElem)
                    elif toElem.getType() is None:
                        toElem.setType(toType)

                    # add references
                    fromElem.addPost(toElem)
                    toElem.addPred(fromElem)
                elif gchild.tag == f"{NAMESPACE}Link" and not gchild.findtext(f"{NAMESPACE}LinkType") == "ControlLink":
                    # To Do: do parallel divergences and convergences
                    pass
                elif gchild.tag == f"{NAMESPACE}Step":
                    stepElem = bml.getElement(gchild.findtext(f"{NAMESPACE}ID"))

                    # starting from this point the element will be adressed by the recipe element id
                    # replace the procedure logic id by the recipe element id
                    if stepElem is not None:
                        stepElem.changeId(gchild.findtext(f"{NAMESPACE}RecipeElementID"))
                        stepElem.setName(gchild.findtext(f"{NAMESPACE}Description"))
                elif gchild.tag == f"{NAMESPACE}Transition":
                    transElem = bml.getElement(gchild.findtext(f"{NAMESPACE}ID"))
                    
                    # add condition
                    transElem.addCond(gchild.findtext(f"{NAMESPACE}Condition"))

                    # add name
                    transElem.setName(name=transElem.getId())

        elif child.tag == f"{NAMESPACE}RecipeElement":
            # get the element
            thisElem = bml.getElement(child.findtext(f"{NAMESPACE}ID"))
            thisElem.setRecipeElementType(child.findtext(f"{NAMESPACE}RecipeElementType"))
            if child.findtext(f"{NAMESPACE}RecipeElementType") == "Begin":
                # set as initial element
                thisElem.setInit()
            else:
                for gchild in child:
                    if gchild.tag == f"{NAMESPACE}ActualEquipmentID":
                        resId = gchild.text

                        res = bml.getResource(resId)

                        if res is None:
                            # resource doesn't exist yet, create new one
                            res = Resource(resId)
                            bml.addResource(res)

                        # add the resource to the element
                        thisElem.addResource(res)
                    elif gchild.tag == f"{NAMESPACE}EquipmentRequirement":
                        reqId = gchild.findtext(f"{NAMESPACE}ID")
                        req = bml.getRequirement(reqId)

                        if req is None:
                            # requirement doesn't exist yet, create new one
                            req = Requirement()

                            # fetch information about requirement
                            req.nameRequirement(reqId)
                            req.addConstraint(gchild.find(f"{NAMESPACE}Constraint").findtext(f"{NAMESPACE}Condition"))

                            # add requirement to bml's requirements
                            bml.addRequirement(req)
                        
                        # add the requirement to the element
                        thisElem.addRequirement(req)
                    elif gchild.tag == f"{NAMESPACE}Parameter":
                        paramId = gchild.findtext(f"{NAMESPACE}ID")
                        param = bml.getParameter(paramId)

                        if param is None:
                            # parameter doesn't exist qet, create new one
                            param = Parameter(id=paramId)
                            param.addDataType(gchild.find(f"{NAMESPACE}Value".findtext(f"{NAMESPACE}DataType")))
                            param.addUnit(gchild.find(f"{NAMESPACE}Value".findtext(f"{NAMESPACE}UnitOfMeasure")))
                            param.addValue(gchild.find(f"{NAMESPACE}Value".findtext(f"{NAMESPACE}ValueString")))

                            # add param to bml
                            bml.addParameter(param)

                        # add param to element
                        thisElem.addParameter(param)

def parseResource(node):
    if node.findtext(f"{NAMESPACE}EquipmentElementType") == "Instance":
        # get the instance
        resId = node.findtext(f"{NAMESPACE}ID")
        thisRes = bml.getResource(resId)

        if thisRes is None:
            # create new resource
            thisRes = Resource(id=resId)

        for child in node:
            if child.tag == f"{NAMESPACE}EquipmentProceduralElement":
                # create procedures
                procId = child.findtext(f"{NAMESPACE}ID")
                thisProc = Procedure(id=procId)

                for gchild in child:
                    if gchild.tag == f"{NAMESPACE}Parameter":
                        # parse parameter
                        paramId = gchild.findtext(f"{NAMESPACE}ID")

                        # see if param exists
                        thisParam = bml.getParameter(paramId)

                        if thisParam is None:
                            # create new Parameter
                            thisParam = Parameter(id=paramId)
                            thisParam.addDataType(gchild.findtext(f"{NAMESPACE}DataType"))
                            thisParam.addUnit(gchild.findtext(f"{NAMESPACE}UnitOfMeasure"))
                            thisParam.addValue(gchild.findtext(f"{NAMESPACE}ValueString"))

                        # add parameter to procedure
                        thisProc.addParameter(thisParam)

                # add procedure to resource
                thisRes.addProcedure(thisProc)

                # see if procedure is also called in step
                procStep = bml.getElement(eID=procId)

                if procStep is not None:
                    procStep.addProcedure(thisProc)

def sortElements() -> list[Element]:
    # get initial element
    initElem = bml.getInitialElement()
    # list of sorted elements
    sortedElems = []
    # helper list during sorting
    helpSort:list[Element] = []

    # add initial element to both lists
    sortedElems.append([initElem])
    helpSort.append(initElem)

    # while there are still unseen elements sort
    while len(helpSort) > 0:
        curr = helpSort[0]
        # differentiate between single objects and nested lists
        if type(curr) is not list:
            # initial is handled differently
            if curr != initElem:
                # check if all of curr's predecessors are already in the list
                preds = curr.getPred()
                isNext = True
                for p in preds:
                    if not any(p in sl for sl in sortedElems):
                        isNext = False
                        break
                if isNext:
                    # all predecessors are already in list, add following elements to sorted and help lists unless post is empty
                    posts = curr.getPost()
                    if len(posts) > 0:
                        sortedElems.append(curr.posts)
                        helpSort.extend(curr.posts)

                    # remove the current element from helpSort
                    helpSort.remove(curr)
                else:
                    # check if there are still other elements in the list
                    if len(helpSort) > 1:
                        # switch current element with next
                        helpSort[1], helpSort[0] = helpSort[0], helpSort[1]
                    else:
                        # error case with unreachable predecessor
                        raise RuntimeError(f"Cannot find predecessing element of {curr.getId()}")

            else:
                # add the initial element's following elements to sorted and help lists unless initial doesn't have following elements
                posts = curr.getPost()
                if len(posts) > 0:
                    sortedElems.append(curr.getPost())
                    helpSort.extend(curr.getPost())

                # remove the current element from helpSort
                helpSort.remove(curr)
        else: 
            # do the same but for nested elements
            for c in curr:
                # check if all of c's predecessors are already in the list
                preds = c.getPred()
                isNext = True
                for p in preds:
                    if not any(p in sl for sl in sortedElems):
                        isNext = False
                        break
                if isNext:
                    # all predecessors are already in list, add following elements to sorted and help lists unless posts is empty
                    posts = c.getPost()
                    if len(posts) > 0:
                        sortedElems.append(c.getPost())
                        helpSort.extend(c.getPost())

                    # remove the current element from helpSort
                    helpSort.remove(c)
                else:
                    # check if there are still other elements in the list
                    if len(helpSort) > 1:
                        # switch current element with next
                        helpSort[1], helpSort[0] = helpSort[0], helpSort[1]
                    else:
                        # error case with unreachable predecessor
                        raise RuntimeError(f"Cannot find predecessing element of {c.getId()}")
                    
    # sortedList is a list of lists
    # we want single elements to simply be part of the list but if there is parallel execution (= sublist with multiple elements) it shall stay sublist
    orderedList = []
    for e in sortedElems:
        if len(e) == 1:
            orderedList.extend(e)
        else:
            orderedList.append(e)
                    
    return orderedList

### start main
# validate b2mml file
xmlschema.validate(TESTXML30, SCHEMA)

# parse b2mml file
tree = parse(TESTXML30)
root = tree.getroot()

# create bml object
bml = Bml()

# iterate over b2mml elements
for child in root:
    if child.tag == f"{NAMESPACE}MasterRecipe":
        # parse MasterRecipe
        parseMasterRecipe(node=child)
    elif child.tag == f"{NAMESPACE}EquipmentElement":
        # parse Resources
        parseResource(node=child)

# create list
sortedList = sortElements()

#print(bml)
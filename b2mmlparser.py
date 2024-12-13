### imports
from __future__ import annotations

from defusedxml.ElementTree import parse
from enum import Enum


### static variables
TESTXML = r"Artefakte\2024-11-03_MasterRecipeHC.xml"
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
    pass

class Resource:
    pass

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
        self.preds = [] # the element(s) that precedes this element
        self.posts = [] # the element(s) that follow this element

    def __str__(self):
        if self.init:
            descr = f"Initial {self.etype} {self.id}:\n"
        else:
            descr = f"{self.etype} {self.id}:\n"

        descr += f"    Predecessors: {','.join(p.id for p in self.preds)}\n"

        if self.etype == "Step":
            descr += f"    Requirements: {','.join(r.id for r in self.reqs)}\n"
            descr += f"    Procedures: {','.join(a.id for a in self.acts)}\n"
            descr += f"    Parameters: {','.join(p.id for p in self.params)}\n"
            descr += f"    Resource: {self.res}\n"
        else:
            descr += f"    Condition: {self.cond}\n"

        descr += f"    Successors: {','.join(p.id for p in self.posts)}\n"

        return descr

    def addPred(self, pred:Element):
        """Adds a predecessor to the list of preds"""
        self.preds.append(pred)

    def addPost(self, post:Element):
        """Adds a sucessor to the list of posts"""
        self.posts.append(post)

    def changeId(self, id:str):
        """Replaces the element ID (Step/Transition) with the RecipeElementID"""
        self.id = id

    def addCond(self, cond:str):
        """Adds a condition to the transition"""
        self.cond = cond

    def getType(self) -> str | None:
        """Returns the type of the element"""
        return self.etype
    
    def setType(self, etype:str):
        """Sets the type of the element"""
        self.etype = etype


class Bml:
    def __init__(self, reqs:list[Requirement] = [], params:list[Parameter] = [], elems:list[Element] = []):
        self.reqs = reqs # list of requirements of the b2mml file
        self.params = params # list of parameters of the b2mml file
        self.elems = elems # list of elements of the b2mml file

    def __str__(self):
        descr = "Requirements:\n"

        for req in self.reqs:
            descr += f"{str(req)}\n"

        descr += "\nParameters:\n"

        for param in self.params:
            descr += f"{str(param)}\n"

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
                elif gchild.tag == f"{NAMESPACE}Transition":
                    transElem = bml.getElement(gchild.findtext(f"{NAMESPACE}ID"))
                    
                    # add condition
                    transElem.addCond(gchild.findtext(f"{NAMESPACE}Condition"))

### start main

# parse b2mml file
tree = parse(TESTXML)
root = tree.getroot()

# create bml object
bml = Bml()

# iterate over b2mml elements
for child in root:
    if child.tag == f"{NAMESPACE}MasterRecipe":
        # parse MasterRecipe
        parseMasterRecipe(node=child)

print(bml)
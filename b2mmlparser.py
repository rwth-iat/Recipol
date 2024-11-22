### imports
from defusedxml.ElementTree import parse

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

class Bml:
    def __init__(self, reqs:list[Requirement] = [], params:list[Parameter] = []):
        self.reqs = reqs # list of requirements of the b2mml file
        self.params = params # list of parameters of the b2mml file

    def __str__(self):
        descr = "Requirements:\n"

        for req in self.reqs:
            descr += f"{str(req)}\n"

        descr += "\nParameters:\n"

        for param in self.params:
            descr += f"{str(param)}\n"

        return descr

    def addRequirement(self, req:Requirement):
        """Adds a requirement to the bml instance."""
        
        self.reqs.append(req)

    def addParameter(self, param:Parameter):
        """Adds a parameter to the bml instance."""

        self.params.append(param)

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
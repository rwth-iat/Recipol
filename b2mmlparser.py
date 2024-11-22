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

class Bml:
    def __init__(self, reqs:list[Requirement] = []):
        self.reqs = reqs # list of requirements of the b2mml file

    def __str__(self):
        descr = "Requirements:\n"
        for req in self.reqs:
            descr += str(req)

        return descr

    def addRequirement(self, req:Requirement):
        """Adds a requirement to the b2mml file."""
        
        self.reqs.append(req)

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
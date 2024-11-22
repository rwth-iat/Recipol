### imports
from defusedxml.ElementTree import parse

### static variables
TESTXML = r"Artefakte\2024-11-03_MasterRecipeHC.xml"

### classes
class Requirement:
    def __init__(self, id:str = "", const:str = ""):
        self.id = id # unique identifier of the requirement
        self.const = const # constraint of the requirement

    def nameRequirement(self, id):
        if self.id != "":
            print("Cannot change id of existing requirement.")
        else:
            self.id = id

    def addConstraint(self, const):
        if self.const != "":
            print("Cannot overwrite existing constraint of requirement.")
        else:
            self.const = const

### start main
tree = parse(TESTXML)
root = tree.getroot()
# for child in root:
#     print(child.tag, child.attrib)
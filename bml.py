### imports
from defusedxml.ElementTree import parse

### static variables
TESTXML = r"Artefakte\2024-11-03_MasterRecipeHC.xml"

### start main
tree = parse(TESTXML)
root = tree.getroot()
# for child in root:
#     print(child.tag, child.attrib)
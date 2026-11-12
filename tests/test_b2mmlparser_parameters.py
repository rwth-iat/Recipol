"""RecipeElement parameters that the Formula does not declare.

BatchML lets a RecipeElement carry its parameters itself; the Formula need not
list them. The parser then creates the parameter from the RecipeElement's own
Value element instead of failing.
"""
from src.backend import b2mmlparser

NS = "http://www.mesa.org/xml/B2MML"

RECIPE = f"""<?xml version="1.0" encoding="utf-8"?>
<b2mml:BatchInformation xmlns:b2mml="{NS}">
  <b2mml:ListHeader><b2mml:ID>Header</b2mml:ID></b2mml:ListHeader>
  <b2mml:MasterRecipe>
    <b2mml:ID>MasterRecipe_Undeclared</b2mml:ID>
    <b2mml:ProcedureLogic>
      <b2mml:Link><b2mml:ID>L1</b2mml:ID>
        <b2mml:FromID><b2mml:FromIDValue>S1</b2mml:FromIDValue><b2mml:FromType>Step</b2mml:FromType></b2mml:FromID>
        <b2mml:ToID><b2mml:ToIDValue>T1</b2mml:ToIDValue><b2mml:ToType>Transition</b2mml:ToType></b2mml:ToID>
        <b2mml:LinkType>ControlLink</b2mml:LinkType></b2mml:Link>
      <b2mml:Link><b2mml:ID>L2</b2mml:ID>
        <b2mml:FromID><b2mml:FromIDValue>T1</b2mml:FromIDValue><b2mml:FromType>Transition</b2mml:FromType></b2mml:FromID>
        <b2mml:ToID><b2mml:ToIDValue>S2</b2mml:ToIDValue><b2mml:ToType>Step</b2mml:ToType></b2mml:ToID>
        <b2mml:LinkType>ControlLink</b2mml:LinkType></b2mml:Link>
      <b2mml:Link><b2mml:ID>L3</b2mml:ID>
        <b2mml:FromID><b2mml:FromIDValue>S2</b2mml:FromIDValue><b2mml:FromType>Step</b2mml:FromType></b2mml:FromID>
        <b2mml:ToID><b2mml:ToIDValue>T2</b2mml:ToIDValue><b2mml:ToType>Transition</b2mml:ToType></b2mml:ToID>
        <b2mml:LinkType>ControlLink</b2mml:LinkType></b2mml:Link>
      <b2mml:Link><b2mml:ID>L4</b2mml:ID>
        <b2mml:FromID><b2mml:FromIDValue>T2</b2mml:FromIDValue><b2mml:FromType>Transition</b2mml:FromType></b2mml:FromID>
        <b2mml:ToID><b2mml:ToIDValue>S3</b2mml:ToIDValue><b2mml:ToType>Step</b2mml:ToType></b2mml:ToID>
        <b2mml:LinkType>ControlLink</b2mml:LinkType></b2mml:Link>
      <b2mml:Step><b2mml:ID>S1</b2mml:ID><b2mml:RecipeElementID>Init</b2mml:RecipeElementID></b2mml:Step>
      <b2mml:Step><b2mml:ID>S2</b2mml:ID><b2mml:RecipeElementID>stir</b2mml:RecipeElementID></b2mml:Step>
      <b2mml:Step><b2mml:ID>S3</b2mml:ID><b2mml:RecipeElementID>End</b2mml:RecipeElementID></b2mml:Step>
      <b2mml:Transition><b2mml:ID>T1</b2mml:ID><b2mml:Condition>True</b2mml:Condition></b2mml:Transition>
      <b2mml:Transition><b2mml:ID>T2</b2mml:ID><b2mml:Condition>True</b2mml:Condition></b2mml:Transition>
    </b2mml:ProcedureLogic>
    <b2mml:RecipeElement><b2mml:ID>Init</b2mml:ID><b2mml:RecipeElementType>Begin</b2mml:RecipeElementType></b2mml:RecipeElement>
    <b2mml:RecipeElement><b2mml:ID>stir</b2mml:ID><b2mml:RecipeElementType>Operation</b2mml:RecipeElementType>
      <b2mml:Parameter><b2mml:ID>duration</b2mml:ID>
        <b2mml:Value><b2mml:ValueString>15</b2mml:ValueString><b2mml:DataType>duration</b2mml:DataType>
          <b2mml:UnitOfMeasure>second</b2mml:UnitOfMeasure></b2mml:Value></b2mml:Parameter>
    </b2mml:RecipeElement>
    <b2mml:RecipeElement><b2mml:ID>End</b2mml:ID><b2mml:RecipeElementType>End</b2mml:RecipeElementType></b2mml:RecipeElement>
  </b2mml:MasterRecipe>
</b2mml:BatchInformation>
"""


def _flat(elements):
    for element in elements:
        if isinstance(element, list):
            yield from _flat(element)
        else:
            yield element


def test_a_parameter_missing_from_the_formula_is_read_from_the_recipe_element(tmp_path):
    path = tmp_path / "undeclared.xml"
    path.write_text(RECIPE, encoding="utf-8")

    steps = [e for e in _flat(b2mmlparser.main(input_file=str(path))) if e.etype == "Step" and e.params]
    assert len(steps) == 1
    parameter = steps[0].params[0]
    assert (parameter.id, parameter.value, parameter.dtype, parameter.unit) == ("duration", "15", "duration", "second")

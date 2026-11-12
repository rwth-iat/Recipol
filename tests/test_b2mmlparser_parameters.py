"""Resolve central and local scalar parameter assignments without ambiguity."""

from copy import deepcopy
from pathlib import Path
from unittest.mock import Mock
from xml.etree import ElementTree as ET

import pytest

from src.backend import b2mmlparser, control


NS = "http://www.mesa.org/xml/B2MML"
Q = f"{{{NS}}}"


def _child(parent, tag, text=None):
    element = ET.SubElement(parent, Q + tag)
    element.text = text
    return element


def _parameter(value="15", *, pid="duration", dtype="integer", unit="second",
               interpretation="Constant"):
    parameter = ET.Element(Q + "Parameter")
    _child(parameter, "ID", pid)
    _child(parameter, "ParameterType", "ProcessParameter")
    if value is not None:
        assignment = _child(parameter, "Value")
        for field, text in (("ValueString", value), ("DataInterpretation", interpretation),
                            ("DataType", dtype), ("UnitOfMeasure", unit)):
            _child(assignment, field, text)
    return parameter


def _recipe(*, formula=None, first=(), second=()):
    """A schema-valid linear recipe with two independently parameterized steps."""
    root = ET.Element(Q + "BatchInformation")
    master = _child(root, "MasterRecipe")
    _child(master, "ID", "MasterRecipe_Parameters")
    if formula is not None:
        _child(master, "Formula").extend(deepcopy(formula))
    logic = _child(master, "ProcedureLogic")
    links = [("S1", "T1"), ("T1", "S2"), ("S2", "T2"),
             ("T2", "S3"), ("S3", "T3"), ("T3", "S4")]
    for index, (source, target) in enumerate(links, 1):
        link = _child(logic, "Link")
        _child(link, "ID", f"L{index}")
        for prefix, ref in (("From", source), ("To", target)):
            endpoint = _child(link, prefix + "ID")
            _child(endpoint, prefix + "IDValue", ref)
            _child(endpoint, prefix + "Type", "Step" if ref.startswith("S") else "Transition")
            _child(endpoint, "IDScope", "Internal")
        _child(link, "LinkType", "ControlLink")
        _child(link, "Depiction", "None")
    for index, ref in enumerate(("Init", "mixA", "mixB", "End"), 1):
        step = _child(logic, "Step")
        _child(step, "ID", f"S{index}")
        _child(step, "RecipeElementID", ref)
        _child(step, "RecipeElementVersion", "1.0")
    for index in range(1, 4):
        transition = _child(logic, "Transition")
        _child(transition, "ID", f"T{index}")
        _child(transition, "Condition", "True")
    for ref, kind, parameters in (("Init", "Begin", ()), ("mixA", "Operation", first),
                                  ("mixB", "Operation", second), ("End", "End", ())):
        element = _child(master, "RecipeElement")
        _child(element, "ID", ref)
        _child(element, "RecipeElementType", kind)
        element.extend(deepcopy(parameters))
    return root


def _write_recipe(tmp_path, root):
    path = tmp_path / "parameters.xml"
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    return path


def _flat(elements):
    for element in elements:
        if isinstance(element, list):
            yield from _flat(element)
        else:
            yield element


def _parse(tmp_path, root):
    path = _write_recipe(tmp_path, root)
    return {
        element.id: element
        for element in _flat(b2mmlparser.main(input_file=str(path)))
        if element.etype == "Step"
    }


@pytest.mark.parametrize("mode", ["central", "local", "both", "central-placeholder"])
def test_parameter_assignments_are_resolved_from_either_source(tmp_path, mode):
    formula = (None if mode == "local" else
               [_parameter(None) if mode == "central-placeholder" else _parameter()])
    local = _parameter(None) if mode == "central" else _parameter()
    steps = _parse(tmp_path, _recipe(formula=formula, first=[local]))
    parameter = steps["mixA"].params[0]
    assert (parameter.id, parameter.value, parameter.dtype, parameter.unit) == (
        "duration", "15", "integer", "second"
    )


@pytest.mark.parametrize("field, replacement", [
    ("ValueString", "30"), ("DataType", "decimal"),
    ("UnitOfMeasure", "minute"), ("DataInterpretation", "Reference"),
])
def test_conflicts_identify_both_sources_and_the_step(tmp_path, field, replacement):
    local = _parameter()
    local.find(f"{Q}Value/{Q}{field}").text = replacement
    with pytest.raises(ValueError, match="conflicting parameter assignments") as raised:
        _parse(tmp_path, _recipe(formula=[_parameter()], first=[local]))
    for detail in ("MasterRecipe_Parameters", "mixA", "duration", field,
                   "Formula=", "RecipeElement=", replacement):
        assert detail in str(raised.value)


def test_central_and_local_parameters_can_be_mixed_in_one_step(tmp_path):
    steps = _parse(tmp_path, _recipe(
        formula=[_parameter()],
        first=[_parameter(None), _parameter("500", pid="speed", unit="rpm")],
    ))
    assert [(p.id, p.value, p.unit) for p in steps["mixA"].params] == [
        ("duration", "15", "second"), ("speed", "500", "rpm")
    ]


def test_same_local_id_in_different_steps_keeps_independent_values(tmp_path):
    steps = _parse(tmp_path, _recipe(
        first=[_parameter()], second=[_parameter("30", unit="minute")],
    ))
    first, second = steps["mixA"].params[0], steps["mixB"].params[0]
    assert (first.value, first.unit) == ("15", "second")
    assert (second.value, second.unit) == ("30", "minute")
    assert first is not second


def test_central_assignment_can_be_used_by_multiple_steps(tmp_path):
    steps = _parse(tmp_path, _recipe(
        formula=[_parameter()], first=[_parameter(None)], second=[_parameter(None)],
    ))
    assert [steps[name].params[0].value for name in ("mixA", "mixB")] == ["15", "15"]


@pytest.mark.parametrize("formula", [None, [_parameter(None)]])
def test_a_reference_without_assignment_is_rejected(tmp_path, formula):
    with pytest.raises(ValueError, match="no Value assignment in Formula or RecipeElement"):
        _parse(tmp_path, _recipe(formula=formula, first=[_parameter(None)]))


def test_another_step_cannot_supply_an_unassigned_local_parameter(tmp_path):
    with pytest.raises(ValueError, match="RecipeElement 'mixB'.*no Value assignment"):
        _parse(tmp_path, _recipe(first=[_parameter()], second=[_parameter(None)]))


@pytest.mark.parametrize("field", ["ValueString", "DataType", "UnitOfMeasure", "DataInterpretation"])
@pytest.mark.parametrize("source", ["Formula", "RecipeElement"])
def test_partial_assignments_are_rejected_in_both_sources(tmp_path, field, source):
    parameter = _parameter()
    value = parameter.find(Q + "Value")
    value.remove(value.find(Q + field))
    root = (_recipe(formula=[parameter], first=[_parameter(None)]) if source == "Formula"
            else _recipe(first=[parameter]))
    with pytest.raises(ValueError, match=f"exactly one {field}"):
        _parse(tmp_path, root)


def test_empty_unit_is_allowed_for_dimensionless_parameters(tmp_path):
    steps = _parse(tmp_path, _recipe(formula=[_parameter(unit="")], first=[_parameter(unit="")]))
    assert steps["mixA"].params[0].unit == ""


@pytest.mark.parametrize("field", ["ValueString", "DataType", "DataInterpretation"])
def test_empty_assignment_fields_are_rejected(tmp_path, field):
    parameter = _parameter()
    parameter.find(f"{Q}Value/{Q}{field}").text = ""
    with pytest.raises(ValueError, match=f"{field} must not be empty"):
        _parse(tmp_path, _recipe(first=[parameter]))


@pytest.mark.parametrize("tag", ["Value", "ValueString"])
def test_multiple_values_are_rejected_instead_of_silently_discarded(tmp_path, tag):
    parameter = _parameter()
    parent = parameter if tag == "Value" else parameter.find(Q + "Value")
    parent.append(deepcopy(parent.find(Q + tag)))
    with pytest.raises(ValueError, match=f"exactly one {tag}"):
        _parse(tmp_path, _recipe(first=[parameter]))


@pytest.mark.parametrize("source", ["Formula", "RecipeElement"])
def test_duplicate_parameter_ids_within_a_source_are_rejected(tmp_path, source):
    parameters = [_parameter(), _parameter("30")]
    root = (_recipe(formula=parameters, first=[_parameter(None)]) if source == "Formula"
            else _recipe(first=parameters))
    with pytest.raises(ValueError, match=f"duplicate parameter ID in {source}"):
        _parse(tmp_path, root)


@pytest.mark.parametrize("pid", [None, "", "   "])
@pytest.mark.parametrize("source", ["Formula", "RecipeElement"])
def test_missing_or_empty_parameter_ids_are_rejected(tmp_path, pid, source):
    parameter = _parameter(pid=pid)
    if pid is None:
        parameter.remove(parameter.find(Q + "ID"))
    root = _recipe(formula=[parameter]) if source == "Formula" else _recipe(first=[parameter])
    with pytest.raises(ValueError, match="parameter ID is missing or empty"):
        _parse(tmp_path, root)


def test_comparison_is_strict_and_does_not_guess_numeric_equivalence(tmp_path):
    with pytest.raises(ValueError, match="conflicting parameter assignments"):
        _parse(tmp_path, _recipe(formula=[_parameter()], first=[_parameter("015")]))


def test_formula_assignments_do_not_leak_between_master_recipes():
    bml = b2mmlparser.Bml()
    for recipe_id, element_id, formula in (
        ("RecipeA", "ElementA", [_parameter()]), ("RecipeB", "ElementB", None),
    ):
        master = ET.Element(Q + "MasterRecipe")
        _child(master, "ID", recipe_id)
        if formula is not None:
            _child(master, "Formula").extend(formula)
        element = _child(master, "RecipeElement")
        _child(element, "ID", element_id)
        _child(element, "RecipeElementType", "Operation")
        element.append(_parameter(None))
        bml.addElement(b2mmlparser.Element("Step", element_id))
        if recipe_id == "RecipeB":
            with pytest.raises(ValueError, match="RecipeB.*no Value assignment"):
                b2mmlparser.parseMasterRecipe(bml, master)
        else:
            b2mmlparser.parseMasterRecipe(bml, master)


def test_conflicts_abort_before_recipe_execution(tmp_path, monkeypatch):
    path = _write_recipe(tmp_path, _recipe(formula=[_parameter()], first=[_parameter("30")]))
    execute = Mock()
    monkeypatch.setattr(control.mtp, "getMtps", lambda **kwargs: [])
    monkeypatch.setattr(control, "main", execute)
    with pytest.raises(ValueError, match="conflicting parameter assignments"):
        control.run_from_files(recipe_files=[str(path)])
    execute.assert_not_called()


@pytest.mark.parametrize("mode", ["local", "both"])
def test_real_recipe_maps_the_same_mtp_values_with_local_assignments(tmp_path, mode):
    artifacts = Path(__file__).resolve().parents[1] / "artifacts"
    original = artifacts / "2026-04-26_BatchML_MasterRecipe1_mit_HC20StirrDur.xml"
    mtp_files = [
        artifacts / "2025-11-18-HC10_MTP_V3.0.0.aml",
        artifacts / "2025-11-10-HC20_MTP_V1.0.0.aml",
    ]
    root = ET.parse(original).getroot()
    master = root.find(Q + "MasterRecipe")
    formula = master.find(Q + "Formula")
    definitions = {p.findtext(Q + "ID"): p for p in formula.findall(Q + "Parameter")}
    for parameter in master.findall(f"{Q}RecipeElement/{Q}Parameter"):
        definition = definitions[parameter.findtext(Q + "ID")]
        parameter.append(deepcopy(definition.find(Q + "Value")))
    if mode == "local":
        master.remove(formula)
    changed = _write_recipe(tmp_path, root)

    def mapped_values(path):
        procedure, _ = control.build_execution_procedure(
            recipe_files=[path], mtp_files=mtp_files,
        )
        return [
            (step["bml"].id, [(parameter.id, value) for parameter, value in step["params"]])
            for step in procedure if isinstance(step, dict) and step["params"]
        ]

    expected = mapped_values(original)
    assert sum(len(parameters) for _, parameters in expected) == 6
    assert mapped_values(changed) == expected


@pytest.mark.parametrize("mode", ["central", "local", "both"])
def test_assignment_examples_validate_against_the_real_xsd(mode):
    etree = pytest.importorskip("lxml.etree")
    root = _recipe(
        formula=[_parameter()] if mode != "local" else None,
        first=[_parameter(None) if mode == "central" else _parameter()],
    )
    schema_path = Path(__file__).resolve().parents[1] / "artifacts/schemas/AllSchemas.xsd"
    schema = etree.XMLSchema(etree.parse(str(schema_path)))
    schema.assertValid(etree.fromstring(ET.tostring(root)))

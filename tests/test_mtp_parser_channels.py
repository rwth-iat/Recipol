from pathlib import Path
from xml.etree.ElementTree import fromstring

from src.backend.mtp_models import Instance
from src.backend.mtp_parser import (
    NAMESPACE,
    _resolve_param_interfaces,
    getMtps,
)


def test_instance_models_text_and_access_without_breaking_existing_fields():
    instance = Instance("value", "value-id")

    assert instance.paramElem["Text"] == {
        "Type": "STRING",
        "ID": None,
        "Default": None,
        "Access": None,
    }
    assert instance.paramElem["V"] == {
        "Type": "REAL",
        "ID": None,
        "Default": None,
        "Access": None,
    }
    assert all("Access" in descriptor for descriptor in instance.paramElem.values())


def test_channel_resolution_reads_identifier_and_access_with_default_fallbacks():
    root = fromstring(
        """
        <Root xmlns="http://www.dke.de/CAEX">
          <InternalElement ID="instance" Name="SyntheticStringView">
            <Attribute Name="Text"><Value>text-interface</Value></Attribute>
            <Attribute Name="VOut"><DefaultValue>vout-interface</DefaultValue></Attribute>
            <Attribute Name="V"><Value>missing-interface</Value></Attribute>
          </InternalElement>
          <ExternalInterface ID="text-interface">
            <Attribute Name="Identifier"><Value>Module.Result.Text</Value></Attribute>
            <Attribute Name="Access"><DefaultValue>1</DefaultValue></Attribute>
          </ExternalInterface>
          <ExternalInterface ID="vout-interface">
            <Attribute Name="Identifier"><DefaultValue>Module.Parameter.VOut</DefaultValue></Attribute>
            <Attribute Name="Access"><Value>3</Value></Attribute>
          </ExternalInterface>
        </Root>
        """
    )
    instance_node = root.find(f"{NAMESPACE}InternalElement")
    interfaces = {
        node.get("ID"): node
        for node in root.findall(f"{NAMESPACE}ExternalInterface")
    }
    instance = Instance("SyntheticStringView", "instance")

    _resolve_param_interfaces(instance_node, instance, interfaces)

    assert instance.paramElem["Text"]["ID"] == "Module.Result.Text"
    assert instance.paramElem["Text"]["Access"] == 1
    assert instance.paramElem["VOut"]["ID"] == "Module.Parameter.VOut"
    assert instance.paramElem["VOut"]["Access"] == 3
    assert instance.paramElem["V"]["ID"] is None
    assert instance.paramElem["V"]["Access"] is None


def test_hc10_string_process_value_and_access_are_available_to_procedures():
    artifact = (
        Path(__file__).resolve().parents[1]
        / "artifacts"
        / "2025-11-18-HC10_MTP_V3.0.0.aml"
    )

    mtp = getMtps([artifact])[0]
    base_value = mtp.getInstanceByName("ProcVal_StartingTime_Heater")
    procedure_values = [
        parameter
        for procedure in mtp.procs
        for parameter in procedure.params
        if parameter.name == "ProcVal_StartingTime_Heater"
    ]

    expected = {
        "Type": "STRING",
        "ID": "GVL_MTP.ProcVal_StartingTime_Heater.Text",
        "Default": None,
        "Access": 1,
    }
    assert base_value.paramElem["Text"] == expected
    assert procedure_values
    assert all(value.parameter_type == "ProcessValueOut" for value in procedure_values)
    assert all(value.paramElem["Text"] == expected for value in procedure_values)


def test_hc10_vout_identifier_preserves_read_access():
    artifact = (
        Path(__file__).resolve().parents[1]
        / "artifacts"
        / "2025-11-18-HC10_MTP_V3.0.0.aml"
    )

    mtp = getMtps([artifact])[0]
    parameter = mtp.getInstanceByName("HC10_Duration_Dosing")

    assert parameter.paramElem["VOut"]["ID"] == (
        "GVL_MTP.HC10_Dosing.HC10_Duration_Dosing.VOut"
    )
    assert parameter.paramElem["VOut"]["Access"] == 1

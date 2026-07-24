from pathlib import Path

from src.backend.control import build_execution_procedure
from src.backend.opcua_recording import (
    OpcUaRecordingManager,
    _recipe_metadata,
)


ARTIFACTS = Path(__file__).resolve().parents[1] / "artifacts"
MTP_FILES = [
    ARTIFACTS / "2025-11-18-HC10_MTP_V3.0.0.aml",
    ARTIFACTS / "2025-11-10-HC20_MTP_V1.0.0.aml",
    ARTIFACTS / "2026-06-12_HC30_Conveying_V3.aml",
]
RECIPE_FILES = [
    ARTIFACTS
    / "2026-06-12_BatchML_MasterRecipe1_Extended_HC30_mit_HC20StirrDur.xml"
]
COMPACT_RECIPE_FILES = [
    ARTIFACTS / "2026-04-26_BatchML_MasterRecipe1_mit_HC20StirrDur.xml"
]
COMPACT_MTP_FILES = MTP_FILES[:2]


def test_real_recipe_selects_only_its_executable_procedure_signals(tmp_path):
    procedure, mtps = build_execution_procedure(
        recipe_files=RECIPE_FILES,
        mtp_files=MTP_FILES,
    )
    executable_steps = [
        step
        for step in procedure
        if isinstance(step, dict)
        and step.get("mtp") is not None
        and step.get("inst") is not None
    ]

    assert len(mtps) == 3
    assert len(executable_steps) == 6
    assert len({id(step["mtp"]) for step in executable_steps}) == 3
    assert {step["mtp"].name for step in executable_steps} == {
        "2025-11-10-HC20-MTP",
        "2025-11-18-HC10_MTP",
        "2026-06-12-HC30-MTP",
    }
    assert sum(len(step["inst"].params) for step in executable_steps) == 34

    manager = OpcUaRecordingManager(
        procedure=procedure,
        recipe_files=RECIPE_FILES,
        logger=lambda _message: None,
        output_path=tmp_path / "lastRecord.csv",
    )

    signals, executable_step_count = manager._build_signal_catalog()

    assert executable_step_count == 6
    assert len(signals) == 30
    assert len(signals) + 2 == 32
    assert len({signal.key for signal in signals}) == 30
    assert [signal.signal_id for signal in signals] == [
        f"S{index:03d}" for index in range(1, 31)
    ]
    assert len({signal.column_name for signal in signals}) == 30
    assert {signal.module_name for signal in signals} == {
        "2025-11-10-HC20-MTP",
        "2025-11-18-HC10_MTP",
        "2026-06-12-HC30-MTP",
    }
    assert {(signal.signal_type, signal.channel) for signal in signals} == {
        ("ProcessValueOut", "V"),
        ("ProcessValueOut", "Text"),
        ("ProcedureParameter", "VOut"),
        ("ProcessValueIn", "V"),
    }
    assert all(signal.access in {"1", "3"} for signal in signals)

    allowed_nodes = set()
    for step in executable_steps:
        mtp = step["mtp"]
        for parameter in step["inst"].params:
            parameter_type = parameter.parameter_type
            if parameter_type == "ProcessValueOut":
                text = parameter.paramElem["Text"]
                channel = "Text" if text["ID"] else "V"
            elif parameter_type == "ProcedureParameter":
                channel = "VOut"
            elif parameter_type == "ProcessValueIn":
                channel = "V"
            else:
                continue

            descriptor = parameter.paramElem[channel]
            if descriptor["ID"] and str(descriptor["Access"]) in {"1", "3"}:
                allowed_nodes.add((mtp.url, mtp.ns, descriptor["ID"]))

    assert {signal.key for signal in signals} == allowed_nodes

    assert _recipe_metadata(RECIPE_FILES) == {
        "recipe_id": "MasterRecipe_1",
        "recipe_version": "1.0.0",
        "product_id": "StirredHeatedWater",
    }


def test_compact_recipe_catalog_contains_runtime_signals_and_recipe_parameters(
    tmp_path,
):
    procedure, mtps = build_execution_procedure(
        recipe_files=COMPACT_RECIPE_FILES,
        mtp_files=COMPACT_MTP_FILES,
    )
    manager = OpcUaRecordingManager(
        procedure=procedure,
        recipe_files=COMPACT_RECIPE_FILES,
        logger=lambda _message: None,
        output_path=tmp_path / "lastRecord.csv",
    )

    signals, executable_step_count = manager._build_signal_catalog()
    manager.signals = signals
    parameters = manager._build_procedure_parameters()

    assert len(mtps) == 2
    assert executable_step_count == 3
    assert len(signals) == 26
    assert len(manager._history_header()) == 28
    assert [signal.signal_id for signal in signals] == [
        f"S{index:03d}" for index in range(1, 27)
    ]
    assert len(parameters) == 6
    assert {parameter.step_id for parameter in parameters} == {"001", "002", "003"}
    assert all(parameter.procedure_id for parameter in parameters)
    assert all(parameter.procedure_number for parameter in parameters)

    set_temperature = next(
        parameter
        for parameter in parameters
        if parameter.parameter_name == "HC10_Set_Temp_Heating"
    )
    assert set_temperature.step_id == "003"
    assert set_temperature.module_name == "2025-11-18-HC10_MTP"
    assert set_temperature.configured_value == "21"
    assert set_temperature.unit == "Grad Celsius"
    assert all(
        parameter.parameter_name != "HC10_Duration_Heating"
        for parameter in parameters
    )

    temperature_signal = next(
        signal for signal in signals if signal.signal_name == "HC10_TempView_T10"
    )
    assert temperature_signal.step_ids == {"003"}
    assert temperature_signal.procedure_ids == {
        "888136a9-c795-41c2-970c-169fa9852d22"
    }

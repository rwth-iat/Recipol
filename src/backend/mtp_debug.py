"""Debug output helpers for parsed MTP files."""

from .mtp_models import Instance, Pea, Procedure
from .mtp_parser import TESTMTPS, getMtps

DEBUG_SENSOR_KEYS = ("V", "VOut", "Pos", "Ctrl")


def _first_sensor_debug_id(instance: Instance) -> tuple[str | None, str | None]:
    for key in DEBUG_SENSOR_KEYS:
        param = instance.paramElem.get(key, {})
        signal_id = param.get("ID")
        if signal_id is not None:
            return key, signal_id

    return None, None


def _print_procedure_debug(procedure: Procedure, indent: str, include_params: bool) -> None:
    print(f"{indent}Procedure: {procedure.name} ({procedure.id})")
    if not include_params:
        return

    if not procedure.params:
        print(f"{indent}  Parameters: <none>")
        return

    print(f"{indent}  Parameters:")
    for param in procedure.params:
        print(f"{indent}    {param.name} ({param.id}), default={param.default}, unit={param.unit}")


def print_mtp_debug(mtp: Pea, include_params: bool = True) -> None:
    """Print parser details for one parsed MTP."""
    print(f"\nMTP: {mtp.name}")
    if mtp.source_file:
        print(f"Source: {mtp.source_file}")

    print("\nServices:")
    printed_procedure_ids = set()
    if mtp.servs:
        for service in mtp.servs:
            print(f"  Service: {service.name} ({service.id})")
            if service.procs:
                for procedure in service.procs:
                    printed_procedure_ids.add(procedure.id)
                    _print_procedure_debug(procedure, "    ", include_params)
            else:
                print("    Procedures: <none>")
    else:
        print("  <none>")

    unassigned_procedures = [
        procedure for procedure in mtp.procs if procedure.id not in printed_procedure_ids
    ]
    if unassigned_procedures:
        print("\nProcedures without Service:")
        for procedure in unassigned_procedures:
            _print_procedure_debug(procedure, "  ", include_params)

    print("\nSensors and Actuators:")
    found_sensor = False
    for instance in mtp.sensacts:
        key, signal_id = _first_sensor_debug_id(instance)
        if signal_id is not None:
            found_sensor = True
            print(f"  {instance.name} [{key}] {signal_id}")

    if not found_sensor:
        print("  <none>")


def print_mtps_debug(mtps: list[Pea], include_params: bool = True) -> None:
    """Print parser details for all parsed MTPs."""
    print(f"Parsed {len(mtps)} MTP file(s)")
    for mtp in mtps:
        print_mtp_debug(mtp, include_params=include_params)


def main() -> None:
    mtps = getMtps(input_files=TESTMTPS)
    print_mtps_debug(mtps)


if __name__ == "__main__":
    main()

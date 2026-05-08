"""Orchestrate Recipe (B2MML) and MTP data for SFC visualization."""

from __future__ import annotations

from pathlib import Path

try:
    from . import b2mmlparser as bml
    from . import mtpparser as mtp
except ImportError:  # pragma: no cover - fallback when run as a script
    import b2mmlparser as bml
    import mtpparser as mtp


def _normalize_proc_id(element_id: str) -> str:
    """Convert recipe step IDs like '001:SomeProc' to 'SomeProc'."""
    if ":" in element_id:
        return element_id.rsplit(":", 1)[-1]
    return element_id


def _map_step_to_mtp(mtps, step_elem):
    proc_id = _normalize_proc_id(step_elem.getId())
    for module in mtps:
        proc = module.getProcedure(procId=proc_id)
        if proc is not None:
            return module, proc
    return None, None


def getProcedure(recipe_files=None, mtp_files=None, logger=None) -> list[dict]:
    """
    Build SFC view data from selected recipe XML files and MTP AML files.

    Returns a flat list of dictionaries that can be rendered directly in the UI.
    """
    results: list[dict] = []
    mtps = mtp.getMtps(input_files=mtp_files) if mtp_files else []

    if recipe_files is None:
        recipe_files = [None]  # use b2mmlparser defaults

    seq = 0
    for recipe_file in recipe_files:
        ordered = bml.main(input_file=recipe_file, validate_schema=False)
        recipe_name = Path(recipe_file).name if recipe_file else "Default Recipe"

        for item in ordered:
            elements = item if isinstance(item, list) else [item]
            is_parallel = isinstance(item, list) and len(item) > 1

            for elem in elements:
                seq += 1
                if elem.getType() == "Step":
                    mapped_mtp, mapped_proc = _map_step_to_mtp(mtps, elem)
                    row = {
                        "seq": seq,
                        "recipe": recipe_name,
                        "kind": "Step",
                        "name": elem.getName() or elem.getId(),
                        "recipe_element_type": elem.getRecipeElementType() or "",
                        "condition": "",
                        "mtp": mapped_mtp.name if mapped_mtp is not None else "",
                        "procedure": mapped_proc.name if mapped_proc is not None else "",
                        "parallel": is_parallel,
                    }
                else:
                    row = {
                        "seq": seq,
                        "recipe": recipe_name,
                        "kind": "Transition",
                        "name": elem.getName() or elem.getId(),
                        "recipe_element_type": elem.getRecipeElementType() or "",
                        "condition": elem.getCond() or "",
                        "mtp": "",
                        "procedure": "",
                        "parallel": is_parallel,
                    }

                results.append(row)

    if logger is not None:
        logger(f"SFC generated: {len(results)} element(s) from {len(recipe_files)} recipe file(s).")

    return results


if __name__ == "__main__":
    data = getProcedure()
    for row in data:
        print(
            f"{row['seq']:>3} | {row['recipe']} | {row['kind']:<10} | "
            f"{row['name']} | {row['condition']}"
        )

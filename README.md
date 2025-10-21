# Recipol

**Recipol** links ISA-88 master recipes expressed in **BatchML/B2MML** to **Module Type Package (MTP)** automation modules and executes the resulting procedure against **OPC UA** equipment. It parses recipe intent, maps steps to PEA services, and drives the plant while logging telemetry.

> In modular automation, **MTP** describes module services and HMI; a **Process Orchestration Layer (POL)** composes these services to run a recipe. Recipol focuses on the "recipe → procedure → OPC UA calls" part of this flow.

---

## Key capabilities
- **Recipe ingest** – Validates and parses BatchML/B2MML master recipes into a navigable graph of steps, transitions, resources, and parameters.
- **MTP interpretation** – Reads **AutomationML (.aml)** MTP manifests and extracts services, parameters, sensing/actuation interfaces, and OPC UA connectivity metadata.
- **Orchestration** – Aligns recipe steps with PEA procedures, enforces parameter bounds and units, and resolves required materials before execution.
- **OPC UA execution** – Issues state transitions and parameter updates to services through the `asyncua` client, with safety checks to recover from idle/completed/stopped/aborted states.
- **Status logging** – Records service states and sensor values in `DataHistory.csv`; renders ASCII sequence diagrams for operator awareness.

---

## Repository layout
```text
Artefakte/        # sample B2MML recipes and AML manifests (user-provided)
Schemas/          # B2MML/BatchML schema bundle (for validation)
DataHistory.csv   # rolling log (created/extended by control.py)
b2mmlparser.py    # BatchML/B2MML parsing & validation
mtpparser.py      # AML/MTP parsing; collects OPC UA endpoints & namespaces
orchestration.py  # maps recipe steps to MTP procedures & builds execution plan
control.py        # orchestrator: drives the recipe, logs data, enforces transitions
sequenz.py        # text-based depiction of the active sequence step
```

---

## Prerequisites
- **Python 3.10+** (3.10/3.11 tested).
- **Access** to the target **OPC UA** servers referenced by your MTP artefacts, or use the local dev server in the quick-start.
- **Python packages** (pinned):
  - `asyncua` (OPC UA async client)
  - `defusedxml` (safe XML parsing)
  - `xmlschema` (XSD validation for B2MML/BatchML)

Create a virtual environment and install:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -U pip
pip install -r requirements.txt
```

**requirements.txt**

```text
asyncua==1.1.8
defusedxml==0.7.1
xmlschema==4.2.0
```

> Tip: If your platform cannot fetch wheels for dependencies, install C build tools first (Linux: `build-essential`, Windows: Visual Studio Build Tools).

---

## Preparing artefacts

You can work **two ways**: (A) quick config-file path (recommended) or (B) the original "edit constants in code" path.

### A) Config-file path (recommended)

Create `configs/example.yaml`:

```yaml
b2mml_recipe: "Artefakte/Wabe102030_Grundrezept.xml"
mtp_modules:
  - "Artefakte/PEA_A.aml"
  - "Artefakte/PEA_B.aml"
schemas_root: "Schemas"  # points to AllSchemas.xsd etc.
opcua:
  # Optional global fallback only if MTP AML does not contain endpoint/namespace
  default_endpoint: "opc.tcp://127.0.0.1:4840"
  default_namespace_hint: 4
log_csv: "DataHistory.csv"
```

Then run:

```bash
python control.py --config configs/example.yaml
```

> If `control.py` does not yet accept `--config`, use path **B** below (edit constants). The config path is recommended for maintainability and can be implemented with minimal changes.

### B) Edit constants in code (legacy)

1. **Master recipe**: place your B2MML/BatchML XML (e.g., `Wabe102030_Grundrezept.xml`) under `Artefakte/` and update the `TESTXML*` constants in `b2mmlparser.py`.
2. **MTP manifests**: add `.aml` files under `Artefakte/` and edit `TESTMTPS` in `mtpparser.py` to list them in execution order.
3. **OPC UA connectivity**: ensure each AML contains a `CommunicationSet` with `Endpoint` and `Namespace`. The parser populates `Pea.url` and `Pea.ns`.

---

## Running the orchestrator

```bash
# Activate venv and install deps (once)
source .venv/bin/activate
pip install -r requirements.txt

# Option A (config file):
python control.py --config configs/example.yaml

# Option B (edited constants):
python control.py
```

What to expect:

- The console prints an ASCII flow of the recipe and pauses for operator confirmation (`y` to continue).
- Terminal output shows state transitions; `DataHistory.csv` captures timestamped states and sensor readings.

---

## Dev quick-start (local OPC UA test server)

To verify your environment without real plant connectivity, run a minimal OPC UA server and point Recipol to it:

```bash
python - <<'PY'
import asyncio
from asyncua import ua, Server

async def main():
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://127.0.0.1:4840/recipol/dev")
    idx = await server.register_namespace("urn:recipol:demo")
    obj = await server.nodes.objects.add_object(idx, "DemoPEA")
    var = await obj.add_variable(idx, "Setpoint", 25.0)
    await var.set_writable()
    print("Server running at opc.tcp://127.0.0.1:4840/recipol/dev (Ctrl+C to stop)")
    async with server:
        while True:
            await asyncio.sleep(1)

asyncio.run(main())
PY
```

Now adapt your config or constants to the endpoint shown above and run `control.py`.

---

## Interpreting outputs

- **`DataHistory.csv`**: one row per sample with timestamps, followed by `<PEA>_<Service>` and `<PEA>_<Sensor>` columns.
- **ASCII diagrams** from `sequenz.drawSequenceDiagram` show the current step (`||`) relative to overall flow.
- Parameter violations or missing mappings cause early runtime exceptions (before execution).

---

## Troubleshooting

- **Schema validation fails** → confirm `Schemas/AllSchemas.xsd` matches the B2MML version of your recipe (v7 is common).
- **OPC UA writes rejected** → verify the namespace index from the server (dynamic on many stacks). Adjust `Pea.ns` or resolve the proper index at runtime.
- **Missing parameter IDs** → ensure recipe parameter IDs align with MTP procedure parameter IDs; orchestration enforces unit/range checks.
- **Security policies** → if your server requires encrypted/sign connections, configure certificate trust and security mode in your client code (`asyncua` supports security modes and user auth).

---

## Safety & production notes

Recipol provides **direct OPC UA writes** for orchestration. In **production**, changes in the **Core Process Control (CPC)** domain should be issued via a **NOA Security Gateway** and **Verification-of-Request (VoR)** (NAMUR **NE 177/NE 178**) rather than ad-hoc client writes. Review site policies before enabling writes to live equipment.

---

## License

GPL-3.0 (see `LICENSE`).

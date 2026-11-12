# Recipol

Recipol is an open-source **Process Orchestration Layer (POL)** for modular process plants. It supports the execution of standardized and formalized **master recipes** in **BatchML/B2MML**, based on **ISA-88**, **Module Type Package (MTP)**, and the **Capability, Skill and Service (CSS)** model.

The software was developed at the Chair of Information and Automation Systems (IAT), RWTH Aachen University, in the context of research on modular automation, capability-based engineering, and recipe-based process orchestration.
> Winter, Michael; Eve, Alicia; Schmetz, Benedikt; Kleinert, Tobias: *A POL for Modular Plants using Capabilities in Master Recipes,* In: 1st IFAC Workshop on Engineering and Architectures of Automation Systems (EAAS 2025), 2025, Padova, Italy.

## Purpose

Recipol connects standardized recipe descriptions with modular plant resources. A master recipe defines the intended process sequence, while MTP files describe the available services, procedures, parameters, communication endpoints, and monitoring information of Process Equipment Assemblies (PEAs).

This POL enables:

* parsing ISA-88-oriented master recipes in BatchML/B2MML,
* parsing MTP files exported as AML,
* mapping of recipe steps to MTP procedures,
* parameterization and trigger of MTP services via OPC UA,
* monitoring service states and process-relevant signal values,
* visualization of the recipe sequence as a Sequential Function Chart (SFC),
* supporting inspection of MTP services, procedures, and parameters,
* providing a research prototype for capability-based orchestration in modular plants according to the CSS Model.

## Graphical User Interface

Recipol includes a desktop GUI based on PyQt6 and qfluentwidgets. The GUI provides several pages:

* **Home** – import, select, inspect, and manage recipe and MTP files,
* **MTP Viewer** – inspect parsed MTP services, procedures, parameters, limits, and units,
* **Recipe Monitor** – visualize recipe execution as a Sequential Function Chart,
* **Logs** – display parsing, orchestration, execution, and error messages.

## Functionalities
- **Recipe Interface**: The sequential process execution in the modular plant is described by a master recipe, provided in the form of a BatchML file. A corresponding interface is implemented in the POL to load and process these recipes.
- **MTP Interface**: The MTP files are imported as AML (Automation Markup Language) files, a neutral data format based on XML. The MTP interface translates this information into a data structure interpreted by the remaining POL software modules to extract services, procedures, parameters, sensing/actuation interfaces, and OPC UA connectivity metadata.
- **OPC UA Connectivity**: Communication between the POL and the PEAs (Process Equipment Assemblies) is realized via OPC UA. Each PEA hosts an OPC UA server on its respective PLC, which is accessed by the POL to enable process control. To facilitate this connectivity, an OPC UA client is implemented within the POL.
- **Process Monitoring**: The current states of the services and signal values of the PEAs, as defined in the MTP file, are queried and continuously monitored. Additionally, an interface is provided to allow external applications — such as graphical user interfaces - to retrieve these signals.
- **Monitoring of Process Sequence Execution**: The execution of the process sequence is visualized as a graphical representation, such as a sequence diagram, on the command line. 
- **HMI Integration**: The MTP files contain graphical information for the creation of an operator interface, typically in the form of a piping and instrumentation diagram (P&ID). An interface has been implemented to extract and preprocess this information for integration into an HMI.
- **Process Orchestration and Execution**: Process orchestration is achieved by verifying the alignment between the process steps defined in the recipe and the IDs specified in the MTP files. Once the sequence has been validated, execution is initiated via OPC UA, triggering the corresponding modules.

## Repository Layout
- `main.py` - Entry point for the PyQt6 desktop application
- `control.py` – Executes the provided recipe via OPC UA using MTP
- `orchestration.py` – Orchestrates process steps from a recipe with corresponding MTP procedures, building a linear/branched execution list
- `b2mmlparser.py` – Parses and verifies the recipes against the BatchML schema in `Schemas/AllSchemas.xsd`
- `mtpparser.py` – Parses MTP files for process orchestration
- `sequenz.py` – Displays the process sequence on the command line
- `artifacts/` – Folder for recipes and corresponding MTP files
- `schemas/` – Folder for B2MML/BatchML schema bundle required for recipe verification



```text
Recipol/
├── artifacts/
│   ├── schemas/
│   │   └── BatchML/B2MML schema files
│   ├── *.xml
│   │   └── example BatchML/B2MML recipe files
│   └── *.aml
│       └── example MTP files
│
├── src/
│   ├── main.py
│   │   └── PyQt6 application entry point
│   │
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── b2mmlparser.py
│   │   ├── control.py
│   │   ├── mtpparser.py
│   │   ├── mtp_parser.py
│   │   ├── mtp_models.py
│   │   ├── mtp_units.py
│   │   ├── orchestration.py
│   │   └── sequenz.py
│   │
│   └── frontend/
│       ├── Home.py
│       ├── Logs.py
│       ├── MTPViewer.py
│       ├── SFCMonitor.py
│       └── Workers.py
│
├── tests/
│   └── automated tests
│
├── README.md
└── LICENSE
```

## Prerequisites
- Python ≥  3.10
- Network access to OPC UA‑enabled PEAs referenced in MTP files
- Python packages: `PyQt6`, `PyQt6-Fluent-Widgets`, `asyncua`, `defusedxml`, `xmlschema`

```bash
pip install PyQt6 PyQt6-Fluent-Widgets asyncua defusedxml xmlschema
```


## Running the GUI
From the repository root, start Recipol with:
```bash
python src/main.py
```
##### 1. Import or Select Files

Use the **Home** page to import or select one or more files.

Typical combinations:

```text
one or more .aml files
one or more .xml files
one .xml recipe file together with matching .aml MTP files
```

##### 2. Inspect Files

Click **Inspect**.

Depending on the selected files, Recipol will:

* parse selected MTP files,
* parse selected recipe files,
* generate an SFC representation,
* map recipe steps to MTP procedures where possible,
* show results in the MTP Viewer or Recipe Monitor.

##### 3. Inspect MTPs

Open the **MTP Viewer** page to inspect parsed services, procedures, and parameters.

##### 4. Inspect the Recipe Sequence

Open the **Recipe Monitor** page to inspect the generated SFC.

##### 5. Execute a Recipe

If both recipe and MTP files are available and mapped, use **Execute Recipe** in the Recipe Monitor.

Execution requires network access to the OPC UA servers referenced in the selected MTP files.




## Recipe Parameter Assignments

A parameter used by a `RecipeElement` can receive its value centrally in the
`MasterRecipe/Formula` or locally in that `RecipeElement`. The complete parameter
ID, including any prefix, associates a local reference with its Formula entry.

| Formula assignment | Local assignment | Result |
| --- | --- | --- |
| Present | Absent | Use the Formula assignment. |
| Absent | Present | Use the local assignment for this RecipeElement only. |
| Present | Identical | Accept the matching assignments. |
| Present | Different | Reject the recipe with the recipe, element, parameter ID and conflicting fields. |
| Absent | Absent | Reject an unresolved parameter reference. |

Each assignment must contain one `Value` with one `ValueString`, `DataType`,
`UnitOfMeasure` and `DataInterpretation`. An empty unit is allowed for dimensionless
parameters; the other fields must not be empty. When both sources assign a value,
these four fields are compared as exact text: numeric spellings and different
units are not automatically converted. For example, `15` and `015` are treated as
different assignments. This check does not add expression evaluation or validate
values against the MTP data type or limits.

The same parameter ID may have different local values in different RecipeElements
when there is no central assignment. IDs must be unique within the Formula and
within each RecipeElement. Assignment errors are raised during parsing, before
recipe execution starts.

## Troubleshooting
- **Schema validation fails**: Confirm `Schemas/AllSchemas.xsd` matches the B2MML/BatchML version of the recipe to be executed. Update the schema bundle if needed.
- **OPC UA writes rejected**: Verify the namespace index retrieved by `getNamespaceId` matches the server configuration; adjust `Pea.ns` or hardcode `nsid` if your server uses a dynamic namespace order.
- **Missing parameter IDs**: Ensure the parameter IDs in your recipe align with those exposed by the MTP procedure. Values and units must be compatible with that procedure; the current execution path does not convert units or validate MTP limits.
## Current Status

Recipol is a research prototype. It demonstrates how standardized recipes according to ISA-88 can be interpreted and executed on modular plant using MTP and the CSS Model.
The implementation is still under development. Interfaces, data structures, and assumptions may change as the orchestration concept is extended.

## Known Limitations

* The current orchestration is primarily focused on structured sequential execution.
* Parallel and branched recipe structures are not covered yet.
* Identifier alignment between recipe steps and MTP procedures is currently central to the mapping.
* Complex transition logic may require additional implementation, e.g., using a `timer`.
* Execution requires reachable OPC UA servers and valid MTP communication metadata.
* The software is intended as a research prototype, not as a certified industrial control system.

## Possible Extensions

* improved support for parallel and branched recipe logic,
* richer transition-condition parsing, e.g., using a `timer`.
* stronger validation between recipe requirements and MTP procedures,
* improved error diagnostics for failed mappings,
* tighter integration with semantic capability descriptions,
* export of execution traces,
* integration with external HMIs or orchestration dashboards,
* extended support for additional MTP variants and vendor-specific exports.


## Citation
If you use this work, please cite:
```
@inproceedings{Winter2025Recipol,
	title = {A POL for Modular Plants using Capabilities in Master Recipes},
	author = {Winter, Michael and Eve, Alicia and Schmetz, Benedikt and Kleinert, Tobias},
	booktitle = {1st IFAC Workshop on Engineering and Architectures of Automation Systems (EAAS 2025)},
	address = {Padova, Italy},
	year = {2025}
}
```

## License
This project is licensed under the MIT License.  


## Contact & Acknowledgements

Maintainer: [Michael Winter](mailto:m.winter@iat.rwth‑aachen.de), [Yuanchen Zhao](mailto:y.zhao@iat.rwth‑aachen.de), [Benedikt Schmetz](mailto:b.schmetz@iat.rwth‑aachen.de)  
Developer: [Alicia Eve](mailto:alicia.eve@rwth-aachen.de)  
Institution: Chair of Information and Automation Systems (IAT), RWTH Aachen University  
Head of Chair: [Prof. Dr.-Ing. Tobias Kleinert](mailto:kleinert@iat.rwth-aachen.de)

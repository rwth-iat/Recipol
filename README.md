# Recipol

Recipol is an open-source Process Orchestration Layer (POL) enabling the execution of standardized and formalized process descriptions (master recipes in BatchML, an XML-Schema according to ISA-88 - Batch Control) in modular plants using the Capability–Skill–Service (CSS) model and Module Type Package (MTP). 
Recipol was developed at the Chair of Information and Automation Systems (IAT), RWTH Aachen University based on:
* _Winter, Michael; Eve, Alicia; Schmetz, Benedikt; Kleinert, Tobias (2025): A POL for Modular Plants using Capabilities in Master Recipes. In: 1st IFAC Workshop on Engineering and Architectures of Automation Systems (EAAS 2025), Padova, Italy._

## Functionalities
- **Recipe Interface**: The sequential process execution in the modular plant is described by a master recipe, provided in the form of a BatchML file. A corresponding interface is implemented in the POL to load and process these recipes.
- **MTP Interface**: The MTP files are imported as AML (Automation Markup Language) files, a neutral data format based on XML. The MTP interface translates this information into a data structure interpreted by the remaining POL software modules to extract services, procedures, parameters, sensing/actuation interfaces, and OPC UA connectivity metadata.
- **OPC UA Connectivity**: Communication between the POL and the PEAs (Process Equipment Assemblies) is realized via OPC UA. Each PEA hosts an OPC UA server on its respective PLC, which is accessed by the POL to enable process control. To facilitate this connectivity, an OPC UA client is implemented within the POL.
- **Process Monitoring**: The current states of the services and signal values of the PEAs, as defined in the MTP file, are queried and continuously monitored. Additionally, an interface is provided to allow external applications — such as graphical user interfaces (which are not part of the currently developed POL) — to retrieve these signals.
- **Monitoring of Process Sequence Execution**: The execution of the process sequence is visualized as a graphical representation, such as a sequence diagram, on the command line. 
- **HMI Integration**: The MTP files contain graphical information for the creation of an operator interface, typically in the form of a piping and instrumentation diagram (P&ID). An interface has been implemented to extract and preprocess this information for integration into an HMI.
- **Sequence Diagram**: Records MTP service states and sensor values in `DataHistory.csv` and prints ASCII sequence diagrams for the operator on the command line.
- **Process Orchestration and Execution**: Process orchestration is achieved by verifying the alignment between the process steps defined in the recipe and the IDs specified in the MTP files. Once the sequence has been validated, execution is initiated via OPC UA, triggering the corresponding modules.

## Repository Layout
- `control.py` – Executes the provided recipe via OPC UA using MTP
- `orchestration.py` – Orchestrates process steps from a recipe with corresponding MTP procedures, building a linear/branched execution list
- `b2mmlparser.py` – Parses and verifies the recipes against the BatchML schema in `Schemas/AllSchemas.xsd`
- `mtpparser.py` – Parses MTP files for process orchestration
- `sequenz.py` – Displays the process sequence on the command line
- `Artefakte/` – Folder for recipes and corresponding MTP files
- `Schemas/` – Folder for B2MML/BatchML schema bundle required for recipe verification
- `Datahistory/` – Folder for generated log files during execution

## Prerequisites
- Python ≥  3.10
- Network access to OPC UA‑enabled PEAs referenced in MTP files
- Python packages: `asyncua`, `defusedxml`, `xmlschema`

## Preparing Artefacts
1. **Master recipe**: Add recipe as BatchML-file (e.g., `Wabe102030_Grundrezept.xml`) under `Artefakte/` and update the `TESTXML*` constants in `b2mmlparser.py` to point to the desired file.
2. **MTP files**: Add MTP files for each PEA used in the Master Recipe under `Artefakte/` and edit `TESTMTPS` in `mtpparser.py` to list them.


## Running the Orchestrator
1. Ensure all dependencies are installed.
2. Populate a master recipe and the corresponding MTP files in `Artefakte/` for process execution.
3. Execute: `python control.py`
4. Recipol prints the process sequence on the command line and pauses for operator confirmation before execution.
5. Monitor terminal output for step transitions of the process sequence; review `DataHistory.csv` for time-stamped steps and sensor readings.


## Troubleshooting
- **Schema validation fails**: Confirm `Schemas/AllSchemas.xsd` matches the B2MML/BatchML version of the recipe to be executed. Update the schema bundle if needed.
- **OPC UA writes rejected**: Verify the namespace index retrieved by `getNamespaceId` matches the server configuration; adjust `Pea.ns` or hardcode `nsid` if your server uses a dynamic namespace order.
- **Missing parameter IDs**: Ensure the parameter IDs in your recipe align with those exposed by the MTP procedure; the orchestrator enforces unit and range checks before execution.

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

Copyright (c) 2025 Alicia Eve  
Includes dependencies under LGPL‑3.0 (e.g., opcua‑asyncio).  
Please refer to the `LICENSE` file for details on third‑party license terms.

## Contact & Acknowledgements

Maintainer: [Michael Winter](mailto:m.winter@iat.rwth‑aachen.de), [Benedikt Schmetz](mailto:b.schmetz@iat.rwth‑aachen.de)  
Developer: [Alicia Eve](mailto:alicia.eve@rwth-aachen.de)  
Institution: Chair of Information and Automation Systems (IAT) - RWTH Aachen University  
Head of Institution: [Prof. Dr.-Ing. Tobias Kleinert](mailto:kleinert@iat.rwth-aachen.de)

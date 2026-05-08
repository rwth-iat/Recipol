"""Main XML parsing workflow for MTP files."""

from copy import deepcopy  # clone base instances so procedure-specific metadata won't pollute global instance list
from defusedxml.ElementTree import parse
from pathlib import Path

from .mtp_models import (
    HMI,
    Instance,
    Junction,
    Line,
    Pea,
    Pipe,
    Port,
    Procedure,
    Service,
    Sink,
    Source,
    VisualObject,
)
from .mtp_units import getUnit

# Path
current_dir = Path(__file__).resolve().parent

### static variables for testing
TESTMTP1 = current_dir / "artifacts" / "MTPs" /  "2025-11-18-Zenon_HC10_MTP_V3.0.0.aml"
TESTMTP2 = current_dir / "artifacts" / "MTPs" / "2025-11-10-HC20-Zenon v1.0.0.aml"
TESTMTPS = [TESTMTP1, TESTMTP2]
NAMESPACE = "{http://www.dke.de/CAEX}"

### start main
def getMtps(input_files=None, logger=None) -> list[Pea]:
    mtps:list[Pea] = []

    if input_files is None:
        input_files =  TESTMTPS     # å¦‚æžœæ²¡ä¼ å‚æ•°ï¼Œå¯ä»¥ä¿ç•™åŽŸæ¥çš„æµ‹è¯•æ•°æ®ä½œä¸ºé»˜è®¤å€¼

    # parse mtp files
    for file in input_files:
        tree = parse(file)
        root = tree.getroot()

        # create mtp object
        mtp = Pea()
        mtp.source_file = str(file)
        mtps.append(mtp)

        # parse mtp
        for child in root:
            if child.tag == f"{NAMESPACE}InstanceHierarchy" and child.get("Name") == "ModuleTypePackage":
                # fetch name of mtp
                mtp.nameMtp(name=child.find(f"{NAMESPACE}InternalElement").get("Name"))

                for gchild in child.iter(f"{NAMESPACE}InternalElement"):
                    if gchild.get("Name") == "CommunicationSet" or gchild.get("Name") == "Communication":
                        for node in gchild:
                            if node.get("Name") == "InstanceList" or node.get("Name") == "Instances":
                                # parse instances
                                for instNode in node.iter(f"{NAMESPACE}InternalElement"):
                                    if (instNode.get("Name") == "InstanceList" or 
                                        instNode.get("Name") == "Instances" or
                                        instNode.get("RefBaseSystemUnitPath") == "MTPDataObjectSUCLib/DataAssembly/PeaElement/PeaInformationLabel" or
                                        instNode.get("RefBaseSystemUnitPath") == "MTPDataObjectSUCLib/DataAssembly/PeaElement/WebServerUrlInfo" or
                                        instNode.get("RefBaseSystemUnitPath") == "MTPDataObjectSUCLib/DataAssembly/ServiceElement/ProcedureHealthView"
                                        ):    #or instNode.get("RefBaseSystemUnitPath") == "MTPDataObjectSUCLib/DataAssembly/ServiceElement/ProcedureHealthView" æŽ’é™¤äº†procedures, å› ä¸ºproceduresåœ¨serviceé‡Œæœ‰å¦å¤–çš„èŠ‚ç‚¹
                                        continue
                                    inst = Instance(name=instNode.get("Name"), id=instNode.get("ID"))
                                    # Base instance type from Communication/InstanceList layer (fallback type in UI).
                                    inst.addRefBaseSystemUnitPath(instNode.get("RefBaseSystemUnitPath"))

                                    for attrNode in instNode.iter(f"{NAMESPACE}Attribute"):
                                        if attrNode.get("Name") == "RefID":
                                            inst.addRefId(attrNode.findtext(f"{NAMESPACE}Value"))
                                        elif attrNode.get("Name") == "WQC":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['WQC']['ID'] = id
                                            inst.paramElem['WQC']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "OSLevel":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['OSLevel']['ID'] = id
                                            inst.paramElem['OSLevel']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "CommandInfo":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['CommandInfo']['ID'] = id
                                            inst.paramElem['CommandInfo']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "CommandOp":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['CommandOp']['ID'] = id
                                            inst.paramElem['CommandOp']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "CommandInt":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['CommandInt']['ID'] = id
                                            inst.paramElem['CommandInt']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "CommandExt":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['CommandExt']['ID'] = id
                                            inst.paramElem['CommandExt']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ProcedureOp":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ProcedureOp']['ID'] = id
                                            inst.paramElem['ProcedureOp']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ProcedureInt":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ProcedureInt']['ID'] = id
                                            inst.paramElem['ProcedureInt']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ProcedureExt":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ProcedureExt']['ID'] = id
                                            inst.paramElem['ProcedureExt']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "StateCur":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['StateCur']['ID'] = id
                                            inst.paramElem['StateCur']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "CommandEn":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['CommandEn']['ID'] = id
                                            inst.paramElem['CommandEn']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ProcedureCur":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ProcedureCur']['ID'] = id
                                            inst.paramElem['ProcedureCur']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ProcedureReq":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ProcedureReq']['ID'] = id
                                            inst.paramElem['ProcedureReq']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "PosTextID":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['PosTextID']['ID'] = id
                                            inst.paramElem['PosTextID']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "InteractQuestionID":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['InteractQuestionID']['ID'] = id
                                            inst.paramElem['InteractQuestionID']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "InteractAnswerID":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['InteractAnswerID']['ID'] = id
                                            inst.paramElem['InteractAnswerID']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "InteractAddInfo":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['InteractAddInfo']['ID'] = id
                                            inst.paramElem['InteractAddInfo']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "StateChannel":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['StateChannel']['ID'] = id
                                            inst.paramElem['StateChannel']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "StateOffAut":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['StateOffAut']['ID'] = id
                                            inst.paramElem['StateOffAut']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "StateOpAut":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['StateOpAut']['ID'] = id
                                            inst.paramElem['StateOpAut']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "StateAutAut":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['StateAutAut']['ID'] = id
                                            inst.paramElem['StateAutAut']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "StateOffOp":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['StateOffOp']['ID'] = id
                                            inst.paramElem['StateOffOp']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "StateOpOp":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['StateOpOp']['ID'] = id
                                            inst.paramElem['StateOpOp']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "StateAutOp":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['StateAutOp']['ID'] = id
                                            inst.paramElem['StateAutOp']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "StateOpAct":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['StateOpAct']['ID'] = id
                                            inst.paramElem['StateOpAct']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "StateAutAct":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['StateAutAct']['ID'] = id
                                            inst.paramElem['StateAutAct']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "StateOffAct":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['StateOffAct']['ID'] = id
                                            inst.paramElem['StateOffAct']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "SrcChannel":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['SrcChannel']['ID'] = id
                                            inst.paramElem['SrcChannel']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "SrcExtAut":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['SrcExtAut']['ID'] = id
                                            inst.paramElem['SrcExtAut']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "SrcIntAut":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['SrcIntAut']['ID'] = id
                                            inst.paramElem['SrcIntAut']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "SrcExtOp":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['SrcExtOp']['ID'] = id
                                            inst.paramElem['SrcExtOp']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "SrcIntOp":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['SrcIntOp']['ID'] = id
                                            inst.paramElem['SrcIntOp']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "SrcIntAct":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['SrcIntAct']['ID'] = id
                                            inst.paramElem['SrcIntAct']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "SrcExtAct":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['SrcExtAct']['ID'] = id
                                            inst.paramElem['SrcExtAct']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ProcParamApplyEn":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ProcParamApplyEn']['ID'] = id
                                            inst.paramElem['ProcParamApplyEn']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ProcParamApplyExt":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ProcParamApplyExt']['ID'] = id
                                            inst.paramElem['ProcParamApplyExt']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ProcParamApplyOp":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ProcParamApplyOp']['ID'] = id
                                            inst.paramElem['ProcParamApplyOp']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ProcParamApplyInt":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ProcParamApplyInt']['ID'] = id
                                            inst.paramElem['ProcParamApplyInt']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ConfigParamApplyEn":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ConfigParamApplyEn']['ID'] = id
                                            inst.paramElem['ConfigParamApplyEn']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ConfigParamApplyExt":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ConfigParamApplyExt']['ID'] = id
                                            inst.paramElem['ConfigParamApplyExt']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ConfigParamApplyOp":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ConfigParamApplyOp']['ID'] = id
                                            inst.paramElem['ConfigParamApplyOp']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ConfigParamApplyInt":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ConfigParamApplyInt']['ID'] = id
                                            inst.paramElem['ConfigParamApplyInt']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ReportValueFreeze":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ReportValueFreeze']['ID'] = id
                                            inst.paramElem['ReportValueFreeze']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ApplyEn":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ApplyEn']['ID'] = id
                                            inst.paramElem['ApplyEn']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ApplyExt":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ApplyExt']['ID'] = id
                                            inst.paramElem['ApplyExt']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ApplyOp":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ApplyOp']['ID'] = id
                                            inst.paramElem['ApplyOp']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "ApplyInt":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['ApplyInt']['ID'] = id
                                            inst.paramElem['ApplyInt']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "Sync":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['Sync']['ID'] = id
                                            inst.paramElem['Sync']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "VExt":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['VExt']['ID'] = id
                                            inst.paramElem['VExt']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "VInt":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['VInt']['ID'] = id
                                            inst.paramElem['VInt']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "VOp":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['VOp']['ID'] = id
                                            inst.paramElem['VOp']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        # elif attrNode.get("Name") == "VReq":
                                        #     elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                        #     id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                        #     inst.paramElem['VReq']['ID'] = id
                                        #     inst.paramElem['VReq']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        #     inst.default = float(attrNode.findtext(f"{NAMESPACE}DefaultValue"))
                                        elif attrNode.get("Name") == "VFbk":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['VFbk']['ID'] = id
                                            inst.paramElem['VFbk']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "VOut":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['VOut']['ID'] = id
                                            inst.paramElem['VOut']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "V":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['V']['ID'] = id
                                            inst.paramElem['V']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "Pos":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['Pos']['ID'] = id
                                            inst.paramElem['Pos']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "Ctrl":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['Ctrl']['ID'] = id
                                            inst.paramElem['Ctrl']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "FwdCtrl":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['FwdCtrl']['ID'] = id
                                            inst.paramElem['FwdCtrl']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "RevCtrl":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['RevCtrl']['ID'] = id
                                            inst.paramElem['RevCtrl']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "VSclMin":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['VSclMin']['ID'] = id
                                            inst.paramElem['VSclMin']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "VSclMax":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['VSclMax']['ID'] = id
                                            inst.paramElem['VSclMax']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        elif attrNode.get("Name") == "VMin":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['VMin']['ID'] = id
                                            inst.paramElem['VMin']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                            inst.addMin(float(attrNode.findtext(f"{NAMESPACE}DefaultValue")))
                                        elif attrNode.get("Name") == "VMax":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['VMax']['ID'] = id
                                            inst.paramElem['VMax']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                            inst.addMax(float(attrNode.findtext(f"{NAMESPACE}DefaultValue")))
                                        elif attrNode.get("Name") == "VUnit":
                                            elemNode = attrNode.findtext(f"{NAMESPACE}Value")
                                            id = gchild.findtext(f".//{NAMESPACE}ExternalInterface[@ID='{elemNode}']/{NAMESPACE}Attribute[@Name='Identifier']/{NAMESPACE}Value")
                                            inst.paramElem['VUnit']['ID'] = id
                                            inst.paramElem['VUnit']['Default'] = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                            unitId = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                            inst.unitval = int(unitId)
                                            inst.addUnit(getUnit(int(unitId)))

                                    # add instance to mtp
                                    mtp.addInstance(inst)
                            elif node.get("Name") == "SourceList" or node.get("Name") == "Sources":
                                # parse url
                                mtp.addUrl(url=node.findtext(f".//*[@Name='Endpoint']/{NAMESPACE}Value"))
                                # parse namespace
                                mtp.ns = node.findtext(f".//*[@Name='Namespace']/{NAMESPACE}Value")

            elif child.tag == f"{NAMESPACE}InstanceHierarchy" and child.get("Name") == "Services":
                for gchild in child:
                    if gchild.tag == f"{NAMESPACE}InternalElement":
                        keys = ['CommandEn',
                                'CommandExt',
                                'CommandInt',
                                'CommandOp',
                                'ConfigParamApplyEn',
                                'ConfigParamApplyExt',
                                'ConfigParamApplyInt',
                                'ConfigParamApplyOp',
                                'InteractAddInfo',
                                'InteractAnswerID',
                                'InteractQuestionID',
                                'OSLevel',
                                'PosTextID',
                                'ProcParamApplyEn',
                                'ProcParamApplyExt',
                                'ProcParamApplyInt',
                                'ProcParamApplyOp',
                                'ProcedureCur',
                                'ProcedureExt',
                                'ProcedureInt',
                                'ProcedureOp',
                                'ProcedureReq',
                                'ReportValueFreeze',
                                'SrcChannel',
                                'SrcExtAct',
                                'SrcExtAut',
                                'SrcExtOp',
                                'SrcIntAct',
                                'SrcIntAut',
                                'SrcIntOp',
                                'StateAutAct',
                                'StateAutAut',
                                'StateAutOp',
                                'StateChannel',
                                'StateCur',
                                'StateOffAct',
                                'StateOffAut',
                                'StateOffOp',
                                'StateOpAct',
                                'StateOpAut',
                                'StateOpOp']

                        inst = mtp.getInstance(instId=gchild.findtext(f"./{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}Value"))
                        serv = Service()
                        serv.name = gchild.get("Name") # name of the service
                        serv.id = gchild.get("ID") # id of the service
                        serv.refid = gchild.findtext(f"./{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}Value")
                        for key in keys:
                            serv.paramElem[key] = inst.paramElem[key]
                        mtp.addService(serv)

                        # get procedures
                        for ggchild in gchild:
                            if ggchild.tag == f"{NAMESPACE}InternalElement":
                                procName = ggchild.get("Name") # name of the procedure
                                procId = ggchild.findtext(f"./{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}Value") # id of the procedure
                                proc = Procedure(name=procName, id=procId)
                                serv.procs.append(proc)
                                mtp.procs.append(proc)
                                proc.serviceId = serv.id

                                for paramNode in ggchild:
                                    # if paramNode.tag == f"{NAMESPACE}InternalElement":
                                    if paramNode.tag == f"{NAMESPACE}InternalElement" and paramNode.get("RefBaseSystemUnitPath") != "MTPServiceSUCLib/RequiredEquipment":     # MODIFIED: æŠŠRefBaseSystemUnitPath="MTPServiceSUCLib/RequiredEquipment ï¼ˆsensor/actuatorï¼‰åŽ»æŽ‰
                                        for refNode in paramNode.iter(f"{NAMESPACE}Attribute"):
                                            if refNode.get("Name") == "RefID" and mtp.hasInstance(refNode.findtext(f"{NAMESPACE}Value")):
                                                # get the instance the procedure refers to
                                                baseParam = mtp.getInstance(refNode.findtext(f"{NAMESPACE}Value"))
                                                # Keep procedure-scoped metadata (e.g. ProcessValueOut) without
                                                # mutating the shared base instance object.
                                                procParam = deepcopy(baseParam)
                                                procParamPath = paramNode.get("RefBaseSystemUnitPath")
                                                if procParamPath:
                                                    # Parameter node path is the final type source shown in MTPViewer.
                                                    procParam.addRefBaseSystemUnitPath(procParamPath)

                                                # add the instance to the procedure's params
                                                proc.addParameter(procParam)
                                    elif paramNode.tag == f"{NAMESPACE}Attribute" and paramNode.get("Name") == "IsSelfCompleting":
                                        proc.setSelfCompleting(paramNode.findtext(f"{NAMESPACE}Value"))
                                    elif paramNode.tag == f"{NAMESPACE}Attribute" and paramNode.get("Name") == "ProcedureID":
                                        proc.procId = int(paramNode.findtext(f"{NAMESPACE}Value"))

            elif child.tag == f"{NAMESPACE}InstanceHierarchy" and child.get("Name") == "HMI":
                # parse HMI Information for HC10/HC2040
                children = child.findall(".//*[@RefBaseSystemUnitPath='MTPHMISUCLib/Picture']")
                if len(children) == 1:
                    # HC2040
                    # create HMI instance
                    hmi = HMI()
                    # set type to RI because HC2040 doesn't support services
                    hmi.type = "RI"
                    # set width, height and hierarchy level
                    for gchild in children[0]:
                        if gchild.tag == f"{NAMESPACE}Attribute":
                            # width
                            if gchild.get("Name") == "Width":
                                if int(gchild.findtext(f"{NAMESPACE}Value")) is not None:
                                    hmi.width = int(gchild.findtext(f"{NAMESPACE}Value"))
                                elif int(gchild.findtext(f"{NAMESPACE}DefaultValue")) is not None:
                                    hmi.width = int(gchild.findtext(f"{NAMESPACE}DefaultValue"))
                            # height
                            elif gchild.get("Name") == "Height":
                                if int(gchild.findtext(f"{NAMESPACE}Value")) is not None:
                                    hmi.height = int(gchild.findtext(f"{NAMESPACE}Value"))
                                elif int(gchild.findtext(f"{NAMESPACE}DefaultValue")) is not None:
                                    hmi.height = int(gchild.findtext(f"{NAMESPACE}DefaultValue"))
                            # hierarchy level
                            elif gchild.get("Name") == "HierarchyLevel":
                                if gchild.findtext(f"{NAMESPACE}Value") is not None:
                                    hmi.hierarchy = gchild.findtext(f"{NAMESPACE}Value")
                                elif gchild.findtext(f"{NAMESPACE}DefaultValue") is not None:
                                    hmi.hierarchy = gchild.findtext(f"{NAMESPACE}DefaultValue")
                        elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/VisualObject":
                            # add visual objects
                            visObj = VisualObject()
                            visObj.name = gchild.get("Name")
                            # width
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}Value") is not None:
                                visObj.width = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}DefaultValue") is not None:
                                visObj.width = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}DefaultValue")
                            # height
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}Value") is not None:
                                visObj.height = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}DefaultValue") is not None:
                                visObj.height = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}DefaultValue")
                            # x coordinate
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                visObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                visObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                            # y coordinate
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                visObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                visObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                            # z index
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value") is not None:
                                visObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue") is not None:
                                visObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue")
                            # rotation
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}Value") is not None:
                                visObj.rotation = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}DefaultValue") is not None:
                                visObj.rotation = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}DefaultValue")
                            # eClass Version
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}Value") is not None:
                                visObj.eClassVer = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}DefaultValue") is not None:
                                visObj.eClassVer = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}DefaultValue")
                            # eClass Classification Class
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}Value") is not None:
                                visObj.eClassClass = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}DefaultValue") is not None:
                                visObj.eClassClass = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}DefaultValue")
                            # eClass IRDI
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}Value") is not None:
                                visObj.eClassIRDI = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}DefaultValue") is not None:
                                visObj.eClassIRDI = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}DefaultValue")
                            # refId
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}Value") is not None:
                                visObj.refId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}DefaultValue") is not None:
                                visObj.refId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}DefaultValue")
                            # refInstance
                            visObj.refInst = mtp.getInstance(instId=visObj.refId)

                            # find nodes that have port information
                            portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                            for pn in portNodes:
                                # create port
                                port = Port()
                                port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                port.name = pn.get("Name")
                                # x coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                # y coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")

                                visObj.ports.append(port)
                            hmi.visuals.append(visObj)
                        elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/TopologyObject/Junction":
                            # add junction objects
                            junc = Junction()
                            junc.name = gchild.get("Name")
                            # x coordinate
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                junc.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                junc.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                            # y coordinate
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                junc.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                junc.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")

                            # find nodes that have port information
                            portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                            for pn in portNodes:
                                # create port
                                port = Port()
                                port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                port.name = pn.get("Name")
                                # x coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                # y coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                
                                junc.ports.append(port)
                            hmi.juncts.append(junc)
                        elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/TopologyObject/Termination/Sink":
                            # add sink objects
                            sinkObj = Sink()
                            sinkObj.name = gchild.get("Name")
                            # x coordinate
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                sinkObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                sinkObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                            # y coordinate
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                sinkObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                sinkObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                            # term ID
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}Value") is not None:
                                sinkObj.termId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}DefaultValue") is not None:
                                sinkObj.termId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}DefaultValue")
                            
                            # find nodes that have port information
                            portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                            for pn in portNodes:
                                # create port
                                port = Port()
                                port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                port.name = pn.get("Name")
                                # x coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                # y coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                
                                sinkObj.ports.append(port)
                            hmi.sinks.append(sinkObj)
                        elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/TopologyObject/Termination/Source":
                            # add source objects
                            sourceObj = Source()
                            sourceObj.name = gchild.get("Name")
                            # x coordinate
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                sourceObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                sourceObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                            # y coordinate
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                sourceObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                sourceObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                            # term ID
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}Value") is not None:
                                sourceObj.termId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}DefaultValue") is not None:
                                sourceObj.termId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}DefaultValue")
                            
                            # find nodes that have port information
                            portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                            for pn in portNodes:
                                # create port
                                port = Port()
                                port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                port.name = pn.get("Name")
                                # x coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                # y coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                
                                sourceObj.ports.append(port)
                            hmi.srcs.append(sourceObj)
                        elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/Connection/Pipe":
                            # add pipe objects
                            pipeObj = Pipe()
                            pipeObj.name = gchild.get("Name")
                            # directed flag
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Directed']/{NAMESPACE}Value") is not None:
                                pipeObj.direct = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Directed']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Directed']/{NAMESPACE}DefaultValue") is not None:
                                pipeObj.direct = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Directed']/{NAMESPACE}DefaultValue")
                            # edge path
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value") is not None:
                                pipeObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue") is not None:
                                pipeObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue")
                            
                            # find nodes that have port information
                            portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                            for pn in portNodes:
                                # create port
                                port = Port()
                                port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                port.name = pn.get("Name")
                                # x coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                # y coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                
                                pipeObj.ports.append(port)
                            hmi.pipes.append(pipeObj)
                        elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/Connection/FunctionLine":
                            # add function line objects
                            functlinObj = Line()
                            functlinObj.type = "Function Line"
                            functlinObj.name = gchild.get("Name")
                            # edge path
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value") is not None:
                                functlinObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue") is not None:
                                functlinObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue")
                            
                            # find nodes that have port information
                            portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/LogicalPort']")
                            for pn in portNodes:
                                # create port
                                port = Port()
                                port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                port.name = pn.get("Name")
                                # x coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                # y coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                
                                functlinObj.ports.append(port)
                            hmi.lines.append(functlinObj)
                        elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/Connection/MeasurementLine":
                            # add measurement line objects
                            measLinObj = Line()
                            measLinObj.type = "Measurement Line"
                            measLinObj.name = gchild.get("Name")
                            # edge path
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value") is not None:
                                measLinObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue") is not None:
                                measLinObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue")
                            
                            # find nodes that have port information
                            portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/MeasurementPoint']")
                            for pn in portNodes:
                                # create port
                                port = Port()
                                port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                port.name = pn.get("Name")
                                # x coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                # y coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                
                                measLinObj.ports.append(port)
                            hmi.lines.append(measLinObj)
                        elif gchild.tag == f"{NAMESPACE}InternalLink":
                            # side A
                            sideA = gchild.get("RefPartnerSideA")
                            # side B
                            sideB = gchild.get("RefPartnerSideB")
                            hmi.links.append((sideA, sideB))

                    mtp.hmis.append(hmi)
                else:
                    # HC10
                    for hminode in children:
                        # create hmi instance
                        hmi = HMI()
                        if hminode.get("Name") == "Services":
                            # set type to service
                            hmi.type = "Service"
                            for gchild in hminode:
                                if gchild.tag == f"{NAMESPACE}Attribute":
                                    if gchild.get("Name") == "Width":
                                        if int(gchild.findtext(f"{NAMESPACE}Value")) is not None:
                                            hmi.width = int(gchild.findtext(f"{NAMESPACE}Value"))
                                        elif int(gchild.findtext(f"{NAMESPACE}DefaultValue")) is not None:
                                            hmi.width = int(gchild.findtext(f"{NAMESPACE}DefaultValue"))
                                    elif gchild.get("Name") == "Height":
                                        if int(gchild.findtext(f"{NAMESPACE}Value")) is not None:
                                            hmi.height = int(gchild.findtext(f"{NAMESPACE}Value"))
                                        elif int(gchild.findtext(f"{NAMESPACE}DefaultValue")) is not None:
                                            hmi.height = int(gchild.findtext(f"{NAMESPACE}DefaultValue"))
                                    elif gchild.get("Name") == "HierarchyLevel":
                                        if gchild.findtext(f"{NAMESPACE}Value") is not None:
                                            hmi.hierarchy = gchild.findtext(f"{NAMESPACE}Value")
                                        elif gchild.findtext(f"{NAMESPACE}DefaultValue") is not None:
                                            hmi.hierarchy = gchild.findtext(f"{NAMESPACE}DefaultValue")
                                elif gchild.tag == f"{NAMESPACE}InternalElement":
                                    # add visual object
                                    visObj = VisualObject()
                                    visObj.name = gchild.get("Name")
                                    visObj.refId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}Value")
                                    visObj.refInst = mtp.getInstance(visObj.refId)
                                    visObj.width = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}Value")
                                    visObj.height = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}Value")
                                    visObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                    visObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                    visObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value")
                                    visObj.rotation = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}Value")
                                    visObj.eClassVer = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}Value")
                                    visObj.eClassClass = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}Value")
                                    visObj.eClassIRDI = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}Value")
                                    hmi.visuals.append(visObj)

                            mtp.hmis.append(hmi)
                        elif hminode.get("Name") == "RI_Fliessbild":
                            # set type to ri
                            hmi.type = "RI"
                            for gchild in hminode:
                                if gchild.tag == f"{NAMESPACE}Attribute":
                                    if gchild.get("Name") == "Width":
                                        if int(gchild.findtext(f"{NAMESPACE}Value")) is not None:
                                            hmi.width = int(gchild.findtext(f"{NAMESPACE}Value"))
                                        elif int(gchild.findtext(f"{NAMESPACE}DefaultValue")) is not None:
                                            hmi.width = int(gchild.findtext(f"{NAMESPACE}DefaultValue"))
                                    elif gchild.get("Name") == "Height":
                                        if int(gchild.findtext(f"{NAMESPACE}Value")) is not None:
                                            hmi.height = int(gchild.findtext(f"{NAMESPACE}Value"))
                                        elif int(gchild.findtext(f"{NAMESPACE}DefaultValue")) is not None:
                                            hmi.height = int(gchild.findtext(f"{NAMESPACE}DefaultValue"))
                                    elif gchild.get("Name") == "HierarchyLevel":
                                        if gchild.findtext(f"{NAMESPACE}Value") is not None:
                                            hmi.hierarchy = gchild.findtext(f"{NAMESPACE}Value")
                                        elif gchild.findtext(f"{NAMESPACE}DefaultValue") is not None:
                                            hmi.hierarchy = gchild.findtext(f"{NAMESPACE}DefaultValue")
                                elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/TopologyObject/Termination/Sink":
                                    # add sink objects
                                    sinkObj = Sink()
                                    sinkObj.name = gchild.get("Name")
                                    # x coordinate
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                        sinkObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                        sinkObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                    # y coordinate
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                        sinkObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                        sinkObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                    # term ID
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}Value") is not None:
                                        sinkObj.termId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}DefaultValue") is not None:
                                        sinkObj.termId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}DefaultValue")
                                    
                                    # find nodes that have port information
                                    portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                                    for pn in portNodes:
                                        # create port
                                        port = Port()
                                        port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                        port.name = pn.get("Name")
                                        # x coordinate
                                        if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                            port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                        elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                            port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                        # y coordinate
                                        if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                            port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                        elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                            port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                        
                                        sinkObj.ports.append(port)
                                    hmi.sinks.append(sinkObj)
                                elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/TopologyObject/Junction":
                                    # add junction objects
                                    junc = Junction()
                                    junc.name = gchild.get("Name")
                                    # x coordinate
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                        junc.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                        junc.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                    # y coordinate
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                        junc.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                        junc.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")

                                    # find nodes that have port information
                                    portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                                    for pn in portNodes:
                                        # create port
                                        port = Port()
                                        port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                        port.name = pn.get("Name")
                                        # x coordinate
                                        if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                            port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                        elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                            port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                        # y coordinate
                                        if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                            port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                        elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                            port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                        
                                        junc.ports.append(port)
                                    hmi.juncts.append(junc)
                                elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/Connection/MeasurementLine":
                                    # add measurement line objects
                                    measLinObj = Line()
                                    measLinObj.type = "Measurement Line"
                                    measLinObj.name = gchild.get("Name")
                                    # edge path
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value") is not None:
                                        measLinObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue") is not None:
                                        measLinObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue")
                                    
                                    # find nodes that have port information
                                    portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/MeasurementPoint']")
                                    for pn in portNodes:
                                        # create port
                                        port = Port()
                                        port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                        port.name = pn.get("Name")
                                        # x coordinate
                                        if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                            port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                        elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                            port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                        # y coordinate
                                        if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                            port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                        elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                            port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                        
                                        measLinObj.ports.append(port)
                                    hmi.lines.append(measLinObj)
                                elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/Connection/FunctionLine":
                                    # add function line objects
                                    functlinObj = Line()
                                    functlinObj.type = "Function Line"
                                    functlinObj.name = gchild.get("Name")
                                    # edge path
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value") is not None:
                                        functlinObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue") is not None:
                                        functlinObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue")
                                    
                                    # find nodes that have port information
                                    portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/LogicalPort']")
                                    for pn in portNodes:
                                        # create port
                                        port = Port()
                                        port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                        port.name = pn.get("Name")
                                        # x coordinate
                                        if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                            port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                        elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                            port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                        # y coordinate
                                        if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                            port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                        elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                            port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                        
                                        functlinObj.ports.append(port)
                                    hmi.lines.append(functlinObj)
                                elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/Connection/Pipe":
                                    # add pipe objects
                                    pipeObj = Pipe()
                                    pipeObj.name = gchild.get("Name")
                                    # directed flag
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Directed']/{NAMESPACE}Value") is not None:
                                        pipeObj.direct = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Directed']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Directed']/{NAMESPACE}DefaultValue") is not None:
                                        pipeObj.direct = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Directed']/{NAMESPACE}DefaultValue")
                                    # edge path
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value") is not None:
                                        pipeObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue") is not None:
                                        pipeObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue")
                                    
                                    # find nodes that have port information
                                    portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                                    for pn in portNodes:
                                        # create port
                                        port = Port()
                                        port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                        port.name = pn.get("Name")
                                        # x coordinate
                                        if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                            port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                        elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                            port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                        # y coordinate
                                        if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                            port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                        elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                            port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                        
                                        pipeObj.ports.append(port)
                                    hmi.pipes.append(pipeObj)
                                elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/VisualObject":
                                    # add visual objects
                                    visObj = VisualObject()
                                    visObj.name = gchild.get("Name")
                                    # width
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}Value") is not None:
                                        visObj.width = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}DefaultValue") is not None:
                                        visObj.width = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}DefaultValue")
                                    # height
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}Value") is not None:
                                        visObj.height = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}DefaultValue") is not None:
                                        visObj.height = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}DefaultValue")
                                    # x coordinate
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                        visObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                        visObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                    # y coordinate
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                        visObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                        visObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                    # z index
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value") is not None:
                                        visObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue") is not None:
                                        visObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue")
                                    # rotation
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}Value") is not None:
                                        visObj.rotation = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}DefaultValue") is not None:
                                        visObj.rotation = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}DefaultValue")
                                    # eClass Version
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}Value") is not None:
                                        visObj.eClassVer = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}DefaultValue") is not None:
                                        visObj.eClassVer = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}DefaultValue")
                                    # eClass Classification Class
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}Value") is not None:
                                        visObj.eClassClass = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}DefaultValue") is not None:
                                        visObj.eClassClass = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}DefaultValue")
                                    # eClass IRDI
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}Value") is not None:
                                        visObj.eClassIRDI = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}DefaultValue") is not None:
                                        visObj.eClassIRDI = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}DefaultValue")
                                    # refId
                                    if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}Value") is not None:
                                        visObj.refId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}Value")
                                    elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}DefaultValue") is not None:
                                        visObj.refId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}DefaultValue")
                                    # refInstance
                                    visObj.refInst = mtp.getInstance(instId=visObj.refId)
                                    
                                    # find nodes that have port information
                                    portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                                    for pn in portNodes:
                                        # create port
                                        port = Port()
                                        port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                        port.name = pn.get("Name")
                                        # x coordinate
                                        if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                            port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                        elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                            port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                        # y coordinate
                                        if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                            port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                        elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                            port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                        
                                        visObj.ports.append(port)
                                    hmi.visuals.append(visObj)
                                elif gchild.tag == f"{NAMESPACE}InternalLink":
                                    sideA = gchild.get("RefPartnerSideA")
                                    sideB = gchild.get("RefPartnerSideB")
                                    hmi.links.append((sideA, sideB))

                            mtp.hmis.append(hmi)
            elif child.tag == f"{NAMESPACE}InstanceHierarchy" and child.get("Name") == "Pictures":
                # parse HMI Information for HC30
                hminode = child.find(f".//*[@RefBaseSystemUnitPath='MTPHMISUCLib/Picture'][@Name='{mtp.name}']")
                # create hmi
                hmi = HMI()
                # set type to RI because HC30 doesn't support services
                hmi.type = "RI"
                for gchild in hminode:
                    if gchild.tag == f"{NAMESPACE}Attribute":
                        if gchild.get("Name") == "Width":
                            if int(gchild.findtext(f"{NAMESPACE}Value")) is not None:
                                hmi.width = int(gchild.findtext(f"{NAMESPACE}Value"))
                            elif int(gchild.findtext(f"{NAMESPACE}DefaultValue")) is not None:
                                hmi.width = int(gchild.findtext(f"{NAMESPACE}DefaultValue"))
                        elif gchild.get("Name") == "Height":
                            if int(gchild.findtext(f"{NAMESPACE}Value")) is not None:
                                hmi.height = int(gchild.findtext(f"{NAMESPACE}Value"))
                            elif int(gchild.findtext(f"{NAMESPACE}DefaultValue")) is not None:
                                hmi.height = int(gchild.findtext(f"{NAMESPACE}DefaultValue"))
                        elif gchild.get("Name") == "HierarchyLevel":
                            if gchild.findtext(f"{NAMESPACE}Value") is not None:
                                hmi.hierarchy = gchild.findtext(f"{NAMESPACE}Value")
                            elif gchild.findtext(f"{NAMESPACE}DefaultValue") is not None:
                                hmi.hierarchy = gchild.findtext(f"{NAMESPACE}DefaultValue")
                    elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/Connection/MeasurementLine":
                        # add measurement line objects
                        measLinObj = Line()
                        measLinObj.type = "Measurement Line"
                        measLinObj.name = gchild.get("Name")
                        # edge path
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value") is not None:
                            measLinObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue") is not None:
                            measLinObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue")
                        # z index
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value") is not None:
                            measLinObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue") is not None:
                            measLinObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue")
                        
                        # find nodes that have port information
                        portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/MeasurementPoint']")
                        for pn in portNodes:
                            # create port
                            port = Port()
                            port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                            port.name = pn.get("Name")
                            # x coordinate
                            if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                            elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                            # y coordinate
                            if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                            elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                            
                            measLinObj.ports.append(port)
                        hmi.lines.append(measLinObj)
                    elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/Connection/Pipe":
                        # add pipe objects
                        pipeObj = Pipe()
                        pipeObj.name = gchild.get("Name")
                        # directed flag
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Directed']/{NAMESPACE}Value") is not None:
                            pipeObj.direct = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Directed']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Directed']/{NAMESPACE}DefaultValue") is not None:
                            pipeObj.direct = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Directed']/{NAMESPACE}DefaultValue")
                        # edge path
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value") is not None:
                            pipeObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue") is not None:
                            pipeObj.ep = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Edgepath']/{NAMESPACE}DefaultValue")
                        # z Index
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value") is not None:
                            pipeObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue") is not None:
                            pipeObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue")
                        
                        # find nodes that have port information
                        portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                        for pn in portNodes:
                            # create port
                            port = Port()
                            port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                            port.name = pn.get("Name")
                            # x coordinate
                            if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                            elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                            # y coordinate
                            if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                            elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                            
                            pipeObj.ports.append(port)
                        hmi.pipes.append(pipeObj)
                    elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/VisualObject":
                        # add visual objects
                        visObj = VisualObject()
                        visObj.name = gchild.get("Name")
                        # width
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}Value") is not None:
                            visObj.width = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}DefaultValue") is not None:
                            visObj.width = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Width']/{NAMESPACE}DefaultValue")
                        # height
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}Value") is not None:
                            visObj.height = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}DefaultValue") is not None:
                            visObj.height = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Height']/{NAMESPACE}DefaultValue")
                        # x coordinate
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                            visObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                            visObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                        # y coordinate
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                            visObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                            visObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                        # z index
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value") is not None:
                            visObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue") is not None:
                            visObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue")
                        # rotation
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}Value") is not None:
                            visObj.rotation = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}DefaultValue") is not None:
                            visObj.rotation = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Rotation']/{NAMESPACE}DefaultValue")
                        # eClass Version
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}Value") is not None:
                            visObj.eClassVer = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}DefaultValue") is not None:
                            visObj.eClassVer = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassVersion']/{NAMESPACE}DefaultValue")
                        # eClass Classification Class
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}Value") is not None:
                            visObj.eClassClass = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}DefaultValue") is not None:
                            visObj.eClassClass = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassClassificationClass']/{NAMESPACE}DefaultValue")
                        # eClass IRDI
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}Value") is not None:
                            visObj.eClassIRDI = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}DefaultValue") is not None:
                            visObj.eClassIRDI = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='eClassIRDI']/{NAMESPACE}DefaultValue")
                        # refId
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}Value") is not None:
                            visObj.refId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}DefaultValue") is not None:
                            visObj.refId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='RefID']/{NAMESPACE}DefaultValue")
                        # refInstance
                        visObj.refInst = mtp.getInstance(instId=visObj.refId)

                        # find nodes that have port information
                        portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                        for pn in portNodes:
                            # create port
                            port = Port()
                            port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                            port.name = pn.get("Name")
                            # x coordinate
                            if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                            elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                            # y coordinate
                            if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                            elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")

                            visObj.ports.append(port)
                        hmi.visuals.append(visObj)
                    elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/TopologyObject/Termination/Source":
                        # add source objects
                        sourceObj = Source()
                        sourceObj.name = gchild.get("Name")
                        # x coordinate
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                            sourceObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                            sourceObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                        # y coordinate
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                            sourceObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                            sourceObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                        # z index
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value") is not None:
                            sourceObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue") is not None:
                            sourceObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue")
                        # term ID
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}Value") is not None:
                            sourceObj.termId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}DefaultValue") is not None:
                            sourceObj.termId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}DefaultValue")
                        
                        # find nodes that have port information
                        portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                        for pn in portNodes:
                            # create port
                            port = Port()
                            port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                            port.name = pn.get("Name")
                            # x coordinate
                            if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                            elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                            # y coordinate
                            if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                            elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                            
                            sourceObj.ports.append(port)
                        hmi.srcs.append(sourceObj)
                    elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/TopologyObject/Termination/Sink":
                        # add sink objects
                        sinkObj = Sink()
                        sinkObj.name = gchild.get("Name")
                        # x coordinate
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                            sinkObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                            sinkObj.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                        # y coordinate
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                            sinkObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                            sinkObj.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                        # z index
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value") is not None:
                            sinkObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue") is not None:
                            sinkObj.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue")
                        # term ID
                        if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}Value") is not None:
                            sinkObj.termId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}Value")
                        elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}DefaultValue") is not None:
                            sinkObj.termId = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='TermID']/{NAMESPACE}DefaultValue")
                        
                        # find nodes that have port information
                        portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                        for pn in portNodes:
                            # create port
                            port = Port()
                            port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                            port.name = pn.get("Name")
                            # x coordinate
                            if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                            elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                            # y coordinate
                            if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                            elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                            
                            sinkObj.ports.append(port)
                        hmi.sinks.append(sinkObj)
                    elif gchild.tag == f"{NAMESPACE}InternalElement" and gchild.get("RefBaseSystemUnitPath") == "MTPHMISUCLib/TopologyObject/Junction":
                            # add junction objects
                            junc = Junction()
                            junc.name = gchild.get("Name")
                            # x coordinate
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                junc.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                junc.x = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                            # y coordinate
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                junc.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                junc.y = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                            # z index
                            if gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value") is not None:
                                junc.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}Value")
                            elif gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue") is not None:
                                junc.zindex = gchild.findtext(f".//{NAMESPACE}Attribute[@Name='ZIndex']/{NAMESPACE}DefaultValue")

                            # find nodes that have port information
                            portNodes = gchild.findall(f".//{NAMESPACE}InternalElement[@RefBaseSystemUnitPath='MTPHMISUCLib/PortObject/Nozzle']")
                            for pn in portNodes:
                                # create port
                                port = Port()
                                port.connectId = pn.find(f".//{NAMESPACE}ExternalInterface[@Name='Connector']").get("ID")
                                port.name = pn.get("Name")
                                # x coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue") is not None:
                                    port.x = pn.findtext(f".//{NAMESPACE}Attribute[@Name='X']/{NAMESPACE}DefaultValue")
                                # y coordinate
                                if pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}Value")
                                elif pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue") is not None:
                                    port.y = pn.findtext(f".//{NAMESPACE}Attribute[@Name='Y']/{NAMESPACE}DefaultValue")
                                
                                junc.ports.append(port)
                            hmi.juncts.append(junc)

                mtp.hmis.append(hmi)
        # get sensors and actuators
        for i in mtp.insts:
            if not (mtp.hasParameter(i.id) or mtp.hasProcedure(i.id) or mtp.hasService(i.id) or i.name == "PeaInforamtionLabel"):
                mtp.sensacts.append(i)
        


    # debugging only
    # for m in mtps:
    #     print(m.name)
    #     for s in m.servs:
    #         print(s.name, s.id)
    #         for p in s.procs:
    #             print("  ", p.name, p.id)
    #             for pa in p.params:
    #                 print("    ", pa.name, pa.id, pa.default, pa.unit)
    #         print("\n")

    ## debugging only
    # print("Services: ")
    # for s in mtp.servs:
    #     print(s.name)
    # print("\n", "Procedures: ")
    # for p in mtp.procs:
    #     print(p.name)
    # print("\n", "Sensors and Actuators: ")
    # for sa in mtp.sensacts:
    #     if sa.paramElem["V"]["ID"] is not None:
    #         print(sa.name, sa.paramElem["V"]["ID"])
    #     elif sa.paramElem["VOut"]["ID"] is not None:
    #         print(sa.name, sa.paramElem["VOut"]["ID"])
    #     elif sa.paramElem["Pos"]["ID"] is not None:
    #         print(sa.name, sa.paramElem["Pos"]["ID"])
    #     elif sa.paramElem["Ctrl"]["ID"] is not None:
    #         print(sa.name, sa.paramElem["Ctrl"]["ID"])

    return mtps
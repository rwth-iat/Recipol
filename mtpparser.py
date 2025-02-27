from defusedxml.ElementTree import parse

### static variables
TESTMTP1 = r"Artefakte\HC10_manifest.aml"
TESTMTP2 = r"Artefakte\HC30_manifest.aml"
TESTMTPS = [TESTMTP1, TESTMTP2] 
NAMESPACE = "{http://www.dke.de/CAEX}"

### classes
class Instance:
    def __init__(self, name, id):
        self.name = name # name of the instance
        self.id = id # ID of the instance
        self.refid = None # refID of the instance
        self.min = None # minimal value of the instance
        self.max = None # maximal value of the instance
        self.unit = None # unit of the instance

    def __str__(self):
        descr = f"NAME: {self.name}, ID={self.id}"
        descr += f"\n    Min: {self.min}, Max: {self.max}, Unit: {self.unit}"
        return descr
    
    def addRefId(self, refId: str):
        """Adds a refID to the instance"""
        self.refid = refId
    
    def addMin(self, minVal:float):
        """Adds a low limit value"""
        self.min = minVal

    def addMax(self, maxVal:float):
        """Adds a high limit value"""
        self.max = maxVal

    def addUnit(self, unit:str):
        """Adds a unit"""
        self.unit = unit

    def getName(self) -> str:
        """Returns the name of the instance"""
        return self.name

class Procedure:
    def __init__(self, name:str, id:str):
        self.name = name # name of the procedure
        self.id = id # id of the procedure
        self.params = [] # list of parameters of the procedure
        self.compl = None # flag that says if procedure is self completing or not

    def __str__(self):
        descr = f"NAME: {self.name}, ID: {self.id}"
        descr += f"\n   Parameter: {self.params}"
        descr += f"\n   Self Completing: {self.compl}"
        return descr
    
    def addParameter(self, param:Instance) -> None:
        """Adds a parameter to the procedure"""
        self.params.append(param)

    def setSelfCompleting(self, complFlag:bool) -> None:
        """Sets the self completing flag of the procedure"""
        self.compl = complFlag

class Mtp:
    def __init__(self):
        self.name = "" # name of the mtp 
        self.insts = [] # list of instances
        self.procs = [] # list of procedures
        self.url = "" # address of the opc ua server

    def __str__(self):
        descr = f"{self.name}\nInstances:"
        for i in self.insts:
            descr += f"\n    {i}"
        descr += f"\nProcedures:"
        for p in self.procs:
            descr += f"\n   {p}"
        return descr

    def nameMtp(self, name:str) -> None:
        """Adds a name to the mtp"""
        self.name = name

    def addInstance(self, inst:Instance) -> None:
        """Adds an instance to the mtp"""
        self.insts.append(inst)

    def hasInstance(self, instId:str) -> bool:
        """Returns true if an instance with the given id exists, otherwise false"""
        for i in self.insts:
            if i.id == instId or i.refid == instId:
                return True
            
        return False
    
    def getInstance(self, instId:str) -> Instance:
        """Returns the instance with the given id"""
        for i in self.insts:
            if i.id == instId or i.refid == instId:
                return i
            
        return None

    def addProcedure(self, proc:Procedure) -> None:
        """Adds a procedure to the mtp."""
        self.procs.append(proc)

    def addUrl(self, url:str) -> None:
        """Adds an opc ua server url to the mtp"""
        self.url = url

    def getUrl(self) -> str:
        """Returns the url of the opc ua server"""
        return self.url
    
    def getProcedure(self, id:str) -> Procedure:
        """Returns the procedure with the specified id"""
        for p in self.procs:
            if p.id == id:
                return p
            
        return None

### functions
def getUnit(unitNr: int) -> str:
    """Returns the unit corresponding to the identifier"""
    match unitNr:
        case 1000:
            return "Kelvin"
        case 1001:
            return "Grad Celsius"
        case 1002:
            return "Grad Fahrenheit"
        case 1003:
            return "Grad Rankine"
        case 1004:
            return "Radiant"
        case 1005:
            return "Grad"
        case 1006:
            return "Minute"
        case 1007:
            return "Sekunde"
        case 1008:
            return "Gon"
        case 1009:
            return "Umdrehung"
        case 1010:
            return "Meter"
        case 1011:
            return "Kilometer"
        case 1012:
            return "Zentimeter"
        case 1013:
            return "Millimeter"
        case 1014:
            return "Mikrometer"
        case 1015:
            return "Nanometer"
        case 1016:
            return "Picometer"
        case 1017:
            return "Angstrom"
        case 1018:
            return "Fuß"
        case 1019:
            return "Zoll"
        case 1020:
            return "Yard"
        case 1021:
            return "Meile"
        case 1022:
            return "Nautische Meile"
        case 1023:
            return "Quadratmeter"
        case 1024:
            return "Quadratkilometer"
        case 1025:
            return "Quadratzentimeter"
        case 1026:
            return "Quadratdezimeter"
        case 1027:
            return "Quadratmillimeter"
        case 1028:
            return "Ar"
        case 1029:
            return "Hektar"
        case 1030:
            return "Quadratzoll"
        case 1031:
            return "Quadratfuß"
        case 1032:
            return "Quadratyard"
        case 1033:
            return "Quadratmeile"
        case 1034:
            return "Kubikmeter"
        case 1035:
            return "Kubikdezimeter"
        case 1036:
            return "Kubikzentimeter"
        case 1037:
            return "Kubikmillimeter"
        case 1038:
            return "Liter"
        case 1039:
            return "Zentiliter"
        case 1040:
            return "Milliliter"
        case 1041:
            return "Hektoliter"
        case 1042:
            return "Kubikzoll"
        case 1043:
            return "Kubikfuß"
        case 1044:
            return "Kubikyard"
        case 1045:
            return "Kubikmeile"
        case 1046:
            return "Pint"
        case 1047:
            return "Quart"
        case 1048:
            return "US-Gallonen"
        case 1049:
            return "Imperial Gallonen"
        case 1050:
            return "Bushel"
        case 1051:
            return "Barrel"
        case 1052:
            return "Barrel flüssig"
        case 1053:
            return "Normkubikfuß"
        case 1054:
            return "Sekunde"
        case 1055:
            return "Kilosekunde"
        case 1056:
            return "Millisekunde"
        case 1057:
            return "Mikrosekunde"
        case 1058:
            return "Minute"
        case 1059:
            return "Stunde"
        case 1060:
            return "Tag"
        case 1061:
            return "Meter pro Sekunde"
        case 1062:
            return "Millimeter pro Sekunde"
        case 1063:
            return "Meter pro Stunde"
        case 1064:
            return "Kilometer pro Stunde"
        case 1065:
            return "Knoten"
        case 1066:
            return "Zoll pro Sekunde"
        case 1067:
            return "Fuß pro Sekunde"
        case 1068:
            return "Yard pro Sekunde"
        case 1069:
            return "Zoll pro Minute"
        case 1070:
            return "Fuß pro Minute"
        case 1071:
            return "Yard pro Minute"
        case 1072:
            return "Zoll pro Stunde"
        case 1073:
            return "Fuß pro Stunde"
        case 1074:
            return "Yard pro Stunde"
        case 1075:
            return "Meilen pro Stunde"
        case 1076:
            return "Meter pro Quadratsekunde"
        case 1077:
            return "Hertz"
        case 1078:
            return "Terahertz"
        case 1079:
            return "Gigahertz"
        case 1080:
            return "Megahertz"
        case 1081:
            return "Kilohertz"
        case 1082:
            return "Pro Sekunde"
        case 1083:
            return "Pro Minute"
        case 1084:
            return "Umdrehungen pro Sekunde"
        case 1085:
            return "Umdrehungen pro Minute"
        case 1086:
            return "Radiant pro Sekunde"
        case 1087:
            return "Pro Quadratsekunden"
        case 1088:
            return "Kilogramm"
        case 1089:
            return "Gramm"
        case 1090:
            return "Milligramm"
        case 1091:
            return "Megagramm"
        case 1092:
            return "Metrische Tonne"
        case 1093:
            return "Unze"
        case 1094:
            return "Pfund"
        case 1095:
            return "US-Tonne"
        case 1096:
            return "Britische Tonne"
        case 1097:
            return "Kilogramm pro Kubikmeter"
        case 1098:
            return "Megagramm pro Kubikmeter"
        case 1099:
            return "Kilogramm pro Kubikdezimeter"
        case 1100:
            return "Gramm pro Kubikzentimeter"
        case 1101:
            return "Gramm pro Kubikmeter"
        case 1102:
            return "Metrische Tonne pro Kubikmeter"
        case 1103:
            return "Kilogramm pro Liter"
        case 1104:
            return "Gramm pro Milliliter"
        case 1105:
            return "Gramm pro Liter"
        case 1106:
            return "Pfund pro Kubikzoll"
        case 1107:
            return "Pfund pro Kubikfuß"
        case 1108:
            return "Pfund pro US-Gallonen"
        case 1109:
            return "US-Tonnen pro Kubikyard"
        case 1110:
            return "Grad Twaddell"
        case 1111:
            return "Grad Baumé (schwer)"
        case 1112:
            return "Grad Baumé (leicht)"
        case 1113:
            return "Grad API"
        case 1114:
            return "Specific gravity units"
        case 1115:
            return "Kilogramm pro Meter"
        case 1116:
            return "Milligramm pro Meter"
        case 1117:
            return "Tex"
        case 1118:
            return "Kilogramm mal Quadratmeter"
        case 1119:
            return "Kilogramm mal Meter pro Sekunde"
        case 1120:
            return "Newton"
        case 1121:
            return "Meganewton"
        case 1122:
            return "Kilonewton"
        case 1123:
            return "Millinewton"
        case 1124:
            return "Mikronewton"
        case 1125:
            return "Kilogramm mal Quadratmeter pro Sekunde"
        case 1126:
            return "Newton mal Meter"
        case 1127:
            return "Meganewton mal Meter"
        case 1128:
            return "Kilonewton mal Meter"
        case 1129:
            return "Millinewton mal Meter"
        case 1130:
            return "Pascal"
        case 1131:
            return "Gigapascal"
        case 1132:
            return "Megapascal"
        case 1133:
            return "Kilopascal"
        case 1134:
            return "Millipascal"
        case 1135:
            return "Mikropascal"
        case 1136:
            return "Hektopascal"
        case 1137:
            return "Bar"
        case 1138:
            return "Millibar"
        case 1139:
            return "Torr"
        case 1140:
            return "Atmosphären"
        case 1141:
            return "Pfund pro Quadratzoll"
        case 1142: 
            return "Pfund pro quadratinch (absolut)"
        case 1143:
            return "Pfund pro quadratinch (gauge)"
        case 1144:
            return "Gramm pro Quadratzentimeter"
        case 1145:
            return "Kilogramm pro Quadratzentimeter"
        case 1146:
            return "Zoll Wassersäule"
        case 1147:
            return "Zoll Wassersäule bei 4 Grad Celsius"
        case 1148:
            return "Zoll Wassersäule bei 68 Grad Fahrenheit"
        case 1149:
            return "Millimeter Wassersäule"
        case 1150:
            return "Millimeter Wassersäule bei 4 Grad Celsius"
        case 1151:
            return "Millimeter Wassersäule bei 68 Grad Fahrenheit"
        case 1152:
            return "Fuß Wassersäule"
        case 1153:
            return "Fuß Wassersäule bei 4 Grad Celsius"
        case 1154:
            return "Fuß Wassersäule bei 68 Grad Fahrenheit"
        case 1155:
            return "Zoll Quecksilbersäule"
        case 1156:
            return "Zoll Quecksilbersäule bei 0 Grad Celsius"
        case 1157:
            return "Millimeter Quecksilbersäule"
        case 1158:
            return "Millimeter Quecksilbersäule bei 0 Grad Celsius"
        case 1159:
            return "Pascalsekunde"
        case 1160:
            return "Quadratmeter pro Sekunde"
        case 1161:
            return "Poise"
        case 1162:
            return "Zentipoise"
        case 1163:
            return "Stokes"
        case 1164:
            return "Zentistokes"
        case 1165:
            return "Newton pro Meter"
        case 1166:
            return "Millinewton pro Meter"
        case 1167:
            return "Joule"
        case 1168:
            return "Exajoule"
        case 1169:
            return "Petajoule"
        case 1170:
            return "Terajoule"
        case 1171:
            return "Gigajoule"
        case 1172:
            return "Megajoule"
        case 1173:
            return "Kilojoule"
        case 1174:
            return "Millijoule"
        case 1175:
            return "Wattstunde"
        case 1176:
            return "Terawattstunde"
        case 1177:
            return "Gigawattstunde"
        case 1178:
            return "Megawattstunde"
        case 1179:
            return "Kilowattstunde"
        case 1180:
            return "Kalorie (thermochemisch)"
        case 1181:
            return "Kilokalorie (thermochemisch)"
        case 1182:
            return "Megakalorie (thermochemisch)"
        case 1183:
            return "British thermal unit"
        case 1184:
            return "Decatherm"
        case 1185:
            return "Fuß mal Pfund"
        case 1186:
            return "Watt"
        case 1187:
            return "Terawatt"
        case 1188:
            return "Gigawatt"
        case 1189:
            return "Megawatt"
        case 1190:
            return "Kilowatt"
        case 1191:
            return "Milliwatt"
        case 1192:
            return "Mikrowatt"
        case 1193:
            return "Nanowatt"
        case 1194:
            return "Picowatt"
        case 1195:
            return "Megakalorie pro Stunde"
        case 1196:
            return "Megajoule pro Stunde"
        case 1197:
            return "Britische thermische Einheit pro Stunde"
        case 1198:
            return "Pferdestärke"
        case 1199:
            return "Watt pro Meter mal Kelvin"
        case 1200:
            return "Watt pro Quadratmeter mal Kelvin"
        case 1201:
            return "Quadratmeter mal Kelvin pro Watt"
        case 1202:
            return "Joule pro Kelvin"
        case 1203:
            return "Kilojoule pro Kelvin"
        case 1204:
            return "Joule pro Kilogramm mal Kelvin"
        case 1205:
            return "Kilojoule pro Kilogramm mal Kelvin"
        case 1206:
            return "Joule pro Kilogramm"
        case 1207:
            return "Megajoule pro Kilogramm"
        case 1208:
            return "Kilojoule pro Kilogramm"
        case 1209: 
            return "Ampere"
        case 1210:
            return "Kiloampere"
        case 1211:
            return "Milliampere"
        case 1212:
            return "Mikroampere"
        case 1213:
            return "Nanoampere"
        case 1214:
            return "Picoampere"
        case 1215:
            return "Coulomb"
        case 1216:
            return "Megacoulomb"
        case 1217:
            return "Kilocoulomb"
        case 1218:
            return "Mikrocoulomb"
        case 1219:
            return "Nanocoulomb"
        case 1220:
            return "Picocoulomb"
        case 1221:
            return "Amperestunde"
        case 1222:
            return "Coulomb pro Kubikmeter"
        case 1223:
            return "Coulomb pro Kubikmillimeter"
        case 1224:
            return "Coulomb pro Kubikzentimeter"
        case 1225:
            return "Kilocoulomb pro Kubikmeter"
        case 1226:
            return "Millicoulomb pro Kubikmeter"
        case 1227:
            return "Mikrocoulomb pro Kubikmeter"
        case 1228:
            return "Coulomb pro Quadratmeter"
        case 1229:
            return "Coulomb pro Quadratmillimeter"
        case 1230:
            return "Coulomb pro Quadratzentimeter"
        case 1231:
            return "Kilocoulomb pro Quadratmeter"
        case 1232:
            return "Millicoulomb pro Quadratmeter"
        case 1233:
            return "Mikrocoulomb pro Quadratmeter"
        case 1234:
            return "Volt pro Meter"
        case 1235:
            return "Megavolt pro Meter"
        case 1236:
            return "Kilovolt pro Meter"
        case 1237:
            return "Volt pro Zentimeter"
        case 1238:
            return "Millivolt pro Meter"
        case 1239:
            return "Mikrovolt pro Meter"
        case 1240:
            return "Volt"
        case 1241:
            return "Megavolt"
        case 1242:
            return "Kilovolt"
        case 1243:
            return "Millivolt"
        case 1244:
            return "Mikrovolt"
        case 1245:
            return "Farad"
        case 1246:
            return "Millifarad"
        case 1247:
            return "Mikrofarad"
        case 1248:
            return "Nanofarad"
        case 1249:
            return "Picofarad"
        case 1250:
            return "Farad pro Meter"
        case 1251:
            return "Mikrofarad pro Meter"
        case 1252:
            return "Nanofarad pro Meter"
        case 1253:
            return "Picofarad pro Meter"
        case 1254:
            return "Coulomb mal Meter"
        case 1255:
            return "Ampere pro Quadratmeter"
        case 1256:
            return "Megaampere pro Quadratmeter"
        case 1257:
            return "Ampere pro Quadratzentimeter"
        case 1258:
            return "Kiloampere pro Quadratmeter"
        case 1259:
            return "Ampere pro Meter"
        case 1260:
            return "Kiloampere pro Meter"
        case 1261:
            return "Ampere pro Zentimeter"
        case 1262:
            return "Tesla"
        case 1263:
            return "Millitesla"
        case 1264:
            return "Mikrotesla"
        case 1265:
            return "Nanotesla"
        case 1266:
            return "Weber"
        case 1267:
            return "Milliweber"
        case 1268:
            return "Weber pro Meter"
        case 1269:
            return "Kiloweber pro Meter"
        case 1270:
            return "Henry"
        case 1271:
            return "Millihenry"
        case 1272:
            return "Mikrohenry"
        case 1273:
            return "Nanohenry"
        case 1274:
            return "Picohenry"
        case 1275:
            return "Henry pro Meter"
        case 1276:
            return "Mikrohenry pro Meter"
        case 1277:
            return "Nanohenry pro Meter"
        case 1278:
            return "Ampere mal Quadratmeter"
        case 1279:
            return "Newton mal Quadratmeter pro Ampere"
        case 1280:
            return "Weber mal Meter"
        case 1281:
            return "Ohm"
        case 1282:
            return "GigaOhm"
        case 1283:
            return "MegaOhm"
        case 1284:
            return "KiloOhm"
        case 1285:
            return "MilliOhm"
        case 1286:
            return "MikroOhm"
        case 1287:
            return "Siemens"
        case 1288:
            return "Kilosiemens"
        case 1289:
            return "Millisiemens"
        case 1290:
            return "Mikrosiemens"
        case 1291:
            return "Ohm mal Meter"
        case 1292:
            return "GigaOhm mal Meter"
        case 1293:
            return "MegaOhm mal Meter"
        case 1294:
            return "KiloOhm mal Meter"
        case 1295:
            return "Ohm mal Zentimeter"
        case 1296:
            return "MilliOhm mal Meter"
        case 1297:
            return "MikroOhm mal Meter"
        case 1298:
            return "NanoOhm mal Meter"
        case 1299:
            return "Siemens pro Meter"
        case 1300:
            return "Megasiemens pro Meter"
        case 1301:
            return "Kilosiemens pro Meter"
        case 1302:
            return "Millisiemens pro Zentimeter"
        case 1303:
            return "Mikrosiemens pro Millimeter"
        case 1304:
            return "Pro Henry"
        case 1305:
            return "Steradiant"
        case 1306:
            return "Watt pro Steradiant"
        case 1307:
            return "Watt pro Steradiant mal Quadratmeter"
        case 1308:
            return "Watt pro Quadratmeter"
        case 1309:
            return "Lumen"
        case 1310:
            return "Lumensekunde"
        case 1311:
            return "Lumenstunde"
        case 1312:
            return "Lumen pro Quadratmeter"
        case 1313:
            return "Lumen pro Watt"
        case 1314:
            return "Lux"
        case 1315:
            return "Luxsekunde"
        case 1316:
            return "Candela"
        case 1317:
            return "Candela pro Quadratmeter"
        case 1318:
            return "Gramm pro Sekunde"
        case 1319:
            return "Gramm pro Minute"
        case 1320:
            return "Gramm pro Stunde"
        case 1321:
            return "Gramm pro Tag"
        case 1322:
            return "Kilogramm pro Sekunde"
        case 1323:
            return "Kilogramm pro Minute"
        case 1324:
            return "Kilogramm pro Stunde"
        case 1325:
            return "Kilogramm pro Tag"
        case 1326:
            return "Metrische Tonne pro Sekunde"
        case 1327:
            return "Metrische Tonne pro Minute"
        case 1328:
            return "Metrische Tonne pro Stunde"
        case 1329:
            return "Metrische Tonne pro Tag"
        case 1330:
            return "Pfund pro Sekunde"
        case 1331:
            return "Pfund pro Minute"
        case 1332:
            return "Pfund pro Stunde"
        case 1333:
            return "Pfund pro Tag"
        case 1334:
            return "US-Tonnen pro Sekunde"
        case 1335:
            return "US-Tonnen pro Minute"
        case 1336:
            return "US-Tonnen pro Stunde"
        case 1337:
            return "US-Tonnen pro Tag"
        case 1338:
            return "Britische Tonnen pro Sekunde"
        case 1339:
            return "Britische Tonnen pro Minute"
        case 1340:
            return "Britische Tonnen pro Stunde"
        case 1341:
            return "Britische Tonnen pro Tag"
        case 1342: 
            return "Prozent"
        case 1343:
            return "Prozent Feststoffe pro Gewichtseinheit"
        case 1344:
            return "Prozent Feststoffe pro Volumeneinheit"
        case 1345:
            return "Prozent Dampfqualität"
        case 1346:
            return "Grad plato"
        case 1347:
            return "Kubikmeter pro Sekunde"
        case 1348:
            return "Kubikmeter pro Minute"
        case 1349:
            return "Kubikmeter pro Stunde"
        case 1350:
            return "Kubikmeter pro Tag"
        case 1351:
            return "Liter pro Sekunde"
        case 1352:
            return "Liter pro Minute"
        case 1353:
            return "Liter pro Stunde"
        case 1354:
            return "Liter pro Tag"
        case 1355:
            return "Megaliter pro Tag"
        case 1356:
            return "Kubikfuß pro Sekunde"
        case 1357:
            return "Kubikfuß pro Minute"
        case 1358:
            return "Kubikfuß pro Stunde"
        case 1359:
            return "Kubikfuß pro Tag"
        case 1360:
            return "Standard Kubikfuß pro Minute"
        case 1361:
            return "Standard Kubikfuß pro Stunde"
        case 1362:
            return "US-Gallonen pro Sekunde"
        case 1363:
            return "US-Gallonen pro Minute"
        case 1364:
            return "US-Gallonen pro Stunde"
        case 1365:
            return "US-Gallonen pro Tag"
        case 1366:
            return "Mega US-Gallonen pro Tag"
        case 1367:
            return "Imperial Gallonen pro Sekunde"
        case 1368:
            return "Imperial Gallonen pro Minute"
        case 1369:
            return "Imperial Gallonen pro Stunde"
        case 1370:
            return "Imperial Gallonen pro Tag"
        case 1371:
            return "Barrel pro Sekunde"
        case 1372:
            return "Barrel pro Minute"
        case 1373:
            return "Barrel pro Stunde"
        case 1374:
            return "Barrel pro Tag"
        case 1375:
            return "Watt pro Quadratmeter"
        case 1376:
            return "Milliwatt pro Quadratmeter"
        case 1377:
            return "Mikrowatt pro Quadratmeter"
        case 1378:
            return "Picowatt pro Quadratmeter"
        case 1379:
            return "Pascalsekunde pro Kubikmeter"
        case 1380:
            return "Newtonsekunde pro Meter"
        case 1381:
            return "Pascalsekunde pro Meter"
        case 1382:
            return "Bel"
        case 1383:
            return "Dezibel"
        case 1384:
            return "Mol"
        case 1385:
            return "Kilomol"
        case 1386:
            return "Millimol"
        case 1387:
            return "Mikromol"
        case 1388:
            return "Kilogramm pro Mol"
        case 1389:
            return "Gramm pro Mol"
        case 1390:
            return "Kubikmeter pro Mol"
        case 1391:
            return "Kubikdezimeter pro Mol"
        case 1392:
            return "Kubikzentimeter pro Mol"
        case 1393:
            return "Liter pro Mol"
        case 1394:
            return "Joule pro Mol"
        case 1395:
            return "Kilojoule pro Mol"
        case 1396:
            return "Joule pro Mol mal Kelvin"
        case 1397:
            return "Mol pro Kubikmeter"
        case 1398:
            return "Mol pro Kubikdezimeter"
        case 1399:
            return "Mol pro Liter"
        case 1400:
            return "Mol pro Kilogramm"
        case 1401:
            return "Millimol pro Kilogramm"
        case 1402:
            return "Becquerel"
        case 1403:
            return "Megabecquerel"
        case 1404:
            return "Kilobecquerel"
        case 1405:
            return "Becquerel pro Kilogramm"
        case 1406:
            return "Kilobecquerel pro Kilogramm"
        case 1407:
            return "Megabecquerel pro Kilogramm"
        case 1408:
            return "Grau"
        case 1409:
            return "Milligray"
        case 1410:
            return "Rad"
        case 1411:
            return "Sievert"
        case 1412:
            return "Millisievert"
        case 1413:
            return "Rem"
        case 1414:
            return "Coulomb pro Kilogramm"
        case 1415:
            return "Millicoulomb pro Kilogramm"
        case 1416:
            return "Röntgen"
        case 1417:
            return "Magnetische Energiedichte"
        case 1418:
            return ""
        case 1419:
            return "Kubikmeter pro Coulomb"
        case 1420:
            return "Volt pro Kelvin"
        case 1421:
            return "Millivolt pro Kelvin"
        case 1422:
            return "pH-Wert"
        case 1423:
            return "Teile pro Million"
        case 1424:
            return "Teile pro Milliarde"
        case 1425:
            return "Teile pro Billion"
        case 1426:
            return "Grad Brix"
        case 1427:
            return "Grad Balling"
        case 1428:
            return "Proof per volume"
        case 1429:
            return "Proof per mass"
        case 1430:
            return "Pfund pro Imperial Gallone"
        case 1431:
            return "Kilokalorie pro Sekunde"
        case 1432:
            return "Kilokalorie pro Minute"
        case 1433:
            return "Kilokalorie pro Stunde"
        case 1434:
            return "Kilokalorie pro Tag"
        case 1435:
            return "Megakalorie pro Sekunde"
        case 1436:
            return "Megakalorie pro Minute"
        case 1437:
            return "Megakalorie pro Tag"
        case 1438:
            return "Kilojoule pro Sekunde"
        case 1439:
            return "Kilojoule pro Minute"
        case 1440:
            return "Kilojoule pro Stunde"
        case 1441:
            return "Kilojoule pro Tag"
        case 1442:
            return "Megajoule pro Sekunde"
        case 1443:
            return "Megajoule pro Minute"
        case 1444:
            return "Megajoule pro Tag"
        case 1445:
            return "Britische thermische Einheit pro Sekunde"
        case 1446:
            return "Britische thermische Einheit pro Minute"
        case 1447:
            return "Britische thermische Einheit pro Tag"
        case 1448:
            return "Mikro US-Gallone pro Sekunde"
        case 1449:
            return "Milli US-Gallone pro Sekunde"
        case 1450:
            return "Kilo US-Gallone pro Sekunde"
        case 1451:
            return "Mega US-Gallone pro Sekunde"
        case 1452:
            return "Mikro US-Gallone pro Minute"
        case 1453:
            return "Milli US-Gallone pro Minute"
        case 1454:
            return "Kilo US-Gallone pro Minute"
        case 1455:
            return "Mega US-Gallone pro Minute"
        case 1456:
            return "Mikro US-Gallone pro Stunde"
        case 1457:
            return "Milli US-Gallone pro Stunde"
        case 1458:
            return "Kilo US-Gallone pro Stunde"
        case 1459:
            return "Mega US-Gallone pro Stunde"
        case 1460:
            return "Mikro US-Gallone pro Tag"
        case 1461:
            return "Milli US-Gallone pro Tag"
        case 1462:
            return "Kilo US-Gallone pro Tag"
        case 1463:
            return "Mikro Imperial Gallone pro Sekunde"
        case 1464:
            return "Milli Imperial Gallone pro Sekunde"
        case 1465:
            return "Kilo Imperial Gallone pro Sekunde"
        case 1466:
            return "Mega Imperial Gallone pro Sekunde"
        case 1467:
            return "Mikro Imperial Gallone pro Minute"
        case 1468:
            return "Milli Imperial Gallone pro Minute"
        case 1469:
            return "Kilo Imperial Gallone pro Minute"
        case 1470:
            return "Mega Imperial Gallone pro Minute"
        case 1471:
            return "Mikro Imperial Gallone pro Stunde"
        case 1472:
            return "Milli Imperial Gallone pro Stunde"
        case 1473:
            return "Kilo Imperial Gallone pro Stunde"
        case 1474:
            return "Mega Imperial Gallone pro Stunde"
        case 1475:
            return "Mikro Imperial Gallone pro Tag"
        case 1476:
            return "Milli Imperial Gallone pro Tag"
        case 1477:
            return "Kilo Imperial Gallone pro Tag"
        case 1478:
            return "Mega Imperial Gallone pro Tag"
        case 1479:
            return "Mikrobarrel pro Sekunde"
        case 1480:
            return "Millibarrel pro Sekunde"
        case 1481:
            return "Kilobarrel pro Sekunde"
        case 1482:
            return "Megabarrel pro Sekunde"
        case 1483:
            return "Mikrobarrel pro Minute"
        case 1484:
            return "Millibarrel pro Minute"
        case 1485:
            return "Kilobarrel pro Minute"
        case 1486:
            return "Megabarrel pro Minute"
        case 1487:
            return "Mikrobarrel pro Stunde"
        case 1488:
            return "Millibarrel pro Stunde"
        case 1489:
            return "Kilobarrel pro Stunde"
        case 1490:
            return "Megabarrel pro Stunde"
        case 1491:
            return "Mikrobarrel pro Tag"
        case 1492:
            return "Millibarrel pro Tag"
        case 1493:
            return "Kilobarrel pro Tag"
        case 1494:
            return "Megabarrel pro Tag"
        case 1495:
            return "Kubikmikrometer pro Sekunde"
        case 1496:
            return "Kubikmillimeter pro Sekunde"
        case 1497:
            return "Kubikkilometer pro Sekunde"
        case 1498:
            return "Kubikmegameter pro Sekunde"
        case 1499:
            return "Kubikmikrometer pro Minute"
        case 1500:
            return "Kubikmillimeter pro Minute"
        case 1501:
            return "Kubikkilometer pro Minute"
        case 1502:
            return "Kubikmegameter pro Minute"
        case 1503:
            return "Kubikmikrometer pro Stunde"
        case 1504:
            return "Kubikmillimeter pro Stunde"
        case 1505:
            return "Kubikkilometer pro Stunde"
        case 1506:
            return "Kubikmegameter pro Stunde"
        case 1507:
            return "Kubikmikrometer pro Tag"
        case 1508:
            return "Kubikmillimeter pro Tag"
        case 1509:
            return "Kubikkilometer pro Tag"
        case 1510:
            return "Kubikmegameter pro Tag"
        case 1511:
            return "Kubikzentimeter pro Sekunde"
        case 1512:
            return "Kubikzentimeter pro Minute"
        case 1513:
            return "Kubikzentimeter pro Stunde"
        case 1514:
            return "Kubikzentimeter pro Tag"
        case 1515:
            return "Kilokalorie pro Kilogramm"
        case 1516:
            return "Britische thermische Einheit pro Pfund"
        case 1517:
            return "Kiloliter"
        case 1518:
            return "Kiloliter pro Minute"
        case 1519:
            return "Kiloliter pro Stunde"
        case 1520:
            return "Kiloliter pro Tag"
        case 1551:
            return "Siemens pro Zentimeter"
        case 1552:
            return "Mikrosiemens pro Zentimeter"
        case 1553:
            return "Millisiemens pro Meter"
        case 1554:
            return "Mikrosiemens pro Meter"
        case 1555:
            return "Megaohm Zentimeter"
        case 1556:
            return "Kiloohm Zentimeter"
        case 1557:
            return "Gewichtprozent"
        case 1558:
            return "Milligramm pro Liter"
        case 1559:
            return "Mikogramm pro Liter"
        case 1560:
            return "-"
        case 1561:
            return "-"
        case 1562:
            return "Volumenprozent"
        case 1563:
            return "Milliliter pro Minute"
        case 1564:
            return "Milligramm pro Kubikzentimeter"
        case 1565:
            return "Milligramm pro Liter"
        case 1566:
            return "Milligramm pro Kubikmeter"
        case 1567:
            return "Karat"
        case 1568:
            return "Pfund (troy or apothecary)"
        case 1569:
            return "Unze (troy or apothecary)"
        case 1570:
            return "Unze (U.S. fluid)"
        case 1571:
            return "Kubikzentimeter"
        case 1572:
            return "acre foot"
        case 1573:
            return "Kubikmeter"
        case 1574:
            return "Liter"
        case 1575:
            return "Standard Kubikmeter"
        case 1576:
            return "Standard Liter"
        case 1577:
            return "Milliliter pro Sekunde"
        case 1578:
            return "Milliliter pro Stunde"
        case 1579:
            return "Milliliter pro Tag"
        case 1580:
            return "acre foot pro Sekunde"
        case 1581:
            return "acre foot pro Minute"
        case 1582:
            return "acre foot pro Stunde"
        case 1583:
            return "acre foot pro Tag"
        case 1584:
            return "Unze pro Sekunde"
        case 1585:
            return "Unze pro Minute"
        case 1586:
            return "Unze pro Stunde"
        case 1587:
            return "Unze pro Tag"
        case 1588:
            return "Standardkubikmeter pro Sekunde"
        case 1589:
            return "Standardkubikmeter pro Minute"
        case 1590:
            return "Standardkubikmeter pro Stunde"
        case 1591:
            return "Standardkubikmeter pro Tag"
        case 1592:
            return "Standardliter pro Sekunde"
        case 1593:
            return "Standardliter pro Minute"
        case 1594:
            return "Standardliter pro Stunde"
        case 1595:
            return "Standardliter pro Tag"
        case 1596:
            return "Standardkubikmeter pro Sekunde"
        case 1597:
            return "Standardkubikmeter pro Minute"
        case 1598:
            return "Standardkubikmeter pro Stunde"
        case 1599:
            return "Standardkubikmeter pro Tag"
        case 1600:
            return "Standardliter pro Sekunde"
        case 1601:
            return "Standardliter pro Minute"
        case 1602:
            return "Standardliter pro Stunde"
        case 1603:
            return "Standardliter pro Tag"
        case 1604:
            return "Standardkubikfuß pro Sekuknde"
        case 1605:
            return "Standardkubikfuß pro Tag"
        case 1606:
            return "Unze pro Sekunde"
        case 1607:
            return "Unze pro Minute"
        case 1608:
            return "Unze pro Stunde"
        case 1609:
            return "Unze pro Tag"
        case 1610:
            return "Pascal (absolut)"
        case 1611:
            return "Pascal (gauge)"
        case 1612:
            return "Gigapascal (absolut)"
        case 1613:
            return "Gigapascal (Gauge)"
        case 1614:
            return "Megapascal (absolut)"
        case 1615:
            return "Megapascal (Gauge)"
        case 1616:
            return "Kilopascal (absolut)"
        case 1617:
            return "Kilopascal (Gauge)"
        case 1618:
            return "Millipascal (absolut)"
        case 1619:
            return "Millipascal (Gauge)"
        case 1620:
            return "Micropascal (absolut)"
        case 1621:
            return "Micropascal (Gauge)"
        case 1622:
            return "Hektopascal (absolut)"
        case 1623:
            return "Hektopascal (Gauge)"
        case 1624:
            return ""
        case 1625:
            return ""
        case 1626:
            return ""
        case 1627:
            return ""
        case 1628:
            return "Standarddichte bei 4°C"
        case 1629:
            return "Standarddichte bei 15°C"
        case 1630:
            return "Standarddichte bei 20°C"
        case 1631:
            return "Metrische Pferdestärken"
        case 1632:
            return "Teile pro Billion"
        case 1633:
            return "Hektoliter pro Sekunde"
        case 1634:
            return "Hektoliter pro Minute"
        case 1635:
            return "Hektoliter pro Stunde"
        case 1636:
            return "Hektoliter pro Tag"
        case 1637:
            return "Barrel (US flüssig) pro Sekunde"
        case 1638:
            return "Barrel (US flüssig) pro Minute"
        case 1639:
            return "Barrel (US flüssig) pro Stunde"
        case 1640:
            return "Barrel (US flüssig) pro Tag"
        case 1641:
            return "Barrel (U.S. federal)"
        case 1642:
            return "Barrel (U.S. federal) pro Sekunde"
        case 1643:
            return "Barrel (U.S. federal) pro Minute"
        case 1644:
            return "Barrel (U.S. federal) pro Stunde"
        case 1645:
            return "Barrel (U.S. federal) pro Tag"
        case 1998:
            return "Maßeinheit nicht bekannt"
        case 1999:
            return "spezial"
        

### start main

mtps:list[Mtp] = []

# parse mtp files
for file in TESTMTPS:
    tree = parse(file)
    root = tree.getroot()

    # create mtp object
    mtp = Mtp()
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
                                if instNode.get("Name") == "InstanceList" or instNode.get("Name") == "Instances":
                                    continue
                                inst = Instance(name=instNode.get("Name"), id=instNode.get("ID"))

                                for attrNode in instNode.iter(f"{NAMESPACE}Attribute"):
                                    if attrNode.get("Name") == "RefID":
                                        inst.addRefId(attrNode.findtext(f"{NAMESPACE}Value"))
                                    elif attrNode.get("Name") == "VMin":
                                        inst.addMin(float(attrNode.findtext(f"{NAMESPACE}DefaultValue")))
                                    elif attrNode.get("Name") == "VMax":
                                        inst.addMax(float(attrNode.findtext(f"{NAMESPACE}DefaultValue")))
                                    elif attrNode.get("Name") == "VUnit":
                                        unitId = attrNode.findtext(f"{NAMESPACE}DefaultValue")
                                        inst.addUnit(getUnit(int(unitId)))

                                # add instance to mtp
                                mtp.addInstance(inst)
                        elif node.get("Name") == "SourceList" or node.get("Name") == "Sources":
                            # parse url
                            for c in node.find(f"{NAMESPACE}InternalElement"):
                                opcUrl = c.findtext(f"{NAMESPACE}Value")
                                if opcUrl == None:
                                    continue
                                else:
                                    mtp.addUrl(url=opcUrl)
                                    break

        elif child.tag == f"{NAMESPACE}InstanceHierarchy" and child.get("Name") == "Services":
            for gchild in child:
                if gchild.tag == f"{NAMESPACE}InternalElement":
                    servName = gchild.get("Name") # name of the service
                    servId = gchild.get("ID") # id of the service
                    procCount = 0 # number of procedures under service

                    # get procedures
                    for ggchild in gchild:
                        if ggchild.tag == f"{NAMESPACE}InternalElement":
                            procName = ggchild.get("Name") # name of the procedure
                            procId = ggchild.get("ID") # id of the procedure
                            proc = Procedure(name=procName, id=procId)
                            procCount += 1

                            # add the procedure to the mtp's procedures
                            mtp.addProcedure(proc)

                            for paramNode in ggchild:
                                if paramNode.tag == f"{NAMESPACE}InternalElement":
                                    for refNode in paramNode.iter(f"{NAMESPACE}Attribute"):
                                        if refNode.get("Name") == "RefID" and mtp.hasInstance(refNode.findtext(f"{NAMESPACE}Value")):
                                            # get the instance the procedure refers to 
                                            procParam = mtp.getInstance(refNode.findtext(f"{NAMESPACE}Value"))

                                            # add the instance to the procedure's params
                                            proc.addParameter(procParam)
                                elif paramNode.tag == f"{NAMESPACE}Attribute" and paramNode.get("Name") == "IsSelfCompleting":
                                    proc.setSelfCompleting(paramNode.findtext(f"{NAMESPACE}Value"))


                    if procCount == 0:
                        # no procedures, add the service instead
                        mtp.addProcedure(Procedure(name=servName, id=servId))

# for m in mtps:
#     print(m)
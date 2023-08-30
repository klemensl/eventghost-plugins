# -*- coding: utf-8 -*-

import eg
import httplib
import xml.etree.ElementTree as ET

eg.RegisterPlugin(
    name = "Homematic",
    author = "klemensl",
    version = "0.0.1a",
    kind = "other",
    description = "...."
)

class HMXMLAPI(eg.PluginBase):
    HM_XMLAPI_URL = "/config/xmlapi/"
    HM_XMLAPI_STATE = "state.cgi?datapoint_id={0}"
    HM_XMLAPI_STATECHANGE = "statechange.cgi?ise_id={0}&new_value={1}"
    HM_XMLRPC_SETVALUE_BODY = "<methodCall><methodName>setValue</methodName><params><param><value><string>{0}</string></value></param><param><value><string>{1}</string></value></param><param><value><string>{2}</string></value></param></params></methodCall>"
    HM_XMLRPC_PRESS_BODY =    "<methodCall><methodName>setValue</methodName><params><param><value><string>{0}</string></value></param><param><value><string>{1}</string></value></param><param><value><boolean>{2}</boolean></value></param></params></methodCall>"
    HM_XMLRPC_GETVALUE_BODY = "<methodCall><methodName>getValue</methodName><params><param><value><string>{0}</string></value></param><param><value><string>{1}</string></value></param></params></methodCall>"
    HM_XMLRPC_ONTIME_BODY = "<methodCall><methodName>setValue</methodName><params><param><value><string>{0}</string></value></param><param><value><string>ON_TIME</string></value></param><param><value><string>{1}</string></value></param></params></methodCall>"
    HM_XMLRPC_EVENT = "<methodCall><methodName>event</methodName><params><param><value><string>{0}</string></value></param><param><value><string>{1}</string></value></param><param><value><string>VALUE</string></value></param><param><value><i4>{2}</i4></value></param></params></methodCall>"

    def __init__(self):
        self.AddAction(sysvarlist)
        self.AddAction(statelist)
        self.AddAction(setValue)
        self.AddAction(turnOnOrOff)
        self.AddAction(setValueFromPayload)
        self.AddAction(callCGIfromPayload)
        self.AddAction(turnOnFromPayload)
        self.AddAction(turnOffFromPayload)
        self.AddAction(setValueXMLRPC)
        self.AddAction(getValueXMLRPC)
        self.AddAction(setDataPointXMLRPC)
        self.AddAction(setDataPointXMLRPCLumi)
        self.AddAction(getDataPointXMLRPC)
        self.AddAction(turnOnOrOffXMLRPC)
        self.AddAction(turnOnOrOffForXXMLRPC)
        self.AddAction(setStateFromAlexaEvent)

    def __start__(self, protocol, host, port):
        self.host = host
        print "Homematic XML API Plugin is started with parameter: " + self.host

    def Configure(self, protocol="HTTP", host="", port=80):
        panel = eg.ConfigPanel(self)
        protocolCtrl = panel.TextCtrl(protocol)
        hostCtrl = panel.TextCtrl(host)
        portCtrl = panel.SpinIntCtrl(port, min=1, max=65535)
        panel.sizer.AddMany([
            panel.StaticText("Protocol:"),
            protocolCtrl,
            panel.StaticText("Host:"),
            hostCtrl,
            panel.StaticText("Port:"),
            portCtrl,
        ])
        while panel.Affirmed():
            panel.SetResult(
                protocolCtrl.GetValue(),
                hostCtrl.GetValue(),
                portCtrl.GetValue()
            )

    def SendRequest(self, requestURL, requestPort=80, requestBody="", method="GET"):
        #print "sending request to: " + self.host + requestURL + " with body:" + requestBody
        conn = httplib.HTTPConnection(self.host, requestPort)
        conn.request(method, requestURL, requestBody)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        dataBody = data.partition('?>')[2]
        #print response.status, response.reason, dataBody
        #print "got response for " + requestURL
        eg.globals.ccu2xmlapiresponse = dataBody
        return dataBody

    def changeStateXMLAPI(self, ise_id, new_value):
        self.SendRequest(self.HM_XMLAPI_URL + self.HM_XMLAPI_STATECHANGE.format(ise_id, new_value).lower())
        responseBody = self.SendRequest(self.HM_XMLAPI_URL + self.HM_XMLAPI_STATE.format(ise_id).lower())
        datapoint = ET.fromstring(responseBody).find('datapoint')
        if datapoint is not None:
            datapointValue = datapoint.get('value')
        else:
            datapointValue = "unknown"
        eg.globals.ccu2statechangedto = datapointValue
        print "ise_id {0} changed to {1}".format(ise_id, datapointValue)
        return datapointValue

    def changeStateXMLRPC(self, device_id, new_value):
        self.SendRequest("/", 2001, self.HM_XMLRPC_SETVALUE_BODY.format(device_id, "STATE", new_value), "POST")
        valueAfterChange = self.getDataPointXMLRPC(device_id, "STATE")
        print "device_id {0} datapoint STATE changed to {1} (actual {2})".format(device_id, new_value, valueAfterChange)
        return valueAfterChange

    def setDataPointXMLRPC(self, device_id, datapoint_name, new_value):
        if (datapoint_name == 'PRESS_SHORT') or (datapoint_name == 'PRESS_LONG'):
            print self.HM_XMLRPC_PRESS_BODY.format(device_id, datapoint_name, new_value)
            self.SendRequest("/", 2001, self.HM_XMLRPC_PRESS_BODY.format(device_id, datapoint_name, new_value), "POST")
        else:
            self.SendRequest("/", 2001, self.HM_XMLRPC_SETVALUE_BODY.format(device_id, datapoint_name, new_value), "POST")
        return self.getDataPointXMLRPC(device_id, datapoint_name)

    def getDataPointXMLRPC(self, device_id, datapoint_name):
        responseBody = self.SendRequest("/", 2001, self.HM_XMLRPC_GETVALUE_BODY.format(device_id, datapoint_name), "POST")
        datapointXML = ET.fromstring(responseBody).find('.//value/*')
        if datapointXML is not None:
            datapointValue = datapointXML.text
            if (datapointXML.tag == "boolean"):
                if (datapointValue == "1"):
                    datapointValue = "true"
                else:
                    datapointValue = "false"
        else:
            datapointValue = "unknown"
        eg.globals.ccu2statechangedto = datapointValue
        print "device_id {0} datapoint {1} is {2}".format(device_id, datapoint_name, datapointValue)
        return datapointValue

##########################
# XML-API
class sysvarlist(eg.ActionBase):
    name = "CCU2 XML-API: sysVarList.cgi"

    def __call__(self):
        #print "Action 'SysVarList'"
        data = self.plugin.SendRequest(self.plugin.HM_XMLAPI_URL + "sysvarlist.cgi")
        eg.globals.ccu2statechangedto = ""


class statelist(eg.ActionBase):
    name = "CCU2 XML-API: stateList.cgi"

    def __call__(self):
        #print "Action 'StateList'"
        self.plugin.SendRequest(self.plugin.HM_XMLAPI_URL + "statelist.cgi")
        eg.globals.ccu2statechangedto = ""


class turnOnOrOff(eg.ActionBase):
    name = "CCU2 XML-API: turnOnOrOff"

    def __call__(self, ise_id, new_value):
        #print "Action 'Statechange' - ID: {0}={1}".format(ise_id, new_value)
        self.plugin.changeStateXMLAPI(ise_id, new_value)

    def GetLabel(self, ise_id, new_value):
        return "Change state of ise_id {0} to {1}".format(ise_id, new_value)

    def Configure(self, ise_id="", new_value=True):
        panel = eg.ConfigPanel(self)
        ise_idCtrl = panel.TextCtrl(ise_id)
        new_valueCtrl = panel.CheckBox(new_value)
        panel.AddLine(panel.StaticText("ise_id:"), ise_idCtrl)
        panel.AddLine(panel.StaticText("ON/OFF:"), new_valueCtrl)
        while panel.Affirmed():
            panel.SetResult(
                ise_idCtrl.GetValue(),
                new_valueCtrl.GetValue()
            )


class setValue(eg.ActionBase):
    name = "CCU2 XML-API: setValue (STATE)"

    def __call__(self, ise_id, new_value):
        #print "Action 'Statechange' - ID: {0}={1}".format(ise_id, new_value)
        self.plugin.changeStateXMLAPI(ise_id, new_value)

    def GetLabel(self, ise_id, new_value):
        return "Set the value of ise_id {0} to {1}".format(ise_id, new_value)

    def Configure(self, ise_id="", new_value=""):
        panel = eg.ConfigPanel(self)
        ise_idCtrl = panel.TextCtrl(ise_id)
        new_valueCtrl = panel.TextCtrl(new_value)
        panel.AddLine(panel.StaticText("ise_id:"), ise_idCtrl)
        panel.AddLine(panel.StaticText("Value:"), new_valueCtrl)
        while panel.Affirmed():
            panel.SetResult(
                ise_idCtrl.GetValue(),
                new_valueCtrl.GetValue()
            )


class setValueFromPayload(eg.ActionBase):
    name = "CCU2 XML-API: SetValue from Event Payload"

    def __call__(self, ise_id):
        if not eg.event.payload:
            print "No payload set - skipping..."
            return False
        new_value = eg.event.payload[0]
        #print "Action 'Statechange' - ID: {0}={1}".format(ise_id, new_value)
        self.plugin.changeStateXMLAPI(ise_id, new_value)

    def GetLabel(self, ise_id, new_value):
        return "Set the value of ise_id {0} to 'eg.event.payload[0]'".format(ise_id)

    def Configure(self, ise_id=""):
        panel = eg.ConfigPanel(self)
        ise_idCtrl = panel.TextCtrl(ise_id)
        panel.AddLine(panel.StaticText("ise_id:"), ise_idCtrl)
        while panel.Affirmed():
            panel.SetResult(
                ise_idCtrl.GetValue()
        )


class callCGIfromPayload(eg.ActionBase):
    name = "CCU2 XML-API: Call CGI from Event Payload"
    description = "Call the CCU2 XML API .CGI with the Payload of the current event -> http://IP/config/xmlapi/eg.event.payload[0].cgi"

    def __call__(self):
        if not eg.event.payload:
            print "No payload set - skipping..."
            return False
        #print "Action 'From Payload' - Payload: " + eg.event.payload[0]
        self.plugin.SendRequest(self.plugin.HM_XMLAPI_URL + eg.event.payload[0] + ".cgi")

class turnOnFromPayload(eg.ActionBase):
    name = "CCU2 XML-API: Turn ise_id 'eg.event.payload[0]' ON"
    description = ""

    def __call__(self):
        if not eg.event.payload:
            print "No payload set - skipping..."
            return False
        ise_id = eg.event.payload[0]
        #print "Action 'Turn ON from Payload' - Payload: " + ise_id
        self.plugin.changeStateXMLAPI(ise_id, "true")


class turnOffFromPayload(eg.ActionBase):
    name = "CCU2 XML-API: Turn ise_id 'eg.event.payload[0]' OFF"
    description = ""

    def __call__(self):
        if not eg.event.payload:
            print "No payload set - skipping..."
            return False
        ise_id = eg.event.payload[0]
        #print "Action 'Turn OFF from Payload' - Payload: " + ise_id
        self.plugin.changeStateXMLAPI(ise_id, "false")

#################################
# XML-RPC

class turnOnOrOffXMLRPC(eg.ActionBase):
    name = "CCU2 XML-RPC: turn ON or OFF"

    def __call__(self, device_id, new_value):
        #print "Action 'setValue STATE XML-RPC' - Device-ID: {0}={1}".format(device_id, new_value)
        self.plugin.changeStateXMLRPC(device_id, str(new_value).lower())

    def GetLabel(self, device_id, new_value):
        return "setValue STATE of Device-ID {0} to {1}".format(device_id, new_value)

def Configure(self, device_id="", new_value=True):
    panel = eg.ConfigPanel(self)
    device_idCtrl = panel.TextCtrl(device_id)
    new_valueCtrl = panel.CheckBox(new_value)
    panel.AddLine(panel.StaticText("Device-ID:"), device_idCtrl)
    panel.AddLine(panel.StaticText("ON/OFF:"), new_valueCtrl)
    while panel.Affirmed():
        panel.SetResult(
            device_idCtrl.GetValue(),
            new_valueCtrl.GetValue()
        )


class turnOnOrOffForXXMLRPC(eg.ActionBase):
    name = "CCU2 XML-RPC: turn ON or OFF for X Seconds"

    def __call__(self, device_id, new_value, seconds):
        #print "Action 'setValue STATE XML-RPC' - Device-ID: {0}={1} for {2} seconds".format(device_id, new_value, seconds)
        self.plugin.SendRequest("/", 2001, self.plugin.HM_XMLRPC_ONTIME_BODY.format(device_id, seconds), "POST")
        self.plugin.changeStateXMLRPC(device_id, str(new_value).lower())

    def GetLabel(self, device_id, new_value, seconds):
        return "setValue STATE of Device-ID {0} to {1} for {2} seconds".format(device_id, new_value, seconds)

    def Configure(self, device_id="", new_value=True, seconds=60):
        panel = eg.ConfigPanel(self)
        device_idCtrl = panel.TextCtrl(device_id)
        new_valueCtrl = panel.CheckBox(new_value)
        secondsCtrl = panel.SpinIntCtrl(seconds)
        panel.AddLine(panel.StaticText("Device-ID:"), device_idCtrl)
        panel.AddLine(panel.StaticText("ON/OFF:"), new_valueCtrl)
        panel.AddLine(panel.StaticText("Seconds:"), secondsCtrl)
        while panel.Affirmed():
            panel.SetResult(
                device_idCtrl.GetValue(),
                new_valueCtrl.GetValue(),
                secondsCtrl.GetValue()
            )


class setValueXMLRPC(eg.ActionBase):
    name = "CCU2 XML-RPC: setValue (STATE)"

    def __call__(self, device_id, new_value):
        #print "Action 'setValue STATE XML-RPC' - Device-ID: {0}={1}".format(device_id, new_value)
        self.plugin.changeStateXMLRPC(device_id, new_value)

    def GetLabel(self, device_id, new_value):
        return "setValue STATE of Device-ID {0} to {1}".format(device_id, new_value)

    def Configure(self, device_id="", new_value=""):
        panel = eg.ConfigPanel(self)
        device_idCtrl = panel.TextCtrl(device_id)
        new_valueCtrl = panel.TextCtrl(new_value)
        panel.AddLine(panel.StaticText("Device-ID:"), device_idCtrl)
        panel.AddLine(panel.StaticText("Value:"), new_valueCtrl)
        while panel.Affirmed():
            panel.SetResult(
                device_idCtrl.GetValue(),
                new_valueCtrl.GetValue()
            )


class getValueXMLRPC(eg.ActionBase):
    name = "CCU2 XML-RPC: getValue (STATE)"

    def __call__(self, device_id):
        #print "Action 'getValue STATE XML-RPC' - Device-ID: {0}".format(device_id)
        return self.plugin.getDataPointXMLRPC(device_id, "STATE")

    def GetLabel(self, device_id):
        return "getValue STATE of Device-ID {0}".format(device_id)

    def Configure(self, device_id=""):
        panel = eg.ConfigPanel(self)
        device_idCtrl = panel.TextCtrl(device_id)
        panel.AddLine(panel.StaticText("Device-ID:"), device_idCtrl)
        while panel.Affirmed():
            panel.SetResult(
                device_idCtrl.GetValue()
            )


class setDataPointXMLRPC(eg.ActionBase):
    name = "CCU2 XML-RPC: setDataPoint"

    def __call__(self, device_id, datapoint_name, new_value, check_inhibit):
        #print "Action 'setDataPoint {1} XML-RPC' - Device-ID: {0} to {2}".format(device_id, datapoint_name, new_value)
        inhibit = "False"
        if check_inhibit:
            inhibit = self.plugin.getDataPointXMLRPC(device_id, "INHIBIT")
        
        if inhibit.lower() != "true":
            return self.plugin.setDataPointXMLRPC(device_id, datapoint_name, new_value)
        else:
            print "Skip because of INHIBIT"
            return "false"

    def GetLabel(self, device_id, datapoint_name, new_value, check_inhibit):
        return "setDataPoint {1} of Device-ID {0} to {2} (check inhibit: {3})".format(device_id, datapoint_name, new_value, check_inhibit)

    def Configure(self, device_id="", datapoint_name="STATE", new_value="", check_inhibit=False):
        panel = eg.ConfigPanel(self)
        device_idCtrl = panel.TextCtrl(device_id)
        dataPointCtrl = wx.ComboBox(panel, -1, value="STATE", choices=['STATE', 'WORKING', 'LEVEL','INHIBIT','PRESS_SHORT','PRESS_LONG'], style=wx.CB_DROPDOWN)
        new_valueCtrl = panel.TextCtrl(new_value)
        check_inhibitCtrl = panel.CheckBox(check_inhibit)

        panel.AddLine(panel.StaticText("Device-ID:"), device_idCtrl)
        panel.AddLine(panel.StaticText("Datapoint:"), dataPointCtrl)
        panel.AddLine(panel.StaticText("Value:"), new_valueCtrl)
        panel.AddLine(panel.StaticText("Check Inhibit First:"), check_inhibitCtrl)
        while panel.Affirmed():
            panel.SetResult(
                device_idCtrl.GetValue(),
                dataPointCtrl.GetValue(),
                new_valueCtrl.GetValue(),
                check_inhibitCtrl.GetValue()
            )

class setDataPointXMLRPCLumi(eg.ActionBase):
    name = "CCU2 XML-RPC: setDataPoint with Lumi"

    def __call__(self, device_id, datapoint_name, new_value, check_inhibit, minLux, maxLux):
        #print "Action 'setDataPoint {1} XML-RPC' - Device-ID: {0} to {2}".format(device_id, datapoint_name, new_value)
        inhibit = "False"
        if check_inhibit:
            inhibit = self.plugin.getDataPointXMLRPC(device_id, "INHIBIT")
        
        print "lumi_lux {0} , minLux {1} , maxLux {2}".format(eg.globals.lumi_lux, minLux, maxLux)

        if inhibit.lower() != "true" and eg.globals.lumi_lux > int(minLux) and  eg.globals.lumi_lux < int(maxLux):
            return self.plugin.setDataPointXMLRPC(device_id, datapoint_name, new_value)
        else:
            print "Skip because of INHIBIT or lumi"
            return "false"

    def GetLabel(self, device_id, datapoint_name, new_value, check_inhibit, minLux, maxLux):
        return "setDataPoint {1} of Device-ID {0} to {2} (check inhibit: {3})".format(device_id, datapoint_name, new_value, check_inhibit)

    def Configure(self, device_id="", datapoint_name="STATE", new_value="", check_inhibit=False, minLux="0", maxLux="100000"):
        panel = eg.ConfigPanel(self)
        device_idCtrl = panel.TextCtrl(device_id)
        dataPointCtrl = wx.ComboBox(panel, -1, value="STATE", choices=['STATE', 'WORKING', 'LEVEL','INHIBIT','PRESS_SHORT','PRESS_LONG'], style=wx.CB_DROPDOWN)
        new_valueCtrl = panel.TextCtrl(new_value)
        check_inhibitCtrl = panel.CheckBox(check_inhibit)
        minLuxCtrl = panel.TextCtrl(minLux)
        maxLuxCtrl = panel.TextCtrl(maxLux)

        panel.AddLine(panel.StaticText("Device-ID:"), device_idCtrl)
        panel.AddLine(panel.StaticText("Datapoint:"), dataPointCtrl)
        panel.AddLine(panel.StaticText("Value:"), new_valueCtrl)
        panel.AddLine(panel.StaticText("Check Inhibit First:"), check_inhibitCtrl)
        panel.AddLine(panel.StaticText("Min Lux"), minLuxCtrl)
        panel.AddLine(panel.StaticText("Max Lux"), maxLuxCtrl)
        while panel.Affirmed():
            panel.SetResult(
                device_idCtrl.GetValue(),
                dataPointCtrl.GetValue(),
                new_valueCtrl.GetValue(),
                check_inhibitCtrl.GetValue(),
                minLuxCtrl.GetValue(),
                maxLuxCtrl.GetValue()
            )

class setLevelXMLRPC(eg.ActionBase):
    name = "CCU2 XML-RPC: setLevel"

    def __call__(self, device_id, datapoint_name, new_value, check_inhibit, aboveLevel, belowLevel):
        #print "Action 'setDataPoint {1} XML-RPC' - Device-ID: {0} to {2}".format(device_id, datapoint_name, new_value)
        inhibit = "False"
        if check_inhibit:
            inhibit = self.plugin.getDataPointXMLRPC(device_id, "INHIBIT")
        
        levelInRange = 1
        if aboveLevel != "" or belowLevel != "":
            level = self.plugin.getDataPointXMLRPC(device_id, "LEVEL")
            
            above = 1
            if aboveLevel != "" and aboveLevel < level:
                above = 0
            
            below = 1
            if belowLevel != "" and belowLevel > level:
                below = 0

            if below == 0 or above == 0:
                levelInRange = 0
        
        if inhibit.lower() != "true" and levelInRange == 1:
            return self.plugin.setDataPointXMLRPC(device_id, "LEVEL", new_value)
        else:
            print "Skip because of INHIBIT ({1}) or level not in range ({2})".format(inhibit, levelInRange)
            return "false"

    def GetLabel(self, device_id, datapoint_name, new_value, check_inhibit, aboveLevel, belowLevel):
        return "setDataPoint {1} of Device-ID {0} to {2} (check inhibit: {3})".format(device_id, datapoint_name, new_value, check_inhibit)

    def Configure(self, device_id="", new_value="", check_inhibit=False, aboveLevel="", belowLevel=""):
        panel = eg.ConfigPanel(self)
        device_idCtrl = panel.TextCtrl(device_id)
        new_valueCtrl = panel.TextCtrl(new_value)
        check_inhibitCtrl = panel.CheckBox(check_inhibit)
        aboveLevelCtrl = panel.TextCtrl(aboveLevel)
        belowLevelCtrl = panel.TextCtrl(belowLevel)

        panel.AddLine(panel.StaticText("Device-ID:"), device_idCtrl)
        panel.AddLine(panel.StaticText("Datapoint:"), dataPointCtrl)
        panel.AddLine(panel.StaticText("Value:"), new_valueCtrl)
        panel.AddLine(panel.StaticText("Check Inhibit First:"), check_inhibitCtrl)
        panel.AddLine(panel.StaticText("Above Level"), aboveLevelCtrl)
        panel.AddLine(panel.StaticText("Below Level"), belowLevelCtrl)
        while panel.Affirmed():
            panel.SetResult(
                device_idCtrl.GetValue(),
                dataPointCtrl.GetValue(),
                new_valueCtrl.GetValue(),
                check_inhibitCtrl.GetValue(),
                aboveLevelCtrl.GetValue(),
                belowLevelCtrl.GetValue()
            )


class getDataPointXMLRPC(eg.ActionBase):
    name = "CCU2 XML-RPC: getDataPoint"

    def __call__(self, device_id, datapoint_name):
        #print "Action 'getDataPoint {1} XML-RPC' - Device-ID: {0}".format(device_id, datapoint_name)
        return self.plugin.getDataPointXMLRPC(device_id, datapoint_name)

    def GetLabel(self, device_id, datapoint_name):
        return "getDataPoint {1} of Device-ID {0}".format(device_id, datapoint_name)

    def Configure(self, device_id="", datapoint_name="STATE"):
        panel = eg.ConfigPanel(self)
        device_idCtrl = panel.TextCtrl(device_id)
        dataPointCtrl = wx.ComboBox(panel, -1, value="STATE", choices=['STATE', 'WORKING', 'LEVEL','INHIBIT'], style=wx.CB_DROPDOWN)
        panel.AddLine(panel.StaticText("Device-ID:"), device_idCtrl)
        panel.AddLine(panel.StaticText("Datapoint:"), dataPointCtrl)
        while panel.Affirmed():
            panel.SetResult(
                device_idCtrl.GetValue(),
                dataPointCtrl.GetValue()
            )

class setStateFromAlexaEvent(eg.ActionBase):
    name = "CCU2 XML-RPC: setStateFromAlexaEvent"
    description = ""

    def __init__(self):
        self.deviceIDMapping = {"esszimmer": "LEQ0883366:1", "kueche": "KEQ0926487:1", u"küche": "KEQ0926487:1", "stiege": "LEQ0236800:1", "gang": "LEQ0236800:2"}
        self.valueMapping = {"einschalten": "1", "ausschalten": "0", "turnonrequest": "1", "turnoffrequest": "0"}

    def __call__(self):
        if not eg.event.payload:
            print "No payload set - skipping..."
            return False

        aktion = eg.event.payload[0]
        aktion_lower = aktion.lower()
        device_id = eg.event.payload[1]
        device_id_lower = device_id.lower()

        if device_id_lower in self.deviceIDMapping:
            device_id = self.deviceIDMapping[device_id_lower]

        if aktion_lower in self.valueMapping:
            new_value = aktion
            new_value_lower = aktion_lower

            if new_value_lower in self.valueMapping:
                new_value = self.valueMapping[new_value_lower]

            self.plugin.changeStateXMLRPC(device_id, new_value)
        elif aktion_lower == "setpercentagerequest":
            new_value = eg.event.payload[2] / 100

            self.plugin.setDataPointXMLRPC(device_id, "LEVEL", new_value)
        else:
            print "unknown..."

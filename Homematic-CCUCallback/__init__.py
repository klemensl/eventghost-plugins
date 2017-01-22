import eg
import xml.etree.ElementTree as ET
import httplib
import time
from datetime import datetime
from threading import Thread
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


class CCUCallbackHandler(BaseHTTPRequestHandler):
    #Handler for the GET requests
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        # Send the html message
        self.wfile.write("Do not use GET")
        return

    #Handler for the POST requests
    def do_POST(self):
        contentLength = int(self.headers.get('content-length'))
        content = self.rfile.read(contentLength)

        root = ET.fromstring(content)
        method = root.find('.//methodName')
        if method is None:
            print "ERROR"
        elif method.text == 'listDevices':
            print "listDevices - Not Yet Implemented"
        elif method.text == 'event':
            paramValues = []
            params = root.find('.//params') #/param
            for param in params.getchildren():
                paramValues.append(param[0][0].text)

            ccuEvent = CCUEvent(paramValues)
            if ccuEvent.datapointName not in self.server.doNotTrigger:
                eg.TriggerEvent("{0}-{1}:{2}".format(ccuEvent.deviceID, ccuEvent.datapointName, ccuEvent.datapointValue), None, "CCU")
        elif method.text == 'system.multicall':
            calls = []
            dataArray = root.find('.//params/param/value/array/data')
            for data in dataArray.getchildren():
                calls.append(data)

            for call in calls:
                valueArray = call.find('.//value/array/data') #/value

                paramValues = []
                for value in valueArray.getchildren():
                    if len(value.getchildren()) == 0:
                        paramValues.append(value.text)
                    else:
                        paramValues.append(value[0].text)

                ccuEvent = CCUEvent(paramValues)
                if ccuEvent.datapointName not in self.server.doNotTrigger:
                    eg.TriggerEvent("{0}-{1}:{2}".format(ccuEvent.deviceID, ccuEvent.datapointName, ccuEvent.datapointValue), None, "CCU")
        else:
            print "UNKNOWN: ", method

        response = "<Status>OK</Status>"

        self.send_response(200)
        self.send_header("Content-type", 'application/xml; charset=UTF-8')
        self.send_header("Content-Length", len(response))
        self.end_headers()
        self.wfile.write(response.encode("UTF-8"))
        self.wfile.close()

    def log_message(self, format, *args):
        # suppress all messages
        pass


class ServerThread(Thread):

    def __init__(self, port, requestHandler):
        Thread.__init__(self, name="CCU Callback Server Thread")
        self.port = port
        self.server = HTTPServer(('', port), requestHandler)
        self.server.doNotTrigger = ['FREQUENCY', 'POWER', 'VOLTAGE', 'CURRENT', 'BOOT', 'ENERGY_COUNTER']

    def run(self):
        # send INIT to CCU
        print "Started CCU Callback Server on port ", self.port
    	self.server.serve_forever()


class CCUEvent:

    def __init__(self, valueArray):
        self.deviceID = valueArray[1] if len(valueArray) >= 1 else "NONE"
        self.datapointName = valueArray[2] if len(valueArray) >= 2 else "NONE"
        self.datapointValue = valueArray[3] if len(valueArray) >= 3 else "NONE"
        self.triggerd = datetime.now()
        self.enabled = True


eg.RegisterPlugin(
    name = "Homematic-CCUCallback",
    author = "klemensl",
    version = "0.0.1",
    kind = "other",
    description = "..."
)

class HMCCUCallback(eg.PluginBase):

    def __init__(self):
        print "Plugin init"

    def __start__(self, ccuProtocol, ccuHost, ccuPort, callbackPort):
        #print "Start Callback Server Thread"
        self.serverThread = ServerThread(callbackPort, CCUCallbackHandler)
        self.serverThread.start()

        """time.sleep(5)
        print "send INIT to CCU"
        #conn = httplib.HTTPConnection("192.168.1.104", 2001)
        conn = httplib.HTTPConnection("requestb.in", 80)
        conn.request("POST", "/vb71r2vb", "<methodCall>\
<methodName>init</methodName>\
<params>\
<param><value><string>http://192.168.1.91:8888</string></value></param>\
<param><value><string>654321</string></value></param>\
</params>\
</methodCall>", {"Content-type": "text/xml"})
        response = conn.getresponse()
        data = response.read()
        conn.close()
        print "DEBUG", response.status, response.reason
        print data"""

    def Configure(self, ccuProtocol="HTTP", ccuHost="192.168.1.104", ccuPort=2001, callbackPort=8888):
        panel = eg.ConfigPanel(self)

        # server config
        ccuProtocolCtrl = panel.TextCtrl(ccuProtocol)
        ccuHostCtrl = panel.TextCtrl(ccuHost)
        ccuPortCtrl = panel.SpinIntCtrl(ccuPort, min=1, max=65535)

        # callback server config
        callbackPortCtrl = panel.SpinIntCtrl(callbackPort, min=1, max=65535)

        acv = wx.ALIGN_CENTER_VERTICAL
        serverSizer = wx.GridBagSizer(5, 10)
        serverSizer.Add(panel.StaticText("Homematic Server:"), (0,0))
        serverSizer.Add(ccuProtocolCtrl, (0,1))
        serverSizer.Add(ccuHostCtrl, (0,2))
        serverSizer.Add(ccuPortCtrl, (0,3))
        serverSizer.Add(panel.StaticText("Callback Server:"), (1,0))
        serverSizer.Add(callbackPortCtrl, (1,1))


        # event list
        eventListSizer = wx.GridBagSizer(2, 1)
        eventListSizer.AddGrowableRow(0)
        eventListSizer.AddGrowableCol(1)

        eventListCtrl = wx.ListCtrl(
            panel,
            -1,
            style=wx.LC_REPORT | wx.VSCROLL | wx.HSCROLL
        )
        eventListCtrl.InsertColumn(0, "Device ID")
        eventListCtrl.InsertColumn(1, "Datapoint")
        eventListCtrl.InsertColumn(2, "Last Value")
        eventListCtrl.InsertColumn(3, "Last Triggered")
        eventListCtrl.InsertColumn(4, "Enabled")
        eventListCtrl.DeleteAllItems()

        eventListSizer.Add(eventListCtrl, (0,0), (1,3), flag = wx.EXPAND)


        panel.sizer.Add(serverSizer, 1, flag = wx.EXPAND)
        panel.sizer.Add(panel.StaticText("Events"))
        panel.sizer.Add(eventListSizer, 1, flag = wx.EXPAND)

        while panel.Affirmed():
            panel.SetResult(
                ccuProtocolCtrl.GetValue(),
                ccuHostCtrl.GetValue(),
                ccuPortCtrl.GetValue(),
                callbackPortCtrl.GetValue()
            )

    def __stop__(self):
        #self.serverThread.exit()
        print "Action 'stop'"

    def __close__(self):
        print "Action 'close'"

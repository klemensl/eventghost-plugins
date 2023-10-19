# -*- coding: utf-8 -*-
from thread import start_new_thread
import eg
import httplib
import xml.etree.ElementTree as ET
import urllib

eg.RegisterPlugin(
    name = "HTTP Relay",
    author = "klemensl",
    version = "0.0.2",
    kind = "other",
    description = "..."
)

class HTTPRelay(eg.PluginBase):

    def __init__(self):
        self.AddAction(sendGETRequest)
        self.AddAction(sendPOSTRequestWithBody)

    def __start__(self):
        print "HTTPRelay Plugin started"

    def Configure(self):
        panel = eg.ConfigPanel(self)
        while panel.Affirmed():
            panel.SetResult()

    def SendGETRequest(self, protocol, host, port, request):
        print "sending request to: {0}:{1}{2}".format(host, port, request)
        conn = httplib.HTTPConnection(host, port)
        conn.request("GET", request)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        if '?>' in data:
            dataBody = data.partition('?>')[2]
        else:
            dataBody = data
        print "DEBUG", response.status, response.reason

        try:
            unicode(dataBody, "ascii")
        except UnicodeError:
            dataBody = unicode(dataBody, "latin1")
        else:
            # value was valid ASCII data
            pass

        return dataBody
    
    def SendGETRequestAsync(self, protocol, host, port, request):
        start_new_thread(self.SendGETRequest,(protocol, host, port, request,))
        return ""
        
    def SendPOSTRequest(self, protocol, host, port, request, body=None, headers=None):
        print "sending request to: {0}:{1}{2}".format(host, port, request)
        conn = httplib.HTTPConnection(host, port)
        conn.request("POST", request, body, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        if '?>' in data:
            dataBody = data.partition('?>')[2]
        else:
            dataBody = data
        print "DEBUG", response.status, response.reason

        try:
            unicode(dataBody, "ascii")
        except UnicodeError:
            dataBody = unicode(dataBody, "latin1")
        else:
            # value was valid ASCII data
            pass

        return dataBody

class sendGETRequest(eg.ActionBase):
    def __call__(self, protocol, host, port, request, async):
        #request = request.encode('utf-8')
        if async:
            eg.globals.httprelayresponse = self.plugin.SendGETRequestAsync(protocol, host, port, request)
        else:
            eg.globals.httprelayresponse = self.plugin.SendGETRequest(protocol, host, port, request)

    def GetLabel(self, protocol, host, port, request, async):
        return "Send a GET (async: {4}) request to: {0}://{1}:{2}{3}".format(protocol, host, port, request, async)

    def Configure(self, protocol="http", host="192.168.1.101", port=8000, request="", async=False):
        panel = eg.ConfigPanel(self)
        protocolCtrl = panel.TextCtrl(protocol)
        hostCtrl = panel.TextCtrl(host)
        portCtrl = panel.SpinIntCtrl(port, min=1, max=65535)
        requestCtrl = panel.TextCtrl(request)
        asyncCtrl = panel.CheckBox(async)
        panel.sizer.AddMany([
            panel.StaticText("Protocol:"),
            protocolCtrl,
            panel.StaticText("Host:"),
            hostCtrl,
            panel.StaticText("Port:"),
            portCtrl,
            panel.StaticText("Request:"),
            requestCtrl,
            panel.StaticText("Async:"),
            asyncCtrl,
        ])
        while panel.Affirmed():
            panel.SetResult(
                protocolCtrl.GetValue(),
                hostCtrl.GetValue(),
                portCtrl.GetValue(),
                requestCtrl.GetValue(),
                asyncCtrl.GetValue(),
            )

class sendPOSTRequestWithBody(eg.ActionBase):
    def __call__(self, protocol, host, port, request, headers, body):
        #request = request.encode('utf-8')
        headerMap = {}
        headerList = headers.split(',')
        for header in headerList:
            headerMap[header.split(":", 1)[0]] = header.split(":", 1)[1]

        #headers = {"Content-type": "text/xml"}
        print headerMap
        eg.globals.httprelayresponse = self.plugin.SendPOSTRequest(protocol, host, port, request, body, headerMap)

    def GetLabel(self, protocol, host, port, request, headers, body):
        return "Send a POST request with body to: {0}://{1}:{2}{3}".format(protocol, host, port, request)

    def Configure(self, protocol="http", host="192.168.1.101", port=8000, request="", headers="Content-type:text/xml", body=""):
        panel = eg.ConfigPanel(self)
        protocolCtrl = panel.TextCtrl(protocol)
        hostCtrl = panel.TextCtrl(host)
        portCtrl = panel.SpinIntCtrl(port, min=1, max=65535)
        requestCtrl = panel.TextCtrl(request)
        headersCtrl = panel.TextCtrl(headers)
        bodyCtrl = panel.TextCtrl(body, style=wx.TE_MULTILINE)
        panel.sizer.AddMany([
            panel.StaticText("Protocol:"),
            protocolCtrl,
            panel.StaticText("Host:"),
            hostCtrl,
            panel.StaticText("Port:"),
            portCtrl,
            panel.StaticText("Request:"),
            requestCtrl,
            panel.StaticText("Headers:"),
            headersCtrl,
            panel.StaticText("Body:"),
            bodyCtrl,
        ])
        while panel.Affirmed():
            panel.SetResult(
                protocolCtrl.GetValue(),
                hostCtrl.GetValue(),
                portCtrl.GetValue(),
                requestCtrl.GetValue(),
                headersCtrl.GetValue(),
                bodyCtrl.GetValue(),
            )

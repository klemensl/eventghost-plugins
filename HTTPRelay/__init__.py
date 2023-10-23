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
        self.AddAction(sendPOSTPUTRequestWithBody)

    def __start__(self):
        print "HTTPRelay Plugin started"

    def Configure(self):
        panel = eg.ConfigPanel(self)
        while panel.Affirmed():
            panel.SetResult()

    def SendGETRequest(self, protocol, host, port, request, https=False):
        print "sending request to: {0}:{1}{2}".format(host, port, request)
        if https:
            conn = httplib.HTTPSConnection(host, port)
        else:
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
        return self.SendPOSTPUTRequest(self, protocol, host, port, "POST", request, body, headers)
    
    def SendPUTRequest(self, protocol, host, port, request, body=None, headers=None):
        return self.SendPOSTPUTRequest(self, protocol, host, port, "POST", request, body, headers)
    
    def SendPOSTPUTRequest(self, protocol, host, port, request, method, body=None, headers=None, https=False):
        print "sending request to: {0}:{1}{2}".format(host, port, request)
        if https:
            conn = httplib.HTTPSConnection(host, port)
        else:
            conn = httplib.HTTPConnection(host, port)
        conn.request(method, request, body, headers)
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
    def __call__(self, protocol, host, port, request, doAsync):
        #request = request.encode('utf-8')
        if doAsync:
            eg.globals.httprelayresponse = self.plugin.SendGETRequestAsync(protocol, host, port, request)
        else:
            eg.globals.httprelayresponse = self.plugin.SendGETRequest(protocol, host, port, request)

    def GetLabel(self, protocol, host, port, request, doAsync, useSSL):
        return "Send a GET (async: {4}, useSSL: {5}) request to: {0}://{1}:{2}{3}".format(protocol, host, port, request, doAsync, useSSL)

    def Configure(self, protocol="http", host="192.168.1.101", port=8000, request="", doAsync=False, useSSL=False):
        panel = eg.ConfigPanel(self)
        protocolCtrl = panel.TextCtrl(protocol)
        hostCtrl = panel.TextCtrl(host)
        portCtrl = panel.SpinIntCtrl(port, min=1, max=65535)
        requestCtrl = panel.TextCtrl(request)
        doAsyncCtrl = panel.CheckBox(doAsync)
        useSSLCtrl = panel.CheckBox(useSSL)
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
            doAsyncCtrl,
            panel.StaticText("SSL:"),
            useSSL,
        ])
        while panel.Affirmed():
            panel.SetResult(
                protocolCtrl.GetValue(),
                hostCtrl.GetValue(),
                portCtrl.GetValue(),
                requestCtrl.GetValue(),
                doAsyncCtrl.GetValue(),
                useSSLCtrl.GetValue(),
            )

class sendPOSTPUTRequestWithBody(eg.ActionBase):
    def __call__(self, protocol, host, port, method, request, headers, body):
        #request = request.encode('utf-8')
        headerMap = {}
        headerList = headers.split(',')
        for header in headerList:
            headerMap[header.split(":", 1)[0]] = header.split(":", 1)[1]

        #headers = {"Content-type": "text/xml"}
        print headerMap
        eg.globals.httprelayresponse = self.plugin.SendPOSTPUTRequest(protocol, host, port, method, request, body, headerMap)

    def GetLabel(self, protocol, host, port, method, request, headers, body, useSSL):
        return "Send a {3} (useSSL: {5}) request with body to: {0}://{1}:{2}{4}".format(protocol, host, port, method, request, useSSL)

    def Configure(self, protocol="http", host="192.168.1.101", port=8000, method="POST", request="", headers="Content-type:text/xml", body="", useSSL=False):
        panel = eg.ConfigPanel(self)
        protocolCtrl = panel.TextCtrl(protocol)
        hostCtrl = panel.TextCtrl(host)
        portCtrl = panel.SpinIntCtrl(port, min=1, max=65535)
        methodCtrl = panel.TextCtrl(method)
        requestCtrl = panel.TextCtrl(request)
        headersCtrl = panel.TextCtrl(headers)
        bodyCtrl = panel.TextCtrl(body, style=wx.TE_MULTILINE)
        useSSLCtrl = panel.CheckBox(useSSL)
        panel.sizer.AddMany([
            panel.StaticText("Protocol:"),
            protocolCtrl,
            panel.StaticText("Host:"),
            hostCtrl,
            panel.StaticText("Port:"),
            portCtrl,
            panel.StaticText("Method:"),
            methodCtrl,
            panel.StaticText("Request:"),
            requestCtrl,
            panel.StaticText("Headers:"),
            headersCtrl,
            panel.StaticText("Body:"),
            bodyCtrl,
            panel.StaticText("SSL:"),
            useSSLCtrl,
        ])
        while panel.Affirmed():
            panel.SetResult(
                protocolCtrl.GetValue(),
                hostCtrl.GetValue(),
                portCtrl.GetValue(),
                methodCtrl.GetValue(),
                requestCtrl.GetValue(),
                headersCtrl.GetValue(),
                bodyCtrl.GetValue(),
                useSSLCtrl.GetValue(),
            )

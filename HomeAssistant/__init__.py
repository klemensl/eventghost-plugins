# -*- coding: utf-8 -*-

import eg
import httplib
import json

eg.RegisterPlugin(
    name = "HomeAssistant",
    author = "klemensl",
    version = "0.0.1a",
    kind = "other",
    description = "...."
)

class HomeAssistant(eg.PluginBase):

    def __init__(self):
        self.AddAction(getEntityState)

    def __start__(self, protocol, host, port, apiKey):
        self.host = host
        self.protocol = protocol
        self.port = port
        self.apiKey = apiKey
        print "HomeAssistant Plugin is started with parameter: {0}://{1}:{2}".format(self.protocol, self.host, self.port)

    def Configure(self, protocol="HTTP", host="192.168.1.64", port=8123, apiKey=""):
        panel = eg.ConfigPanel(self)
        protocolCtrl = panel.TextCtrl(protocol)
        hostCtrl = panel.TextCtrl(host)
        portCtrl = panel.SpinIntCtrl(port, min=1, max=65535)
        apiKeyCtrl = panel.TextCtrl(apiKey)
        panel.sizer.AddMany([
            panel.StaticText("Protocol:"),
            protocolCtrl,
            panel.StaticText("Host:"),
            hostCtrl,
            panel.StaticText("Port:"),
            portCtrl,
            panel.StaticText("API KEY:"),
            apiKeyCtrl,
        ])
        while panel.Affirmed():
            panel.SetResult(
                protocolCtrl.GetValue(),
                hostCtrl.GetValue(),
                portCtrl.GetValue(),
                apiKeyCtrl.GetValue()
            )

    def SendRequest(self, requestURL, port=8123, body="", method="GET"):
        print "requestURL {0}, requestPort: {1}, self.apiKey: {2}".format(requestURL, port, self.apiKey)
        headers = {"Authorization": "Bearer " + self.apiKey, "Accept": "*/*" }
        conn = httplib.HTTPConnection(self.host, port)
        conn.request(method, requestURL, body, headers)
        response = conn.getresponse()
        responseBody = response.read()
        conn.close()
        eg.globals._hassResponse = responseBody
        return responseBody

    def getEntityState(self, entity):
        responseBody = self.SendRequest("/api/states/" + entity)
        responseBodyJson = json.loads(responseBody)
        entityState = responseBodyJson["state"]
        eg.globals._hassEntityState = entityState
        print "entity {0} state: {1}".format(entity, entityState)
        return entityState


class getEntityState(eg.ActionBase):
    name = "HASS getEntityState"

    def __call__(self, entity):
        #print "Action 'getValue STATE XML-RPC' - Device-ID: {0}".format(device_id)
        return self.plugin.getEntityState(entity)

    def GetLabel(self, entity):
        return "get state of Entity {0}".format(entity)

    def Configure(self, entity=""):
        panel = eg.ConfigPanel(self)
        entityCtrl = panel.TextCtrl(entity)
        panel.AddLine(panel.StaticText("Entiy:"), entityCtrl)
        while panel.Affirmed():
            panel.SetResult(
                entityCtrl.GetValue()
            )
# -*- coding: utf-8 -*-

import eg
import xml.etree.ElementTree as ET
import httplib
import time
import json
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
        #print "test"
        #print json
        jsonContent = json.loads(content)

        if jsonContent["header"] is not None: #Smarthome Skill
            print "Smarthome Skill..."
            #print content

            if jsonContent['header']['namespace'] == 'Alexa.Discovery':
                PowerController = {"type": "AlexaInterface","interface": "Alexa.PowerController","version": "3","properties": {"supported": [{"name": "powerState"}],"proactivelyReportable": false,"retrievable": false}}
                PercentageController = {"type": "AlexaInterface","interface": "Alexa.PercentageController","version": "3","properties": {"supported": [{"name": "percentage"}],"proactivelyReportable": false,"retrievable": false}}

                #payload = { "discoveredAppliances":[ { "endpointId":"device001", "manufacturerName":"yourManufacturerName", "modelName":"model 01", "version":"your software version number here.", "friendlyName":"Smart Home Virtual Device", "description":"", stdActorActions, "cookie":{ "extraDetail1":"optionalDetailForSkillAdapterToReferenceThisDevice", "extraDetail2":"There can be multiple entries", "extraDetail3":"but they should only be used for reference purposes.", "extraDetail4":"This is not a suitable place to maintain current device state" } } ] }
                applianceKueche =  { "endpointId":"KEQ0926487:1", "displayCategories": ["LIGHT"], "manufacturerName":"Homematic", "version":"1.0", "friendlyName":"Kueche", "description":"Kueche", "capabilities":[ PowerController ], "cookie":{"system":"homematic"} }
                applianceInsel =  { "endpointId":"LEQ1226477:1", "displayCategories": ["LIGHT"], "manufacturerName":"Homematic", "version":"1.0", "friendlyName":"Insel", "description":"Insel", "capabilities":[ PowerController ], "cookie":{"system":"homematic"} }
                applianceVitrine =  { "endpointId":"KEQ0926487:2", "displayCategories": ["LIGHT"], "manufacturerName":"Homematic", "version":"1.0", "friendlyName":"Vitrine", "description":"Vitrine", "capabilities":[ PowerController ], "cookie":{"system":"homematic"} }
                applianceStiege =  { "endpointId":"LEQ0236800:1", "displayCategories": ["LIGHT"], "manufacturerName":"Homematic", "version":"1.0", "friendlyName":"Stiege", "description":"Stiege", "capabilities":[ PowerController ], "cookie":{"system":"homematic"} }
                applianceGang =  { "endpointId":"LEQ0236800:2", "displayCategories": ["LIGHT"], "manufacturerName":"Homematic", "version":"1.0", "friendlyName":"Gang", "description":"Gang", "capabilities":[ PowerController ], "cookie":{"system":"homematic"} }
                applianceEsszimmer =  { "endpointId":"LEQ0883366:1", "displayCategories": ["LIGHT"], "manufacturerName":"Homematic", "version":"1.0", "friendlyName":"Esszimmer", "description":"Esszimmer", "capabilities":[ PowerController ], "cookie":{"system":"homematic"} }
                applianceWohnzimmer =  { "endpointId":"OEQ0378808:1", "displayCategories": ["LIGHT"], "manufacturerName":"Homematic", "version":"1.0", "friendlyName":"Wohnzimmer", "description":"Wohnzimmer", "capabilities":[ PowerController ], "cookie":{"system":"homematic"} }
                applianceStehlampe =  { "endpointId":"MEQ0271709:1", "displayCategories": ["LIGHT"], "manufacturerName":"Homematic", "version":"1.0", "friendlyName":"Stehlampe", "description":"Stehlampe", "capabilities":[ PowerController ], "cookie":{"system":"homematic"} }
                applianceAmbient =  { "endpointId":"212:12", "displayCategories": ["LIGHT"], "manufacturerName":"Sonoff", "version":"1.0", "friendlyName":"Ambient", "description":"Ambient", "capabilities":[ PowerController ], "cookie":{"system":"sonoff"} }
                applianceFernseher =  { "endpointId":"Fernseher", "manufacturerName":"Panasonic", "version":"1.0", "friendlyName":"Fernseher", "description":"Fernseher", "capabilities":[ "turnOff" ], "cookie":{"system":"panasonic"} }
                applianceRolloKuche =  { "endpointId":"LEQ1032184:1", "manufacturerName":"Homematic", "version":"1.0", "friendlyName":"Rollo Kueche", "description":"Rollo Kueche", "capabilities":[ PowerController, PercentageController ], "cookie":{"system":"homematic"} }
                applianceRolloEsszimmer =  { "endpointId":"LEQ1029223:1", "manufacturerName":"Homematic", "version":"1.0", "friendlyName":"Rollo Esszimmer", "description":"Rollo Esszimmer", "capabilities":[ PowerController, PercentageController ], "cookie":{"system":"homematic"} }
                applianceRolloTerasse =  { "endpointId":"MEQ0733239:1", "manufacturerName":"Homematic", "version":"1.0", "friendlyName":"Rollo Terasse", "description":"Rollo Terasse", "capabilities":[ PowerController, PercentageController ], "cookie":{"system":"homematic"} }

                payload = { "endpoints":[applianceKueche, applianceInsel, applianceVitrine, applianceStiege, applianceGang, applianceEsszimmer,
                    applianceWohnzimmer, applianceStehlampe, applianceFernseher, applianceAmbient, applianceRolloKuche, applianceRolloEsszimmer, applianceRolloTerasse]
                }
                response = json.dumps(payload)
            elif "Controller" in jsonContent['header']['namespace']:
                device_id = jsonContent['endpoint']['endpointId']
                aktion = jsonContent['header']['name'] #== TurnOnRequest, SetPercentageRequest
                system = jsonContent['endpoint']['cookie']['system']

                if jsonContent['header']['namespace'] == 'Alexa.PowerController':
                    eg.TriggerEvent("Triggered", [aktion, device_id, system], "Alexa")
                    eg.TriggerEvent("Triggered." + aktion + "." + device_id, None, "Alexa") #wird aktuell nicht verwendet
                elif jsonContent['header']['namespace'] == 'Alexa.PercentageController':
                    percentage = jsonContent['payload']['percentage']
                    eg.TriggerEvent("Triggered", [aktion, device_id, percentage, system], "Alexa")
                    eg.TriggerEvent("Triggered." + aktion + "." + device_id, [percentage], "Alexa") #wird aktuell nicht verwendet
                else:
                    print "unknown..."

                payload = {}
                response = json.dumps(payload)
            elif jsonContent['header']['namespace'] == 'Alexa' and jsonContent['header']['namespace'] == 'ReportState':
                device_id = jsonContent['endpoint']['endpointId']
                system = jsonContent['endpoint']['cookie']['system']

                payload = {}
                response = json.dumps(payload)

        #print response
        self.send_response(200)
        self.send_header("Content-type", 'application/json; charset=UTF-8')
        self.send_header("Content-Length", len(response))
        self.end_headers()
        self.wfile.write(response.encode("UTF-8"))
        self.wfile.close()

    def log_message(self, format, *args):
        # suppress all messages
        pass


class ServerThread(Thread):

    def __init__(self, port, requestHandler):
        Thread.__init__(self, name="Alexa Callback Server Thread")
        self.port = port
        self.server = HTTPServer(('', port), requestHandler)

    def run(self):
        # send INIT to CCU
        print "Started Alexa Callback Server on port ", self.port
    	self.server.serve_forever()


eg.RegisterPlugin(
    name = "Homematic-Alexa V3",
    author = "klemensl",
    version = "0.0.3",
    kind = "other",
    description = "..."
)

class HMAlexaCallback(eg.PluginBase):

    def __init__(self):
        print "Plugin init"

    def __start__(self, callbackPort):
        #print "Start Callback Server Thread"
        self.serverThread = ServerThread(callbackPort, CCUCallbackHandler)
        self.serverThread.start()

    def Configure(self, callbackPort=8899):
        panel = eg.ConfigPanel(self)

        # callback server config
        callbackPortCtrl = panel.SpinIntCtrl(callbackPort, min=1, max=65535)

        acv = wx.ALIGN_CENTER_VERTICAL
        serverSizer = wx.GridBagSizer(5, 10)
        serverSizer.Add(callbackPortCtrl, (0,1))

        panel.sizer.Add(serverSizer, 1, flag = wx.EXPAND)

        while panel.Affirmed():
            panel.SetResult(
                callbackPortCtrl.GetValue()
            )

    def __stop__(self):
        print "Action 'stop'"

    def __close__(self):
        print "Action 'close'"



'''
{
payload = {
            "discoveredAppliances":[
                {
                    "endpointId":"KEQ0926487:1",
                    "manufacturerName":"Homematic",
                    "modelName":"Aktor",
                    "version":"1.0",
                    "friendlyName":"Kueche",
                    "description":"",
                   
                    "capabilities":[
                        "turnOn",
                        "turnOff"
                    ],
                    "cookie":{}
                }
            ]
        }

'''

'''
header = {
        "namespace":"Alexa.ConnectedHome.Control",
        "name":"TurnOnConfirmation",
        "payloadVersion":"2",
        "messageId": message_id
        }
return { 'header': header, 'payload': payload }
'''

'''
{"header": {"payloadVersion": "2", "namespace": "Alexa.ConnectedHome.Discovery", "name": "DiscoverAppliancesRequest"}, "payload": {"accessToken": "someaccesstoken"}}
'''

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

            if jsonContent['header']['namespace'] == 'Alexa.ConnectedHome.Discovery':
                #payload = { "discoveredAppliances":[ { "applianceId":"device001", "manufacturerName":"yourManufacturerName", "modelName":"model 01", "version":"your software version number here.", "friendlyName":"Smart Home Virtual Device", "friendlyDescription":"", "isReachable":True, "actions":[ "turnOn", "turnOff" ], "additionalApplianceDetails":{ "extraDetail1":"optionalDetailForSkillAdapterToReferenceThisDevice", "extraDetail2":"There can be multiple entries", "extraDetail3":"but they should only be used for reference purposes.", "extraDetail4":"This is not a suitable place to maintain current device state" } } ] }
                applianceKueche =  { "applianceId":"KEQ0926487:1", "manufacturerName":"Homematic", "modelName":"Aktor", "version":"1.0", "friendlyName":"Kueche", "friendlyDescription":"Kueche", "isReachable":True, "actions":[ "turnOn", "turnOff" ], "additionalApplianceDetails":{"system":"homematic"} }
                applianceInsel =  { "applianceId":"LEQ1226477:1", "manufacturerName":"Homematic", "modelName":"Aktor", "version":"1.0", "friendlyName":"Insel", "friendlyDescription":"Insel", "isReachable":True, "actions":[ "turnOn", "turnOff" ], "additionalApplianceDetails":{"system":"homematic"} }
                applianceVitrine =  { "applianceId":"KEQ0926487:2", "manufacturerName":"Homematic", "modelName":"Aktor", "version":"1.0", "friendlyName":"Vitrine", "friendlyDescription":"Vitrine", "isReachable":True, "actions":[ "turnOn", "turnOff" ], "additionalApplianceDetails":{"system":"homematic"} }
                #applianceStiege =  { "applianceId":"LEQ0236800:1", "manufacturerName":"Homematic", "modelName":"Aktor", "version":"1.0", "friendlyName":"Stiege", "friendlyDescription":"Stiege", "isReachable":True, "actions":[ "turnOn", "turnOff" ], "additionalApplianceDetails":{"system":"homematic"} }
                applianceStiege =  { "applianceId":"MEQ1007952:1", "manufacturerName":"Homematic", "modelName":"Aktor", "version":"1.0", "friendlyName":"Stiege", "friendlyDescription":"Stiege", "isReachable":True, "actions":[ "turnOn", "turnOff" ], "additionalApplianceDetails":{"system":"homematic"} }
                #applianceGang =  { "applianceId":"LEQ0236800:2", "manufacturerName":"Homematic", "modelName":"Aktor", "version":"1.0", "friendlyName":"Gang", "friendlyDescription":"Gang", "isReachable":True, "actions":[ "turnOn", "turnOff" ], "additionalApplianceDetails":{"system":"homematic"} }
                #applianceGang =  { "applianceId":"MEQ1007952:2", "manufacturerName":"Homematic", "modelName":"Aktor", "version":"1.0", "friendlyName":"Gang", "friendlyDescription":"Gang", "isReachable":True, "actions":[ "turnOn", "turnOff" ], "additionalApplianceDetails":{"system":"homematic"} }
                applianceGang =  { "applianceId":"OEQ2401294:1", "manufacturerName":"Homematic", "modelName":"Aktor", "version":"1.0", "friendlyName":"Gang", "friendlyDescription":"Gang", "isReachable":True, "actions":[ "turnOn", "turnOff" ], "additionalApplianceDetails":{"system":"homematic"} }
                applianceEsszimmer =  { "applianceId":"LEQ0883366:1", "manufacturerName":"Homematic", "modelName":"Aktor", "version":"1.0", "friendlyName":"Esszimmer", "friendlyDescription":"Esszimmer", "isReachable":True, "actions":[ "turnOn", "turnOff" ], "additionalApplianceDetails":{"system":"homematic"} }
                applianceWohnzimmer =  { "applianceId":"OEQ0378808:1", "manufacturerName":"Homematic", "modelName":"Aktor", "version":"1.0", "friendlyName":"Wohnzimmer", "friendlyDescription":"Wohnzimmer", "isReachable":True, "actions":[ "turnOn", "turnOff" ], "additionalApplianceDetails":{"system":"homematic"} }
                applianceStehlampe =  { "applianceId":"MEQ0271709:1", "manufacturerName":"Homematic", "modelName":"Aktor", "version":"1.0", "friendlyName":"Stehlampe", "friendlyDescription":"Stehlampe", "isReachable":True, "actions":[ "turnOn", "turnOff" ], "additionalApplianceDetails":{"system":"homematic"} }
                #applianceFernseher =  { "applianceId":"Fernseher", "manufacturerName":"Panasonic", "modelName":"Aktor", "version":"1.0", "friendlyName":"Fernseher", "friendlyDescription":"Fernseher", "isReachable":True, "actions":[ "turnOff" ], "additionalApplianceDetails":{"system":"panasonic"} }
                applianceAmbient =  { "applianceId":"212:12", "manufacturerName":"Sonoff", "modelName":"Aktor", "version":"1.0", "friendlyName":"Ambient", "friendlyDescription":"Ambient", "isReachable":True, "actions":[ "turnOn", "turnOff" ], "additionalApplianceDetails":{"system":"sonoff"} }
                applianceRolloKuche =  { "applianceId":"LEQ1032184:1", "manufacturerName":"Homematic", "modelName":"Aktor", "version":"1.0", "friendlyName":"Rollo Kueche", "friendlyDescription":"Rollo Kueche", "isReachable":True, "actions":[ "turnOn", "turnOff", "setPercentage" ], "additionalApplianceDetails":{"system":"homematic"} }
                applianceRolloEsszimmer =  { "applianceId":"LEQ1029223:1", "manufacturerName":"Homematic", "modelName":"Aktor", "version":"1.0", "friendlyName":"Rollo Esszimmer", "friendlyDescription":"Rollo Esszimmer", "isReachable":True, "actions":[ "turnOn", "turnOff", "setPercentage" ], "additionalApplianceDetails":{"system":"homematic"} }
                applianceRolloTerasse =  { "applianceId":"MEQ0733239:1", "manufacturerName":"Homematic", "modelName":"Aktor", "version":"1.0", "friendlyName":"Rollo Terasse", "friendlyDescription":"Rollo Terasse", "isReachable":True, "actions":[ "turnOn", "turnOff", "setPercentage" ], "additionalApplianceDetails":{"system":"homematic"} }
                applianceSchlafzimmer =  { "applianceId":"OEQ2399112:1", "manufacturerName":"Homematic", "modelName":"Aktor", "version":"1.0", "friendlyName":"Schlafzimmer", "friendlyDescription":"Schlafzimmer", "isReachable":True, "actions":[ "turnOn", "turnOff" ], "additionalApplianceDetails":{"system":"homematic"} }

                payload = { "discoveredAppliances":[applianceKueche, applianceInsel, applianceVitrine, applianceStiege, applianceGang, applianceEsszimmer,
                    applianceWohnzimmer, applianceStehlampe, applianceAmbient, applianceRolloKuche, applianceRolloEsszimmer, applianceRolloTerasse, applianceSchlafzimmer]
                }
                response = json.dumps(payload)
            elif jsonContent['header']['namespace'] == 'Alexa.ConnectedHome.Control':
                device_id = jsonContent['payload']['appliance']['applianceId']
                aktion = jsonContent['header']['name'] #== TurnOnRequest, SetPercentageRequest
                system = jsonContent['payload']['appliance']['additionalApplianceDetails']['system']
                #print "Aktion:", aktion

                if aktion == 'TurnOnRequest' or aktion == 'TurnOffRequest':
                    eventPayload = [aktion, device_id, system]
                    eg.TriggerEvent("Triggered", eventPayload, "Alexa")
                    eg.TriggerEvent("Triggered." + system, eventPayload, "Alexa")
                    eg.TriggerEvent("Triggered." + system + "." + aktion, eventPayload, "Alexa")
                    eg.TriggerEvent("Triggered." + aktion + "." + device_id, None, "Alexa") #wird aktuell nicht verwendet
                elif aktion == 'SetPercentageRequest':
					percentage = jsonContent['payload']['percentageState']['value']
					eventPayload = [aktion, device_id, percentage, system]
					eg.TriggerEvent("Triggered", eventPayload, "Alexa")
					eg.TriggerEvent("Triggered." + aktion + "." + device_id, eventPayload, "Alexa") #wird aktuell nicht verwendet
					eg.TriggerEvent("Triggered." + system + "." + aktion, eventPayload, "Alexa") #wird aktuell nicht verwendet
				

                payload = {}
                response = json.dumps(payload)
        elif jsonContent["request"] is not None: #Custom Skill
            print "Custom Skill..."

            intent = jsonContent["request"]["intent"]
            print "Intent: ", intent["name"]

            if intent["name"] == "Licht_Schalten":
                zimmer = intent["slots"]["Zimmer"]["value"]
                aktion = intent["slots"]["Aktion"]["value"]

                #print zimmer, aktion
                eventPayload = [zimmer, aktion]
                eg.TriggerEvent(intent["name"], eventPayload, "Alexa")

                responseMessage = "Klar doch!"
                jsonResponse = json.loads('{ "version": "1.0", "response": { "outputSpeech": { "type": "PlainText", "text": "PLACEHOLDER" }, "card": { "type": "Simple", "title": "PLACEHOLDER" }, "shouldEndSession": true } }')
                jsonResponse["response"]["outputSpeech"]["text"] = responseMessage
                jsonResponse["response"]["card"]["title"] = responseMessage
                response = json.dumps(jsonResponse)
            else:
                response = '{ "version": "1.0", "response": { "outputSpeech": { "type": "PlainText", "text": "Die Temperatur im Schlafzimmer ist 22 Grad." }, "card": { "type": "Simple", "title": "Homematic A87", "content": "Die Temperatur im Schlafzimmer ist 22 Grad." }, "shouldEndSession": true } }'

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
        
    def stop(self):
        self.server.server_close()


eg.RegisterPlugin(
    name = "Homematic-Alexa",
    author = "klemensl",
    version = "0.0.2c",
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

    def Configure(self, callbackPort=8889):
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
        self.serverThread.stop()
        print "Action 'stop'"

    def __close__(self):
        self.serverThread.stop()
        print "Action 'close'"



'''
{
payload = {
            "discoveredAppliances":[
                {
                    "applianceId":"KEQ0926487:1",
                    "manufacturerName":"Homematic",
                    "modelName":"Aktor",
                    "version":"1.0",
                    "friendlyName":"Kueche",
                    "friendlyDescription":"",
                    "isReachable":True,
                    "actions":[
                        "turnOn",
                        "turnOff"
                    ],
                    "additionalApplianceDetails":{}
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

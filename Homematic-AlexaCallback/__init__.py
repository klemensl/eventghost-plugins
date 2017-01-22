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
        jsonResponse = json.loads('{ "version": "1.0", "response": { "outputSpeech": { "type": "PlainText", "text": "PLACEHOLDER" }, "card": { "type": "Simple", "title": "PLACEHOLDER" }, "shouldEndSession": true } }')

        contentLength = int(self.headers.get('content-length'))
        content = self.rfile.read(contentLength)

        jsonContent = json.loads(content)
        intent = jsonContent["request"]["intent"]
        print "Intent: ", intent["name"]

        if intent["name"] == "Licht_Schalten":
            zimmer = intent["slots"]["Zimmer"]["value"]
            aktion = intent["slots"]["Aktion"]["value"]

            #print zimmer, aktion
            eventPayload = [zimmer, aktion]
            eg.TriggerEvent(intent["name"], eventPayload, "Alexa")

            #responseMessage = "Das Licht im {0} ist jetzt {1}.".format(zimmer, aktion)
            responseMessage = "Klar doch!"
            jsonResponse["response"]["outputSpeech"]["text"] = responseMessage
            jsonResponse["response"]["card"]["title"] = responseMessage
            response = json.dumps(jsonResponse)
        else:
            response = '{ "version": "1.0", "response": { "outputSpeech": { "type": "PlainText", "text": "Die Temperatur im Schlafzimmer ist 22 Grad." }, "card": { "type": "Simple", "title": "Homematic A87", "content": "Die Temperatur im Schlafzimmer ist 22 Grad." }, "shouldEndSession": true } }'

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
    name = "Homematic-Alexa",
    author = "klemensl",
    version = "0.0.1",
    kind = "other",
    description = "..."
)

class HMXMLAPI(eg.PluginBase):

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
        print "Action 'stop'"

    def __close__(self):
        print "Action 'close'"

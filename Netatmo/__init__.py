# Published Jan 2013
# Revised Jan 2014 (to add new modules data)
# Author : Philippe Larduinat, philippelt@users.sourceforge.net
# Public domain source code
# https://github.com/philippelt/netatmo-api-python

# This API provides access to the Netatmo (Internet weather station) devices
# This package can be used with Python2 or Python3 applications and do not
# require anything else than standard libraries

# PythonAPI Netatmo REST data access
# coding=utf-8

#from sys import version_info
import json, time

# HTTP libraries depends upon Python 2 or 3
#if version_info.major == 3 :
#    import urllib.parse, urllib.request
#else:
from urllib import urlencode
import urllib2

from threading import Thread, Event

######################## USER SPECIFIC INFORMATION ######################

# To be able to have a program accessing your netatmo data, you have to register your program as
# a Netatmo app in your Netatmo account. All you have to do is to give it a name (whatever) and you will be
# returned a client_id and secret that your app has to supply to access netatmo servers.

_CLIENT_ID     = ""   # Your client ID from Netatmo app registration at http://dev.netatmo.com/dev/listapps
_CLIENT_SECRET = ""   # Your client app secret   '     '
_USERNAME      = ""   # Your netatmo account username
_PASSWORD      = ""   # Your netatmo account password

#########################################################################


# Common definitions

_BASE_URL       = "https://api.netatmo.net/"
_AUTH_REQ       = _BASE_URL + "oauth2/token"
_GETUSER_REQ    = _BASE_URL + "api/getuser"
_DEVICELIST_REQ = _BASE_URL + "api/devicelist"
_GETMEASURE_REQ = _BASE_URL + "api/getmeasure"
_FORECAST		= _BASE_URL + "api/simplifiedfuturemeasure"


eg.RegisterPlugin(
    name = "Netatmo",
    author = "klemensl",
    version = "0.0.1",
    kind = "other",
    description = "..."
)

class Threshold():

    def __init__(self, name, id, datatype, lowerTH, lowerTHName, upperTH, upperTHName, stationName, isModule):
        self.id = id
        self.name = name
        self.datatype = datatype
        self.lowerTH = lowerTH
        self.lowerTHName = lowerTHName
        self.upperTH = upperTH
        self.upperTHName = upperTHName
        self.stationName = stationName
        self.isModule = isModule

        self.lastFiredEvent = ""
        self.lastFiredDate = None
        self.fireAgain = False

class SchedulerThread(Thread):

    def __init__(self, authorization, eventPrefix):
        print "Starting Thread"

        Thread.__init__(self, name="TheThread")
        self.finished = Event()
        self.authorization = authorization
        self.eventPrefix = eventPrefix
        self.abort = False
        self.thresholdList = []

    def run(self):
        print "Got {0} Threshold configured!".format(len(self.thresholdList))
        while (self.abort == False):
            print "In loop, waiting 5s"
            self.finished.wait(5)

            if self.abort:
                break

            devList = DeviceList(self.authorization)

            for threshold in self.thresholdList:
                moduleOrStation = devList.moduleById(threshold.id)
                if moduleOrStation == None:
                    moduleOrStation = devList.stationById(threshold.id)

                currentValue = moduleOrStation['dashboard_data'][threshold.datatype]
                print "currentValue: {0}".format(currentValue)
                if currentValue < threshold.lowerTH:
                    fireEvent = threshold.lowerTHName
                elif currentValue > threshold.upperTH:
                    fireEvent = threshold.upperTHName

                if fireEvent == None:
                    print "threshold OK, no event fired!"
                else:
                    if (threshold.lastFiredEvent != fireEvent) or (threshold.fireAgain == True):
                    #if threshold.lastFiredEvent != fireEvent:
                        eg.TriggerEvent(fireEvent, None, self.eventPrefix)
                        threshold.lastFiredEvent = fireEvent
                    else:
                        print "Event already fired, won't fire again..."


    def AbortScheduler(self):
        self.abort = True
        print "Thread stopped"
        self.finished.set()



class ClientAuth:
    "Request authentication and keep access token available through token method. Renew it automatically if necessary"

    def __init__(self, clientId=_CLIENT_ID,
                       clientSecret=_CLIENT_SECRET,
                       username=_USERNAME,
                       password=_PASSWORD):

        postParams = {
                "grant_type" : "password",
                "client_id" : clientId,
                "client_secret" : clientSecret,
                "username" : username,
                "password" : password,
                "scope" : "read_station"
                }
        resp = postRequest(_AUTH_REQ, postParams)
        print resp
        self._clientId = clientId
        self._clientSecret = clientSecret
        self._accessToken = resp['access_token']
        self.refreshToken = resp['refresh_token']
        self._scope = resp['scope']
        self.expiration = int(resp['expire_in'] + time.time())

    @property
    def accessToken(self):

        if self.expiration < time.time(): # Token should be renewed

            postParams = {
                    "grant_type" : "refresh_token",
                    "refresh_token" : self.refreshToken,
                    "client_id" : self._clientId,
                    "client_secret" : self._clientSecret
                    }
            resp = postRequest(_AUTH_REQ, postParams)

            self._accessToken = resp['access_token']
            self.refreshToken = resp['refresh_token']
            self.expiration = int(resp['expire_in'] + time.time())

        return self._accessToken

class User:

    def __init__(self, authData):

        postParams = {
                "access_token" : authData.accessToken
                }
        resp = postRequest(_GETUSER_REQ, postParams)
        print resp
        self.rawData = resp['body']
        self.id = self.rawData['_id']
        try:
            self.devList = self.rawData['devices']
        except:
            print "No devices yet..."
        self.ownerMail = self.rawData['mail']

class DeviceList:

    def __init__(self, authData):

        self.getAuthToken = authData.accessToken
        postParams = {
                "access_token" : self.getAuthToken,
                "app_type" : "app_station"
                }
        resp = postRequest(_DEVICELIST_REQ, postParams)
        self.rawData = resp['body']
        print self.rawData
        #self.stations = { d['_id'] : d for d in self.rawData['devices'] }
        #self.stations = [d['_id'] for d in self.rawData['devices']]
        self.stations = dict((d['_id'], d) for d in self.rawData['devices'])
        #print self.stations
        #self.modules = { m['_id'] : m for m in self.rawData['modules'] }
        #self.modules = [m['_id'] for m in self.rawData['modules']]
        self.modules = dict((m['_id'], m) for m in self.rawData['modules'])
        #print self.modules
        self.default_station = list(self.stations.values())[0]['station_name']
        #self.default_station = self.stations[0]

    def modulesNamesList(self, station=None):
        res = [m['module_name'] for m in self.modules.values()]
        res.append(self.stationByName(station)['module_name'])
        return res

    def stationByName(self, station=None):
        if not station : station = self.default_station
        for i,s in self.stations.items():
            if s['station_name'] == station : return self.stations[i]
        return None

    def stationById(self, sid):
        return None if sid not in self.stations else self.stations[sid]

    def moduleByName(self, module, station=None):
        s = None
        if station :
            s = self.stationByName(station)
            if not s : return None
        for m in self.modules:
            mod = self.modules[m]
            if mod['module_name'] == module :
                if not s or mod['main_device'] == s['_id'] : return mod
        return None

    def moduleById(self, mid, sid=None):
        s = self.stationById(sid) if sid else None
        if mid in self.modules :
            return self.modules[mid] if not s or self.modules[mid]['main_device'] == s['_id'] else None

    def lastData(self, station=None, exclude=0):
        s = self.stationByName(station)
        if not s : return None
        lastD = dict()
        # Define oldest acceptable sensor measure event
        limit = (time.time() - exclude) if exclude else 0
        ds = s['dashboard_data']
        if ds['time_utc'] > limit :
            lastD[s['module_name']] = ds.copy()
            lastD[s['module_name']]['When'] = lastD[s['module_name']].pop("time_utc")
            lastD[s['module_name']]['wifi_status'] = s['wifi_status']
        for mId in s["modules"]:
            ds = self.modules[mId]['dashboard_data']
            if ds['time_utc'] > limit :
                mod = self.modules[mId]
                lastD[mod['module_name']] = ds.copy()
                lastD[mod['module_name']]['When'] = lastD[mod['module_name']].pop("time_utc")
                # For potential use, add battery and radio coverage information to module data if present
                for i in ('battery_vp', 'rf_status') :
                    if i in mod : lastD[mod['module_name']][i] = mod[i]
        return lastD

    def checkNotUpdated(self, station=None, delay=3600):
        res = self.lastData(station)
        ret = []
        for mn,v in res.items():
            if time.time()-v['When'] > delay : ret.append(mn)
        return ret if ret else None

    def checkUpdated(self, station=None, delay=3600):
        res = self.lastData(station)
        ret = []
        for mn,v in res.items():
            if time.time()-v['When'] < delay : ret.append(mn)
        return ret if ret else None

    def getMeasure(self, device_id, scale, mtype, module_id=None, date_begin=None, date_end=None, limit=None, optimize=False, real_time=False):
        postParams = { "access_token" : self.getAuthToken }
        postParams['device_id']  = device_id
        if module_id : postParams['module_id'] = module_id
        postParams['scale']      = scale
        postParams['type']       = mtype
        if date_begin : postParams['date_begin'] = date_begin
        if date_end : postParams['date_end'] = date_end
        if limit : postParams['limit'] = limit
        postParams['optimize'] = "true" if optimize else "false"
        postParams['real_time'] = "true" if real_time else "false"
        return postRequest(_GETMEASURE_REQ, postParams)

    def MinMaxTH(self, station=None, module=None, frame="last24"):
        if not station : station = self.default_station
        s = self.stationByName(station)
        if not s :
            s = self.stationById(station)
            if not s : return None
        if frame == "last24":
            end = time.time()
            start = end - 24*3600 # 24 hours ago
        elif frame == "day":
            start, end = todayStamps()
        if module and module != s['module_name']:
            m = self.moduleByName(module, s['station_name'])
            if not m :
                m = self.moduleById(s['_id'], module)
                if not m : return None
            # retrieve module's data
            resp = self.getMeasure(
                    device_id  = s['_id'],
                    module_id  = m['_id'],
                    scale      = "max",
                    mtype      = "Temperature,Humidity",
                    date_begin = start,
                    date_end   = end)
        else : # retrieve station's data
            resp = self.getMeasure(
                    device_id  = s['_id'],
                    scale      = "max",
                    mtype      = "Temperature,Humidity",
                    date_begin = start,
                    date_end   = end)
        if resp:
            T = [v[0] for v in resp['body'].values()]
            H = [v[1] for v in resp['body'].values()]
            return min(T), max(T), min(H), max(H)
        else:
            return None

# Utilities routines

def postRequest(url, params):
    #if version_info.major == 3:
    #    req = urllib.request.Request(url)
    #    req.add_header("Content-Type","application/x-www-form-urlencoded;charset=utf-8")
    #    params = urllib.parse.urlencode(params).encode('utf-8')
    #    resp = urllib.request.urlopen(req, params).readall().decode("utf-8")
    #else:
    params = urlencode(params)
    headers = {"Content-Type" : "application/x-www-form-urlencoded;charset=utf-8"}
    #print params
    #print url
    req = urllib2.Request(url=url, data=params, headers=headers)
    resp = urllib2.urlopen(req).read()
    #print json.loads(resp)
    return json.loads(resp)

def toTimeString(value):
    return time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(int(value)))

def toEpoch(value):
    return int(time.mktime(time.strptime(value,"%Y-%m-%d_%H:%M:%S")))

def todayStamps():
    today = time.strftime("%Y-%m-%d")
    today = int(time.mktime(time.strptime(today,"%Y-%m-%d")))
    return today, today+3600*24

# Global shortcut

def getStationMinMaxTH(station=None, module=None):
    authorization = ClientAuth()
    devList = DeviceList(authorization)
    if not station : station = devList.default_station
    if module :
        mname = module
    else :
        mname = devList.stationByName(station)['module_name']
    lastD = devList.lastData(station)
    if mname == "*":
        result = dict()
        for m in lastD.keys():
            if time.time()-lastD[m]['When'] > 3600 : continue
            r = devList.MinMaxTH(module=m)
            result[m] = (r[0], lastD[m]['Temperature'], r[1])
    else:
        if time.time()-lastD[mname]['When'] > 3600 : result = ["-", "-"]
        else : result = [lastD[mname]['Temperature'], lastD[mname]['Humidity']]
        result.extend(devList.MinMaxTH(station, mname))
    return result


class Netatmo(eg.PluginBase):
    def __init__(self):
        self.started = False
        self.schedulerThread = None

        self.authorization = None;
        self.user = None;
        self.devList = None;

        self.AddAction(getValue)

    def __start__(self, username, password, clientId, clientSecret, eventPrefix, refreshRate):
        self.username = username
        self.password = password
        self.clientId = clientId
        self.clientSecret = clientSecret
        self.eventPrefix = eventPrefix
        self.refreshRate = refreshRate
        print "Netatmo: listener started"

        self.authorization = ClientAuth(_CLIENT_ID, _CLIENT_SECRET, _USERNAME, _PASSWORD)
        self.user = User(self.authorization)
        self.devList = DeviceList(self.authorization)
        print "Netatmo: authorized and devices loaded"


    def Configure(self,
        username=_USERNAME,
        password=_PASSWORD,
        clientId=_CLIENT_ID,
        clientSecret=_CLIENT_SECRET,
        eventPrefix="Netatmo",
        refreshRate=300):

        panel = eg.ConfigPanel(self)

        usernameCtrl = panel.TextCtrl(username)
        passwordCtrl = panel.TextCtrl(password)
        clientIdCtrl = panel.TextCtrl(clientId)
        clientSecretCtrl = panel.TextCtrl(clientSecret)
        eventPrefixCtrl = panel.TextCtrl(eventPrefix)
        refreshRateCtrl = panel.SpinIntCtrl(refreshRate, 1, 600)

        acv = wx.ALIGN_CENTER_VERTICAL
        authSizer = wx.GridBagSizer(5, 10)
        authSizer.Add(panel.StaticText("Username:"), (0,0))
        authSizer.Add(usernameCtrl, (0,1))
        authSizer.Add(panel.StaticText("Password:"), (0,2))
        authSizer.Add(passwordCtrl, (0,3))
        authSizer.Add(panel.StaticText("Client ID:"), (1,0))
        authSizer.Add(clientIdCtrl, (1,1))
        authSizer.Add(panel.StaticText("Client Secret:"), (1,2))
        authSizer.Add(clientSecretCtrl, (1,3))
        authSizer.Add(panel.StaticText("Event Prefix:"), (2,0))
        authSizer.Add(eventPrefixCtrl, (2,1))
        authSizer.Add(panel.StaticText("Refreshrate (s):"), (3,0))
        authSizer.Add(refreshRateCtrl, (3,1))


        moduleListSizer = wx.GridBagSizer(2, 1)
        moduleListSizer.AddGrowableRow(0)
        moduleListSizer.AddGrowableCol(1)

        moduleListCtrl = wx.ListCtrl(
            panel,
            -1,
            style=wx.LC_REPORT | wx.VSCROLL | wx.HSCROLL
        )
        moduleListCtrl.InsertColumn(0, "Name")
        moduleListCtrl.InsertColumn(1, "ID")
        moduleListCtrl.InsertColumn(2, "DataTypes")
        moduleListCtrl.InsertColumn(3, "Station/Module")
        moduleListCtrl.InsertColumn(4, "Station")

        moduleListSizer.Add(moduleListCtrl, (0,0), (1,3), flag = wx.EXPAND)

        #buttons
        testConnectionButton = wx.Button(panel, -1, "Test Connection")
        moduleListSizer.Add(testConnectionButton, (1,0))

        startThreadButton = wx.Button(panel, -1, "Start Thread")
        moduleListSizer.Add(startThreadButton, (1,1), flag=wx.ALIGN_RIGHT)

        stopThreadButton = wx.Button(panel, -1, "Stop Thread")
        moduleListSizer.Add(stopThreadButton, (1,2), flag=wx.ALIGN_LEFT)


        thresholdListSizer = wx.GridBagSizer(2, 1)
        thresholdListSizer.AddGrowableRow(0)
        thresholdListSizer.AddGrowableCol(1)

        thresholdListCtrl = wx.ListCtrl(
            panel,
            -1,
            style=wx.LC_REPORT | wx.VSCROLL | wx.HSCROLL
        )
        thresholdListCtrl.InsertColumn(0, "Name")
        thresholdListCtrl.InsertColumn(1, "ID")
        thresholdListCtrl.InsertColumn(2, "DataType")
        thresholdListCtrl.InsertColumn(3, "Lower TH")
        thresholdListCtrl.InsertColumn(4, "LTH Event")
        thresholdListCtrl.InsertColumn(5, "Upper TH")
        thresholdListCtrl.InsertColumn(6, "UTH Event")
        thresholdListCtrl.InsertColumn(7, "Station/Module")
        thresholdListCtrl.InsertColumn(8, "Station")

        thresholdListSizer.Add(thresholdListCtrl, (0,0), (1,2), flag = wx.EXPAND)

        removeThresholdButton = wx.Button(panel, -1, "Remove")
        thresholdListSizer.Add(removeThresholdButton, (1,0))

        def RemoveThreshold(event):
            selected = thresholdListCtrl.GetFirstSelected()
            if selected >= 0:
                thresholdListCtrl.DeleteItem(selected)

        removeThresholdButton.Bind(wx.EVT_BUTTON, RemoveThreshold)
        #removeThresholdButton.Disable()

        def AddThreshold(event):
            moduleOrStation = self.devList.moduleById(moduleIDCtrl_1.GetValue())
            if moduleOrStation == None:
                moduleOrStation = self.devList.stationById(moduleIDCtrl_1.GetValue())
                stationName = moduleOrStation['station_name']
            else:
                stationName = self.devList.stations[moduleOrStation['main_device']]['station_name']

            print "module or station? {0}".format(moduleOrStation)

            thresholdListCtrl.InsertStringItem(0, moduleOrStation['module_name'])
            thresholdListCtrl.SetStringItem(0, 1, moduleIDCtrl_1.GetValue())
            thresholdListCtrl.SetStringItem(0, 2, moduleDataTypeCtrl_1.GetValue())
            thresholdListCtrl.SetStringItem(0, 3, str(moduleLowerTHCtrl_1.GetValue()))
            thresholdListCtrl.SetStringItem(0, 4, str(moduleLowerTHEvent_1.GetValue()))
            thresholdListCtrl.SetStringItem(0, 5, str(moduleUpperTHCtrl_1.GetValue()))
            thresholdListCtrl.SetStringItem(0, 6, str(moduleUpperTHEvent_1.GetValue()))
            thresholdListCtrl.SetStringItem(0, 8, stationName)

            startThreadButton.Enable()


        moduleIDCtrl_1 = wx.ComboBox(panel, -1, value="", choices=[''], style=wx.CB_DROPDOWN)
        moduleDataTypeCtrl_1 = wx.ComboBox(panel, -1, value="Temperature", choices=['Temperature', 'CO2', 'Humidity', 'Noise', 'Pressure', 'Rain'], style=wx.CB_DROPDOWN)
        moduleLowerTHCtrl_1 = panel.SpinIntCtrl(value=20, min=-10000, max=10000)
        moduleUpperTHCtrl_1 = panel.SpinIntCtrl(value=25, min=-10000, max=10000)
        moduleLowerTHEvent_1 = panel.TextCtrl()
        moduleUpperTHEvent_1 = panel.TextCtrl()

        addThresholdButton = wx.Button(panel, -1, "Add")
        addThresholdButton.Bind(wx.EVT_BUTTON, AddThreshold)

        addThresholdSizer = wx.GridBagSizer(4, 8)
        addThresholdSizer.Add(panel.StaticText("Module ID:"), (1,0))
        addThresholdSizer.Add(moduleIDCtrl_1, (1,1))
        addThresholdSizer.Add(panel.StaticText("DataType:"), (1,2))
        addThresholdSizer.Add(moduleDataTypeCtrl_1, (1,3))
        addThresholdSizer.Add(panel.StaticText("Lower TH:"), (2,0))
        addThresholdSizer.Add(moduleLowerTHCtrl_1, (2,1))
        addThresholdSizer.Add(panel.StaticText("Upper TH:"), (2,2))
        addThresholdSizer.Add(moduleUpperTHCtrl_1, (2,3))
        addThresholdSizer.Add(panel.StaticText("Lower TH Event:"), (3,0))
        addThresholdSizer.Add(moduleLowerTHEvent_1, (3,1))
        addThresholdSizer.Add(panel.StaticText("Upper TH Event:"), (3,2))
        addThresholdSizer.Add(moduleUpperTHEvent_1, (3,3))
        addThresholdSizer.Add(addThresholdButton, (4,0))

        def RetrieveModules (event):
            moduleListCtrl.DeleteAllItems()

            self.authorization = ClientAuth(clientIdCtrl.GetValue(), clientSecretCtrl.GetValue(), usernameCtrl.GetValue(), passwordCtrl.GetValue())
            self.user = User(self.authorization)
            self.devList = DeviceList(self.authorization)

            moduleIDCtrl_1.Clear()

            row = 0
            for stationID, station in self.devList.stations.iteritems():
                moduleIDCtrl_1.Append(stationID)
                moduleListCtrl.InsertStringItem(row, station['module_name'])
                moduleListCtrl.SetStringItem(row, 1, stationID)
                moduleListCtrl.SetStringItem(row, 2, ", ".join(station['data_type']))
                moduleListCtrl.SetStringItem(row, 3, "Station")
                moduleListCtrl.SetStringItem(row, 4, station['station_name'])
                row += 1

            for moduleID, module in self.devList.modules.iteritems():
                moduleIDCtrl_1.Append(moduleID)
                moduleListCtrl.InsertStringItem(row, module['module_name'])
                moduleListCtrl.SetStringItem(row, 1, moduleID)
                moduleListCtrl.SetStringItem(row, 2, ", ".join(module['data_type']))
                moduleListCtrl.SetStringItem(row, 3, "Module")
                moduleListCtrl.SetStringItem(row, 4, self.devList.stations[module['main_device']]['station_name'])
                row += 1

        testConnectionButton.Bind(wx.EVT_BUTTON, RetrieveModules)

        def StartScheduler(event):
            self.schedulerThread = SchedulerThread(self.authorization, eventPrefixCtrl.GetValue())

            for row in range(thresholdListCtrl.GetItemCount()):
                item = self.schedulerThread.thresholdList.append(
                    Threshold(thresholdListCtrl.GetItem(itemId=row, col=0).GetText(),
                    thresholdListCtrl.GetItem(itemId=row, col=1).GetText(),
                    thresholdListCtrl.GetItem(itemId=row, col=2).GetText(),
                    int(thresholdListCtrl.GetItem(itemId=row, col=3).GetText()),
                    thresholdListCtrl.GetItem(itemId=row, col=4).GetText(),
                    int(thresholdListCtrl.GetItem(itemId=row, col=5).GetText()),
                    thresholdListCtrl.GetItem(itemId=row, col=6).GetText(),
                    thresholdListCtrl.GetItem(itemId=row, col=8).GetText(),
                    True))

            self.schedulerThread.start()
            self.started = True
            startThreadButton.Disable()
            stopThreadButton.Enable()
            addThresholdButton.Disable()
            removeThresholdButton.Disable()

        startThreadButton.Bind(wx.EVT_BUTTON, StartScheduler)
        startThreadButton.Disable()


        def AbortScheduler(event):
            if self.started == True:
                self.schedulerThread.AbortScheduler()
            self.started = False
            startThreadButton.Enable()
            stopThreadButton.Disable()
            addThresholdButton.Enable()
            removeThresholdButton.Enable()

        stopThreadButton.Bind(wx.EVT_BUTTON, AbortScheduler)
        stopThreadButton.Disable()


        panel.sizer.Add(authSizer, 1, flag = wx.EXPAND)
        panel.sizer.Add(panel.StaticText("Available Modules"))
        panel.sizer.Add(moduleListSizer, 1, flag = wx.EXPAND)
        panel.sizer.Add(panel.StaticText("Defined Threshholds"))
        panel.sizer.Add(thresholdListSizer, 1, flag = wx.EXPAND)
        panel.sizer.Add(addThresholdSizer, 1, flag = wx.EXPAND)

        if self.schedulerThread <> None:
            if self.started == True:
                startThreadButton.Disable()
                stopThreadButton.Enable()
            else:
                startThreadButton.Enable()
                stopThreadButton.Disable()

            for threshold in self.schedulerThread.thresholdList:
                print "adding threshold: {0}".format(threshold.name)

                thresholdListCtrl.InsertStringItem(0, threshold.name)
                thresholdListCtrl.SetStringItem(0, 1, threshold.id)
                thresholdListCtrl.SetStringItem(0, 2, threshold.datatype)
                thresholdListCtrl.SetStringItem(0, 3, str(threshold.lowerTH))
                thresholdListCtrl.SetStringItem(0, 4, threshold.lowerTHName)
                thresholdListCtrl.SetStringItem(0, 5, str(threshold.upperTH))
                thresholdListCtrl.SetStringItem(0, 6, threshold.upperTHName)
                thresholdListCtrl.SetStringItem(0, 8, threshold.stationName)

        while panel.Affirmed():
            panel.SetResult(
                usernameCtrl.GetValue(),
                passwordCtrl.GetValue(),
                clientIdCtrl.GetValue(),
                clientSecretCtrl.GetValue(),
                eventPrefixCtrl.GetValue(),
                refreshRateCtrl.GetValue()
            )

    def __stop__(self):
        if self.started == True:
            self.schedulerThread.AbortScheduler()
        self.started = False


    def __close__(self):
        if self.started == True:
            self.schedulerThread.AbortScheduler()
        self.started = False


class getValue(eg.ActionBase):
    def __call__(self, moduleID, data_type):
        devList = DeviceList(self.plugin.authorization)

        moduleOrStation = devList.moduleById(moduleID)
        if moduleOrStation == None:
            moduleOrStation = devList.stationById(moduleID)

        print "Got '{2}' of module '{1}' ({0})".format(moduleID, moduleOrStation['module_name'], moduleOrStation['dashboard_data'][data_type])
        return moduleOrStation['dashboard_data'][data_type]

    def GetLabel(self, moduleID, data_type):
        return "Get '{1}' of module with the ID {0}".format(moduleID, data_type)

    def Configure(self, moduleID="", data_type=""):
        panel = eg.ConfigPanel(self)
        moduleIDCtrl = panel.TextCtrl(moduleID)
        panel.AddLine(panel.StaticText("Module ID:"), moduleIDCtrl)
        data_typeCtrl = panel.TextCtrl(data_type)
        panel.AddLine(panel.StaticText("DataType:"), data_typeCtrl)
        while panel.Affirmed():
            panel.SetResult(
                moduleIDCtrl.GetValue(),
                data_typeCtrl.GetValue()
            )

#class testConnection(eg.ActionBase):
#    def __call__(self):
#        authorization = ClientAuth(self.plugin.clientId, self.plugin.clientSecret, self.plugin.username, self.plugin.password)
#        user = User(authorization)                  # Test GETUSER
#        devList = DeviceList(authorization)         # Test DEVICELIST
#        print devList.MinMaxTH()                    # Test GETMEASURE

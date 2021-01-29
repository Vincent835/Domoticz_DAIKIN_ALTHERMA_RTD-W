#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python plugin for Domoticz - RTD-W monitoring and control interface for Altherma HT hydroboxes. 
Original author: Vincent835

Requirements: 
    1.python module minimalmodbus -> http://minimalmodbus.readthedocs.io/en/master/
        (pi@raspberrypi:~$ sudo pip3 install minimalmodbus)
    2.Communication module Modbus USB to RS485 converter module
    3.RTD-W monitoring and control interface for Altherma HT hydroboxes (http://www.realtime-controls.co.uk/index.php/site/multi-language-download/rtd_w_daikin_control_interface)

    The RTD-W is a monitoring and control interface for Altherma HT hydroboxes (heating only and reversible),
    small inverter chillers (EWA/YQ16..64 series) and VRV heating only hydrobox.
    The interface is compatible with all units that are operated using a BRC21 remote controller network
    connection and allows control of up to 16 units in a single group.
    Note: this plugin is intended for a single RTD-W at address 1, with a single unit.
"""

"""
<plugin key="RTD-W" name="DAIKIN ALTHERMA HT (RTD-W Modbus)" version="0.1.2" author="Vincent835">
    <params>
        <param field="SerialPort" label="Modbus Port" width="200px" required="true" default="/dev/ttyUSB1" />
        <param field="Mode1" label="Baud rate" width="40px" required="true" default="9600"  />
        <param field="Mode2" label="Device ID" width="40px" required="true" default="1" />
        <param field="Mode3" label="Reading Interval min." width="40px" required="true" default="1" />
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="true" />
            </options>
        </param>
    </params>
</plugin>
"""

import minimalmodbus
import serial
import Domoticz
from enum import IntEnum, unique  # , auto


@unique
class unit(IntEnum):
    """
        Device Unit numbers
        Define here your units numbers. These can be used to update your devices.
        Be sure the these have a unique number!
    """

#   Device units
    Leaving_Temp = 1
    Return_Temp = 2
    DHW_Tank_Temp = 3 
    Outdoor_Temp = 4
    Room_Temp = 5
    Room_Temp_Setpoint = 6
    Leaving_Water_Setpoint = 7
    ON_OFF_Command_Space_Heating = 8
    DHW_Reheat_Command = 9
    Start_DHW_Storage = 10
    Control_Source = 11
    Quiet_Mode = 12
    Weather_Dependent_Setpoint_Operation = 13
    Shift_Value_Leaving_Water_Temp = 14
    Reset_Run_Hour_Counter = 15   
    ON_OFF_Space_Heating = 16
    Circulation_Pump = 17
    Compressor = 18
    Disinfection = 19
    Setback = 20
    Defrost = 21
    DHW_Reheat = 22
    DHW_Storage = 23
    Pump_Running_Hour_Counter = 24 
    
    
class BasePlugin:

    ########################################################################################
    """
        Constants

        The onHeartbeat method is called every 10 seconds.
            self.__HEARTBEATS2MIN is the number of heartbeats per minute. By using
            self.__HEARTBEATS2MIN * self.__MINUTES you can specify the frequency in
            minutes of updating your devices in the onHeartbeat method.
    """

    __HEARTBEATS2MIN = 6
    __MINUTES = 1

    """
        Constants which can be used to create the devices. Look at onStart where 
        the devices are created.
            self.__UNUSED, the user has to add this devices manually
            self.__USED, the device will be directly available
    """
    __UNUSED = 0
    __USED = 1
    __NVALUE = 0 
    __SVALUE = 1


    ########################################################################################
    """
        Device definitions
    
            0       1       2               3       4           5           6           7      8
            id,     name,   named type,     type,   subtype,    Switchtype, options,    used,  Description
    Nota : la description n'est pas associée au dispositif s'il est créé en UNUSED.
    """
    __UNITS = [
        [unit.Leaving_Temp, "Température eau départ", "Temperature", 0, 0, 0, {}, __USED, ""],
        [unit.Return_Temp, "Température eau retour", "Temperature", 0, 0, 0, {}, __USED, ""],
        [unit.DHW_Tank_Temp, "Température eau chaude sanitaire", "Temperature", 0, 0, 0, {}, __USED, ""],
        [unit.Outdoor_Temp, "Température extérieure", "Temperature", 0, 0, 0, {}, __USED, ""],
        [unit.Room_Temp, "Température intérieure", "Temperature", 0, 0, 0, {}, __USED, ""],
        [unit.Room_Temp_Setpoint, "Consigne température de la pièce", None, 242, 1, 0, {}, __USED, "Réglable entre 16 et 32°C"],
        [unit.Leaving_Water_Setpoint, "Consigne température eau chauffage", None, 242, 1, 0, {}, __USED, "Réglable entre 25 et 80°C"],
        [unit.ON_OFF_Command_Space_Heating, "Commande M/A chauffage", "Switch", 0, 0, 0, {}, __UNUSED, ""],
        [unit.DHW_Reheat_Command, "Commande réchauffage ECS", "Switch", 0, 0, 0, {}, __UNUSED, ""],
        [unit.Start_DHW_Storage, "Commande stockage ECS", "Switch", 0, 0, 0, {}, __UNUSED, ""],
        [unit.Control_Source, "Sources de contrôle", "Selector Switch", 0, 0, 0,
            {"LevelNames" : "Tout|Externe|Local|Tout",
             "LevelOffHidden" : "true",
             "SelectorStyle" : "0"},
             __UNUSED, ""],
        [unit.Quiet_Mode, "Mode silencieux", "Switch", 0, 0, 0, {}, __UNUSED, ""],
        [unit.Weather_Dependent_Setpoint_Operation, "Temp départ / Temp ext.", "Switch", 0, 0, 0, {}, __UNUSED, ""],
        [unit.Shift_Value_Leaving_Water_Temp, "Décalage temp. départ", "Selector Switch", 0, 0, 0,
             {"LevelNames" : "|-5°C|-4°C|-3°C|-2°C|-1°C|0°C|+1°C|+2°C|+3°C|+4°C|+5°C",
              "LevelOffHidden" : "true",
              "SelectorStyle" : "1"},
             __USED, "Réglable entre -5 et +5°C"],
        [unit.Reset_Run_Hour_Counter, "Reset compteur", "Push On", 0, 0, 0, {}, __UNUSED,""],
        [unit.ON_OFF_Space_Heating, "Etat chauffage", "Contact", 0, 0, 0, {}, __USED, ""],
        [unit.Circulation_Pump, "Etat pompe", "Contact", 0, 0, 0, {}, __USED, ""],
        [unit.Compressor, "Etat compresseur", "Contact", 0, 0, 0, {}, __USED, ""],
        [unit.Disinfection, "Etat désinfection ECS", "Contact", 0, 0, 0, {}, __USED, ""],        
        [unit.Setback, "Mode réduit", "Contact", 0, 0, 0, {}, __USED, ""],  
        [unit.Defrost, "Dégivrage", "Contact", 0, 0, 0, {}, __USED, ""],  
        [unit.DHW_Reheat, "Etat réchauffage ECS", "Contact", 0, 0, 0, {}, __USED, ""],  
        [unit.DHW_Storage, "Etat Stockage ECS", "Contact", 0, 0, 0, {}, __USED, ""],  
        [unit.Pump_Running_Hour_Counter, "Compteur horaire pompe", None, 113, 0, 3,{"ValueQuantity":"Temps","ValueUnits":"heures"}, __USED, ""]
        ]
        
##"""
##        Device registers
##            0   1        2              3           4       5
##            id, address, nd_décimals,   function,   Signed, Type
##"""
    __REGISTERS = [
        [unit.Leaving_Temp, 123, 2, 4, True, __SVALUE],
        [unit.Return_Temp, 131, 2, 4, True, __SVALUE],
        [unit.DHW_Tank_Temp, 132, 2, 4, True, __SVALUE],
        [unit.Outdoor_Temp, 133, 2, 4, True, __SVALUE],
        [unit.Room_Temp, 50, 2, 4, True, __SVALUE],
        [unit.Room_Temp_Setpoint, 5, 0, 3, False, __SVALUE],
        [unit.Leaving_Water_Setpoint, 1, 0,  3, False, __SVALUE],
        [unit.ON_OFF_Command_Space_Heating, 4, 0, 3, False, __NVALUE],
        [unit.DHW_Reheat_Command, 6, 0, 3, False, __NVALUE],
        [unit.Start_DHW_Storage, 7, 0, 3, False, __NVALUE],
        [unit.Control_Source, 8, 0, 3, False, __SVALUE],
        [unit.Quiet_Mode, 9, 0, 3, False, __NVALUE],
        [unit.Weather_Dependent_Setpoint_Operation, 10, 0, 3, False, __NVALUE],
        [unit.Shift_Value_Leaving_Water_Temp, 11, 0, 3, True, __SVALUE],
        [unit.Reset_Run_Hour_Counter, 12, 0,  3, False, __SVALUE],    
        [unit.ON_OFF_Space_Heating, 70, 0, 4, False, __NVALUE],
        [unit.Circulation_Pump, 71, 0, 4, False, __NVALUE],
        [unit.Compressor, 72, 0, 4, False, __NVALUE],
        [unit.Disinfection, 74, 0, 4, False, __NVALUE],      
        [unit.Setback, 75, 0, 4, False, __NVALUE],
        [unit.Defrost, 76, 0, 4, False, __NVALUE],         
        [unit.DHW_Reheat, 77, 0, 4, False, __NVALUE],
        [unit.DHW_Storage, 78, 0, 4, False, __NVALUE],
        [unit.Pump_Running_Hour_Counter, 80, 0, 4, False, __SVALUE]
         ]
    
    ########################################################################################

    def __init__(self):
        self.__runAgain = 0


    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand: {}, {}, {}, {}".format(Unit, Command, Level, Hue))

        # ON/OFF or Level payload value
        payload = int(Level) # Set payload from slider/scroll or setpoint device
        # Set payload if a button has been pressed
        if (str(Command) == "On"): payload = 1
        if (str(Command) == "Off"): payload = 0
        # Check limit temperature setpoint
        if (Unit == unit.Room_Temp_Setpoint):
            if(Level < 16):
                payload = int(16 )
            elif(Level > 32):
                payload = int(32 )
        if (Unit == unit.Leaving_Water_Setpoint):
            if(Level < 25):
                payload = int(25)
            elif(Level > 80):
                payload = int(80)
        if (Unit == unit.Shift_Value_Leaving_Water_Temp):
            payload = int((Level / 10)-6)
            if(payload < -5):
                payload = int(-5)
            elif(payload > 5):
                payload = int(5)
        if (Unit == unit.Control_Source):
            payload = int((Level / 10))
            if(payload < 0 or payload > 3):
                payload = int(0)


        ########################################
        # WRITE PAYLOAD 
        ########################################
        register_info = self.__REGISTERS[Unit-1]
        if register_info[3] ==  3:
            try:
                # Function to execute
                result = self.rs485.write_register(register_info[1], payload, number_of_decimals=register_info[2], functioncode=6, signed=register_info[4])

                Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
                Domoticz.Log("write_register n° " + str(register_info[1]) + "', Payload= " + str(payload) +  ", nb_decimals = " + str(register_info[2]) +", signed: " + str(register_info[4]))

                Domoticz.Debug("MODBUS DEBUG - RESULT: " + str(result))
                if (str(Command) == "On"): Devices[Unit].Update(1, "1") # Update device to ON
                if (str(Command) == "Off"): Devices[Unit].Update(0, "0") # Update device to OFF
                if (str(Command) == "Set Level"):
                    if (Unit == unit.Shift_Value_Leaving_Water_Temp):
                        Devices[Unit].Update(int(payload!=0), str((payload+6) * 10))   # Update Level device convert for switch selector
                    elif (Unit == unit.Control_Source):
                        Devices[Unit].Update(int(payload!=2), str(payload * 10))
                    else:
                        Devices[Unit].Update(0, str(payload)) # Update Level device
                   
            except:
                Domoticz.Error("Modbus error communicating! check your settings!")
                Devices[unit].Update(1, "0") # Set value to 0 (error)

        

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug(
            "onConnect: {}, {}, {}".format(Connection.Name, Status, Description)
        )

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect: {}".format(Connection.Name))

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat")
        self.__runAgain -= 1
        if self.__runAgain <= 0:
            self.__runAgain = self.__HEARTBEATS2MIN * self.__MINUTES
                               
            # Get data from RTD-W and Update devices
            for Unit in self.__REGISTERS:
                if Unit[0] == unit.Pump_Running_Hour_Counter:
                    value = self.rs485.read_long(Unit[1], functioncode=Unit[3], signed=Unit[4])
                else:
                    value = self.rs485.read_register(Unit[1], number_of_decimals=Unit[2], functioncode=Unit[3], signed=Unit[4])
##                if Unit[5] == int(__NVALUE):
                if Unit[5] == 0:
                    if Unit[0] == unit.ON_OFF_Command_Space_Heating or Unit[0] == unit.DHW_Reheat_Command:
                        pass
                    elif Unit[0] == unit.ON_OFF_Space_Heating:
                        Devices[Unit[0]].Update( int(value), str(value * 100))
                        Devices[unit.ON_OFF_Command_Space_Heating].Update( int(value), str(value * 100))
                    elif Unit[0] == unit.DHW_Reheat:
                        Devices[Unit[0]].Update( int(value), str(value * 100))
                        Devices[unit.DHW_Reheat_Command].Update( int(value), str(value * 100))
                    else:
                        Devices[Unit[0]].Update( int(value), str(value * 100))
                elif Unit[0] == unit.Shift_Value_Leaving_Water_Temp:
                    Devices[Unit[0]].Update( int(value!=0), str((value+6) * 10))
                elif (Unit[0] == unit.Control_Source):
                    Devices[Unit[0]].Update(int(value!=2), str(value * 10))
                elif Unit[0] == unit.Pump_Running_Hour_Counter:
                    Devices[Unit[0]].Update( 0, str(value)+";0")
                else:
                    Devices[Unit[0]].Update( 0, str(value))
        else:
            Domoticz.Debug( "onHeartbeat - run again in {} heartbeats".format(self.__runAgain) )

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage: {}, {}".format(Connection.Name, Data))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug(
            "onNotification: {}, {}, {}, {}, {}, {}, {}".format(
                Name, Subject, Text, Status, Priority, Sound, ImageFile
            )
        )

    def onStart(self):
        # Debug level
        Domoticz.Debug("onStart")
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
        else:
            Domoticz.Debugging(0)

        #Code
        self.rs485 = minimalmodbus.Instrument(Parameters["SerialPort"], int(Parameters["Mode2"]))
        self.rs485.serial.baudrate = Parameters["Mode1"]
        self.rs485.serial.bytesize = 8
        self.rs485.serial.parity = minimalmodbus.serial.PARITY_NONE
        self.rs485.serial.stopbits = 1
        self.rs485.serial.timeout = 1
        self.rs485.debug = False
            
        self.rs485.mode = minimalmodbus.MODE_RTU
        devicecreated = []
        Domoticz.Log("DAIKIN RTD-W Modbus plugin start")

        #
        # Validate parameters
        #
##        # Check if images are in database
##        if "xfr_template" not in Images:
##            Domoticz.Image("xfr_template.zip").Create()
##        try:
##            image = Images["xfr_template"].ID
##        except:
##            image = 0
##        Domoticz.Debug("Image created. ID: " + str(image))
        #
        # Create devices
        for Unit in self.__UNITS:
            if Unit[0] not in Devices:
                if Unit[2] is None:
                    Domoticz.Device(
                        Unit=Unit[0],
                        Name=Unit[1],
                        Type=Unit[3],
                        Subtype=Unit[4],
                        Switchtype=Unit[5],
                        Options=Unit[6],
                        Used=Unit[7],
                        Description=Unit[8]
                    ).Create()
                else:
                    Domoticz.Device(
                        Unit=Unit[0],
                        Name=Unit[1],
                        TypeName=Unit[2],
#                        Switchtype=Unit[5],
                        Options=Unit[6],
                        Used=Unit[7],
                        Description=Unit[8]
                    ).Create()
        #
        # Log config
        DumpConfigToLog()
        #
        # Connection

    def onStop(self):
        Domoticz.Debug("onStop")


global _plugin
_plugin = BasePlugin()


def onStart():
    global _plugin
    _plugin.onStart()


def onStop():
    global _plugin
    _plugin.onStop()


def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)


def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)


def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)


def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)


def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)


def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()


################################################################################
# Generic helper functions
################################################################################
def DumpConfigToLog():
    # Show parameters
    Domoticz.Debug("Parameters count.....: " + str(len(Parameters)))
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("Parameter '" + x + "'...: '" + str(Parameters[x]) + "'")
        # Show settings
        Domoticz.Debug("Settings count...: " + str(len(Settings)))
    for x in Settings:
        Domoticz.Debug("Setting '" + x + "'...: '" + str(Settings[x]) + "'")
    # Show images
    Domoticz.Debug("Image count..........: " + str(len(Images)))
    for x in Images:
        Domoticz.Debug("Image '" + x + "...': '" + str(Images[x]) + "'")
    # Show devices
    Domoticz.Debug("Device count.........: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device...............: " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device Idx...........: " + str(Devices[x].ID))
        Domoticz.Debug(
            "Device Type..........: "
            + str(Devices[x].Type)
            + " / "
            + str(Devices[x].SubType)
        )
        Domoticz.Debug("Device Name..........: '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue........: " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue........: '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device Options.......: '" + str(Devices[x].Options) + "'")
        Domoticz.Debug("Device Used..........: " + str(Devices[x].Used))
        Domoticz.Debug("Device ID............: '" + str(Devices[x].DeviceID) + "'")
        Domoticz.Debug("Device LastLevel.....: " + str(Devices[x].LastLevel))
        Domoticz.Debug("Device Image.........: " + str(Devices[x].Image))


def UpdateDevice(Unit, nValue, sValue, TimedOut=0, AlwaysUpdate=False):
    if Unit in Devices:
        if (
            Devices[Unit].nValue != nValue
            or Devices[Unit].sValue != sValue
            or Devices[Unit].TimedOut != TimedOut
            or AlwaysUpdate
        ):
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue), TimedOut=TimedOut)
            Domoticz.Debug(
                "Update "
                + Devices[Unit].Name
                + ": "
                + str(nValue)
                + " - '"
                + str(sValue)
                + "'"
            )


def UpdateDeviceOptions(Unit, Options={}):
    if Unit in Devices:
        if Devices[Unit].Options != Options:
            Devices[Unit].Update(
                nValue=Devices[Unit].nValue,
                sValue=Devices[Unit].sValue,
                Options=Options,
            )
            Domoticz.Debug(
                "Device Options update: " + Devices[Unit].Name + " = " + str(Options)
            )


def UpdateDeviceImage(Unit, Image):
    if Unit in Devices and Image in Images:
        if Devices[Unit].Image != Images[Image].ID:
            Devices[Unit].Update(
                nValue=Devices[Unit].nValue,
                sValue=Devices[Unit].sValue,
                Image=Images[Image].ID,
            )
            Domoticz.Debug(
                "Device Image update: "
                + Devices[Unit].Name
                + " = "
                + str(Images[Image].ID)
            )


def DumpHTTPResponseToLog(httpDict):
    if isinstance(httpDict, dict):
        Domoticz.Debug("HTTP Details (" + str(len(httpDict)) + "):")
        for x in httpDict:
            if isinstance(httpDict[x], dict):
                Domoticz.Debug("....'" + x + " (" + str(len(httpDict[x])) + "):")
                for y in httpDict[x]:
                    Domoticz.Debug("........'" + y + "':'" + str(httpDict[x][y]) + "'")
            else:
                Domoticz.Debug("....'" + x + "':'" + str(httpDict[x]) + "'")

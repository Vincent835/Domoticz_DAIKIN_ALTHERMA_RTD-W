# Domoticz_DAIKIN_ALTHERMA_RTD-W
## Plugin for DAIKIN ALTHERMA HT with RTD-W module

Control your ALTHERMA HT
* Monitor temperatures, Compressor, Defrost, Running Hours Accumulated,
* Command Heating, Domestic Hot Water storage, Quiet mode,
* Set Room Temperature Setpoint,
* Shift value leaving water temperature Setpoint.

The RTD-W is a monitoring and control interface for Altherma HT hydroboxes (heating only and reversible), small inverter chillers (EWA/YQ16..64 series) and VRV heating only hydrobox.<br>
The interface is compatible with all units that are operated using a BRC21 remote controller network connection and allows control of up to 16 units in a single group.<br>
Note: this plugin is intended for a single RTD-W at address 1, with a single unit.<br>

## Requirements: <br>
* Working Domoticz instance with working python plugin service (see logs in domoticz)<br>
  If python plugin service is not working try "sudo apt-get install python3.7 libpython3.7 python3.7-dev -y"<br>
* Python module minimalmodbus -> http://minimalmodbus.readthedocs.io/en/master/<br>
        (pi@raspberrypi:~$ sudo pip3 install minimalmodbus)<br>
* RTD-W monitoring and control interface for Altherma HT hydroboxes (http://www.realtime-controls.co.uk/index.php/site/multi-language-download/rtd_w_daikin_control_interface)<br>
* Communication module Modbus USB to RS485 converter<br>

## Installation: <br>
cd ~/domoticz/plugins<br>
git clone https://github.com/Vincent835/Domoticz_DAIKIN_ALTHERMA_RTD-W <br>

## Configuration: <br>
Select "DAIKIN ALTHERMA HT (RTD-W Modbus)" in Hardware configuration screen<br>
24 new devices will be automatically added. Go to devices tab, there you can find them.<br>
Some are not set to "used" by default.
Don't forget to restart your Domoticz server.<br>
Tested on domoticz v2020.2


## Change log

| Version | Information|
| ----- | ---------- |
| 0.1.2 | Update Switch selector local/externe/tout |
| 0.1.1 | Sync. switchs heating and reheat DHW status with contacs status|
| 0.1.0 | Initial private upload version |


## Todo list
Test if devices exist before updating them

Done : Correct the state feedback of the heating and DHW heating on / off switches

I noticed that holding register:
* H0004 Modbus ON / OFF space heating or cooling (device 8)
* H0006 Modbus Domestic Hot Water reheat (device 9)<br>
do not correspond to states displayed on Remote controler.
 
The commands transmitted remotely are taken into account.
But the settings made locally do not go back to these registers.<br>
I am waiting for a notice from RealTime Control Systems.

However, devices unit 16 and 22 indicate actual state.

## Used python modules: <br>
pyserial -> https://pythonhosted.org/pyserial/ <br>
minimalmodbus -> http://minimalmodbus.readthedocs.io<br>
# Domoticz_DAIKIN_ALTHERMA_RTD-W
 Plugin for DAIKIN ALTHERMA HT with RTD-W module
------------------------

Requirements: <br>
    1. Working Domoticz instance with working python plugin service (see logs in domoticz)<br>
       If python plugin service is not working try "sudo apt-get install python3.7 libpython3.7 python3.7-dev -y"<br>
    2.python module minimalmodbus -> http://minimalmodbus.readthedocs.io/en/master/
        (pi@raspberrypi:~$ sudo pip3 install minimalmodbus)
    3.RTD-W monitoring and control interface for Altherma HT hydroboxes (http://www.realtime-controls.co.uk/index.php/site/multi-language-download/rtd_w_daikin_control_interface)
    4.Communication module Modbus USB to RS485 converter module

    The RTD-W is a monitoring and control interface for Altherma HT hydroboxes (heating only and reversible),
    small inverter chillers (EWA/YQ16..64 series) and VRV heating only hydrobox.
    The interface is compatible with all units that are operated using a BRC21 remote controller network
    connection and allows control of up to 16 units in a single group.
    Note: this plugin is intended for a single RTD-W at address 1, with a single unit.
<br>
Installation: <br>
cd ~/domoticz/plugins<br>
git clone https://github.com/Vincent835/Domoticz_DAIKIN_ALTHERMA_RTD-W <br>
<br>
Configuration: <br>
Select "DAIKIN ALTHERMA HT (RTD-W Modbus)" in Hardware configuration screen<br>
If needed modify some parameters (defaults will do) and click add<br>
Hint: Set reading interval to 0 if you want updates per "heartbeat" of the system (aprox 10s in my case)<br>
<br>
24 new devices will be automatically added. Go to devices tab, there you can find them<br>
Don't forget to restart your Domoticz server<br>
Tested on domoticz v2020.2
<br><br><br>
Used python modules: <br>
pyserial -> https://pythonhosted.org/pyserial/ <br>
minimalmodbus -> http://minimalmodbus.readthedocs.io<br>

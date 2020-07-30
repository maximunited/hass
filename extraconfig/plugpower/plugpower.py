#!/usr/bin/python
#
# Power Probe - Wattage of smartplugs - JSON Output

import pytuya
from time import sleep
import datetime

# Device Info - EDIT THIS
DEVICEID="03783133cc50e31418c2"
DEVICEIP="192.168.1.111"

# how my times to try to probe plug before giving up
RETRY=20

def deviceInfo( deviceid, ip ):
    watchdog = 0
    while True:
        try:
            d = pytuya.OutletDevice(deviceid, ip, '7481489bb8baa9e2')
            data = d.status()
            if(d):
                print('Dictionary %r' % data)
                print('Switch On: %r' % data['dps']['1'])
                if '5' in data['dps'].keys():
                    print('Power (W): %f' % (float(data['dps']['5'])/10.0))
                    print('Current (mA): %f' % float(data['dps']['4']))
                    print('Voltage (V): %f' % (float(data['dps']['6'])/10.0))
                    return(float(data['dps']['5'])/10.0)
                else:
                    return(0.0)
            else:
                return(0.0)
            break
        except KeyboardInterrupt:
            pass
        except:
            watchdog+=1
            if(watchdog>RETRY):
                print("ERROR: No response from plug %s [%s]." % (deviceid,ip))
                return(0.0)
            sleep(2)

print("Polling Device %s at %s" % (DEVICEID,DEVICEIP))

devicepower = deviceInfo(DEVICEID,DEVICEIP)



# weewx ObserverIP driver

This is an ObserverIP driver for the weewx platform. Since the Ambient Weather WS-1200-IP and WS-1400-IP don't offer a way to update any weather services other than Weather Underground, this driver simply grabs the values from the ObserverIP's tiny website and then sends the values to weewx. 

This driver relies on you setting a static IP for your ObserverIP. 

You can configure the loop time, and the IP of the device. 

## Install
- Copy the driver observerip.py to the weewx driver folder. For my CentOS install it's located at `/usr/share/weewx/weewx/drivers`
- Copy the text in the `weewx.conf` here to your `weewx.conf`
- Modify the configuration in `weewx.conf` to update the IP and hardware description
- Restart weewx

### Version
1.0 - Initial

### Warranty

There is none. It's a bit buggy right now. The driver may cause your weewx to crash if the ObserverIP is rebooted, or otherwise slowed down (the ObserverIP is not a very strong device).

If weewx crashes, that means your data is not being logged. 

I'm open to pull requests to make this better!

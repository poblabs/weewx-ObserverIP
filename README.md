# weewx ObserverIP driver

This is my take on an ObserverIP driver for the weewx platform. There are a couple of other ones out there, too. Since the Ambient Weather WS-1200-IP and WS-1400-IP don't offer a way to update any weather services other than Weather Underground, this driver simply grabs the values from the ObserverIP's tiny website and then sends the values to weewx. Once weewx has the data, then you can have weewx update CWOP, PWSWeather, WeatherBug and more. 

This driver relies on you setting a static IP for your ObserverIP. 

You can configure the loop time, and the IP of the device from weewx.conf.

## Important Notice
During my testing of a LOOP interval at 15 seconds, I've seen that the **screen scraping of the ObserverIP has caused it to lock up, sometimes up to 45 minutes at a time**. The lockup periods were typically only once per day. I believe this is happening because the ObserverIP is not a powerful device, so access it every 15 seconds overloads the tiny device. You could set your LOOP interval to 30 or 60 seconds and may have better results. 

**I've decided to move away from the screen scraping method** and instead I am using a more (slightly advanced) way of getting data off the ObserverIP using a socket server and WeeWX listens on that socket for data. For more details on the project with a detailed write up, check it out here:

Writeup of the new method: http://obrienlabs.net/redirecting-weather-station-data-from-observerip/

Driver for the new method: https://github.com/poblabs/weewx-socketlogger

## Install
- You'll need to have the Python requests library installed (It can be installed from command line. For example: `pip install requests`)
- Copy the observerip.py driver to the `bin/user` folder (For my CentOS install it's located at `/usr/share/weewx/user`)
- Copy the text snippets from the `weewx.conf` here to your `weewx.conf`
- Modify the configuration in `weewx.conf` to update the IP and hardware description
- Restart weewx

## Version
1.0 - Initial

## Warranty

There is no warranty that this will work. Admittedly, it's a bit buggy right now. The driver may cause your ObserverIP to lock up. It may also cause weewx to crash if the ObserverIP is rebooted, or otherwise slowed down (the ObserverIP is not a very strong device). If weewx crashes, then no data is being captured, which means your data is not being logged and you're not updating any weather services.

I would suggest the socket method outlined above. It's a little more work, but much more reliable than screen scraping. 

If you see a bug, or a way to make this better, send a pull request!


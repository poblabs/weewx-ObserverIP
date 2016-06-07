# $Id: pobwx.py 2766 2014-12-02 02:45:36Z tkeffer $
# Copyright (c) 2012 Tom Keffer <tkeffer@gmail.com>
# See the file LICENSE.txt for your full rights.
""" weewx Driver for the Ambient Weather ObserverIP

	Pat O'Brien
	https://github.com/poblabs/weewx-ObserverIP
	
"""

from __future__ import with_statement
from lxml import html
import math, time, syslog, requests

import weedb
import weewx.drivers
import weeutil.weeutil
import weewx.wxformulas

DRIVER_NAME = 'ObserverIP'
DRIVER_VERSION = '1.0'

def loader(config_dict, engine):
	station = ObserverIP(**config_dict['ObserverIP'])
	return station
		
class ObserverIP(weewx.drivers.AbstractDevice):
	"""Custom driver for Ambient Weather ObserverIP. Mostly based off Simulator """
	
	def __init__(self, **stn_dict):
		self.loop_interval = float(stn_dict.get('loop_interval'))
		
		self.station_ip = stn_dict.get('ip_address')
		self.station_url = "http://%s/livedata.htm" % self.station_ip
		
		self.station_hardware = stn_dict.get('hardware')
		
		self.lastrain = None
		
	def getTime(self):
		# The ObserverIP doesn't do seconds, so using the time from the ObserverIP
		# with a loop packet of every 15 seconds is useless. All measurements will be archived
		# from the same minute timestamp, even though the values could be different within the same minute. 
		# This method uses mwall's method from his fork of ObserverIP
		epoch = int(time.time() + 0.5 )
		return epoch
	
	def hardware_name(self):
		return self.station_hardware
		
	def get_battery_status(self, data):
		if (data == "Normal"):
			return 0
		else:
			return 1
			
	def check_rain(self, data):
		# Handle the rain accum by taking the Daily Rain reading and only submitting the increments
		rain = 0.0
		current_rain = float(data)
		if self.lastrain is not None:
			if (current_rain >= self.lastrain):
				#print "Checking for new rain accumulation"
				rain = float(current_rain) - float(self.lastrain)
		self.lastrain = current_rain
		return rain

	def genLoopPackets(self):

		while True:				
			# Screen scrape the ObserverIP to get sensor readings.
			try:
				page = requests.get(self.station_url)
				tree = html.fromstring(page.content)
				
				# Can weewx take this value?
				#uvi = tree.xpath('//input[@name="uvi"]')[0].value
				inBattery = tree.xpath('//input[@name="inBattSta"]')[0].value
				outBattery = tree.xpath('//input[@name="outBattSta1"]')[0].value
				inTemp = tree.xpath('//input[@name="inTemp"]')[0].value
				inHumid = tree.xpath('//input[@name="inHumi"]')[0].value
				outTemp = tree.xpath('//input[@name="outTemp"]')[0].value
				outHumid = tree.xpath('//input[@name="outHumi"]')[0].value
				absPressure = tree.xpath('//input[@name="AbsPress"]')[0].value
				relPressure = tree.xpath('//input[@name="RelPress"]')[0].value
				windDir = tree.xpath('//input[@name="windir"]')[0].value
				windSpeed = tree.xpath('//input[@name="avgwind"]')[0].value
				windGust = tree.xpath('//input[@name="gustspeed"]')[0].value
				solarRadiation = tree.xpath('//input[@name="solarrad"]')[0].value
				uv = tree.xpath('//input[@name="uv"]')[0].value
				dailyRainAccum = tree.xpath('//input[@name="rainofdaily"]')[0].value

			except Exception as e:
				syslog.syslog("ObserverIP driver couldn't access the livedata.htm webpage.")
				syslog.syslog("Error caught was: %s" % e)
				pass # Continue without exiting. TODO: Better error handling and error sleeping
				
			# Build the packet data
			try:
				_packet = { 
					'dateTime' : self.getTime(),
					'usUnits' : weewx.US,
					'outTemp' : float(outTemp),
					'outHumidity' : float(outHumid),
					'inTemp' : float(inTemp),
					'inHumidity' : float(inHumid),
					'pressure' : float(relPressure),
					'barometer' : float(absPressure),
					'rain': self.check_rain(dailyRainAccum),
					'windDir' : float(windDir),
					'windSpeed' : float(windSpeed),
					'windGust' : float(windGust),
					'radiation' : float(solarRadiation),
					'UV' : float(uv),
					'outTempBatteryStatus' : self.get_battery_status(outBattery),
					'inTempBatteryStatus' : self.get_battery_status(inBattery)
				}

				yield _packet
			except Exception as e:
				syslog.syslog("ObserverIP driver had an error yielding data packet to weewx.")
				syslog.syslog("Error caught was: %s" % e)
				pass # Continue without exiting. TODO: Better error handling and error sleeping
			
			# Sleep time
			#syslog.syslog("Sleeping for %s" % self.loop_interval)
			time.sleep(self.loop_interval)

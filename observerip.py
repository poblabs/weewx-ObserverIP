# $Id: pobwx.py 2766 2014-12-02 02:45:36Z tkeffer $
# Copyright (c) 2012 Tom Keffer <tkeffer@gmail.com>
# See the file LICENSE.txt for your full rights.
"""weewx Driver for the Ambient Weather ObserverIP

	Pat O'Brien
	Changelog: v1.0
		December 28, 2015
		Initial attempt
	
"""

from __future__ import with_statement
from lxml import html
import math, time, syslog, requests

import weedb
import weewx.drivers
import weeutil.weeutil
import weewx.wxformulas


def loader(config_dict, engine):

	station = observerip(**config_dict['observerip'])
	return station
		
class observerip(weewx.drivers.AbstractDevice):
	"""Custom driver for Ambient Weather ObserverIP. Mostly based off Simulator """
	
	def __init__(self, **stn_dict):
		self.loop_interval = float(stn_dict.get('loop_interval'))
		
		self.station_ip = stn_dict.get('ip_address')
		self.station_url = "http://%s/livedata.htm" % self.station_ip
		
		self.station_hardware = stn_dict.get('hardware')
		
	def get_station_time(self):
		page = requests.get(self.station_url)
		tree = html.fromstring(page.content)

		stationTime = tree.xpath('//input[@name="CurrTime"]')[0].value
		pattern = '%H:%M %m/%d/%Y'
		station_time_epoch = int(time.mktime(time.strptime(stationTime, pattern)))
		return station_time_epoch

	def getTime(self):
		# Get the station time.
		#return time.time()
		return self.get_station_time()
	
	def hardware_name(self):
		return self.station_hardware

	def genLoopPackets(self):

		while True:				
			# Screen scrape the ObserverIP to get sensor readings. Some help from:
			try:
				page = requests.get(self.station_url)
			except Exception as e:
				syslog.syslog("ObserverIP driver couldn't access the livedata.htm webpage.")
				syslog.syslog("Error caught was: %s" % e)
				pass # Continue without exiting

			tree = html.fromstring(page.content)

			#inBattery = tree.xpath('//input[@name="inBattSta"]')[0].value
			#outBattery = tree.xpath('//input[@name="outBattSta1"]')[0].value
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
			#uvi = tree.xpath('//input[@name="uvi"]')[0].value

			rainHourly = tree.xpath('//input[@name="rainofhourly"]')[0].value
			
			# Build the packet data
			try:
				_packet = { 
					#'dateTime': int(time.time() + 0.5),
					#'outTempBatteryStatus' : str(outBattery),
					#'inTempBatteryStatus' : str(inBattery),
					'dateTime' : self.get_station_time(),
					'usUnits' : weewx.US,
					'outTemp' : float(outTemp),
					'outHumidity' : float(outHumid),
					'inTemp' : float(inTemp),
					'inHumidity' : float(inHumid),
					'pressure' : float(relPressure),
					'barometer' : float(absPressure),
					'rain': float(rainHourly),
					'windDir' : float(windDir),
					'windSpeed' : float(windSpeed),
					'windGust' : float(windGust),
					'radiation' : float(solarRadiation),
					'UV' : float(uv)
				}

				yield _packet
			except Exception as e:
				syslog.syslog("ObserverIP driver had an error yielding data packet to weewx. The ObserverIP unit may have been rebooting. Will follow sleep routine and try again.")
				syslog.syslog("Error caught was: %s" % e)
				#pass # Continue without exiting
			
			# Sleep time
			#syslog.syslog("Sleeping for %s" % self.loop_interval)
			start_time = time.time()
			sleep_time = (start_time - time.time()) + self.loop_interval
			if sleep_time > 0:
				  time.sleep(sleep_time)

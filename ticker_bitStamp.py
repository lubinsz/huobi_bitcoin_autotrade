#!/usr/bin/python
# -*- coding: utf-8 -*-

# query price data from BTCChina.

import urllib2
import json 
import socket 

timeout = 40

socket.setdefaulttimeout(timeout)

def instance_ticker():
    # returns something like {"high":738.88,"low":689.10,"buy":713.50,"sell":717.30,"last":717.41,"vol":4797.32000000}
  try:
    remote_file = urllib2.urlopen('https://www.bitstamp.net/api/ticker/')
    remote_data = remote_file.read()
    remote_file.close()
    remote_data = json.loads(remote_data)
#    print remote_data
    return remote_data
  except Exception, e:
    return  False 

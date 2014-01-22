#!/usr/bin/env python
import urllib
import urllib2
import cookielib
import sys
import io
import json
import os

# App directory
localDir = os.path.expanduser("~") + "/.local/share/magtifun"
localAuthFile = localDir + "/credentials.json"

# URLs used in requests
reqUrls = dict(
	login = 'http://www.magtifun.ge/index.php?page=11&lang=ge',
	send  = 'http://www.magtifun.ge/scripts/sms_send.php')

# CookieJar and opener
cookieJar = cookielib.CookieJar()
opener = urllib2.build_opener(
	urllib2.HTTPCookieProcessor(cookieJar))
urllib2.install_opener(opener)

# Command router
def routeCommand(cmd):
	if (cmd == 'login'):
		username = raw_input("Enter username: ")
		password = raw_input("Enter password: ")
		login(username, password)
	elif (cmd == 'logout'):
		logout()
	elif (cmd == 'send'):
		# Get number and message
		# this is first variant, without '--to', '--msg'
		try:
			number  = sys.argv[2]
			message = sys.argv[3]
		except IndexError:
			error("Number and/or message is not defined")
			print "type 'magtifun --help' for help"
		else:
			sendSms(number, message)
	else:
		error("Invalid operation " + cmd)
	return

def sendSms(number, message):
	if not os.path.isfile(localAuthFile):
		if prompt("You are currently logged out. Login?", 1):
			routeCommand('login')
		else:
			return
	number = int(number)
	smsPostData = dict(
		recipients = number,
		message_body = message)
	smsPostDataStr = urllib.urlencode(smsPostData)
	req = urllib2.Request(url_1, data)
	res = urllib2.urlopen(req)
	print res
	return # return boolean status

def login(username, password):
	if not os.path.exists(localDir):
		try:
			os.makedirs(localDir)
		except OSError as exception:
			if exception.errno != errno.EEXIST:
				raise
	authFileData = dict(
		username = username,
		password = password)
	authPostData = dict(
		user = 'username',
		password = 'password',
		act = '1')
	with open(localAuthFile, 'w+') as outFile:
		json.dump(authFileData, outFile)
	authPostDataStr = urllib.urlencode(authPostData)
	req = urllib2.Request(reqUrls['login'], authPostDataStr)
	res = urllib2.urlopen(req)
	# TODO check if login was successfull
	return # return boolean login status

def logout():
	if os.path.isfile(localAuthFile):
		os.remove(localAuthFile) # TODO make this silent
	else:
		print("Error: %s file not found" % localAuthFile)
	return

def man():
	print """magtifun 0.1.0 for Linux
Usage: magtifun send number message
       magtifun command [options]

magtifun is a simple command line interface for sending short text messages via Magti's free sms servce called MagtiFun.
	"""
	return

# Display an error
def error(message):
	print "E: " + message
	return

def prompt(message, defaultY):
	opts = " [Y/n]" if defaultY else " [y/N]"
	answer = raw_input(message + opts)
	if defaultY:
		return (answer <> "N" and answer <> "n")
	else:
		return (answer == "Y" or answer == "y")

############
# Main point
try:
	inCmd = sys.argv[1]
except IndexError:
	man()
else:
	routeCommand(inCmd)
finally:
	pass
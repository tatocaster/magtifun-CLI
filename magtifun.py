#!/usr/bin/env python
import urllib
import urllib2
import cookielib
import sys
import io
import json
import os
import getpass
import base64

# App directory
localDir = os.path.expanduser("~") + "/.local/share/magtifun"
localAuthFile = localDir + "/credentials.json"
logData = False; # Set this True for development

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
	log("routing command: " + cmd)
	if (cmd == 'login'):
		username = raw_input("Enter username: ")
		# password = raw_input("Enter password: ")
		password = getpass.getpass("password: ")
		log("auth input: " + username + ":" + password)
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
			log("trying to send message '" + message + "' to " + number)
			sendSms(number, message)
	else:
		error("Invalid operation " + cmd)
	return

def sendSms(number, message):
	log("entered sendSms()")
	if not os.path.isfile(localAuthFile):
		if prompt("You are currently logged out. Login?", 1):
			log("logged out. going to relogin")
			routeCommand('login')
		else:
			log("logged out. no relogin. exiting")
			return
	authFileSource = open(localAuthFile, 'r')
	authFileDict = json.load(authFileSource)
	authFileSource.close()
	try:
		authUser = authFileDict["username"]
		authPass = authFileDict["password"]
	except KeyError:
		if prompt("Corrupt authorization data. Relogin?", 1):
			log("corrupt. going to relogin")
			routeCommand('login')
			log("corrupt relogined. preparing to resend")
			sendSms(number, message)
			log("resending finished")
			return
		else:
			log("corrupt. no relogin. exiting")
			return
	log("pre-send login")
	login(authUser, authPass)
	log("pre-send login finished")
	number = int(number)
	smsPostData = dict(
		recipients = number,
		message_body = message)
	log("sending")
	smsPostDataStr = urllib.urlencode(smsPostData)
	req = urllib2.Request(reqUrls['send'], smsPostDataStr)
	res = urllib2.urlopen(req).read()
	log("responce: " + res)
	if (res == "not_logged_in"):
		if prompt("Server session expired. Relogin?", 1):
			log("session expired. going to relogin")
			routeCommand('login')
			sendSms(number, message)
			return
		else:
			log("session expired. no relogin. exiting")
			return
	elif (res == "success"):
		log("sent")
	return # return boolean status

def login(username, password):
	if not os.path.exists(localDir):
		log("no app dir in .local/share")
		try:
			log("creating app dir in .local/share")
			os.makedirs(localDir)
		except OSError as exception:
			if exception.errno != errno.EEXIST:
				log("local dir creating failed")
				raise
	authFileData = dict(
		username = username,
		password = password)
	# authFileData = dict(     need to decode . or  md5 will be fine
	# 	username = base64.b64encode(username),
	# 	password = base64.b64encode(password))
	authPostData = dict(
		user = username,
		password = password,
		act = '1')
	log("reading auth data from file")
	with open(localAuthFile, 'w+') as outFile:
		json.dump(authFileData, outFile)
	authPostDataStr = urllib.urlencode(authPostData)
	log("sending login request: " + authPostDataStr)
	reqLogin = urllib2.Request(reqUrls['login'], authPostDataStr)
	resLogin = urllib2.urlopen(reqLogin)
	log("login finished")
	# TODO check if login was successfull
	return # return boolean login status

def logout():
	if os.path.isfile(localAuthFile):
		log("deleting auth file")
		os.remove(localAuthFile) # TODO make this silent
	else:
		log("file doesn't exist")
		print("Error: %s file not found" % localAuthFile)
	return

def man():
	print """magtifun 0.1.1 for Linux
Usage: magtifun login|logout|send
       magtifun send number message
       magtifun command [options]

magtifun is a simple command line interface for sending
short text messages via free sms servce called MagtiFun.
	"""
	return

# Display an error
def error(message):
	print "E: " + message
	return

def prompt(message, defaultY):
	opts = " [Y/n]" if defaultY else " [y/N] "
	answer = raw_input(message + opts)
	if defaultY:
		return (answer <> "N" and answer <> "n")
	else:
		return (answer == "Y" or answer == "y")

def log(message):
	if not logData:
		return
	print "[LOG] " + message

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
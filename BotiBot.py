#!/usr/bin/python
################################################################################################
# Name: 		Boti
#
# Beschreibung:	Telegram Bot
#               Erlaubte Chat_ID's und Token muss in token.json eingetragen werden               
#
# Version: 		1.4.0
# Author: 		Stefan Mayer
# Author URI: 	http://www.2komma5.org
# License: 		GPL2
# License URI: 	http://www.gnu.org/licenses/gpl-2.0.html
################################################################################################
# Changelog 
# 1.0.0 - 	Initial release
# 1.1.0 -   Camera Pi - Foto
# 1.2.0 -	Video sudo apt-get install gpac
# 1.3.0 -	Refactoring to python-telegram-bot 3.0
# 1.4.0 -   Auslagerung der Security Daten (Token, erlaubte ChatID)
################################################################################################
import sys
import logging
import subprocess 
import json
import time
import datetime as dt
import picamera
import telegram
from subprocess import call
from classes.weather import Weather
from classes.sensor import Sensor
from telegram import Updater

JSON_File = path + "/files/token.json"
picture = '/home/pi/klimamonitor/files/Wetter.jpg'
video_file = '/home/pi/klimamonitor/files/video.h264'
mp4 = '/home/pi/klimamonitor/files/video.mp4'
camera = picamera.PiCamera()
camera.vflip = True
camera.hflip = True

# Enable logging
root = logging.getLogger()
root.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = \
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

logger = logging.getLogger(__name__)

# helper functions
def readJSONData():
	with open(JSON_File) as data_file:    
		data = json.load(data_file)
	print data
	return data
	
def getForecastText(forecast):
	if forecast == 6:
		 text = "sonnig"
	elif forecast == 5:
		text = "heiter"
	elif forecast == 4:
		text = "bewoelkt"
	elif forecast == 3:
		text = "bedeckt"
	elif forecast == 2:
		text = "wechselhaft"
	elif forecast == 1:
		text = "vereinzelt Regen"
	elif forecast == 0:
		text = "Regen"
	elif forecast == -1:
		text = "Gewitter"
	else:
		text ="else"
	return text
	
def getForecastIcon(forecast):
	if forecast == 6:
		 icon = telegram.Emoji.SUN_WITH_FACE
	elif forecast == 5:
		icon = telegram.Emoji.SUN_BEHIND_CLOUD
	elif forecast == 4:
		icon = telegram.Emoji.SUN_BEHIND_CLOUD
	elif forecast == 3:
		icon = telegram.Emoji.CLOUD
	elif forecast == 2:
		icon = telegram.Emoji.CLOUD
	elif forecast == 1:
		icon = telegram.Emoji.UMBRELLA_WITH_RAIN_DROPS
	elif forecast == 0:
		icon = telegram.Emoji.UMBRELLA_WITH_RAIN_DROPS
	elif forecast == -1:
		icon = telegram.Emoji.HIGH_VOLTAGE_SIGN
	else:
		icon ="else"
	return icon	
	
def getWeather():
	weatherInst = Weather()
	sensorInst = Sensor()
	# Get sensor data
	hum  = sensorInst.getHumData()
	temp =  sensorInst.getTempData()
	pressure = sensorInst.getPressData()
	forecast,trend = weatherInst.checkForecast()

	text = "Vorhersage: " + getForecastText(forecast) + " " + getForecastIcon(forecast) + "\nTrend: " + trend + "\nLuftdruck = %.2f hPa" % pressure + "\nrel Feuchte = %.2f " % hum  + "\nTemperatur = %.2f C" % temp
	return text 

# check chat ID in list		
def check_chat_id(bot, update):
	ok_list = sec["ChatId"]
	print "ChatID", update.message.chat_id
	if update.message.chat_id in ok_list:
		bot.sendMessage(update.message.chat_id, text='Hallo ' + str(update.message.from_user.first_name)+ ', Boti wird Dir gleich antworten')
		bol = True
	else:
		bol = False
		bot.sendMessage(chat_id=update.message.chat_id, text='Invalid Chat Id')
		bot.sendMessage(chat_id=sec["ChatId"][0], text='Chat Id: ' + str(update.message.chat_id) + '\n Vorname: ' + str(update.message.from_user.first_name) + ' Nachname: ' + str(update.message.from_user.last_name) + '\n Username: ' + str(update.message.from_user.username))
	return bol
		
# command handlers
def	start(bot, update):
	bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
	bot.sendMessage(update.message.chat_id, text='Bot wurde gestartet')
	bot.sendMessage(update.message.chat_id, text='Hilfe \n /wetter - Wettervorhersage \n /bild - aktuelles Bild \n /video - aktuelles Video \n /help - Hilfe')

def	help(bot, update):
	if False == check_chat_id(bot, update):
		return
	bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
	bot.sendMessage(update.message.chat_id, text='Hilfe \n /wetter - Wettervorhersage \n /bild - aktuelles Bild \n /video - aktuelles Video \n /help - Hilfe')

def	wetter(bot, update):
	if False == check_chat_id(bot, update):
		return
	bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
	bot.sendMessage(update.message.chat_id, text=getWeather())
	
def	bild(bot, update):
	if False == check_chat_id(bot, update):
		return
	bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
	pic_time = dt.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
	camera.annotate_text = pic_time
	#camera.iso = 800
	try:
		camera.capture(picture)
		time.sleep(5)
		photo = open(picture, 'rb')
		bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
		bot.sendPhoto(chat_id=update.message.chat_id, photo=photo)
		photo.close()
		bot.sendMessage(update.message.chat_id, text=pic_time)
	except:
		bot.sendMessage(update.message.chat_id, text='Cam Error')
	
def video(bot, update):
	if False == check_chat_id(bot, update):
		return
	bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
	vid_time = dt.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
	camera.annotate_text = vid_time
	try:
		camera.start_recording(video_file)
		bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.RECORD_VIDEO)
		camera.wait_recording(5)
		camera.stop_recording()
		#convert video
		call ('MP4Box -fps 30 /home/pi/klimamonitor/files/video.h264 /home/pi/klimamonitor/files/video.mp4',shell=True)
		#print resultCode
		time.sleep(5)
		stream = open(mp4, 'rb')
		bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.UPLOAD_VIDEO)
		bot.sendVideo(chat_id=update.message.chat_id, video=stream)
		stream.close()
		bot.sendMessage(update.message.chat_id, text=vid_time)
	except:
		bot.sendMessage(update.message.chat_id, text='Cam Error')

def echo(bot, update):
   	if False == check_chat_id(bot, update):
		return
	#bot.sendMessage(update.message.chat_id, text='Papagei Lora: ' + update.message.text)
	
def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))		

def unknown(bot, update):
   bot.sendMessage(chat_id=update.message.chat_id, text="Dieser Befehl ist nicht bekannt. Bitte in /help nachschauen!")
	
def main():
    # security data
	global sec 
	sec = readJSONData()
	#create event handler
	updater = Updater(token = sec["Token"])
	dispatcher = updater.dispatcher
	# register handlers
	dispatcher.addTelegramCommandHandler("start", start)
	dispatcher.addTelegramCommandHandler("help", help)
	dispatcher.addTelegramCommandHandler("bild", bild)
	dispatcher.addTelegramCommandHandler("wetter", wetter)
	dispatcher.addTelegramCommandHandler("video", video)
    	
	# on noncommand
	dispatcher.addUnknownTelegramCommandHandler(unknown)
	dispatcher.addTelegramMessageHandler(echo)
	# Error handler
	dispatcher.addErrorHandler(error)
	#start BOT
	updater.start_polling(timeout=5)
	updater.idle()
	
if __name__ == '__main__':
	main()

	

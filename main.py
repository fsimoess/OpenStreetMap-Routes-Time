import openrouteservice
from openrouteservice.directions import directions
from openrouteservice.isochrones import isochrones
from geopy.geocoders import Nominatim
from geopy import distance
from geopy.distance import vincenty
from telegram.ext import Updater, CommandHandler
import logging

def calculate(start, stop, method):
	nom = Nominatim()
	init = nom.geocode(start)
	end = nom.geocode(stop)
	init_gps = (init.longitude, init.latitude)
	end_gps = (end.longitude, end.latitude)
	meters = " m"

	coords = (init_gps,end_gps)

	client = openrouteservice.Client(key='5b3ce3597851110001cf62481b9fa807fc1b4f01b32cdd8ee727dc99') # Specify your personal API key
	routes = client.directions(coords, profile=method, preference="fastest", units="m", instructions=False)

	dist = routes['routes'][0]['summary']['distance']
	time = routes['routes'][0]['summary']['duration']

	if dist > 1000:
		meters = " km"
		dist = dist/1000
	
	hour = time//3600
	time %= 3660
	minutes = time//60
	time %= 60
	sec = time

	return str(round(dist, 2))+meters, " | ", str(round(hour))+" hours, "+str(round(minutes))+" minutes, "+str(round(sec))+" seconds."

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
    	text="Olá, sou o bot de cálculo de caminho entre dois lugares\nFeito por: Filipe Simões")

def route(bot, update, args):
	text_caps = ' '.join(args)
	text_route = text_caps.split(' - ')
	if len(text_route) > 2:
		bot.send_message(chat_id=update.message.chat_id, text="Erro")

	car_distance = calculate(text_route[0],text_route[1],"driving-car")
	car_distance = "🚗 Distance: "+car_distance[0]+" | Time: "+car_distance[2]
	walk_distance = calculate(text_route[0],text_route[1],"foot-walking")
	walk_distance = "🚶‍♂️ Distance: "+walk_distance[0]+" | Time: "+walk_distance[2]
	bike_distance = calculate(text_route[0],text_route[1],"cycling-regular")
	bike_distance = "🚲 Distance: "+bike_distance[0]+" | Time: "+bike_distance[2]
	
	string = car_distance+"\n\n"+walk_distance+"\n\n"+bike_distance
	bot.send_message(chat_id=update.message.chat_id, text=string)

def help(bot, update):
	bot.send_message(chat_id=update.message.chat_id,
    	text="Para descobrir uma rota, use o formato: \\route Local - Destino\n\nIMPORTANTE: Colocar a cidade primeiro em ambos os campos\n\nEXEMPLO: /route Rio de Janeiro, Copacabana - Rio de Janeiro, Maracana")

updater = Updater('YOUR TOKEN HERE')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
dp = updater.dispatcher
dp.add_handler(CommandHandler('start',start))
dp.add_handler(CommandHandler('route',route,pass_args=True))
dp.add_handler(CommandHandler('help',help))
updater.start_polling()
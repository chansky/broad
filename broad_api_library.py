### API Library ###
import json
import requests
import numpy as np

import graph_list_class as graph

headers = {'Content-Type': 'application/json'}

def handle_bad_status(code, message=""):
	if (len(message)<1):
		return "Something went wrong, status code: {}".format(code)
	else:
		return message

def format_long_form_names(data):
	long_names = ""
	for row in data:
		long_names += row['attributes']['long_name'] + "\n"
	return(long_names[:-1])

def make_api_call(url, message = ""):
	response = requests.get(url, headers=headers)

	if response.status_code == 200:
		decoded_response = json.loads(response.content.decode('utf-8'))
		data = decoded_response['data']
		return data
	else:
		return handle_bad_status(response.status_code)

def get_routes_by_type():
	# choosing to use this url type for a couple of reasons
	# one, modifying the string to pull for other route types is a simple extension of the function
	# two, this url will limit the amount of data being transferred
	url = "https://api-v3.mbta.com/routes?filter[type]=0,1"
	return make_api_call(url)



def get_stop_data(route_id):
	# API choice again between something like:
	# 1) https://api-v3.mbta.com/stops?filter[route]=Green-C VS.
	# 2) https://api-v3.mbta.com/stops?filter[route_type]=0,1
	# 3) fields[stop]
	# This time I am choosing to go with an approach where we make an api call for each stop
	# reason being that without doing this it looks like we'd have to grep to 
	# identify which stops belong to which line wheereas through the api we can provide an 
	# ID for a route and get all stops for that route.
	# This seems a bit more future proof as you would expect that a change in something 
	# as fundamental as the route id would have to be handled throughout the entire api
	url = "https://api-v3.mbta.com/stops?filter[route]={}".format(route_id)
	return make_api_call(url)

def get_all_stops_data(route_data):
	all_stops_data = []
	for row in route_data:
		stops = get_stop_data(row['id'])
		all_stops_data.append({'id':row['id'], 'long_name':row['attributes']['long_name'], 'stops':stops})
	#print(all_stops_data)
	return all_stops_data


def get_route_with_most_stops(data):
	#
	most_stops = 0
	route_name =""
	for row in data:
		if len(row['stops']) > most_stops:
			most_stops = len(row['stops'])
			route_name = row['long_name']
	return "The route with the most stops is {} with {} stops".format(route_name, most_stops)


def get_route_with_fewest_stops(data):
	least_stops = np.Inf
	route_name =""
	for row in data:
		if len(row['stops']) < least_stops:
			least_stops = len(row['stops'])
			route_name = row['long_name']
	return "The route with the fewest stops is {} with {} stops".format(route_name, least_stops)

def get_connecting_routes(data):
	#One option - double for loop, if we see any stop name twice that means that stop connects two or more routes
	# 
	stop_count_dict = {}
	for row in data:
		for stop in row['stops']:
			if stop['attributes']['name'] in stop_count_dict:
				stop_count_dict[stop['attributes']['name']] +=1
			else:
				stop_count_dict[stop['attributes']['name']] = 1

	result = "List if stops that connect two or more routes: \n"
	for stop in stop_count_dict:
		if stop_count_dict[stop] > 1:
			result += "{} connects {} routes \n".format(stop, stop_count_dict[stop])

	return result[:-1], stop_count_dict

def is_stop_valid(s):
	# function that could return whether or not the stop exists
	return True


def explore_route_for_stop(route, stop, data):
	# return true if stop is on route
	for row in data:
		if row['long_name'] == route:
			for s in row['stops']:
				if stop == s['attributes']['name']:
					return True
			return False
	return False


def bfs_two_stops(s1, s2, data):
	# first build graph
	g = graph.Graph()
	for row in data:
		prev_stop = ""
		for stop in row['stops']:
			curr_stop = stop['attributes']['name']
			if(len(prev_stop) > 0 ):
				g.addEdge(prev_stop, curr_stop)
				g.addEdge(curr_stop, prev_stop)
			prev_stop = curr_stop

	path = g.BFS(s1,s2)
	stop_found = False
	route_list = []
	for key_stop in path:
		for row in data:
			for stop in row['stops']:
				curr_stop = stop['attributes']['name']
				if key_stop == curr_stop and row['long_name'] not in route_list:
					for x in route_list:
						if(explore_route_for_stop(x, key_stop, data) == False):
							route_list.append(row['long_name'])
							stop_found = True
							break
						else:
							stop_found = True
							break
					if(len(route_list) < 1):
						route_list.append(row['long_name'])
						stop_found = True
						break
			if(stop_found):
				stop_found = False
				break

	solution = ""
	for route in route_list:
		solution = solution + route + " --> "
	print(solution[:-5])
	return solution

	# so now what we should do is get all the unique routes of the stops included in the path



#exercise for extension - add in commuter rail or bus routes
#exercise for extension - what if a stop is removed or closed



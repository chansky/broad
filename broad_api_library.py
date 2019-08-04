### API Library ###
import json
import requests
import numpy as np

import graph_list_class as graph

headers = {'Content-Type': 'application/json'}

class ListNode:
	def __init__(self, data):
		# store data
		self.data = data
		# store reference (next item)
		self.next = None
		return

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
	return True


def explore_route_for_stop(route, stop, data):
	# return true if stop is on route
	route_data = data[route]
	for s in route_data:
		if s == stop:
			return True
	return False


def get_routes_connected_to_this_route(route, data):
	# return the list of routes that connect to input route
	route_data = data[route]
	connected_routes = []
	for stop in route_data:
		for stop in row['stops']:
			for row in data:
				if row['long_name'] != route:
					if(explore_route_for_stop(row['long_name'], stop)):
						connected_routes.append(row['long_name'])
	return connected_routes

def are_two_routes_connected(r1, r2, data):
	r1_stops = data[r1]
	r2_stops = data[r2]
	for stop in r1_stops:
		if stop in r2_stops:
			return True
	return False



def bfs_two_stops(s1, s2, data):
	# first build graph
	g = graph.Graph()
	for row in data:
		i=1
		prev_stop = ""
		for stop in row['stops']:
			curr_stop = stop['attributes']['name']
			if(len(prev_stop) > 0 ):
				g.addEdge(prev_stop, curr_stop)
				g.addEdge(curr_stop, prev_stop)
			prev_stop = curr_stop

	path = g.BFS(s1,s2)
	print(path)



def get_rail_route_given_stops(s1, s2, data):
	# initial thoughts
	# 1 -> could have a function that checks if the two input stops are valid (ie they exist)
	# 2 -> could first see if the two stops are on the same route
	# 3 -> if not 2, then 
	# find the route the first stop exists on:
	# if second stop is on route (case 2) then done and return this route
	# otherwise find all routes connected to this route
	# see if stop is on any of those connected routes
	# continue to explore all new connections until all stops have been visited
	# return the set of routes 

	# first check if stops on the same route
	lines_needed = {}
	for row in data:
		for stop in row['stops']:
			if stop['attributes']['name'] == s1:
				# found route with starting stop
				lines_needed['s1'] = row['long_name']
			if stop['attributes']['name'] == s2:
				# found route with ending stop
				lines_needed['s2'] = row['long_name']
		if (lines_needed['s1'] == lines_needed['s2']):
			return lines_needed['s1']
	# since the above finds us the routes the start and end exist on, if they are connected
	# then we are also done
	if (are_two_routes_connected(lines_needed['s1'], lines_needed['s2'])):
		return lines_needed['s1'] + '-->' + lines_needed['s2']

	# otherwise we now have a dictionary with the two stops and the routes they are on
	# stop when final_connection_route = s2 route
	lines_needed['final_connection'] = ''
	explored_lines = [lines_needed['s1'], lines_needed['s2']]
	lines_to_explore = get_routes_connected_to_this_route(lines_needed['s1'], data)
	while(lines_needed['final_connection'] != lines_needed['s2'] and len(explored_lines) < len(data) and len(lines_to_explore) > 0):
		route = lines_to_explore.pop()
		explored_lines.append(route)
		if (are_two_routes_connected(route, lines_needed['s2'])):
			lines_needed['final_connection'] = route
			break
		else:
			routes_to_explore = get_routes_connected_to_this_route(route)
			lines_needed[route] = route
			for new_route in routes_to_explore:
				# only expore routes we have not looked at already
				if new_route not in explored_lines:
					lines_to_explore.append(new_route)

	if (lines_needed['final_connection'] == lines_needed['s2']):
		solution = ""
		for route in lines_needed:
			solution = route + " -->"
		return solution
	else:
		return 'no route exists'




#exercise for extension - add in commuter rail or bus routes



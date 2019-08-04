### Broad API Assignment ###

import broad_api_library as lib

### QUESTION 1
# subway_results = lib.get_routes_by_type()
# route_names = lib.format_long_form_names(subway_results)
# print(route_names)


### QUESTION 2
# part 1
subway_results = lib.get_routes_by_type()
get_stop_data = lib.get_all_stops_data(subway_results)
# print(lib.get_route_with_most_stops(get_stop_data))

# part 2
#print(lib.get_route_with_fewest_stops(get_stop_data))

# part 3
#print(lib.get_connecting_routes(get_stop_data)[0])


### QUESTION 3
stop_1 = "Alewife"
stop_2 = "Ruggles"
#lib.get_rail_route_given_stops(stop_1, stop_2, get_stop_data)
path = lib.bfs_two_stops(stop_1, stop_2, get_stop_data)



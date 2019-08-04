class Node:
	def __init__(self,val, route):
		self.value = val
		self.children = []
		self.route = route
		self.parent = None
		#init Node class so we can pass in values as nodes and set children to empty list

    def add_child(self, obj):
		self.children.append(obj)
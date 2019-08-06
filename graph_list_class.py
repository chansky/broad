from collections import defaultdict 

# This class represents a directed graph 
# using adjacency list representation 
class Graph: 

	# Constructor 
	def __init__(self): 
		# default dictionary to store graph 
		self.graph = defaultdict(list) 
  
	# function to add an edge to graph 
	def addEdge(self,u,v): 
		self.graph[u].append(v)

	def BFS(self, s, e):
		# Mark all the vertices as not visited 
		#visited = [False] * (len(self.graph)) 
  
		# Create a queue for BFS 
		queue = [] 
  
		# Mark the source node as  
		# visited and enqueue it 
		queue.append([s])
		visited = {}
		visited[s] = True

		while queue:
			#print(queue)
			path = queue.pop(0) 
			#print(path)
			node = path[-1]
			if (e == node):
				return path
  
			# Get all adjacent vertices of the 
			# dequeued vertex node. If a adjacent 
			# has not been visited, then mark it 
			# visited and enqueue it 
			for i in self.graph[node]: 
				if i not in visited: 
					visited[i] = True
					new_path = list(path)
					new_path.append(i)
					queue.append(new_path)



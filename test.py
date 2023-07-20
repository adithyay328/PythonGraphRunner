from pythongraphrunner.TaskGraph import *

# This is the adder test
# OK, now testing
class Number(ItemBase):
  def __init__(self):
    super().__init__("empty", "done", None)
    self.val = 0

# Defining our task graph, and adding all states
taskGraph : TaskGraph[Number] = TaskGraph()
taskGraph.addStates( ["empty", "add", "print", "done"] )

# Adding all our edges
def emptyEdgeHandler(x : Number) -> str:
  return "add"

emptyEdge : TaskEdge[Number] = TaskEdge( ["empty"], ["add"], [], emptyEdgeHandler)

def addEdgeHandler(x : Number) -> str:
  x.val += 1
  return "print"

addEdge : TaskEdge[Number] = TaskEdge( ["add"], ["print"], [], addEdgeHandler)

def printEdgeHandler(x : Number) -> str:
  print(x.val)
  print("Done!")
  return "done"

printEdge : TaskEdge[Number] = TaskEdge( ["print"], ["done"], [], printEdgeHandler)

# Adding all edges to the graph
taskGraph.addEdges( [emptyEdge, addEdge, printEdge] )

# Adding all items
item1 = Number()
taskGraph.addItem(item1)

# Run fix
taskGraph.fixItems()
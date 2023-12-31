# Defines the utilities needed for a task graph
from typing import Generic, TypeVar, Set, Callable, Optional, Dict, List, Tuple
import uuid

import networkx as nx

class ItemBase:
  """
  This is the base
  class for all object
  instances that interact
  with a task graph.
  Mainly, it defines setters
  for the current and desired
  states, and provides
  some other utilities
  """
  def __init__(self, currState : str, desiredState : str, id : Optional[str]):
    self.__currState = currState
    self.__desiredState = desiredState

    # Set the id based on if
    # the optinal is set or not
    self.__id : str = id if id is not None else uuid.uuid4().hex
  
  # Getters and setters
  @property
  def currState(self) -> str:
    return self.__currState
  @currState.setter
  def currState(self, newState : str):
    self.__currState = newState
  
  @property
  def desiredState(self) -> str:
    return self.__desiredState
  @desiredState.setter
  def desiredState(self, newState : str):
    self.__desiredState = newState
  
  @property
  def id(self) -> str:
    return self.__id
  
  @property
  def isDiscrepant(self) -> bool:
    return self.currState != self.desiredState

T = TypeVar('T', bound = ItemBase)

class TaskEdge(Generic[T]):
  """
  Represents an edge in a task graph.
  Contains a handler that runs code
  during the transition, and defines
  its start and end states

  :params startStates: A list of start states that
    items can be in to trigger this edge
  :params endStates: A list of end states that
    items may be transferred to. It is up to the
    callable to determine which state to transfer
    to
  :params errorEndStates: A list of end states that
    items may be transferred to if an error occurs. These
    are not added to the graph to prevent the planner
    from trying to use these, but are used internally
    to enforce a valid response if an error condition
    is met
  """
  def __init__(self, startStates : List[str], endStates : List[str], errorEndStates : List[str], runner : Callable[ [T], str], id : Optional[str] = None):
    self._startStates = startStates
    self._endStates = endStates
    self._errorEndStates = errorEndStates
    self._runner = runner

    self._id : str = id if id is not None else uuid.uuid4().hex

    # A set for valid outputs
    self._validOutputs : Set[str] = set( self._endStates + self._errorEndStates )
  
  # Getters for states
  @property
  def startStates(self) -> List[str]:
    return self._startStates
  
  @property
  def endStates(self) -> List[str]:
    return self._endStates

  @property
  def errorEndStates(self) -> List[str]:
    return self._errorEndStates

  # Getters for the id and runner
  @property
  def runner(self) -> Callable[ [T], str]:
    return self._runner

  @property
  def id(self) -> str:
    return self._id

  def __call__(self, o : T) -> str:
    """
    Calls the internal runner,
    and verifies we exit into a valid
    state.
    """
    outState = self._runner(o)

    if outState not in self._validOutputs:
      raise ValueError(f"Invalid output state {outState}!")
    else:
      return outState

class TaskGraph(Generic[T]):
  """
  Represents a task graph. In here
  is a networkx graph, where each state
  is a node, and each edge has a callable
  that transitions between states
  """
  def __init__(self):
    # Constructing our graph
    self._graph = nx.DiGraph()
    
    # Contains a set of states we allow
    self._states : Set[str] = set()

    # For right now, I'll expirement with the task
    # graph owning the items. Will see if this works
    self._items : Dict[str, T] = {}

    # Maintains a set of discrepant items
    self._discrepantItems : Set[str] = set()
    
  def addState(self, stateName : str):
    """
    Adds a state to the graph
    """
    self._states.add(stateName)
    self._graph.add_node(stateName)
  
  def addStates(self, stateNames : List[str]):
    """
    Adds a list of states to the graph
    """
    for stateName in stateNames:
      self.addState(stateName)
    
  def addEdge(self, taskEdge : TaskEdge[T]):
    """
    Adds an edge to the graph
    """
    # Check if the states are valid
    for state in taskEdge.startStates + taskEdge.endStates + taskEdge.errorEndStates:
      if state not in self._states:
        raise ValueError(f"State {state} is not in the graph!")
    
    # Add the edge, as a node
    self._graph.add_node(taskEdge.id, edgeObj = taskEdge)

    # Add all edges to the node that aren't error edges
    for startState in taskEdge.startStates:
      self._graph.add_edge(startState, taskEdge.id)
    
    # Add all end states to the node
    for endState in taskEdge.endStates:
      self._graph.add_edge(taskEdge.id, endState)
  
  def addEdges(self, taskEdges : List[TaskEdge[T]]):
    """
    Adds a list of edges to the graph
    """
    for taskEdge in taskEdges:
      self.addEdge(taskEdge)
  
  def addItem(self, item : T):
    """
    Adds an item to the graph
    """
    # Check if the item is already in the graph
    if item.id in self._items:
      raise ValueError(f"Item with id {item.id} is already in the graph!")
    
    # Add the item to the graph
    self._items[item.id] = item

    # Check if the item is discrepant, and
    # add it to the set if needed
    if item.isDiscrepant:
      self._discrepantItems.add(item.id)
    
  def removeItem(self, itemID : str):
    """
    Removes an item from the graph
    """
    # Check if the item is in the graph
    if itemID not in self._items:
      raise ValueError(f"Item with id {itemID} is not in the graph!")
    
    # Remove the item from the graph
    self._items.pop(itemID)

    # Check if the item is discrepant, and
    # remove it from the set if needed
    if itemID in self._discrepantItems:
      self._discrepantItems.remove(itemID)
  
  def getItemCurrState(self, itemID : str) -> str:
    return self._items[itemID].currState

  def getItemDesiredState(self, itemID : str) -> str:
    return self._items[itemID].desiredState

  def getItem(self, itemID : str) -> T:
    return self._items[itemID]
  
  def getItemIDs(self) -> List[str]:
    return list(self._items.keys())
  
  def getItems(self) -> List[ Tuple[str, T] ]:
    return list(self._items.items())
  
  def updateItemStates(self, itemID : str, currState : str, desiredState : str):
    if itemID not in self._items:
      raise ValueError(f"Item with id {itemID} is not in the graph!")
  
    # Update the item's states
    self._items[itemID].currState = currState
    self._items[itemID].desiredState = desiredState

    # Check if the item is discrepant, and
    # add it to the set if needed
    if self._items[itemID].isDiscrepant and itemID not in self._discrepantItems:
      self._discrepantItems.add(itemID)
    elif not self._items[itemID].isDiscrepant and itemID in self._discrepantItems:
      self._discrepantItems.remove(itemID)
  
  def fixItems(self):
    """
    For all discrepant items, run the
    appropriate transition
    """
    for itemID in self._discrepantItems:
      # Get the item
      item = self._items[itemID]
      startState = item.currState
      endState = item.desiredState
      
      # Determine the shortest path between
      # the current state and desired
      path : list = list(nx.shortest_path( self._graph, startState, endState))

      # The index we're currently at. If
      # the state we enter into, which
      # is the return value from the
      # edge's callable, is not what we
      # expect, a deviation has occurred.
      # In this case, re-compute path and re-run
      idx = 1
      
      # We go till len(path) - 1 since the last
      # state, which is the terminal state, is
      # where we are aiming to enter. It doens't make
      # sense to keep on running transitions
      # after we've hit the destination. In that case,
      # change the destination to where you actually
      # want to go
      while idx < len(path) - 1:
        nextState = self._graph.nodes[path[idx]]["edgeObj"] (item)

        # Set the item's curr state
        item.currState = nextState

        if nextState == path[idx + 1]:
          # In this branch, the transition was
          # as planned
          idx += 2
        else:
          # Transition went differently, re-run djkstra's, and
          # set idx to 1
          idx -= idx + 1

          path.clear()
          path = path + list(nx.shortest_path( self._graph, startState, endState ))
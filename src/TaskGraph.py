# Defines the utilities needed for a task graph
from typing import Generic, TypeVar, Set, Callable

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
  def __init__(self, currState : str, desiredState : str):
    self.__currState = currState
    self.__desiredState = desiredState
  
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
  def isDiscrepant(self) -> bool:
    return self.currState != self.desiredState

T = TypeVar('T', bound = ItemBase)

class TaskEdge(Generic[T]):
  """
  Represents an edge in a task graph.
  Contains a handler that runs code
  during the transition, and defines
  its start and end states
  """
  def __init__(self, startState : str, endState : str, runner : Callable[ [T], str]):
    self.__startState = startState
    self.__endState = endState
    self.__runner = runner
  
  # Getters for both states
  @property
  def startState(self) -> str:
    return self.__startState
  
  @property
  def endState(self) -> str:
    return self.__endState

  def __call__(self, o : T) -> str:
    """
    Calls the internal runner.
    """
    return self.__runner(o)

class TaskGraph(Generic[T]):
  """
  Represents a task graph. In here
  is a networkx graph, where each state
  is a node, and each edge has a callable
  that transitions between states
  """
  def __init__(self):
    # Constructing our graph
    self.__graph = nx.DiGraph()
    
    # Contains a set of states we allow
    self.__states : Set[str] = set()
    
  def addState(self, stateName : str):
    """
    Adds a state to the graph
    """
    self.__states.add(stateName)
    self.__graph.add_node(stateName)
    
  def addEdge(self, taskEdge : TaskEdge[T]):
    """
    Adds an edge to the graph
    """
    # Check if the states are valid
    if taskEdge.startState not in self.__states:
      raise ValueError(f"Start state {taskEdge.startState} is not a valid state!")
    if taskEdge.endState not in self.__states:
      raise ValueError(f"End state {taskEdge.endState} is not a valid state!")
    
    # Add the edge
    self.__graph.add_edge(taskEdge.startState, taskEdge.endState, edgeObj = taskEdge)
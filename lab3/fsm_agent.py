"""
FSM Agent - Core Finite State Machine implementation for disaster response agents
Lab 3: Goals, Events, and Reactive Behavior
"""

from enum import Enum
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime
import logging


class AgentGoal:
    """Represents an agent's goal"""
    def __init__(self, goal_id: str, description: str, priority: int = 1):
        self.goal_id = goal_id
        self.description = description
        self.priority = priority
        self.status = "pending"  # pending, active, completed, failed
        self.created_at = datetime.now()
        self.completed_at = None
    
    def complete(self):
        self.status = "completed"
        self.completed_at = datetime.now()
    
    def fail(self):
        self.status = "failed"
        self.completed_at = datetime.now()
    
    def __repr__(self):
        return f"Goal({self.goal_id}: {self.description}, status={self.status})"


class Event:
    """Represents an event that can trigger agent reactions"""
    def __init__(self, event_type: str, data: Dict[str, Any], priority: int = 1):
        self.event_type = event_type
        self.data = data
        self.priority = priority
        self.timestamp = datetime.now()
        self.event_id = f"{event_type}_{self.timestamp.strftime('%Y%m%d%H%M%S%f')}"
    
    def __repr__(self):
        return f"Event({self.event_type}, priority={self.priority}, data={self.data})"


class FSMState(Enum):
    """Base states for FSM - to be extended by specific agent types"""
    IDLE = "idle"
    ACTIVE = "active"
    COMPLETED = "completed"
    ERROR = "error"


class Transition:
    """Represents a state transition with condition and action"""
    def __init__(self, from_state, to_state, condition: Callable, action: Optional[Callable] = None):
        self.from_state = from_state
        self.to_state = to_state
        self.condition = condition
        self.action = action
    
    def can_transition(self, agent, event=None) -> bool:
        """Check if transition condition is met"""
        try:
            return self.condition(agent, event)
        except Exception as e:
            logging.error(f"Error checking transition condition: {e}")
            return False
    
    def execute_action(self, agent, event=None):
        """Execute transition action if defined"""
        if self.action:
            self.action(agent, event)


class FSMAgent:
    """Base FSM Agent with reactive behavior"""
    
    def __init__(self, agent_id: str, name: str, initial_state):
        self.agent_id = agent_id
        self.name = name
        self.current_state = initial_state
        self.goals: List[AgentGoal] = []
        self.transitions: List[Transition] = []
        self.event_queue: List[Event] = []
        self.state_history = [(initial_state, datetime.now(), "initialized")]
        self.execution_trace = []
        
        # Setup logging
        self.logger = logging.getLogger(f"Agent-{agent_id}")
        self._log_trace(f"Agent {name} initialized in state {initial_state}")
    
    def add_goal(self, goal: AgentGoal):
        """Add a goal to the agent"""
        self.goals.append(goal)
        self._log_trace(f"Goal added: {goal.description}")
    
    def add_transition(self, transition: Transition):
        """Add a transition rule to the FSM"""
        self.transitions.append(transition)
    
    def receive_event(self, event: Event):
        """Receive an event and add to queue"""
        self.event_queue.append(event)
        self.event_queue.sort(key=lambda e: e.priority, reverse=True)
        self._log_trace(f"Event received: {event.event_type} - {event.data}")
    
    def process_events(self):
        """Process events in the queue and trigger reactive behavior"""
        while self.event_queue:
            event = self.event_queue.pop(0)
            self._log_trace(f"Processing event: {event.event_type}")
            self._react_to_event(event)
    
    def _react_to_event(self, event: Event):
        """React to an event by checking possible transitions"""
        for transition in self.transitions:
            if transition.from_state == self.current_state:
                if transition.can_transition(self, event):
                    old_state = self.current_state
                    
                    # Execute transition action
                    if transition.action:
                        transition.execute_action(self, event)
                    
                    # Change state
                    self.current_state = transition.to_state
                    self.state_history.append((
                        self.current_state, 
                        datetime.now(), 
                        f"transition from {old_state} due to {event.event_type}"
                    ))
                    
                    self._log_trace(
                        f"State transition: {old_state} -> {self.current_state} "
                        f"(triggered by {event.event_type})"
                    )
                    
                    # Only one transition per event
                    break
    
    def update(self):
        """Update agent - process events and check goals"""
        self.process_events()
        self._check_goals()
    
    def _check_goals(self):
        """Check and update goal status"""
        for goal in self.goals:
            if goal.status == "active":
                # Subclasses should override this to implement goal-specific logic
                pass
    
    def _log_trace(self, message: str):
        """Log execution trace"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        trace_entry = f"[{timestamp}] [{self.agent_id}] {message}"
        self.execution_trace.append(trace_entry)
        self.logger.info(message)
    
    def get_execution_trace(self) -> List[str]:
        """Get the execution trace"""
        return self.execution_trace
    
    def get_state_history(self) -> List[tuple]:
        """Get the state history"""
        return self.state_history
    
    def get_current_goal(self) -> Optional[AgentGoal]:
        """Get the current active goal"""
        for goal in self.goals:
            if goal.status == "active":
                return goal
        return None
    
    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.agent_id}, state={self.current_state})"

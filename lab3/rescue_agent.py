"""
Rescue Agent - FSM-based rescue agent for disaster response
Lab 3: Goals, Events, and Reactive Behavior
"""

from enum import Enum
from fsm_agent import FSMAgent, AgentGoal, Event, Transition
from typing import Optional


class RescueAgentState(Enum):
    """States for rescue agent FSM"""
    IDLE = "idle"
    RESPONDING = "responding"
    RESCUING = "rescuing"
    TRANSPORTING = "transporting"
    COMPLETED = "completed"


class RescueAgent(FSMAgent):
    """Rescue agent with FSM-based reactive behavior"""
    
    def __init__(self, agent_id: str, name: str):
        super().__init__(agent_id, name, RescueAgentState.IDLE)
        self.current_location = (0, 0)
        self.target_location: Optional[tuple] = None
        self.rescued_count = 0
        self.current_mission: Optional[dict] = None
        
        # Define goals
        self._define_goals()
        
        # Define FSM transitions
        self._define_transitions()
    
    def _define_goals(self):
        """Define rescue and response goals"""
        # Goal 1: Respond to emergencies quickly
        goal1 = AgentGoal(
            goal_id="quick_response",
            description="Respond to emergency events within minimal time",
            priority=5
        )
        
        # Goal 2: Rescue trapped individuals
        goal2 = AgentGoal(
            goal_id="rescue_trapped",
            description="Locate and rescue trapped individuals",
            priority=5
        )
        
        # Goal 3: Transport victims to safety
        goal3 = AgentGoal(
            goal_id="transport_victims",
            description="Transport rescued victims to medical facilities",
            priority=4
        )
        
        self.add_goal(goal1)
        self.add_goal(goal2)
        self.add_goal(goal3)
    
    def _define_transitions(self):
        """Define FSM state transitions"""
        
        # IDLE → RESPONDING: When emergency event is received
        self.add_transition(Transition(
            from_state=RescueAgentState.IDLE,
            to_state=RescueAgentState.RESPONDING,
            condition=lambda agent, event: event and event.event_type in [
                "BUILDING_COLLAPSE", "MAJOR_EARTHQUAKE", "FIRE_DETECTED"
            ],
            action=lambda agent, event: agent._start_response(event)
        ))
        
        # RESPONDING → RESCUING: When arrived at location
        self.add_transition(Transition(
            from_state=RescueAgentState.RESPONDING,
            to_state=RescueAgentState.RESCUING,
            condition=lambda agent, event: agent.current_location == agent.target_location,
            action=lambda agent, event: agent._start_rescue()
        ))
        
        # RESCUING → TRANSPORTING: When rescue is complete
        self.add_transition(Transition(
            from_state=RescueAgentState.RESCUING,
            to_state=RescueAgentState.TRANSPORTING,
            condition=lambda agent, event: agent.current_mission and agent.current_mission.get("rescued", False),
            action=lambda agent, event: agent._start_transport()
        ))
        
        # TRANSPORTING → COMPLETED: When victims delivered
        self.add_transition(Transition(
            from_state=RescueAgentState.TRANSPORTING,
            to_state=RescueAgentState.COMPLETED,
            condition=lambda agent, event: agent.current_location == (0, 0),  # Base location
            action=lambda agent, event: agent._complete_mission()
        ))
        
        # COMPLETED → IDLE: Ready for next mission
        self.add_transition(Transition(
            from_state=RescueAgentState.COMPLETED,
            to_state=RescueAgentState.IDLE,
            condition=lambda agent, event: True,
            action=lambda agent, event: agent._reset_for_next_mission()
        ))
    
    def _start_response(self, event: Event):
        """Action: Start responding to emergency"""
        self.target_location = event.data.get("location")
        self.current_mission = {
            "event_type": event.event_type,
            "location": self.target_location,
            "rescued": False,
            "victim_count": event.data.get("trapped_people", event.data.get("injured_count", 1))
        }
        
        # Activate quick response goal
        for goal in self.goals:
            if goal.goal_id == "quick_response":
                goal.status = "active"
        
        self._log_trace(f"Responding to {event.event_type} at location {self.target_location}")
    
    def _start_rescue(self, event: Event = None):
        """Action: Start rescue operation"""
        # Activate rescue goal
        for goal in self.goals:
            if goal.goal_id == "rescue_trapped":
                goal.status = "active"
        
        self._log_trace(f"Starting rescue operation at {self.current_location}")
        self._log_trace(f"Attempting to rescue {self.current_mission.get('victim_count', 0)} victims")
    
    def _start_transport(self, event: Event = None):
        """Action: Start transporting victims"""
        # Complete rescue goal
        for goal in self.goals:
            if goal.goal_id == "rescue_trapped":
                goal.complete()
            if goal.goal_id == "transport_victims":
                goal.status = "active"
        
        self._log_trace(f"Transporting {self.current_mission.get('victim_count', 0)} victims to safety")
    
    def _complete_mission(self, event: Event = None):
        """Action: Complete mission"""
        victim_count = self.current_mission.get('victim_count', 0)
        self.rescued_count += victim_count
        
        # Complete all active goals
        for goal in self.goals:
            if goal.status == "active":
                goal.complete()
        
        self._log_trace(f"Mission completed! Delivered {victim_count} victims. Total rescued: {self.rescued_count}")
    
    def _reset_for_next_mission(self, event: Event = None):
        """Action: Reset for next mission"""
        self.current_mission = None
        self.target_location = None
        self._log_trace("Agent ready for next mission")
    
    def update(self):
        """Update agent state - simulate movement and actions"""
        # Simulate movement toward target
        if self.current_state == RescueAgentState.RESPONDING and self.target_location:
            self._move_toward_target()
        
        # Simulate rescue operation
        elif self.current_state == RescueAgentState.RESCUING and self.current_mission:
            self._perform_rescue()
        
        # Simulate transport
        elif self.current_state == RescueAgentState.TRANSPORTING:
            self._move_to_base()
        
        # Process events after taking actions
        super().update()
    
    def _move_toward_target(self):
        """Simulate movement toward target location"""
        if self.target_location and self.current_location != self.target_location:
            # Simple movement simulation
            x, y = self.current_location
            tx, ty = self.target_location
            
            new_x = x + (1 if tx > x else -1 if tx < x else 0)
            new_y = y + (1 if ty > y else -1 if ty < y else 0)
            
            self.current_location = (new_x, new_y)
            self._log_trace(f"Moving to target: now at {self.current_location}")
    
    def _perform_rescue(self):
        """Simulate rescue operation"""
        if self.current_mission and not self.current_mission.get("rescued"):
            self.current_mission["rescued"] = True
            self._log_trace("Rescue operation successful!")
    
    def _move_to_base(self):
        """Simulate movement back to base"""
        base_location = (0, 0)
        if self.current_location != base_location:
            x, y = self.current_location
            new_x = x + (1 if 0 > x else -1 if 0 < x else 0)
            new_y = y + (1 if 0 > y else -1 if 0 < y else 0)
            
            self.current_location = (new_x, new_y)
            self._log_trace(f"Returning to base: now at {self.current_location}")

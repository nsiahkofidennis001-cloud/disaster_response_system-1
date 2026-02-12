"""
Medical Agent - FSM-based medical response agent
Lab 3: Goals, Events, and Reactive Behavior
"""

from enum import Enum
from fsm_agent import FSMAgent, AgentGoal, Event, Transition
from typing import Optional


class MedicalAgentState(Enum):
    """States for medical agent FSM"""
    IDLE = "idle"
    DISPATCHED = "dispatched"
    TREATING = "treating"
    TRANSPORTING = "transporting"
    COMPLETED = "completed"


class MedicalAgent(FSMAgent):
    """Medical agent with FSM-based reactive behavior"""
    
    def __init__(self, agent_id: str, name: str):
        super().__init__(agent_id, name, MedicalAgentState.IDLE)
        self.current_location = (0, 0)
        self.target_location: Optional[tuple] = None
        self.patients_treated = 0
        self.current_mission: Optional[dict] = None
        self.medical_supplies = 100  # percentage
        
        # Define goals
        self._define_goals()
        
        # Define FSM transitions
        self._define_transitions()
    
    def _define_goals(self):
        """Define medical response goals"""
        # Goal 1: Rapid medical response
        goal1 = AgentGoal(
            goal_id="rapid_response",
            description="Reach medical emergency quickly",
            priority=5
        )
        
        # Goal 2: Provide medical treatment
        goal2 = AgentGoal(
            goal_id="provide_treatment",
            description="Stabilize and treat injured patients",
            priority=5
        )
        
        # Goal 3: Evacuate critical patients
        goal3 = AgentGoal(
            goal_id="evacuate_patients",
            description="Transport critical patients to medical facilities",
            priority=4
        )
        
        self.add_goal(goal1)
        self.add_goal(goal2)
        self.add_goal(goal3)
    
    def _define_transitions(self):
        """Define FSM state transitions"""
        
        # IDLE → DISPATCHED: When medical emergency event is received
        self.add_transition(Transition(
            from_state=MedicalAgentState.IDLE,
            to_state=MedicalAgentState.DISPATCHED,
            condition=lambda agent, event: event and event.event_type == "MEDICAL_EMERGENCY",
            action=lambda agent, event: agent._dispatch_to_emergency(event)
        ))
        
        # DISPATCHED → TREATING: When arrived at location
        self.add_transition(Transition(
            from_state=MedicalAgentState.DISPATCHED,
            to_state=MedicalAgentState.TREATING,
            condition=lambda agent, event: agent.current_location == agent.target_location,
            action=lambda agent, event: agent._start_treatment()
        ))
        
        # TREATING → TRANSPORTING: When treatment complete and evacuation needed
        self.add_transition(Transition(
            from_state=MedicalAgentState.TREATING,
            to_state=MedicalAgentState.TRANSPORTING,
            condition=lambda agent, event: (
                agent.current_mission and 
                agent.current_mission.get("treated", False) and
                agent.current_mission.get("needs_evacuation", False)
            ),
            action=lambda agent, event: agent._start_evacuation()
        ))
        
        # TREATING → COMPLETED: When treatment complete and no evacuation needed
        self.add_transition(Transition(
            from_state=MedicalAgentState.TREATING,
            to_state=MedicalAgentState.COMPLETED,
            condition=lambda agent, event: (
                agent.current_mission and 
                agent.current_mission.get("treated", False) and
                not agent.current_mission.get("needs_evacuation", False)
            ),
            action=lambda agent, event: agent._complete_on_site()
        ))
        
        # TRANSPORTING → COMPLETED: When patients delivered to hospital
        self.add_transition(Transition(
            from_state=MedicalAgentState.TRANSPORTING,
            to_state=MedicalAgentState.COMPLETED,
            condition=lambda agent, event: agent.current_location == (0, 0),  # Hospital location
            action=lambda agent, event: agent._complete_evacuation()
        ))
        
        # COMPLETED → IDLE: Ready for next mission
        self.add_transition(Transition(
            from_state=MedicalAgentState.COMPLETED,
            to_state=MedicalAgentState.IDLE,
            condition=lambda agent, event: True,
            action=lambda agent, event: agent._reset_for_next_mission()
        ))
    
    def _dispatch_to_emergency(self, event: Event):
        """Action: Dispatch to medical emergency"""
        self.target_location = event.data.get("location")
        self.current_mission = {
            "location": self.target_location,
            "injured_count": event.data.get("injured_count", 1),
            "severity": event.data.get("severity", "medium"),
            "needs_evacuation": event.data.get("needs_evacuation", False),
            "treated": False
        }
        
        # Activate rapid response goal
        for goal in self.goals:
            if goal.goal_id == "rapid_response":
                goal.status = "active"
        
        self._log_trace(
            f"Dispatched to medical emergency at {self.target_location} "
            f"({self.current_mission['injured_count']} injured, severity: {self.current_mission['severity']})"
        )
    
    def _start_treatment(self, event: Event = None):
        """Action: Start treating patients"""
        # Complete rapid response goal, activate treatment goal
        for goal in self.goals:
            if goal.goal_id == "rapid_response":
                goal.complete()
            if goal.goal_id == "provide_treatment":
                goal.status = "active"
        
        self._log_trace(
            f"Starting treatment of {self.current_mission['injured_count']} patients "
            f"(severity: {self.current_mission['severity']})"
        )
    
    def _start_evacuation(self, event: Event = None):
        """Action: Start evacuating critical patients"""
        # Complete treatment goal, activate evacuation goal
        for goal in self.goals:
            if goal.goal_id == "provide_treatment":
                goal.complete()
            if goal.goal_id == "evacuate_patients":
                goal.status = "active"
        
        self._log_trace(f"Evacuating {self.current_mission['injured_count']} critical patients to hospital")
    
    def _complete_on_site(self, event: Event = None):
        """Action: Complete treatment on-site (no evacuation needed)"""
        patient_count = self.current_mission.get('injured_count', 0)
        self.patients_treated += patient_count
        
        # Complete treatment goal
        for goal in self.goals:
            if goal.goal_id == "provide_treatment":
                goal.complete()
        
        self._log_trace(
            f"Treatment completed on-site for {patient_count} patients. "
            f"Total patients treated: {self.patients_treated}"
        )
    
    def _complete_evacuation(self, event: Event = None):
        """Action: Complete patient evacuation"""
        patient_count = self.current_mission.get('injured_count', 0)
        self.patients_treated += patient_count
        
        # Complete evacuation goal
        for goal in self.goals:
            if goal.status == "active":
                goal.complete()
        
        self._log_trace(
            f"Evacuation completed! Delivered {patient_count} patients to hospital. "
            f"Total patients treated: {self.patients_treated}"
        )
    
    def _reset_for_next_mission(self, event: Event = None):
        """Action: Reset for next mission"""
        self.current_mission = None
        self.target_location = None
        self._log_trace(f"Medical agent ready for next mission (supplies: {self.medical_supplies}%)")
    
    def update(self):
        """Update agent state - simulate movement and actions"""
        # Simulate movement toward target
        if self.current_state == MedicalAgentState.DISPATCHED and self.target_location:
            self._move_toward_target()
        
        # Simulate treatment
        elif self.current_state == MedicalAgentState.TREATING and self.current_mission:
            self._perform_treatment()
        
        # Simulate evacuation transport
        elif self.current_state == MedicalAgentState.TRANSPORTING:
            self._move_to_hospital()
        
        # Process events after taking actions
        super().update()
    
    def _move_toward_target(self):
        """Simulate movement toward emergency location"""
        if self.target_location and self.current_location != self.target_location:
            x, y = self.current_location
            tx, ty = self.target_location
            
            new_x = x + (1 if tx > x else -1 if tx < x else 0)
            new_y = y + (1 if ty > y else -1 if ty < y else 0)
            
            self.current_location = (new_x, new_y)
            self._log_trace(f"Moving to emergency: now at {self.current_location}")
    
    def _perform_treatment(self):
        """Simulate medical treatment"""
        if self.current_mission and not self.current_mission.get("treated"):
            # Use medical supplies based on severity
            severity_cost = {
                "low": 5,
                "medium": 15,
                "high": 25,
                "critical": 40
            }
            cost = severity_cost.get(self.current_mission["severity"], 15)
            self.medical_supplies -= cost
            
            self.current_mission["treated"] = True
            self._log_trace(f"Treatment successful! (Medical supplies remaining: {self.medical_supplies}%)")
    
    def _move_to_hospital(self):
        """Simulate movement to hospital"""
        hospital_location = (0, 0)
        if self.current_location != hospital_location:
            x, y = self.current_location
            new_x = x + (1 if 0 > x else -1 if 0 < x else 0)
            new_y = y + (1 if 0 > y else -1 if 0 < y else 0)
            
            self.current_location = (new_x, new_y)
            self._log_trace(f"Transporting to hospital: now at {self.current_location}")

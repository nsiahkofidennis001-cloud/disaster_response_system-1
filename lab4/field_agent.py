"""
Field Agent - Responds to coordinator requests and sends situation reports
Lab 4: Agent Communication using FIPA-ACL
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lab3'))

from enum import Enum
from typing import Optional, Dict
from communicating_agent import CommunicatingAgent
from fipa_acl import ACLMessage, Performative
from fsm_agent import AgentGoal, Transition


class FieldAgentState(Enum):
    """States for field agent"""
    IDLE = "idle"
    TRAVELING = "traveling"
    INVESTIGATING = "investigating"
    REPORTING = "reporting"
    COMPLETED = "completed"


class FieldAgent(CommunicatingAgent):
    """
    Field agent that responds to coordinator requests via FIPA-ACL
    """
    
    def __init__(self, agent_id: str, name: str):
        super().__init__(agent_id, name, FieldAgentState.IDLE)
        
        # Field operations
        self.current_location = (0, 0)
        self.target_location: Optional[tuple] = None
        self.current_mission: Optional[Dict] = None
        self.coordinator_id: Optional[str] = None
        self.discoveries: list = []
        
        # Override REQUEST handler to respond to coordinator
        self.register_message_handler(Performative.REQUEST, self._handle_coordinator_request)
        self.register_message_handler(Performative.QUERY_IF, self._handle_query)
        self.register_message_handler(Performative.CONFIRM, self._handle_coordinator_confirm)
        
        # Define FSM transitions
        self._define_transitions()
        
        self._log_trace("Field agent initialized and ready for deployment")
    
    def set_coordinator(self, coordinator_id: str):
        """Set the coordinator for this field agent"""
        self.coordinator_id = coordinator_id
        self._log_trace(f"Assigned to coordinator: {coordinator_id}")
    
    def _define_transitions(self):
        """Define FSM state transitions"""
        
        # IDLE → TRAVELING: When mission accepted
        self.add_transition(Transition(
            from_state=FieldAgentState.IDLE,
            to_state=FieldAgentState.TRAVELING,
            condition=lambda agent, event: agent.current_mission is not None,
            action=None
        ))
        
        # TRAVELING → INVESTIGATING: When arrived at location
        self.add_transition(Transition(
            from_state=FieldAgentState.TRAVELING,
            to_state=FieldAgentState.INVESTIGATING,
            condition=lambda agent, event: agent.current_location == agent.target_location,
            action=lambda agent, event: agent._start_investigation()
        ))
        
        # INVESTIGATING → REPORTING: When investigation complete
        self.add_transition(Transition(
            from_state=FieldAgentState.INVESTIGATING,
            to_state=FieldAgentState.REPORTING,
            condition=lambda agent, event: (
                agent.current_mission and 
                agent.current_mission.get("investigation_complete", False)
            ),
            action=lambda agent, event: agent._send_investigation_report()
        ))
        
        # REPORTING → COMPLETED: When report sent
        self.add_transition(Transition(
            from_state=FieldAgentState.REPORTING,
            to_state=FieldAgentState.COMPLETED,
            condition=lambda agent, event: True,
            action=lambda agent, event: agent._complete_mission()
        ))
        
        # COMPLETED → IDLE: Ready for next mission
        self.add_transition(Transition(
            from_state=FieldAgentState.COMPLETED,
            to_state=FieldAgentState.IDLE,
            condition=lambda agent, event: True,
            action=lambda agent, event: agent._reset_for_next_mission()
        ))
    
    def _handle_coordinator_request(self, message: ACLMessage):
        """Handle REQUEST from coordinator"""
        sender = message.sender
        content = message.content
        
        if not isinstance(content, dict):
            # Invalid request format
            refuse_msg = message.create_reply(
                performative=Performative.REFUSE,
                content={"reason": "Invalid request format"},
                sender=self.agent_id
            )
            self.send_message(refuse_msg)
            return
        
        action = content.get("action")
        parameters = content.get("parameters", {})
        
        self._log_trace(f"Received REQUEST from {sender}: action={action}")
        
        # Process different actions
        if action == "investigate_location":
            self._accept_investigation_mission(message, parameters)
        
        elif action == "return_to_base":
            self._accept_return_mission(message)
        
        elif action == "assist_agent":
            self._accept_assist_mission(message, parameters)
        
        else:
            # Unknown action - refuse
            refuse_msg = message.create_reply(
                performative=Performative.REFUSE,
                content={"reason": f"Unknown action: {action}"},
                sender=self.agent_id
            )
            self.send_message(refuse_msg)
    
    def _accept_investigation_mission(self, request_msg: ACLMessage, parameters: Dict):
        """Accept investigation mission"""
        # Check if already on mission
        if self.current_mission is not None:
            refuse_msg = request_msg.create_reply(
                performative=Performative.REFUSE,
                content={"reason": "Already on active mission"},
                sender=self.agent_id
            )
            self.send_message(refuse_msg)
            return
        
        # Accept mission
        self.current_mission = {
            "action": "investigate_location",
            "location": parameters.get("location"),
            "type": parameters.get("mission_type"),
            "priority": parameters.get("priority"),
            "investigation_complete": False,
            "conversation_id": request_msg.conversation_id
        }
        
        self.target_location = parameters.get("location")
        self.coordinator_id = request_msg.sender
        
        # Send AGREE reply
        agree_msg = request_msg.create_reply(
            performative=Performative.AGREE,
            content={
                "action": "investigate_location",
                "location": self.target_location,
                "estimated_arrival": "calculating..."
            },
            sender=self.agent_id
        )
        self.send_message(agree_msg)
        
        self._log_trace(f"Accepted investigation mission to {self.target_location}")
    
    def _accept_return_mission(self, request_msg: ACLMessage):
        """Accept return to base mission"""
        self.target_location = (0, 0)
        
        agree_msg = request_msg.create_reply(
            performative=Performative.AGREE,
            content={"action": "return_to_base"},
            sender=self.agent_id
        )
        self.send_message(agree_msg)
        
        self._log_trace("Returning to base")
    
    def _accept_assist_mission(self, request_msg: ACLMessage, parameters: Dict):
        """Accept mission to assist another agent"""
        target_agent = parameters.get("agent_id")
        location = parameters.get("location")
        
        agree_msg = request_msg.create_reply(
            performative=Performative.AGREE,
            content={"action": "assist_agent", "target_agent": target_agent},
            sender=self.agent_id
        )
        self.send_message(agree_msg)
        
        self._log_trace(f"Moving to assist agent {target_agent} at {location}")
    
    def _handle_query(self, message: ACLMessage):
        """Handle QUERY_IF from coordinator"""
        query = message.content.get("query") if isinstance(message.content, dict) else message.content
        
        if query == "mission_status":
            # Send status update
            status_msg = message.create_reply(
                performative=Performative.INFORM,
                content={
                    "type": "status_update",
                    "status": self.current_state.value,
                    "location": self.current_location,
                    "mission": self.current_mission.get("type") if self.current_mission else None
                },
                sender=self.agent_id
            )
            self.send_message(status_msg)
    
    def _handle_coordinator_confirm(self, message: ACLMessage):
        """Handle CONFIRM from coordinator"""
        self._log_trace(f"Coordinator confirmed: {message.content}")
    
    def _start_investigation(self, event=None):
        """Action: Start investigating location"""
        self._log_trace(f"Starting investigation at {self.current_location}")
    
    def _send_investigation_report(self, event=None):
        """Action: Send investigation report to coordinator"""
        if not self.coordinator_id:
            self._log_trace("ERROR: No coordinator assigned")
            return
        
        # Simulate findings
        import random
        findings = random.choice([
            "No survivors found, area secure",
            "5 survivors located, need immediate evacuation",
            "Structural damage detected, area unsafe",
            "Medical emergency - 3 critical patients",
            "Gas leak detected, evacuating area"
        ])
        
        self.discoveries.append(findings)
        
        # Determine severity
        severity = "critical" if any(word in findings.lower() for word in ["critical", "emergency", "leak"]) else "normal"
        
        # Send INFORM message to coordinator
        report_msg = ACLMessage(
            performative=Performative.INFORM,
            sender=self.agent_id,
            receiver=self.coordinator_id,
            content={
                "type": "discovery",
                "discovery": findings,
                "location": self.current_location,
                "severity": severity,
                "timestamp": "current"
            },
            conversation_id=self.current_mission.get("conversation_id")
        )
        
        self.send_message(report_msg)
        self._log_trace(f"Sent discovery report: {findings}")
    
    def _complete_mission(self, event=None):
        """Action: Complete mission"""
        if self.coordinator_id:
            # Send mission completion INFORM
            complete_msg = ACLMessage(
                performative=Performative.INFORM,
                sender=self.agent_id,
                receiver=self.coordinator_id,
                content={
                    "type": "mission_complete",
                    "result": "success",
                    "discoveries": len(self.discoveries)
                },
                conversation_id=self.current_mission.get("conversation_id") if self.current_mission else None
            )
            self.send_message(complete_msg)
        
        self._log_trace("Mission completed")
    
    def _reset_for_next_mission(self, event=None):
        """Action: Reset for next mission"""
        self.current_mission = None
        self.target_location = None
        self._log_trace("Ready for next mission")
    
    def update(self):
        """Update agent state"""
        # Simulate movement
        if self.current_state == FieldAgentState.TRAVELING and self.target_location:
            self._move_toward_target()
        
        # Simulate investigation
        elif self.current_state == FieldAgentState.INVESTIGATING and self.current_mission:
            self._perform_investigation()
        
        # Process messages and events
        super().update()
    
    def _move_toward_target(self):
        """Simulate movement toward target location"""
        if self.target_location and self.current_location != self.target_location:
            x, y = self.current_location
            tx, ty = self.target_location
            
            new_x = x + (1 if tx > x else -1 if tx < x else 0)
            new_y = y + (1 if ty > y else -1 if ty < y else 0)
            
            self.current_location = (new_x, new_y)
            self._log_trace(f"Moving to target: now at {self.current_location}")
    
    def _perform_investigation(self):
        """Simulate investigation"""
        if self.current_mission and not self.current_mission.get("investigation_complete"):
            self.current_mission["investigation_complete"] = True
            self._log_trace("Investigation complete")

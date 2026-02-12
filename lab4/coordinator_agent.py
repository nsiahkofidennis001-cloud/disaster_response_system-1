"""
Coordinator Agent - Manages disaster response coordination via FIPA-ACL
Lab 4: Agent Communication using FIPA-ACL
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lab3'))

from enum import Enum
from typing import List, Dict, Optional
from communicating_agent import CommunicatingAgent
from fipa_acl import ACLMessage, Performative
from fsm_agent import AgentGoal


class CoordinatorState(Enum):
    """States for coordinator agent"""
    IDLE = "idle"
    ASSESSING = "assessing"
    COORDINATING = "coordinating"
    MONITORING = "monitoring"
    COMPLETED = "completed"


class CoordinatorAgent(CommunicatingAgent):
    """
    Coordinator agent that manages field agents using FIPA-ACL communication
    """
    
    def __init__(self, agent_id: str, name: str):
        super().__init__(agent_id, name, CoordinatorState.IDLE)
        
        # Coordination tracking
        self.field_agents: List[str] = []  # List of field agent IDs
        self.active_missions: Dict[str, Dict] = {}  # agent_id -> mission_info
        self.situation_reports: List[Dict] = []
        
        #handlers
        self.register_message_handler(Performative.INFORM, self._handle_field_inform)
        self.register_message_handler(Performative.CONFIRM, self._handle_confirmation)
        self.register_message_handler(Performative.REFUSE, self._handle_refusal)
        
        self._log_trace("Coordinator agent initialized")
    
    def register_field_agent(self, agent_id: str):
        """Register a field agent under this coordinator"""
        if agent_id not in self.field_agents:
            self.field_agents.append(agent_id)
            self._log_trace(f"Registered field agent: {agent_id}")
    
    def assess_situation(self, disaster_info: Dict):
        """Assess disaster situation and plan response"""
        self.current_state = CoordinatorState.ASSESSING
        self._log_trace(f"Assessing disaster situation: {disaster_info}")
        

        assessment = {
            "disaster_type": disaster_info.get("type"),
            "location": disaster_info.get("location"),
            "severity": disaster_info.get("severity"),
            "required_agents": disaster_info.get("required_agents", 2)
        }
        
        self.situation_reports.append(assessment)
        self.current_state = CoordinatorState.COORDINATING
    
    def dispatch_field_agents(self, mission_details: Dict):
        """
        Dispatch field agents to disaster location
        
        Uses REQUEST performative to ask agents to perform actions
        """
        self.current_state = CoordinatorState.COORDINATING
        
        location = mission_details.get("location")
        mission_type = mission_details.get("type")
        
        
        dispatched = 0
        required = mission_details.get("required_agents", 1)
        
        for agent_id in self.field_agents:
            if dispatched >= required:
                break
            
            if agent_id not in self.active_missions:
                # Send REQUEST to field agent
                request_msg = ACLMessage(
                    performative=Performative.REQUEST,
                    sender=self.agent_id,
                    receiver=agent_id,
                    content={
                        "action": "investigate_location",
                        "parameters": {
                            "location": location,
                            "mission_type": mission_type,
                            "priority": mission_details.get("priority", "high")
                        }
                    }
                )
                
                self.send_message(request_msg)
                
                # Track mission
                self.active_missions[agent_id] = {
                    "location": location,
                    "type": mission_type,
                    "status": "dispatched",
                    "conversation_id": request_msg.conversation_id
                }
                
                dispatched += 1
                self._log_trace(f"Dispatched {agent_id} to investigate {location}")
        
        if dispatched > 0:
            self.current_state = CoordinatorState.MONITORING
            self._log_trace(f"Dispatched {dispatched} agents. Now monitoring operations.")
        else:
            self._log_trace("WARNING: No available field agents to dispatch")
    
    def request_status_update(self, agent_id: str):
        """Request status update from a field agent"""
        query_msg = ACLMessage(
            performative=Performative.QUERY_IF,
            sender=self.agent_id,
            receiver=agent_id,
            content={"query": "mission_status", "agent": agent_id}
        )
        self.send_message(query_msg)
        self._log_trace(f"Requested status update from {agent_id}")
    
    def _handle_field_inform(self, message: ACLMessage):
        """Handle INFORM messages from field agents"""
        sender = message.sender
        info = message.content
        
        self._log_trace(f"Received report from {sender}: {info}")
        
        # Process different types of information
        if isinstance(info, dict):
            info_type = info.get("type")
            
            if info_type == "discovery":
                self._process_discovery_report(sender, info, message)
            
            elif info_type == "status_update":
                self._process_status_update(sender, info)
            
            elif info_type == "mission_complete":
                self._process_mission_completion(sender, info)
            
            elif info_type == "emergency":
                self._process_emergency_report(sender, info, message)
    
    def _process_discovery_report(self, agent_id: str, info: Dict, message: ACLMessage):
        """Process discovery report from field agent"""
        discovery = info.get("discovery")
        location = info.get("location")
        
        self._log_trace(f"Field agent {agent_id} discovered: {discovery} at {location}")
        
        # Send confirmation
        confirm_msg = message.create_reply(
            performative=Performative.CONFIRM,
            content={"acknowledged": True, "discovery": discovery},
            sender=self.agent_id
        )
        self.send_message(confirm_msg)
        
        # If critical discovery, dispatch more agents
        if info.get("severity") == "critical":
            self._log_trace("Critical discovery - requesting additional support")
    
    def _process_status_update(self, agent_id: str, info: Dict):
        """Process status update from field agent"""
        status = info.get("status")
        
        if agent_id in self.active_missions:
            self.active_missions[agent_id]["status"] = status
            self._log_trace(f"Updated {agent_id} status: {status}")
    
    def _process_mission_completion(self, agent_id: str, info: Dict):
        """Process mission completion report"""
        self._log_trace(f"Agent {agent_id} completed mission: {info.get('result')}")
        
        # Remove from active missions
        if agent_id in self.active_missions:
            del self.active_missions[agent_id]
        
        # Check if all missions complete
        if not self.active_missions:
            self.current_state = CoordinatorState.COMPLETED
            self._log_trace("All missions completed. Coordinator returning to IDLE")
    
    def _process_emergency_report(self, agent_id: str, info: Dict, message: ACLMessage):
        """Process emergency report"""
        emergency = info.get("emergency")
        self._log_trace(f"EMERGENCY reported by {agent_id}: {emergency}")
        
        # Acknowledge emergency
        ack_msg = message.create_reply(
            performative=Performative.CONFIRM,
            content={"emergency_acknowledged": True, "support_dispatched": True},
            sender=self.agent_id
        )
        self.send_message(ack_msg)
    
    def _handle_confirmation(self, message: ACLMessage):
        """Handle CONFIRM messages"""
        sender = message.sender
        content = message.content
        self._log_trace(f"Received confirmation from {sender}: {content}")
    
    def _handle_refusal(self, message: ACLMessage):
        """Handle REFUSE messages from field agents"""
        sender = message.sender
        reason = message.content.get("reason") if isinstance(message.content, dict) else message.content
        
        self._log_trace(f"Agent {sender} refused request. Reason: {reason}")
        
        # Remove from active missions
        if sender in self.active_missions:
            del self.active_missions[sender]
        
        # TODO: Reassign mission to another agent
    
    def get_active_missions_summary(self) -> str:
        """Get summary of active missions"""
        if not self.active_missions:
            return "No active missions"
        
        summary = f"Active missions: {len(self.active_missions)}\n"
        for agent_id, mission in self.active_missions.items():
            summary += f"  - {agent_id}: {mission['type']} at {mission['location']} ({mission['status']})\n"
        
        return summary

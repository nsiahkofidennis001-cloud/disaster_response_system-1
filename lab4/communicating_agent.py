"""
Communicating Agent - Base agent with FIPA-ACL communication capabilities
Lab 4: Agent Communication using FIPA-ACL
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lab3'))

from typing import List, Dict, Callable, Optional, Any
from datetime import datetime
import logging
from fipa_acl import ACLMessage, Performative, MessageParser
from fsm_agent import FSMAgent, Event


class CommunicatingAgent(FSMAgent):
    """
    Agent with FIPA-ACL communication capabilities
    
    Extends FSMAgent to support message-based communication
    """
    
    def __init__(self, agent_id: str, name: str, initial_state):
        super().__init__(agent_id, name, initial_state)
        
        # Message handling
        self.inbox: List[ACLMessage] = []
        self.outbox: List[ACLMessage] = []
        self.message_history: List[ACLMessage] = []
        self.message_handlers: Dict[Performative, Callable] = {}
        
        # Message parser
        self.parser = MessageParser()
        
        # Register default handlers
        self._register_default_handlers()
        
        self._log_trace("Communication capabilities initialized")
    
    def _register_default_handlers(self):
        """Register default message handlers"""
        self.register_message_handler(Performative.INFORM, self._handle_inform)
        self.register_message_handler(Performative.REQUEST, self._handle_request)
        self.register_message_handler(Performative.QUERY_IF, self._handle_query_if)
        self.register_message_handler(Performative.CONFIRM, self._handle_confirm)
        self.register_message_handler(Performative.REFUSE, self._handle_refuse)
    
    def register_message_handler(
        self,
        performative: Performative,
        handler: Callable[[ACLMessage], None]
    ):
        """Register a handler for a specific performative"""
        self.message_handlers[performative] = handler
        self._log_trace(f"Registered handler for {performative.value}")
    
    def send_message(self, message: ACLMessage):
        """
        Send an ACL message
        
        Args:
            message: The ACL message to send
        """
        # Validate message
        is_valid, error = message.validate()
        if not is_valid:
            self._log_trace(f"ERROR: Invalid message - {error}")
            return
        
        # Add to outbox and history
        self.outbox.append(message)
        self.message_history.append(message)
        
        self._log_trace(
            f"SENT {message.performative.value.upper()} to {message.receiver}: "
            f"{message.content}"
        )
    
    def receive_message(self, message: ACLMessage):
        """
        Receive an ACL message
        
        Args:
            message: The ACL message received
        """
        self.inbox.append(message)
        self.message_history.append(message)
        
        self._log_trace(
            f"RECEIVED {message.performative.value.upper()} from {message.sender}: "
            f"{message.content}"
        )
    
    def process_messages(self):
        """Process all messages in inbox"""
        while self.inbox:
            message = self.inbox.pop(0)
            self._process_message(message)
    
    def _process_message(self, message: ACLMessage):
        """Process a single message"""
        self._log_trace(f"Processing message: {message.message_id}")
        
        # Get handler for this performative
        handler = self.message_handlers.get(message.performative)
        
        if handler:
            try:
                handler(message)
            except Exception as e:
                self._log_trace(f"ERROR in message handler: {e}")
                # Send NOT_UNDERSTOOD reply
                self._send_not_understood(message, str(e))
        else:
            self._log_trace(f"No handler for {message.performative.value}")
            self._send_not_understood(message, f"No handler for {message.performative.value}")
    
    def _send_not_understood(self, original_message: ACLMessage, reason: str):
        """Send NOT_UNDERSTOOD reply"""
        reply = original_message.create_reply(
            performative=Performative.NOT_UNDERSTOOD,
            content={"reason": reason, "original_message": original_message.message_id},
            sender=self.agent_id
        )
        self.send_message(reply)
    
    # Default message handlers (can be overridden by subclasses)
    
    def _handle_inform(self, message: ACLMessage):
        """Handle INFORM performative"""
        info = self.parser.extract_information(message)
        self._log_trace(f"Informed: {info}")
        # Subclasses should override to implement specific behavior
    
    def _handle_request(self, message: ACLMessage):
        """Handle REQUEST performative"""
        action = self.parser.extract_action(message)
        self._log_trace(f"Request to perform action: {action}")
        # Subclasses should override to implement specific behavior
        
        # Default: send REFUSE reply
        reply = message.create_reply(
            performative=Performative.REFUSE,
            content={"reason": "Action not supported", "action": action},
            sender=self.agent_id
        )
        self.send_message(reply)
    
    def _handle_query_if(self, message: ACLMessage):
        """Handle QUERY_IF performative"""
        query = message.content
        self._log_trace(f"Query: {query}")
        # Subclasses should override to implement specific behavior
    
    def _handle_confirm(self, message: ACLMessage):
        """Handle CONFIRM performative"""
        proposition = message.content
        self._log_trace(f"Confirmed: {proposition}")
    
    def _handle_refuse(self, message: ACLMessage):
        """Handle REFUSE performative"""
        self._log_trace(f"Request refused: {message.content}")
    
    def update(self):
        """Update agent - process messages first, then events"""
        self.process_messages()
        super().update()
    
    def get_sent_messages(self) -> List[ACLMessage]:
        """Get all sent messages"""
        return [msg for msg in self.message_history if msg.sender == self.agent_id]
    
    def get_received_messages(self) -> List[ACLMessage]:
        """Get all received messages"""
        return [msg for msg in self.message_history if msg.receiver == self.agent_id]
    
    def get_conversation_messages(self, conversation_id: str) -> List[ACLMessage]:
        """Get all messages in a conversation"""
        return [
            msg for msg in self.message_history 
            if msg.conversation_id == conversation_id
        ]

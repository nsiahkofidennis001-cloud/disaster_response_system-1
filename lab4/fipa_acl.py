"""
FIPA-ACL - Foundation for Intelligent Physical Agents - Agent Communication Language
Lab 4: Agent Communication using FIPA-ACL
"""

from enum import Enum
from typing import Any, Dict, Optional, List
from datetime import datetime
import json


class Performative(Enum):
    """FIPA-ACL Performatives"""
    INFORM = "inform"           # Inform about a fact
    REQUEST = "request"         # Request an action
    QUERY_IF = "query-if"       # Query if statement is true
    QUERY_REF = "query-ref"     # Query for reference
    CONFIRM = "confirm"         # Confirm truth of proposition
    DISCONFIRM = "disconfirm"   # Disconfirm truth of proposition
    AGREE = "agree"             # Agree to perform action
    REFUSE = "refuse"           # Refuse to perform action
    PROPOSE = "propose"         # Propose negotiation
    ACCEPT_PROPOSAL = "accept-proposal"
    REJECT_PROPOSAL = "reject-proposal"
    CFP = "cfp"                 # Call for proposal
    NOT_UNDERSTOOD = "not-understood"


class ACLMessage:
    """
    FIPA-ACL Message Structure
    
    Standard FIPA-ACL message with support for key performatives
    and message fields as defined by FIPA specifications.
    """
    
    def __init__(
        self,
        performative: Performative,
        sender: str,
        receiver: str,
        content: Any,
        language: str = "python-dict",
        ontology: str = "disaster-response",
        protocol: str = "fipa-request",
        conversation_id: Optional[str] = None,
        reply_to: Optional[str] = None,
        in_reply_to: Optional[str] = None
    ):
        """
        Initialize ACL Message
        
        Args:
            performative: The communicative act type
            sender: Agent identifier of the sender
            receiver: Agent identifier of the receiver
            content: The message content
            language: Content language (default: python-dict)
            ontology: Domain ontology (default: disaster-response)
            protocol: Interaction protocol (default: fipa-request)
            conversation_id: Conversation identifier
            reply_to: Message ID to reply to
            in_reply_to: Message this is a reply to
        """
        self.performative = performative
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.language = language
        self.ontology = ontology
        self.protocol = protocol
        self.conversation_id = conversation_id or self._generate_conversation_id()
        self.reply_to = reply_to
        self.in_reply_to = in_reply_to
        
        # Message metadata
        self.message_id = self._generate_message_id()
        self.timestamp = datetime.now()
    
    def _generate_message_id(self) -> str:
        """Generate unique message ID"""
        return f"MSG_{self.sender}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    def _generate_conversation_id(self) -> str:
        """Generate conversation ID"""
        return f"CONV_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "message_id": self.message_id,
            "performative": self.performative.value,
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "language": self.language,
            "ontology": self.ontology,
            "protocol": self.protocol,
            "conversation_id": self.conversation_id,
            "reply_to": self.reply_to,
            "in_reply_to": self.in_reply_to,
            "timestamp": self.timestamp.isoformat()
        }
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ACLMessage':
        """Create message from dictionary"""
        performative = Performative(data["performative"])
        msg = cls(
            performative=performative,
            sender=data["sender"],
            receiver=data["receiver"],
            content=data["content"],
            language=data.get("language", "python-dict"),
            ontology=data.get("ontology", "disaster-response"),
            protocol=data.get("protocol", "fipa-request"),
            conversation_id=data.get("conversation_id"),
            reply_to=data.get("reply_to"),
            in_reply_to=data.get("in_reply_to")
        )
        # Restore message ID and timestamp if available
        if "message_id" in data:
            msg.message_id = data["message_id"]
        if "timestamp" in data:
            msg.timestamp = datetime.fromisoformat(data["timestamp"])
        return msg
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ACLMessage':
        """Create message from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def create_reply(
        self,
        performative: Performative,
        content: Any,
        sender: str
    ) -> 'ACLMessage':
        """Create a reply to this message"""
        return ACLMessage(
            performative=performative,
            sender=sender,
            receiver=self.sender,  # Reply to original sender
            content=content,
            language=self.language,
            ontology=self.ontology,
            protocol=self.protocol,
            conversation_id=self.conversation_id,  # Same conversation
            in_reply_to=self.message_id
        )
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate message structure
        
        Returns:
            (is_valid, error_message)
        """
        # Check required fields
        if not self.sender:
            return False, "Sender is required"
        if not self.receiver:
            return False, "Receiver is required"
        if not self.performative:
            return False, "Performative is required"
        if self.content is None:
            return False, "Content is required"
        
        # Validate content based on performative
        if self.performative == Performative.REQUEST:
            if not isinstance(self.content, dict) or "action" not in self.content:
                return False, "REQUEST performative requires content with 'action' field"
        
        return True, None
    
    def __repr__(self) -> str:
        return (
            f"ACLMessage(id={self.message_id}, "
            f"performative={self.performative.value}, "
            f"sender={self.sender}, receiver={self.receiver})"
        )
    
    def __str__(self) -> str:
        """Human-readable string representation"""
        return (
            f"[{self.timestamp.strftime('%H:%M:%S')}] "
            f"{self.performative.value.upper()}: "
            f"{self.sender} -> {self.receiver}\n"
            f"Content: {self.content}"
        )


class MessageParser:
    """Parse and validate ACL messages"""
    
    @staticmethod
    def parse(message: ACLMessage) -> Dict[str, Any]:
        """
        Parse message content based on performative
        
        Returns:
            Parsed message data
        """
        parsed = {
            "performative": message.performative,
            "sender": message.sender,
            "receiver": message.receiver,
            "conversation_id": message.conversation_id,
            "timestamp": message.timestamp
        }
        
        if message.performative == Performative.INFORM:
            parsed["information"] = message.content
            parsed["fact"] = message.content.get("fact") if isinstance(message.content, dict) else message.content
        
        elif message.performative == Performative.REQUEST:
            if isinstance(message.content, dict):
                parsed["action"] = message.content.get("action")
                parsed["parameters"] = message.content.get("parameters", {})
            else:
                parsed["action"] = message.content
                parsed["parameters"] = {}
        
        elif message.performative == Performative.QUERY_IF:
            parsed["query"] = message.content
        
        elif message.performative in [Performative.CONFIRM, Performative.DISCONFIRM]:
            parsed["proposition"] = message.content
        
        elif message.performative in [Performative.AGREE, Performative.REFUSE]:
            parsed["action"] = message.content
        
        return parsed
    
    @staticmethod
    def extract_action(message: ACLMessage) -> Optional[str]:
        """Extract action from REQUEST message"""
        if message.performative == Performative.REQUEST:
            if isinstance(message.content, dict):
                return message.content.get("action")
            return str(message.content)
        return None
    
    @staticmethod
    def extract_information(message: ACLMessage) -> Any:
        """Extract information from INFORM message"""
        if message.performative == Performative.INFORM:
            return message.content
        return None

"""
Message Logger - Logs and analyzes FIPA-ACL message exchanges
Lab 4: Agent Communication using FIPA-ACL
"""

from typing import List, Dict, Optional
from datetime import datetime
import json
from fipa_acl import ACLMessage, Performative


class MessageLogger:
    """
    Logger for FIPA-ACL messages
    
    Captures all message exchanges and provides analysis capabilities
    """
    
    def __init__(self):
        self.messages: List[ACLMessage] = []
        self.conversations: Dict[str, List[ACLMessage]] = {}
    
    def log_message(self, message: ACLMessage):
        """Log a message"""
        self.messages.append(message)
        
        # Group by conversation
        conv_id = message.conversation_id
        if conv_id not in self.conversations:
            self.conversations[conv_id] = []
        self.conversations[conv_id].append(message)
    
    def get_messages_by_agent(self, agent_id: str) -> List[ACLMessage]:
        """Get all messages involving a specific agent"""
        return [
            msg for msg in self.messages 
            if msg.sender == agent_id or msg.receiver == agent_id
        ]
    
    def get_messages_by_performative(self, performative: Performative) -> List[ACLMessage]:
        """Get all messages with a specific performative"""
        return [msg for msg in self.messages if msg.performative == performative]
    
    def get_conversation(self, conversation_id: str) -> List[ACLMessage]:
        """Get all messages in a conversation"""
        return self.conversations.get(conversation_id, [])
    
    def get_statistics(self) -> Dict:
        """Get message statistics"""
        stats = {
            "total_messages": len(self.messages),
            "conversations": len(self.conversations),
            "by_performative": {},
            "by_agent": {}
        }
        
        # Count by performative
        for msg in self.messages:
            perf = msg.performative.value
            stats["by_performative"][perf] = stats["by_performative"].get(perf, 0) + 1
        
        # Count by agent (sent)
        for msg in self.messages:
            agent = msg.sender
            stats["by_agent"][agent] = stats["by_agent"].get(agent, 0) + 1
        
        return stats
    
    def save_to_file(self, filename: str = "message_log.txt"):
        """Save message log to file"""
        with open(filename, 'w') as f:
            f.write("="*80 + "\n")
            f.write("FIPA-ACL MESSAGE LOG - DISASTER RESPONSE SYSTEM\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            # Write statistics
            stats = self.get_statistics()
            f.write("MESSAGE STATISTICS\n")
            f.write("-"*80 + "\n")
            f.write(f"Total Messages: {stats['total_messages']}\n")
            f.write(f"Total Conversations: {stats['conversations']}\n\n")
            
            f.write("Messages by Performative:\n")
            for perf, count in stats['by_performative'].items():
                f.write(f"  - {perf.upper()}: {count}\n")
            
            f.write("\nMessages by Agent (sent):\n")
            for agent, count in stats['by_agent'].items():
                f.write(f"  - {agent}: {count}\n")
            
            f.write("\n" + "="*80 + "\n\n")
            
            # Write all messages
            f.write("ALL MESSAGES (Chronological)\n")
            f.write("="*80 + "\n\n")
            
            for i, msg in enumerate(self.messages, 1):
                f.write(f"Message #{i}\n")
                f.write("-"*80 + "\n")
                f.write(f"Message ID: {msg.message_id}\n")
                f.write(f"Timestamp: {msg.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
                f.write(f"Performative: {msg.performative.value.upper()}\n")
                f.write(f"Sender: {msg.sender}\n")
                f.write(f"Receiver: {msg.receiver}\n")
                f.write(f"Conversation ID: {msg.conversation_id}\n")
                if msg.in_reply_to:
                    f.write(f"In Reply To: {msg.in_reply_to}\n")
                f.write(f"Content: {msg.content}\n")
                f.write("\n")
            
            # Write conversations
            f.write("="*80 + "\n")
            f.write("CONVERSATIONS (Grouped)\n")
            f.write("="*80 + "\n\n")
            
            for conv_id, msgs in self.conversations.items():
                f.write(f"\nConversation: {conv_id}\n")
                f.write("-"*80 + "\n")
                f.write(f"Messages: {len(msgs)}\n\n")
                
                for msg in msgs:
                    f.write(f"  [{msg.timestamp.strftime('%H:%M:%S')}] ")
                    f.write(f"{msg.performative.value.upper()}: ")
                    f.write(f"{msg.sender} -> {msg.receiver}\n")
                    f.write(f"    Content: {msg.content}\n\n")
        
        print(f"Message log saved to: {filename}")
    
    def save_to_json(self, filename: str = "message_log.json"):
        """Save message log to JSON file"""
        data = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "total_messages": len(self.messages),
                "conversations": len(self.conversations)
            },
            "statistics": self.get_statistics(),
            "messages": [msg.to_dict() for msg in self.messages]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Message log (JSON) saved to: {filename}")
    
    def print_summary(self):
        """Print summary to console"""
        stats = self.get_statistics()
        
        print("\n" + "="*80)
        print("MESSAGE EXCHANGE SUMMARY")
        print("="*80)
        print(f"\nTotal Messages: {stats['total_messages']}")
        print(f"Conversations: {stats['conversations']}")
        
        print("\nMessages by Performative:")
        for perf, count in sorted(stats['by_performative'].items(), key=lambda x: x[1], reverse=True):
            print(f"  - {perf.upper()}: {count}")
        
        print("\nMessages by Agent:")
        for agent, count in sorted(stats['by_agent'].items(), key=lambda x: x[1], reverse=True):
            print(f"  - {agent}: {count} sent")
        
        print("="*80 + "\n")

"""
Lab 4 Main - Execution script for FIPA-ACL agent communication
Lab 4: Agent Communication using FIPA-ACL
"""

import sys
import logging
from datetime import datetime
from coordinator_agent import CoordinatorAgent
from field_agent import FieldAgent
from message_logger import MessageLogger
from fipa_acl import ACLMessage, Performative

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lab4_execution.log'),
        logging.StreamHandler(sys.stdout)
    ]
)


def print_separator(title=""):
    """Print a visual separator"""
    if title:
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}\n")
    else:
        print(f"{'='*80}\n")


def route_messages(agents):
    """Route messages between agents (simulates message transport layer)"""
    for sender in agents:
        while sender.outbox:
            msg = sender.outbox.pop(0)
            # Find receiver
            for receiver in agents:
                if receiver.agent_id == msg.receiver:
                    receiver.receive_message(msg)
                    break


def main():
    """Main execution for Lab 4"""
    print_separator("LAB 4: AGENT COMMUNICATION USING FIPA-ACL")
    
    print("Initializing Multi-Agent Communication System...")
    print()
    
    # Create message logger
    logger = MessageLogger()
    
    # Create coordinator
    coordinator = CoordinatorAgent("COORD-001", "Central Coordinator")
    
    # Create field agents
    field_agent1 = FieldAgent("FIELD-001", "Field Agent Alpha")
    field_agent2 = FieldAgent("FIELD-002", "Field Agent Bravo")
    field_agent3 = FieldAgent("FIELD-003", "Field Agent Charlie")
    
    # Register field agents with coordinator
    coordinator.register_field_agent(field_agent1.agent_id)
    coordinator.register_field_agent(field_agent2.agent_id)
    coordinator.register_field_agent(field_agent3.agent_id)
    
    # Set coordinators for field agents
    field_agent1.set_coordinator(coordinator.agent_id)
    field_agent2.set_coordinator(coordinator.agent_id)
    field_agent3.set_coordinator(coordinator.agent_id)
    
    agents = [coordinator, field_agent1, field_agent2, field_agent3]
    
    print("Agents created:")
    print(f"  - {coordinator.name} ({coordinator.agent_id})")
    print(f"  - {field_agent1.name} ({field_agent1.agent_id})")
    print(f"  - {field_agent2.name} ({field_agent2.agent_id})")
    print(f"  - {field_agent3.name} ({field_agent3.agent_id})")
    print()
    
    print_separator("SCENARIO 1: Earthquake Response Coordination")
    
    # Scenario 1: Major earthquake
    print("Disaster Event: Major earthquake detected in city center")
    print("Coordinator assessing situation and dispatching field agents...\n")
    
    coordinator.assess_situation({
        "type": "earthquake",
        "location": (25, 30),
        "severity": "high",
        "required_agents": 2
    })
    
    coordinator.dispatch_field_agents({
        "location": (25, 30),
        "type": "earthquake_response",
        "priority": "critical",
        "required_agents": 2
    })
    
    # Route messages and update agents
    print("Simulating agent communication and operations...\n")
    for step in range(50):
        # Route messages between agents
        route_messages(agents)
        
        # Update all agents
        for agent in agents:
            agent.update()
        
        # Log all messages
        for agent in agents:
            for msg in agent.message_history:
                if msg not in logger.messages:
                    logger.log_message(msg)
        
        # Check if missions complete
        if all(agent.current_state.value == "idle" for agent in [field_agent1, field_agent2]):
            break
    
    print("\nScenario 1 Complete!")
    print(f"Field Agent Alpha: {field_agent1.current_state.value} - Discoveries: {len(field_agent1.discoveries)}")
    print(f"Field Agent Bravo: {field_agent2.current_state.value} - Discoveries: {len(field_agent2.discoveries)}")
    
    print_separator("SCENARIO 2: Multi-Site Emergency Response")
    
    # Scenario 2: Multiple emergencies
    print("Multiple emergency reports coming in...")
    print("Coordinating response across multiple locations...\n")
    
    # Site 1: Fire
    coordinator.assess_situation({
        "type": "fire",
        "location": (15, 20),
        "severity": "medium",
        "required_agents": 1
    })
    
    coordinator.dispatch_field_agents({
        "location": (15, 20),
        "type": "fire_response",
        "priority": "high",
        "required_agents": 1
    })
    
    # Wait a bit
    for step in range(10):
        route_messages(agents)
        for agent in agents:
            agent.update()
    
    # Site 2: Building collapse
    coordinator.assess_situation({
        "type": "building_collapse",
        "location": (40, 35),
        "severity": "critical",
        "required_agents": 2
    })
    
    coordinator.dispatch_field_agents({
        "location": (40, 35),
        "type": "rescue_operation",
        "priority": "critical",
        "required_agents": 2
    })
    
    # Continue simulation
    for step in range(100):
        route_messages(agents)
        for agent in agents:
            agent.update()
        
        # Log messages
        for agent in agents:
            for msg in agent.message_history:
                if msg not in logger.messages:
                    logger.log_message(msg)
        
        # Check completion
        if coordinator.current_state.value == "completed":
            break
    
    print("\nScenario 2 Complete!")
    print(coordinator.get_active_missions_summary())
    
    print_separator("SCENARIO 3: Direct Inter-Agent Communication")
    
    # Demonstrate INFORM between field agents
    print("Field Agent Alpha sending information to Field Agent Bravo...\n")
    
    info_msg = ACLMessage(
        performative=Performative.INFORM,
        sender=field_agent1.agent_id,
        receiver=field_agent2.agent_id,
        content={
            "type": "situation_update",
            "message": "Area secured, proceeding to next location",
            "location": field_agent1.current_location
        }
    )
    
    field_agent1.send_message(info_msg)
    logger.log_message(info_msg)
    
    # Route and process
    route_messages([field_agent1, field_agent2])
    field_agent2.update()
    
    print("Direct communication successful!")
    
    print_separator("GENERATING MESSAGE LOGS")
    
    # Ensure all messages are logged
    for agent in agents:
        for msg in agent.message_history:
            if msg not in logger.messages:
                logger.log_message(msg)
    
    # Generate logs
    logger.save_to_file("lab4_message_log.txt")
    logger.save_to_json("lab4_message_log.json")
    
    # Print summary
    logger.print_summary()
    
    print_separator("MESSAGE EXCHANGE EXAMPLES")
    
    # Show examples of INFORM and REQUEST
    print("Example REQUEST Message:")
    print("-" * 80)
    request_msgs = logger.get_messages_by_performative(Performative.REQUEST)
    if request_msgs:
        example_request = request_msgs[0]
        print(f"From: {example_request.sender}")
        print(f"To: {example_request.receiver}")
        print(f"Content: {example_request.content}")
    
    print("\n")
    print("Example INFORM Message:")
    print("-" * 80)
    inform_msgs = logger.get_messages_by_performative(Performative.INFORM)
    if inform_msgs:
        example_inform = inform_msgs[0]
        print(f"From: {example_inform.sender}")
        print(f"To: {example_inform.receiver}")
        print(f"Content: {example_inform.content}")
    
    print_separator("EXECUTION SUMMARY")
    
    print("Communication Statistics:")
    stats = logger.get_statistics()
    print(f"  - Total Messages Exchanged: {stats['total_messages']}")
    print(f"  - REQUEST Performatives: {stats['by_performative'].get('request', 0)}")
    print(f"  - INFORM Performatives: {stats['by_performative'].get('inform', 0)}")
    print(f"  - AGREE Responses: {stats['by_performative'].get('agree', 0)}")
    print(f"  - CONFIRM Responses: {stats['by_performative'].get('confirm', 0)}")
    print(f"  - Total Conversations: {stats['conversations']}")
    
    print("\nAgent Activity:")
    for agent in agents:
        print(f"  - {agent.name}:")
        print(f"      Sent: {len(agent.get_sent_messages())} messages")
        print(f"      Received: {len(agent.get_received_messages())} messages")
    
    print_separator()
    print("Lab 4 Execution Complete!")
    print("\nOutputs generated:")
    print("  1. lab4_message_log.txt - Complete message exchange log")
    print("  2. lab4_message_log.json - Machine-readable message log")
    print("  3. lab4_execution.log - System log file")
    print("\nKey Performatives Demonstrated:")
    print("  [OK] REQUEST - Coordinator requesting actions from field agents")
    print("  [OK] INFORM - Field agents informing coordinator of discoveries")
    print("  [OK] AGREE - Agents agreeing to perform requested actions")
    print("  [OK] CONFIRM - Coordinator confirming received information")
    print_separator()


if __name__ == "__main__":
    main()

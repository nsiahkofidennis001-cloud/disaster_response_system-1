"""
Lab 3 Main - Execution script for FSM-based disaster response agents
Lab 3: Goals, Events, and Reactive Behavior
"""

import sys
import logging
from datetime import datetime
from rescue_agent import RescueAgent
from medical_agent import MedicalAgent
from event_system import EventGenerator, SensorReport
from fsm_agent import Event

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lab3_execution.log'),
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


def save_execution_trace(agents, filename="execution_trace.txt"):
    """Save execution traces from all agents to a file"""
    with open(filename, 'w') as f:
        f.write("="*80 + "\n")
        f.write("EXECUTION TRACE - DISASTER RESPONSE MULTI-AGENT SYSTEM\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
        
        for agent in agents:
            f.write(f"\n{'='*80}\n")
            f.write(f"Agent: {agent.name} (ID: {agent.agent_id})\n")
            f.write(f"{'='*80}\n\n")
            
            # Write state history
            f.write("STATE HISTORY:\n")
            f.write("-" * 80 + "\n")
            for state, timestamp, reason in agent.get_state_history():
                f.write(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] "
                       f"State: {state.value if hasattr(state, 'value') else state} - {reason}\n")
            
            f.write("\n")
            
            # Write goals
            f.write("GOALS:\n")
            f.write("-" * 80 + "\n")
            for goal in agent.goals:
                f.write(f"- [{goal.status.upper()}] {goal.description} (Priority: {goal.priority})\n")
            
            f.write("\n")
            
            # Write execution trace
            f.write("EXECUTION TRACE:\n")
            f.write("-" * 80 + "\n")
            for trace_entry in agent.get_execution_trace():
                f.write(trace_entry + "\n")
            
            f.write("\n")
    
    print(f"Execution trace saved to: {filename}")


def main():
    """Main execution for Lab 3"""
    print_separator("LAB 3: GOALS, EVENTS, AND REACTIVE BEHAVIOR")
    
    print("Initializing Disaster Response Multi-Agent System...")
    print()
    
    # Create agents
    rescue_agent1 = RescueAgent("R001", "Rescue Unit Alpha")
    rescue_agent2 = RescueAgent("R002", "Rescue Unit Bravo")
    medical_agent1 = MedicalAgent("M001", "Medical Team Alpha")
    medical_agent2 = MedicalAgent("M002", "Medical Team Bravo")
    
    agents = [rescue_agent1, rescue_agent2, medical_agent1, medical_agent2]
    
    print("Agents created:")
    for agent in agents:
        print(f"  - {agent.name} ({agent.agent_id}): State = {agent.current_state.value}")
    print()
    
    # Create event generator
    event_gen = EventGenerator(seed=42)
    
    print_separator("SCENARIO 1: Building Collapse")
    
    # Scenario 1: Building collapse
    collapse_report = SensorReport(
        sensor_id="SENSOR_1001",
        sensor_type="structural",
        location=(15, 20),
        reading={"damage_level": 0.9, "trapped_people": 5}
    )
    
    print(f"Sensor Report: {collapse_report}")
    events = event_gen.process_sensor_report(collapse_report)
    print(f"Generated Events: {events}")
    print()
    
    # Send event to rescue agent
    for event in events:
        rescue_agent1.receive_event(event)
    
    # Simulate agent execution (multiple update cycles)
    print("Simulating rescue operation...\n")
    for step in range(40):  # Enough steps for complete mission
        rescue_agent1.update()
        if rescue_agent1.current_state.value == "idle":
            break
    
    print(f"\nRescue Agent 1 Status:")
    print(f"  - Current State: {rescue_agent1.current_state.value}")
    print(f"  - Total Rescued: {rescue_agent1.rescued_count}")
    print(f"  - Location: {rescue_agent1.current_location}")
    
    print_separator("SCENARIO 2: Medical Emergency")
    
    # Scenario 2: Medical emergency
    medical_report = SensorReport(
        sensor_id="SENSOR_2001",
        sensor_type="medical",
        location=(10, 15),
        reading={
            "injured_count": 8,
            "severity": "critical",
            "needs_evacuation": True
        }
    )
    
    print(f"Sensor Report: {medical_report}")
    events = event_gen.process_sensor_report(medical_report)
    print(f"Generated Events: {events}")
    print()
    
    # Send event to medical agent
    for event in events:
        medical_agent1.receive_event(event)
    
    # Simulate agent execution
    print("Simulating medical response...\n")
    for step in range(40):
        medical_agent1.update()
        if medical_agent1.current_state.value == "idle":
            break
    
    print(f"\nMedical Agent 1 Status:")
    print(f"  - Current State: {medical_agent1.current_state.value}")
    print(f"  - Patients Treated: {medical_agent1.patients_treated}")
    print(f"  - Medical Supplies: {medical_agent1.medical_supplies}%")
    print(f"  - Location: {medical_agent1.current_location}")
    
    print_separator("SCENARIO 3: Multiple Simultaneous Emergencies")
    
    # Generate multiple events
    print("Simulating disaster scenario with random events...\n")
    disaster_events = event_gen.simulate_disaster_scenario(duration_steps=5)
    
    print(f"Generated {len(disaster_events)} events:")
    for i, event in enumerate(disaster_events, 1):
        print(f"  {i}. {event.event_type} at {event.data.get('location')} (priority: {event.priority})")
    print()
    
    # Distribute events to agents
    event_idx = 0
    for event in disaster_events:
        if event.event_type in ["BUILDING_COLLAPSE", "MAJOR_EARTHQUAKE", "FIRE_DETECTED"]:
            # Assign to rescue agents alternately
            rescue_agent2.receive_event(event)
        elif event.event_type == "MEDICAL_EMERGENCY":
            # Assign to medical agents
            medical_agent2.receive_event(event)
        event_idx += 1
    
    # Simulate all agents for multiple steps
    print("Simulating coordinated response...\n")
    for step in range(50):
        for agent in [rescue_agent2, medical_agent2]:
            agent.update()
    
    print("Final Agent Status:")
    print(f"  - Rescue Unit Bravo: State={rescue_agent2.current_state.value}, Rescued={rescue_agent2.rescued_count}")
    print(f"  - Medical Team Bravo: State={medical_agent2.current_state.value}, Treated={medical_agent2.patients_treated}")
    
    print_separator("GENERATING EXECUTION TRACE")
    
    # Save execution trace
    save_execution_trace(agents, "lab3_execution_trace.txt")
    
    # Print summary
    print_separator("EXECUTION SUMMARY")
    
    print("Goals Achieved:")
    for agent in agents:
        print(f"\n{agent.name}:")
        for goal in agent.goals:
            status_symbol = "[X]" if goal.status == "completed" else "[ ]"
            print(f"  {status_symbol} {goal.description} [{goal.status.upper()}]")
    
    print()
    print("Overall Statistics:")
    total_rescued = sum(agent.rescued_count for agent in agents if hasattr(agent, 'rescued_count'))
    total_treated = sum(agent.patients_treated for agent in agents if hasattr(agent, 'patients_treated'))
    print(f"  - Total People Rescued: {total_rescued}")
    print(f"  - Total Patients Treated: {total_treated}")
    print(f"  - Total Events Processed: {len(event_gen.event_history)}")
    
    print_separator()
    print("Lab 3 Execution Complete!")
    print("\nOutputs generated:")
    print("  1. lab3_execution_trace.txt - Complete execution trace")
    print("  2. lab3_execution.log - System log file")
    print("\nNext: Run 'python generate_fsm_diagram.py' to create FSM diagrams")
    print_separator()


if __name__ == "__main__":
    main()

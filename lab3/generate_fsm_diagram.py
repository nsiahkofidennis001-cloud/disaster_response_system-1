"""
FSM Diagram Generator - Creates visual diagrams of agent FSMs
Lab 3: Goals, Events, and Reactive Behavior
"""

try:
    from graphviz import Digraph
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False
    print("Warning: graphviz not available. Will generate text-based diagram.")

from rescue_agent import RescueAgentState
from medical_agent import MedicalAgentState


def create_rescue_agent_diagram():
    """Create FSM diagram for Rescue Agent"""
    
    if GRAPHVIZ_AVAILABLE:
        dot = Digraph(comment='Rescue Agent FSM')
        dot.attr(rankdir='LR')
        dot.attr('node', shape='circle', style='filled', fillcolor='lightblue')
        
        # Add states
        states = [state for state in RescueAgentState]
        for state in states:
            if state == RescueAgentState.IDLE:
                dot.node(state.value, state.value.upper(), fillcolor='lightgreen')
            elif state == RescueAgentState.COMPLETED:
                dot.node(state.value, state.value.upper(), fillcolor='gold')
            else:
                dot.node(state.value, state.value.upper())
        
        # Add transitions
        dot.edge('idle', 'responding', label='Emergency Event\n(BUILDING_COLLAPSE,\nMAJOR_EARTHQUAKE,\nFIRE_DETECTED)')
        dot.edge('responding', 'rescuing', label='Arrived at\nLocation')
        dot.edge('rescuing', 'transporting', label='Rescue\nComplete')
        dot.edge('transporting', 'completed', label='Victims\nDelivered')
        dot.edge('completed', 'idle', label='Ready for\nNext Mission')
        
        # Save diagram
        dot.render('fsm_rescue_agent', format='png', cleanup=True)
        print("[OK] Rescue Agent FSM diagram saved: fsm_rescue_agent.png")
        return True
    else:
        return False


def create_medical_agent_diagram():
    """Create FSM diagram for Medical Agent"""
    
    if GRAPHVIZ_AVAILABLE:
        dot = Digraph(comment='Medical Agent FSM')
        dot.attr(rankdir='LR')
        dot.attr('node', shape='circle', style='filled', fillcolor='lightcoral')
        
        # Add states
        states = [state for state in MedicalAgentState]
        for state in states:
            if state == MedicalAgentState.IDLE:
                dot.node(state.value, state.value.upper(), fillcolor='lightgreen')
            elif state == MedicalAgentState.COMPLETED:
                dot.node(state.value, state.value.upper(), fillcolor='gold')
            else:
                dot.node(state.value, state.value.upper())
        
        # Add transitions
        dot.edge('idle', 'dispatched', label='Medical\nEmergency')
        dot.edge('dispatched', 'treating', label='Arrived at\nLocation')
        dot.edge('treating', 'transporting', label='Treatment Complete\n& Evacuation Needed')
        dot.edge('treating', 'completed', label='Treatment Complete\n& No Evacuation')
        dot.edge('transporting', 'completed', label='Patients\nDelivered')
        dot.edge('completed', 'idle', label='Ready for\nNext Mission')
        
        # Save diagram
        dot.render('fsm_medical_agent', format='png', cleanup=True)
        print("[OK] Medical Agent FSM diagram saved: fsm_medical_agent.png")
        return True
    else:
        return False


def create_text_diagrams():
    """Create text-based FSM diagrams"""
    
    rescue_text = """
RESCUE AGENT FSM
================

    [IDLE] --(Emergency Event)--> [RESPONDING] --(Arrived)--> [RESCUING]
      ^                                                           |
      |                                                           |
      +--(Reset)-- [COMPLETED] <--(Delivered)-- [TRANSPORTING] <--+
                                                  (Rescue Complete)

States:
  - IDLE: Agent waiting for emergency
  - RESPONDING: Moving to emergency location
  - RESCUING: Performing rescue operation
  - TRANSPORTING: Transporting victims to safety
  - COMPLETED: Mission completed

Events:
  - BUILDING_COLLAPSE: Building has collapsed, people trapped
  - MAJOR_EARTHQUAKE: Major earthquake detected
  - FIRE_DETECTED: Fire emergency detected
"""
    
    medical_text = """
MEDICAL AGENT FSM
=================

    [IDLE] --(Medical Emergency)--> [DISPATCHED] --(Arrived)--> [TREATING]
      ^                                                             |    |
      |                                                             |    |
      +--(Reset)------ [COMPLETED] <--------------------------------+    |
                            ^                                            |
                            |                                            |
                            +----(Delivered)---- [TRANSPORTING] <--------+
                                                (Needs Evacuation)

States:
  - IDLE: Agent waiting for medical emergency
  - DISPATCHED: Moving to emergency location
  - TREATING: Providing medical treatment
  - TRANSPORTING: Evacuating critical patients
  - COMPLETED: Mission completed

Events:
  - MEDICAL_EMERGENCY: Medical emergency with injured patients
"""
    
    with open('fsm_diagrams_text.txt', 'w', encoding='utf-8') as f:
        f.write(rescue_text)
        f.write("\n" + "="*80 + "\n\n")
        f.write(medical_text)
    
    print("[OK] Text-based FSM diagrams saved: fsm_diagrams_text.txt")


def main():
    """Generate FSM diagrams"""
    print("="*80)
    print("  FSM DIAGRAM GENERATOR - Lab 3")
    print("="*80)
    print()
    
    if GRAPHVIZ_AVAILABLE:
        print("Generating graphical FSM diagrams...\n")
        create_rescue_agent_diagram()
        create_medical_agent_diagram()
        print("\n[OK] All graphical diagrams generated successfully!")
    else:
        print("Graphviz not available. Install with: pip install graphviz")
        print("Note: You also need to install Graphviz system package.")
        print("      Visit: https://graphviz.org/download/\n")
    
    print("\nGenerating text-based FSM diagrams...\n")
    create_text_diagrams()
    
    print("\n" + "="*80)
    print("Diagram generation complete!")
    print("="*80)


if __name__ == "__main__":
    main()

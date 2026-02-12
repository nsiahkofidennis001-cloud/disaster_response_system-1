# Disaster Response Multi-Agent System
## Labs 3 & 4 Implementation

A comprehensive multi-agent disaster response system implementing FSM-based reactive behavior (Lab 3) and FIPA-ACL agent communication (Lab 4).

## System Overview

This system demonstrates intelligent agent coordination in disaster response scenarios using:
- **Finite State Machines (FSM)** for agent behavior modeling
- **Event-driven reactive behavior** from sensor reports
- **FIPA-ACL standardized messaging** for inter-agent communication
- **Goal-oriented agents** with multiple objectives

## Project Structure

```
disaster_response_system-1/
├── lab3/                          # Lab 3: FSM & Reactive Behavior
│   ├── fsm_agent.py              # Core FSM agent implementation
│   ├── event_system.py           # Event generation from sensors
│   ├── rescue_agent.py           # Rescue agent with FSM
│   ├── medical_agent.py          # Medical agent with FSM
│   ├── lab3_main.py              # Lab 3 execution script
│   └── generate_fsm_diagram.py   # FSM diagram generator
│
├── lab4/                          # Lab 4: FIPA-ACL Communication
│   ├── fipa_acl.py               # FIPA-ACL message structure
│   ├── communicating_agent.py    # Base communicating agent
│   ├── coordinator_agent.py      # Coordinator agent
│   ├── field_agent.py            # Field agent
│   ├── message_logger.py         # Message logging system
│   └── lab4_main.py              # Lab 4 execution script
│
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Lab 3: Goals, Events, and Reactive Behavior

### Agent Types

1. **Rescue Agent**
   - States: IDLE → RESPONDING → RESCUING → TRANSPORTING → COMPLETED
   - Goals: Quick response, rescue trapped individuals, transport victims
   - Triggers: Building collapse, earthquake, fire events

2. **Medical Agent**
   - States: IDLE → DISPATCHED → TREATING → TRANSPORTING → COMPLETED
   - Goals: Rapid response, provide treatment, evacuate patients
   - Triggers: Medical emergency events

### Running Lab 3

```bash
# Navigate to project directory
cd "C:\Users\Administrator\Disaster_Response_System -1\disaster_response_system-1"

# Run Lab 3
python lab3/lab3_main.py

# Generate FSM diagrams
python lab3/generate_fsm_diagram.py
```

### Lab 3 Deliverables

✓ **FSM Diagram**: `fsm_diagrams_text.txt` (text-based diagrams)  
✓ **Python Implementation**: All agent classes with FSM behavior  
✓ **Execution Trace**: `lab3_execution_trace.txt`

## Lab 4: Agent Communication using FIPA-ACL

### Communication Architecture

- **Coordinator Agent**: Sends REQUEST messages, receives INFORM messages
- **Field Agents**: Receive REQUEST messages, send INFORM messages with discoveries
- **Message Types**: INFORM, REQUEST, AGREE, REFUSE, CONFIRM, QUERY-IF

### Key Performatives Used

1. **REQUEST**: Coordinator requests field agents to investigate locations
2. **INFORM**: Field agents inform coordinator of discoveries and status
3. **AGREE**: Agents agree to perform requested actions
4. **CONFIRM**: Coordinator confirms received information

### Running Lab 4

```bash
# Run Lab 4
python lab4/lab4_main.py
```

### Lab 4 Deliverables

✓ **Message Logs**: `lab4_message_log.txt` (human-readable)  
✓ **Message Logs (JSON)**: `lab4_message_log.json` (machine-readable)  
✓ **Agent Communication Code**: All FIPA-ACL implementation files

## Key Features

### Lab 3 Features
- ✅ Goal-oriented agent behavior
- ✅ Event-triggered reactive behavior
- ✅ FSM state management with transitions
- ✅ Sensor report processing
- ✅ Execution trace generation
- ✅ Multiple agent types (rescue, medical)

### Lab 4 Features
- ✅ Full FIPA-ACL message structure
- ✅ Multiple performatives (INFORM, REQUEST, AGREE, etc.)
- ✅ Message parsing and validation
- ✅ Conversation tracking
- ✅ Message logging and analysis
- ✅ Inter-agent coordination

## Installation

### Prerequisites
- Python 3.7 or higher

### Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: For FSM diagram generation with Graphviz, you also need to install Graphviz system package:
- Windows: https://graphviz.org/download/
- After installing, add Graphviz to your PATH

## Output Files

### Lab 3 Outputs
- `lab3_execution_trace.txt` - Complete agent execution trace
- `lab3_execution.log` - System execution log
- `fsm_diagrams_text.txt` - Text-based FSM diagrams
- `fsm_rescue_agent.png` - Rescue agent FSM diagram (if Graphviz available)
- `fsm_medical_agent.png` - Medical agent FSM diagram (if Graphviz available)

### Lab 4 Outputs
- `lab4_message_log.txt` - Human-readable message log
- `lab4_message_log.json` - Machine-readable JSON message log
- `lab4_execution.log` - System execution log

## Example Usage

### Lab 3 Example - Disaster Scenario

```python
from rescue_agent import RescueAgent
from event_system import EventGenerator, SensorReport

# Create rescue agent
agent = RescueAgent("R001", "Rescue Unit Alpha")

# Generate earthquake event
report = SensorReport("SENSOR_1001", "structural", (15, 20), 
                     {"damage_level": 0.9, "trapped_people": 5})
events = EventGenerator().process_sensor_report(report)

# Agent reacts to event
agent.receive_event(events[0])
agent.update()  # Transitions through FSM states
```

### Lab 4 Example - Agent Communication

```python
from coordinator_agent import CoordinatorAgent
from field_agent import FieldAgent
from fipa_acl import ACLMessage, Performative

# Create agents
coordinator = CoordinatorAgent("COORD-001", "Central Coordinator")
field_agent = FieldAgent("FIELD-001", "Field Agent Alpha")

# Coordinator sends REQUEST
coordinator.dispatch_field_agents({
    "location": (25, 30),
    "type": "earthquake_response",
    "priority": "critical"
})

# Field agent receives and responds with INFORM
# (Automatic through message processing)
```

## Understanding the System

### FSM State Transitions (Lab 3)

Agents transition between states based on:
1. **Events**: External triggers from sensors
2. **Conditions**: Internal state checks
3. **Actions**: Side effects during transitions

### FIPA-ACL Messages (Lab 4)

Message structure includes:
- **Performative**: Type of communicative act
- **Sender/Receiver**: Agent identifiers
- **Content**: Message payload
- **Conversation ID**: Groups related messages
- **Ontology**: Domain knowledge representation

## Learning Objectives Achievement

### Lab 3 ✓
- [x] Model agent goals and event-triggered behavior
- [x] Implement FSMs for reactive agents
- [x] Process sensor reports and generate events
- [x] Generate execution traces and FSM diagrams

### Lab 4 ✓
- [x] Enable inter-agent communication
- [x] Implement FIPA-ACL message exchange
- [x] Use INFORM and REQUEST performatives
- [x] Parse messages and trigger agent actions
- [x] Generate comprehensive message logs

## Troubleshooting

**Issue**: Graphviz not found  
**Solution**: Install Graphviz system package or use text-based diagrams

**Issue**: Module import errors  
**Solution**: Ensure you're running from the project root directory

**Issue**: No output files generated  
**Solution**: Check file permissions and ensure scripts complete execution

## Future Enhancements

- Add more agent types (fire, hazmat, logistics)
- Implement negotiation protocols
- Add real-time visualization
- Integrate with actual sensor data
- Implement learning and adaptation

## Author

Created for Multi-Agent Systems Lab 3 & 4

## License

Educational use for laboratory assignments
"""
Event System - Sensor reports and event triggering for disaster response
Lab 3: Goals, Events, and Reactive Behavior
"""

import random
from typing import List, Dict, Any
from datetime import datetime
from fsm_agent import Event


class SensorReport:
    """Represents a sensor report from the disaster zone"""
    def __init__(self, sensor_id: str, sensor_type: str, location: tuple, reading: Dict[str, Any]):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type  # seismic, fire, gas, structural, medical
        self.location = location  # (x, y) coordinates
        self.reading = reading
        self.timestamp = datetime.now()
    
    def __repr__(self):
        return f"SensorReport({self.sensor_type} at {self.location}: {self.reading})"


class EventGenerator:
    """Generates events from sensor reports for disaster scenarios"""
    
    def __init__(self, seed: int = None):
        if seed:
            random.seed(seed)
        self.event_history: List[Event] = []
    
    def process_sensor_report(self, report: SensorReport) -> List[Event]:
        """Process a sensor report and generate events"""
        events = []
        
        if report.sensor_type == "seismic":
            events.extend(self._process_seismic(report))
        elif report.sensor_type == "fire":
            events.extend(self._process_fire(report))
        elif report.sensor_type == "gas":
            events.extend(self._process_gas(report))
        elif report.sensor_type == "structural":
            events.extend(self._process_structural(report))
        elif report.sensor_type == "medical":
            events.extend(self._process_medical(report))
        
        self.event_history.extend(events)
        return events
    
    def _process_seismic(self, report: SensorReport) -> List[Event]:
        """Process seismic sensor data"""
        events = []
        magnitude = report.reading.get("magnitude", 0)
        
        if magnitude > 6.0:
            events.append(Event(
                event_type="MAJOR_EARTHQUAKE",
                data={
                    "location": report.location,
                    "magnitude": magnitude,
                    "sensor_id": report.sensor_id
                },
                priority=5
            ))
        elif magnitude > 4.0:
            events.append(Event(
                event_type="EARTHQUAKE_DETECTED",
                data={
                    "location": report.location,
                    "magnitude": magnitude,
                    "sensor_id": report.sensor_id
                },
                priority=3
            ))
        
        return events
    
    def _process_fire(self, report: SensorReport) -> List[Event]:
        """Process fire sensor data"""
        events = []
        temperature = report.reading.get("temperature", 0)
        smoke_level = report.reading.get("smoke_level", 0)
        
        if temperature > 100 or smoke_level > 0.7:
            events.append(Event(
                event_type="FIRE_DETECTED",
                data={
                    "location": report.location,
                    "temperature": temperature,
                    "smoke_level": smoke_level,
                    "severity": "high" if temperature > 150 else "medium"
                },
                priority=4
            ))
        
        return events
    
    def _process_gas(self, report: SensorReport) -> List[Event]:
        """Process gas leak sensor data"""
        events = []
        gas_concentration = report.reading.get("gas_concentration", 0)
        
        if gas_concentration > 0.5:
            events.append(Event(
                event_type="GAS_LEAK_DETECTED",
                data={
                    "location": report.location,
                    "concentration": gas_concentration,
                    "gas_type": report.reading.get("gas_type", "unknown")
                },
                priority=4
            ))
        
        return events
    
    def _process_structural(self, report: SensorReport) -> List[Event]:
        """Process structural damage sensor data"""
        events = []
        damage_level = report.reading.get("damage_level", 0)
        
        if damage_level > 0.7:
            events.append(Event(
                event_type="BUILDING_COLLAPSE",
                data={
                    "location": report.location,
                    "damage_level": damage_level,
                    "trapped_people": report.reading.get("trapped_people", 0)
                },
                priority=5
            ))
        elif damage_level > 0.4:
            events.append(Event(
                event_type="STRUCTURAL_DAMAGE",
                data={
                    "location": report.location,
                    "damage_level": damage_level
                },
                priority=3
            ))
        
        return events
    
    def _process_medical(self, report: SensorReport) -> List[Event]:
        """Process medical emergency sensor data"""
        events = []
        injured_count = report.reading.get("injured_count", 0)
        severity = report.reading.get("severity", "low")
        
        if injured_count > 0:
            events.append(Event(
                event_type="MEDICAL_EMERGENCY",
                data={
                    "location": report.location,
                    "injured_count": injured_count,
                    "severity": severity,
                    "needs_evacuation": report.reading.get("needs_evacuation", False)
                },
                priority=5 if severity == "critical" else 3
            ))
        
        return events
    
    def generate_random_sensor_report(self) -> SensorReport:
        """Generate a random sensor report for testing"""
        sensor_types = ["seismic", "fire", "gas", "structural", "medical"]
        sensor_type = random.choice(sensor_types)
        location = (random.randint(0, 100), random.randint(0, 100))
        
        readings = {
            "seismic": {"magnitude": random.uniform(3.0, 7.5)},
            "fire": {
                "temperature": random.uniform(20, 200),
                "smoke_level": random.uniform(0, 1)
            },
            "gas": {
                "gas_concentration": random.uniform(0, 1),
                "gas_type": random.choice(["CO", "CH4", "CO2"])
            },
            "structural": {
                "damage_level": random.uniform(0, 1),
                "trapped_people": random.randint(0, 10)
            },
            "medical": {
                "injured_count": random.randint(1, 20),
                "severity": random.choice(["low", "medium", "high", "critical"]),
                "needs_evacuation": random.choice([True, False])
            }
        }
        
        return SensorReport(
            sensor_id=f"SENSOR_{random.randint(1000, 9999)}",
            sensor_type=sensor_type,
            location=location,
            reading=readings[sensor_type]
        )
    
    def simulate_disaster_scenario(self, duration_steps: int = 10) -> List[Event]:
        """Simulate a disaster scenario with multiple sensor reports"""
        all_events = []
        
        for step in range(duration_steps):
            report = self.generate_random_sensor_report()
            events = self.process_sensor_report(report)
            all_events.extend(events)
        
        return all_events

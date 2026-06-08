from dataclasses import dataclass
from enum import Enum

class BTType(Enum):
    ROBOT = 1
    HUMAN = 2

@dataclass
class Action: 
    name: str

@dataclass
class Step: 
    actions: list[Action]
    name: str

@dataclass
class Subgoal: 
    steps: list[Step]
    name: str

@dataclass
class Goal: 
    subgoals: list[Subgoal]
    name: str

@dataclass
class BehaviorTree: 
    goal: Goal 
    bt_type: BTType


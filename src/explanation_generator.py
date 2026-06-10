from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from lxml import etree
from bt import Subgoal, Step, Action 
from bt_parser import BehaviorTreeXMLParser, BehaviorTreeParseError
import util


DEBUG_ENABLED: bool = True


class TriggerType(Enum):
    SUBGOAL_MISMATCH = 1
    STEPS_MISMATCH = 2
    STEPS_SEQUENCE_MISMATCH = 2
    ACTION_UNSUCCESSFUL = 3


@dataclass
class Trigger: 
    relevant_elements: list[Subgoal|Step|Action]
    trigger_type: TriggerType


class ExplanationGenerator:
    def __init__(self, bt_robot_path: Path, bt_human_path: Path): 
        parser = BehaviorTreeXMLParser()
        parser.validate(bt_robot_path)
        parser.validate(bt_human_path)

        try:
            self.__bt_robot = parser.parse(bt_robot_path)
            self.__bt_human = parser.parse(bt_human_path)

            if DEBUG_ENABLED:
                print("Parsed behavior trees: \n")
                util.print_bt(self.__bt_robot)
                print("\n")
                util.print_bt(self.__bt_human)
                print("\n")
            

        except etree.DocumentInvalid as e:
            print(f"Schema error: {e}")
        except BehaviorTreeParseError as e:
            print(f"Semantic error: {e}")

    def compute_triggers(self) -> list[Trigger]|None:
        """
        Computes triggers based on the comparison of the robot's and human's behavior tree. 
        The following triggers exist: 
          1. Subgoals of both behavior trees don't match
          2. Steps mismatch for a subgoal
          3. Sequence mismatch of steps with relevant sequence
          4. Action was not successful 

        :return: list of triggers resulting from the comparison of both behavior trees
        :rtype: list[Trigger]
        """
        return [Trigger(relevant_elements=[], trigger_type=TriggerType.SUBGOAL_MISMATCH)]

    def generate_explanation(self, trigger: Trigger) -> tuple[str, str]: 
        """
        Generates an explanation based on the trigger. 

        :param trigger: trigger for the explanation
        :type trigger: Trigger
        :return: tuple with question, answer 
        :rtype: tuple[str, str]
        """
        _ = trigger
        return "", ""


from dataclasses import dataclass
from enum import Enum
from os import EX_CANTCREAT, name
from pathlib import Path
from lxml import etree
from bt import Goal, Subgoal, Step, Action 
from bt_parser import BehaviorTreeXMLParser, BehaviorTreeParseError
import util


DEBUG_ENABLED: bool = True


class TriggerType(Enum):
    SUBGOAL_MISMATCH = 1
    SUBGOAL_MISMATCH_MISSING = 2
    SUBGOAL_MISMATCH_EXTRA = 3
    STEPS_MISMATCH = 4
    STEPS_SEQUENCE_MISMATCH = 5
    ACTION_UNSUCCESSFUL = 6


@dataclass
class Trigger: 
    trigger_type: TriggerType
    relevant_elements: list[Goal|Subgoal|Step|Action]


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

    def detect_triggers(self) -> list[Trigger]:
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
        triggers: list[Trigger]|None = []
        # case 1: SUBGOAL_MISMATCH*
        subgoal_mismatch_trigger: Trigger|None = self.__detect_subgoal_mismatch()
        if subgoal_mismatch_trigger is not None:
            triggers.append(subgoal_mismatch_trigger)

        # case 2: STEPS_MISMATCH
        # case 3: STEPS_SEQUENCE_MISMATCH
        # case 4: ACTION_UNSUCCESSFUL
        return triggers

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


    def __detect_subgoal_mismatch(self) -> Trigger|None:
        """
        Checks if a subgoal mismatch is present in the bts
        :return: Trigger if a mismatch has been detected else None
        :rtype: Trigger|None
        """
        robot_subgoals = {x.name for x in self.__bt_robot.goal.subgoals}
        human_subgoals = {x.name for x in self.__bt_human.goal.subgoals}
        extra_subgoals = robot_subgoals - human_subgoals
        missing_subgoals = human_subgoals - robot_subgoals

        if not missing_subgoals and not extra_subgoals:
            return None

        # SUBGOAL_MISMATCH
        elif missing_subgoals and extra_subgoals:
            # use procedure description of parent goal entity
            return Trigger(
                trigger_type=TriggerType.SUBGOAL_MISMATCH,
                relevant_elements=[self.__bt_robot.goal]
            )

        # SUBGOAL_MISMATCH_MISSING
        elif missing_subgoals and not extra_subgoals:
            # use procedure description of parent goal entity
            # TODO: find a more meaningful way of creating an explanation
            return Trigger(
                trigger_type=TriggerType.SUBGOAL_MISMATCH_MISSING,
                relevant_elements=[self.__bt_robot.goal, self.__bt_human.goal]
            )
        
        # SUBGOAL_MISMATCH_EXTRA
        else:
            # use subgoal description for explaining relevance
            subgoals = []
            for subgoal_name in extra_subgoals: 
                for subgoal in self.__bt_robot.goal.subgoals:
                    if subgoal.name == subgoal_name:
                        subgoals.append(subgoal)
                        break
            return Trigger(
                trigger_type=TriggerType.SUBGOAL_MISMATCH_EXTRA,
                relevant_elements=subgoals
            )


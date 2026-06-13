from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from lxml import etree
from bt_parser import BehaviorTreeXMLParser
import util


DEBUG_ENABLED: bool = True
GOAL_NAME: str = "clean the kitchen counter"


class TriggerType(Enum):
    SUBGOAL_MISMATCH = 1
    SUBGOAL_MISMATCH_MISSING = 2
    SUBGOAL_MISMATCH_EXTRA = 3
    STEPS_MISMATCH = 4
    STEPS_MISMATCH_EXTRA = 5
    #TODO: STEPS_SEQUENCE_MISMATCH
    ACTION_UNSUCCESSFUL = 6


@dataclass
class Trigger: 
    trigger_type: TriggerType
    relevant_elements: list[dict]


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
                print(self.__bt_robot)
                util.print_bt(self.__bt_robot)
                print("\n")
                util.print_bt(self.__bt_human)
                print("\n")

        except etree.DocumentInvalid as e:
            print(f"Schema error: {e}")

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
        result: list[Trigger] = []
        # case 1: SUBGOAL_MISMATCH*
        triggers: list[Trigger] = self.__detect_subgoal_mismatch()
        for t in triggers: 
            result.append(t)

        # case 2: STEPS_MISMATCH
        triggers = self.__detect_step_mismatches()
        for t in triggers:
            result.append(t)

        #TODO: case 3: ACTION_UNSUCCESSFUL

        return result

    def generate_explanation(self, trigger: Trigger) -> tuple[str, str]: 
        """
        Generates an explanation based on the trigger. 

        :param trigger: trigger for the explanation
        :type trigger: Trigger
        :return: tuple with question, answer 
        :rtype: tuple[str, str]
        """
        match trigger.trigger_type:
            case TriggerType.SUBGOAL_MISMATCH: 
                return (
                    "How do you do you plan to " + GOAL_NAME + "?", 
                    self.__bt_robot[GOAL_NAME]["description"] 
            )
            case TriggerType.SUBGOAL_MISMATCH_MISSING: 
                pass
            case TriggerType.SUBGOAL_MISMATCH_EXTRA: 
                pass
            case TriggerType.STEPS_MISMATCH: 
                pass
            case TriggerType.STEPS_MISMATCH_EXTRA: 
                pass
            case TriggerType.ACTION_UNSUCCESSFUL: 
                pass

        return "", ""


    def __detect_subgoal_mismatch(self) -> list[Trigger]:
        """
        Checks if a subgoal mismatch is present in the BTs
        :return: Trigger if a mismatch has been detected else None
        :rtype: list[Trigger]
        """
        robot_subgoals = {x for x in self.__bt_robot[GOAL_NAME]["subgoals"].keys()}
        human_subgoals = {x for x in self.__bt_human[GOAL_NAME]["subgoals"].keys()}
        extra_subgoals = robot_subgoals - human_subgoals
        missing_subgoals = human_subgoals - robot_subgoals

        if not missing_subgoals and not extra_subgoals:
            return []

        # SUBGOAL_MISMATCH
        elif missing_subgoals and extra_subgoals:
            # use procedure description of parent goal entity
            return [Trigger(
                trigger_type=TriggerType.SUBGOAL_MISMATCH,
                relevant_elements=[self.__bt_robot]
            )]
        # SUBGOAL_MISMATCH_MISSING
        elif missing_subgoals and not extra_subgoals:
            # use procedure description of parent goal entity
            # TODO: find a more meaningful way of creating an explanation
            return [Trigger(
                trigger_type=TriggerType.SUBGOAL_MISMATCH_MISSING,
                relevant_elements=[self.__bt_robot[GOAL_NAME], self.__bt_human[GOAL_NAME]]
            )]
        
        # SUBGOAL_MISMATCH_EXTRA
        else:
            # use subgoal description for explaining relevance
            subgoals = {
                name: steps
                for name, steps in self.__bt_robot[GOAL_NAME]["subgoals"].items()
                if name in extra_subgoals
            }
            return [Trigger(
                trigger_type=TriggerType.SUBGOAL_MISMATCH_EXTRA,
                relevant_elements=[subgoals]
            )]

    def __detect_step_mismatches(self) -> list[Trigger]:
        """
        Checks if a step mismatch is present in the BTs
        :return: Trigger if a mismatch has been detected else None
        :rtype: list[Trigger]
        """
        result: list[Trigger] = []
        # get_matching_subgoals
        robot_subgoal_names = {x for x in self.__bt_robot[GOAL_NAME]["subgoals"].keys()}
        human_subgoal_names = {x for x in self.__bt_human[GOAL_NAME]["subgoals"].keys()}
        robot_subgoals = {
            x: self.__bt_robot[GOAL_NAME]["subgoals"][x] 
            for x in robot_subgoal_names & human_subgoal_names
        } 
        human_subgoals = {
            x: self.__bt_human[GOAL_NAME]["subgoals"][x] 
            for x in robot_subgoal_names & human_subgoal_names
        } 
        # get steps human and robot
        for subgoal_name, robot_steps in robot_subgoals.items():
            human_steps: dict = human_subgoals[subgoal_name] 
            robot_step_names = set(robot_steps.keys())
            human_step_names = set(human_steps.keys())
            missing_steps_names: set[str] = human_step_names - robot_step_names
            extra_steps_names: set[str] = robot_step_names - human_step_names

            if not missing_steps_names and not extra_steps_names:
                continue
            elif missing_steps_names:
                # explain the overall process to fulfill the subgoal
                result.append(Trigger(
                    trigger_type=TriggerType.STEPS_MISMATCH,
                    relevant_elements=[self.__bt_robot[GOAL_NAME]["subgoals"][subgoal_name]]
                ))
            elif not missing_steps_names and extra_steps_names:
                # explain the reason for every extra step
                result.append(Trigger(
                    trigger_type=TriggerType.STEPS_MISMATCH_EXTRA,
                    relevant_elements=[self.__bt_robot[GOAL_NAME]["subgoals"][subgoal_name][x] 
                                       for x in extra_steps_names]
                ))

        return result

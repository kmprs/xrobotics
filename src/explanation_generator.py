from dataclasses import dataclass
from enum import Enum
from typing import Dict
from pathlib import Path
from lxml import etree
from bt_parser import BehaviorTreeXMLParser
from simulation_execution import SimulationExecution
import util
import constants


class TriggerType(Enum):
    SUBGOAL_MISMATCH = 1
    SUBGOAL_MISMATCH_MISSING = 2
    SUBGOAL_MISMATCH_EXTRA = 3
    STEPS_MISMATCH = 4
    STEPS_MISMATCH_EXTRA = 5
    #TODO: STEPS_SEQUENCE_MISMATCH
    ACTION_UNSUCCESSFUL = 6


BehaviorTree = Dict


@dataclass
class Trigger: 
    trigger_type: TriggerType
    relevant_elements: list


class ExplanationGenerator:
    def __init__(self, bt_robot_path: Path, bt_human_path: Path, simulation_execution: SimulationExecution): 
        self.__simulation_execution = simulation_execution
        parser = BehaviorTreeXMLParser()
        parser.validate(bt_robot_path)
        parser.validate(bt_human_path)

        try:
            self.__bt_robot: BehaviorTree = parser.parse(bt_robot_path)
            self.__bt_human: BehaviorTree = parser.parse(bt_human_path)
            print(self.__bt_human)
            self.__goal_name: str = next(iter(self.__bt_robot.keys()))

            if constants.DEBUG_ENABLED:
                print("Parsed behavior trees: \n")
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

        # case 3: ACTION_UNSUCCESSFUL
        if not self.__simulation_execution.was_successful() and self.__simulation_execution.erronous_element:
            erronous_element = util.find_object(self.__bt_robot, self.__simulation_execution.erronous_element[0])
            if erronous_element is None:
                raise ValueError(f"Element with name not found")

            result.append(Trigger(
                trigger_type=TriggerType.ACTION_UNSUCCESSFUL,
                # 0: step name, 1: reason
                relevant_elements=self.__simulation_execution.erronous_element
            ))

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
            case TriggerType.SUBGOAL_MISMATCH | TriggerType.SUBGOAL_MISMATCH_MISSING:
                return (
                    constants.MISMATCH_GENERAL_QUESTION_PHRASE + self.__goal_name + "?", 
                    trigger.relevant_elements[0][self.__goal_name]["description"] 
                )
            case TriggerType.SUBGOAL_MISMATCH_EXTRA: 
                subgoal_name = next(iter(trigger.relevant_elements[0].keys()))
                return (
                    constants.MISMATCH_EXTRA_QUESTION_PHRASE + subgoal_name + constants.QUESTION_MARK,
                    ("I " + subgoal_name + 
                         " because " + trigger.relevant_elements[0][subgoal_name]["need"])
                )
            case TriggerType.STEPS_MISMATCH: 
                subgoal_name = list(trigger.relevant_elements[0].keys())[0] 
                return (
                    constants.MISMATCH_GENERAL_QUESTION_PHRASE + subgoal_name +
                    constants.QUESTION_MARK, 
                    trigger.relevant_elements[0][subgoal_name]["description"] 
                )
            case TriggerType.STEPS_MISMATCH_EXTRA: 
                step_name = next(iter(trigger.relevant_elements[0].keys()))
                return (
                    constants.MISMATCH_EXTRA_QUESTION_PHRASE + step_name + constants.QUESTION_MARK,
                    ("I " + step_name + 
                         " because " + trigger.relevant_elements[0][step_name]["need"])
                )
            case TriggerType.ACTION_UNSUCCESSFUL: 
                # relevant_elements: 1=STEP: dict, 2=REASON: str
                step_name: str = trigger.relevant_elements[0]
                reason: str = trigger.relevant_elements[1]
                return (
                    constants.UNINTENTIONAL_BEHAVIOR_QUESTION_PHRASE + step_name +
                    constants.QUESTION_MARK,
                    constants.UNINTENTIONAL_BEHAVIOR_ANSWER_PHRASE + step_name + " because " +
                    reason + ".")

    @property
    def bt_robot(self):
        return self.__bt_robot

    @property
    def bt_human(self):
        return self.__bt_human


    def __detect_subgoal_mismatch(self) -> list[Trigger]:
        """
        Checks if a subgoal mismatch is present in the BTs
        :return: Trigger if a mismatch has been detected else None
        :rtype: list[Trigger]
        """
        robot_subgoals = {x for x in self.__bt_robot[self.__goal_name]["subgoals"].keys()}
        human_subgoals = {x for x in self.__bt_human[self.__goal_name]["subgoals"].keys()}
        extra_subgoals = robot_subgoals - human_subgoals
        missing_subgoals = human_subgoals - robot_subgoals

        if not missing_subgoals and not extra_subgoals:
            return []

        # SUBGOAL_MISMATCH or SUBGOAL_MISMATCH_MISSING
        # TODO: find a more meaningful way of creating an explanation for SUBGOAL_MISMATCH_MISSING
        elif (missing_subgoals and extra_subgoals) or (missing_subgoals and not extra_subgoals):
            # use procedure description of parent goal entity
            return [Trigger(
                trigger_type=TriggerType.SUBGOAL_MISMATCH,
                relevant_elements=[self.__bt_robot]
            )]
        # SUBGOAL_MISMATCH_EXTRA
        else:
            # use subgoal need for explaining relevance
            result: list[Trigger] = []
            for name, content in self.__bt_robot[self.__goal_name]["subgoals"].items():
                if name in extra_subgoals:
                    result.append(Trigger(
                        trigger_type=TriggerType.SUBGOAL_MISMATCH_EXTRA,
                        relevant_elements=[{name: content}]
                    ))
            return result

    def __detect_step_mismatches(self) -> list[Trigger]:
        """
        Checks if a step mismatch is present in the BTs
        :return: Trigger if a mismatch has been detected else None
        :rtype: list[Trigger]
        """
        result: list[Trigger] = []
        # get_matching_subgoals
        robot_subgoal_names = {x for x in self.__bt_robot[self.__goal_name]["subgoals"].keys()}
        human_subgoal_names = {x for x in self.__bt_human[self.__goal_name]["subgoals"].keys()}
        robot_subgoals = {
            x: self.__bt_robot[self.__goal_name]["subgoals"][x] 
            for x in robot_subgoal_names & human_subgoal_names
        } 
        human_subgoals = {
            x: self.__bt_human[self.__goal_name]["subgoals"][x] 
            for x in robot_subgoal_names & human_subgoal_names
        } 
        # get steps human and robot
        for subgoal_name, robot_steps in robot_subgoals.items():
            robot_steps = robot_steps["steps"]
            human_steps: dict = human_subgoals[subgoal_name]["steps"] 
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
                    relevant_elements=[{subgoal_name: self.__bt_robot[self.__goal_name]["subgoals"][subgoal_name]}]
                ))
            elif not missing_steps_names and extra_steps_names:
                # explain the reason for every extra step
                result.append(Trigger(
                    trigger_type=TriggerType.STEPS_MISMATCH_EXTRA,
                    relevant_elements=[{x: self.__bt_robot[self.__goal_name]["subgoals"][subgoal_name]["steps"][x]} 
                                       for x in extra_steps_names]
                ))

        return result

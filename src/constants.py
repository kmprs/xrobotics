from pathlib import Path


BT_ROBOT_FILE_PATH = Path(__file__).parent  / "../assets/bt/bt_robot.xml"
BT_HUMAN_FILE_PATH = Path(__file__).parent  / "../assets/bt/bt_human.xml"
SCENARIO_FILE_PATH = Path(__file__).parent / "../assets/simulation_runs/load_dishwasher.json"

DEBUG_ENABLED: bool = True
GOAL_NAME: str = "load the dishwasher"

QUESTION_MARK: str = "?"
MISMATCH_GENERAL_QUESTION_PHRASE: str = "How do you plan to "
MISMATCH_EXTRA_QUESTION_PHRASE: str = "Why do you "
UNINTENTIONAL_BEHAVIOR_QUESTION_PHRASE: str = "Why did you fail to "
UNINTENTIONAL_BEHAVIOR_ANSWER_PHRASE: str = "I failed to "


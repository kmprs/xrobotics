from lxml import etree
from pathlib import Path
from bt_parser import BehaviorTreeXMLParser, BehaviorTreeParseError
from explanation_generator import ExplanationGenerator
import util


BT_ROBOT_FILE_PATH = Path(__file__).parent  / "../assets/bt/bt_robot_delivery.xml"
BT_HUMAN_FILE_PATH = Path(__file__).parent  / "../assets/bt/bt_human_delivery.xml"


def main(): 
    explanation_generator = ExplanationGenerator(
        bt_robot_path=BT_ROBOT_FILE_PATH,
        bt_human_path=BT_HUMAN_FILE_PATH
    )
    _ = explanation_generator


if __name__ == "__main__":
    main()


from lxml import etree
from pathlib import Path
from bt_parser import BehaviorTreeXMLParser, BehaviorTreeParseError
import util


TREE_ROBOT_FILE_PATH = Path(__file__).parent  / "../assets/bt/bt_robot_delivery.xml"
TREE_HUMAN_FILE_PATH = Path(__file__).parent  / "../assets/bt/bt_human_delivery.xml"


def main(): 
    parser = BehaviorTreeXMLParser() 
    parser.validate(TREE_ROBOT_FILE_PATH)
    parser.validate(TREE_HUMAN_FILE_PATH)

    try:
        tree_robot = parser.parse(TREE_ROBOT_FILE_PATH)
        tree_human = parser.parse(TREE_HUMAN_FILE_PATH)
        util.print_bt(tree_robot)
        util.print_bt(tree_human)
        
    except etree.DocumentInvalid as e:
        print(f"Schema error: {e}")
    except BehaviorTreeParseError as e:
        print(f"Semantic error: {e}")


if __name__ == "__main__":
    main()


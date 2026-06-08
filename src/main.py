from lxml import etree
from pathlib import Path
from bt_parser import BehaviorTreeXMLParser, BehaviorTreeParseError
import util


TREE_FILE_PATH = Path(__file__).parent  / "../assets/bt/example_tree.xml"


def main(): 
    parser = BehaviorTreeXMLParser() 
    parser.validate(TREE_FILE_PATH)

    try:
        tree = parser.parse(TREE_FILE_PATH)
        util.print_bt(tree)
        
    except etree.DocumentInvalid as e:
        print(f"Schema error: {e}")
    except BehaviorTreeParseError as e:
        print(f"Semantic error: {e}")


if __name__ == "__main__":
    main()


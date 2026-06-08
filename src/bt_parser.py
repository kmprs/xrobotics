import xml.etree.ElementTree as ET
from pathlib import Path
from lxml import etree
from bt import Action, BehaviorTree, BTType, Goal, Step, Subgoal

BT_SCHEMA_PATH = Path(__file__).parent  / "schemes/behavior_tree.xsd"


class BehaviorTreeParseError(Exception):
    """Raised when XML is structurally valid but semantically incorrect."""


class BehaviorTreeXMLParser:
    def __init__(self, schema_path: Path | str = BT_SCHEMA_PATH) -> None:
        self._schema = self.__load_schema(Path(schema_path))

    def parse(self, xml_path: Path | str) -> BehaviorTree:
        xml_path = Path(xml_path)
        if not xml_path.exists():
            raise FileNotFoundError(f"XML file not found: {xml_path}")

        root = self.__validate_and_parse(xml_path)
        return self.__parse_bt(root)

    def validate(self, xml_path: Path | str) -> bool:
        try:
            xml_path = Path(xml_path)
            doc = etree.parse(str(xml_path))
            self._schema.assertValid(doc)
            return True
        except (etree.DocumentInvalid, etree.XMLSyntaxError) as exc:
            print(f"Validation failed: {exc}")
            return False


    @staticmethod
    def __load_schema(schema_path: Path) -> etree.XMLSchema:
        if not schema_path.exists():
            raise FileNotFoundError(f"XSD schema not found: {schema_path}")
        schema_doc = etree.parse(str(schema_path))
        return etree.XMLSchema(schema_doc)

    def __validate_and_parse(self, xml_path: Path) -> ET.Element:
        doc = etree.parse(str(xml_path))
        self._schema.assertValid(doc) 
        return ET.parse(str(xml_path)).getroot()

    def __parse_bt(self, element: ET.Element) -> BehaviorTree:
        bt_type_str = element.attrib["bt_type"]
        try:
            bt_type = BTType[bt_type_str]
        except KeyError as exc:
            valid = [m.name for m in BTType]
            raise BehaviorTreeParseError(
                f"Unknown bt_type '{bt_type_str}'. Valid values: {valid}"
            ) from exc

        goal_element = element.find("Goal")
        if goal_element is None: 
            raise BehaviorTreeParseError(
                f"Failed to parse behavior tree: no goal defined!"
            )
        goal = self.__parse_goal(goal_element)
        return BehaviorTree(goal=goal, bt_type=bt_type)

    def __parse_goal(self, element: ET.Element) -> Goal:
        name = element.attrib["name"]
        subgoals = [
            self.__parse_subgoal(child)
            for child in element.findall("Subgoal")
        ]
        return Goal(subgoals=subgoals, name=name)

    def __parse_subgoal(self, element: ET.Element) -> Subgoal:
        name = element.attrib["name"]
        steps = [
            self.__parse_step(child)
            for child in element.findall("Step")
        ]
        return Subgoal(steps=steps, name=name)

    def __parse_step(self, element: ET.Element) -> Step:
        name = element.attrib["name"]
        actions = [
            self.__parse_action(child)
            for child in element.findall("Action")
        ]
        return Step(actions=actions, name=name)

    @staticmethod
    def __parse_action(element: ET.Element) -> Action:
        return Action(name=element.attrib["name"])


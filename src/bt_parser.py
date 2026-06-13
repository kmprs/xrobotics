from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from lxml import etree


BT_SCHEMA_PATH: Path = Path(__file__).parent / "schemes/behavior_tree.xsd"


BTDict = dict[str, dict]


@dataclass
class ValidationError:
    line: int
    column: int
    message: str

    def __str__(self) -> str:
        return f"Line {self.line}, col {self.column}: {self.message}"


 
class BehaviorTreeValidationError(ValueError):
    def __init__(self, source: str, errors: list[ValidationError]) -> None:
        self.source = source
        self.errors = errors
        detail = "\n".join(f"  • {e}" for e in errors)
        super().__init__(f"'{source}' failed XSD validation:\n{detail}")
 
 
class BehaviorTreeXMLParser:
    def __init__(self, schema_path: Path | str = BT_SCHEMA_PATH) -> None:
        self.schema_path = Path(schema_path)
        schema_doc = etree.parse(str(self.schema_path))
        self._schema = etree.XMLSchema(schema_doc)
 
    def validate(self, xml_path: Path | str) -> None:
        xml_path = Path(xml_path)
        doc = etree.parse(str(xml_path))
        self.__assert_valid(doc, source=xml_path.name)
 
    def parse(self, xml_path: Path | str) -> BTDict:
        xml_path = Path(xml_path)
        doc = etree.parse(str(xml_path))
        self.__assert_valid(doc, source=xml_path.name)
        return self.__parse_tree(doc.getroot())
 
    def parse_string(self, xml_string: str) -> BTDict:
        root = etree.fromstring(xml_string.encode())
        doc = etree.ElementTree(root)
        self.__assert_valid(doc, source="<string>")
        return self.__parse_tree(root)
 

    def __assert_valid(self, doc: etree._ElementTree, *, source: str) -> None:
        if not self._schema.validate(doc):
            errors = [
                ValidationError(
                    line=entry.line,
                    column=entry.column,
                    message=entry.message,
                )
                for entry in self._schema.error_log
            ]
            raise BehaviorTreeValidationError(source=source, errors=errors)
 
    def __parse_tree(self, root: etree._Element) -> BTDict:
        goal_elem = root.find("Goal")
        description_elem = goal_elem.find("Description")
        return {
            goal_elem.attrib["name"]: {
                "bt_type": root.attrib["bt_type"],
                "description": (description_elem.attrib["value"] 
                                if description_elem is not None
                                else None),
                "subgoals": {
                    sg.attrib["name"]: self.__parse_subgoal(sg)
                    for sg in goal_elem.findall("Subgoal")
                },
            }
        }
 
    def __parse_subgoal(self, subgoal_elem: etree._Element) -> dict:
        return {
            step_elem.attrib["name"]: self.__parse_step(step_elem)
            for step_elem in subgoal_elem.findall("Step")
        }
 
    @staticmethod
    def __parse_step(step_elem: etree._Element) -> dict:
        return {
            "actions": [
                action_elem.attrib["name"]
                for action_elem in step_elem.findall("Action")
            ]
        }

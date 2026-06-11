from pathlib import Path
from explanation_generator import ExplanationGenerator


BT_ROBOT_FILE_PATH = Path(__file__).parent  / "../assets/bt/bt_robot_delivery.xml"
BT_HUMAN_FILE_PATH = Path(__file__).parent  / "../assets/bt/bt_human_delivery.xml"


def main(): 
    explanation_generator = ExplanationGenerator(
        bt_robot_path=BT_ROBOT_FILE_PATH,
        bt_human_path=BT_HUMAN_FILE_PATH
    )
    triggers = explanation_generator.detect_triggers()
    if len(triggers) > 0: 
        for trigger in triggers: 
            print(trigger.trigger_type)
    else: 
        print("No triggers detected")


if __name__ == "__main__":
    main()


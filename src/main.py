from pathlib import Path
from explanation_generator import ExplanationGenerator
import constants


def main(): 
    explanation_generator = ExplanationGenerator(
        bt_robot_path=constants.BT_ROBOT_FILE_PATH,
        bt_human_path=constants.BT_HUMAN_FILE_PATH
    )
    triggers = explanation_generator.detect_triggers()
    if len(triggers) == 0: 
        print("No explanation triggers detected")
    else:
        print("──────────────────────────────────────────────────────────────────────────────")
        for trigger in triggers:
            question, answer = explanation_generator.generate_explanation(trigger)
            print(f"QUESTION: {question}")
            if constants.DEBUG_ENABLED:
                print(f"───>TRIGGER: {trigger.trigger_type}")
            print(f"\nANSWER: {answer}")
            print("──────────────────────────────────────────────────────────────────────────────\n\n")

if __name__ == "__main__":
    main()


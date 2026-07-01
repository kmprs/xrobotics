from pathlib import Path
from explanation_generator import ExplanationGenerator
import constants
from simulation_execution import SimulationExecution


def main(): 
    simulation_execution = SimulationExecution(
        scenario_data=constants.SCENARIO_FILE_PATH
    )
    explanation_generator = ExplanationGenerator(
        bt_robot_path=constants.BT_ROBOT_FILE_PATH,
        bt_human_path=constants.BT_HUMAN_FILE_PATH,
        simulation_execution=simulation_execution 
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
            print("──────────────────────────────────────────────────────────────────────────────")

if __name__ == "__main__":
    main()


from pathlib import Path
from tempfile import TemporaryDirectory
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
from explanation_generator import ExplanationGenerator
from simulation_execution import SimulationExecution
import util


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

app = Flask(
    __name__, 
    template_folder=ROOT / "ui",
    static_folder=ROOT / "ui",
    static_url_path=""
)
CORS(app)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(ASSETS, filename)

@app.route("/compare", methods=["POST"])
def compare():
    if "robotTree" not in request.files:
        return jsonify({"error": "Missing robot behavior tree."}), 400

    if "humanTree" not in request.files:
        return jsonify({"error": "Missing human behavior tree."}), 400

    if "scenario" not in request.files:
        return jsonify({"error": "Missing scenario file."}), 400

    robot_bt_file = request.files["robotTree"]
    human_bt_file = request.files["humanTree"]
    scenario_file = request.files["scenario"]

    with TemporaryDirectory() as tmp:

        robot_bt_path= Path(tmp) / str(robot_bt_file.filename)
        human_bt_path = Path(tmp) / str(human_bt_file.filename)
        scenario_path = Path(tmp) / str(scenario_file.filename)

        robot_bt_file.save(robot_bt_path)
        human_bt_file.save(human_bt_path)
        scenario_file.save(scenario_path)

        simulation_execution = SimulationExecution(scenario_path)
        explanation_generator = ExplanationGenerator(
            robot_bt_path,
            human_bt_path,
            simulation_execution
        )
        triggers = explanation_generator.detect_triggers()
        explanations = []
        
        for trigger in triggers:
        
            question, answer = explanation_generator.generate_explanation(trigger)
        
            explanations.append({
                "question": question,
                "answer": answer
            })
        
        bt_robot = util.bt_to_frontend(explanation_generator.bt_robot)
        bt_human = util.bt_to_frontend(explanation_generator.bt_human)

        response = {
            "robotTree": bt_robot, 
            "humanTree": bt_human,
            "video": simulation_execution.video_path,
            "explanations": explanations
        }

        return jsonify(response)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True,
    )

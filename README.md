# xrobotics

> Explainable robotics through behavior tree comparison.

`xrobotics` compares a robot's Behavior Tree with an expected (human) Behavior Tree and execution trace to automatically detect behavioral mismatches and generate natural-language explanations for the robot's decisions.

The project includes both:

* a command-line interface for running explanations on predefined scenarios
* a web interface for uploading Behavior Trees and simulation data for interactive comparison

---

## Features

* Compare robot and human Behavior Trees
* Parse Behavior Trees from XML
* Analyze execution traces from simulation runs
* Detect explanation triggers automatically
* Generate human-readable questions and answers
* Web UI for interactive comparison
* Example assets and scenarios included

---

## Requirements

* Python 3.11+
* pip

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the CLI

The default CLI uses the example assets defined in `src/constants.py`.

```bash
python3 src/main.py
```

If explanation triggers are found, the program prints a sequence of generated questions and explanations.

Example:

```text
QUESTION:
Why do you move to the counter?

ANSWER:
...
```

---

## Running the Web Interface

Start the Flask server:

```bash
python3 src/server.py
```

Open your browser:

```text
http://localhost:8000
```

The web interface allows you to upload

* Robot Behavior Tree
* Human Behavior Tree
* Simulation scenario

and generates explanations for any detected behavioral differences.

---

## Input Files

The project expects:

### Robot Behavior Tree

An XML Behavior Tree describing the robot's actual behavior.

### Human Behavior Tree

An XML Behavior Tree describing the expected or desired behavior.

### Simulation Scenario

A JSON execution trace representing the robot's execution during a task. The video input in the
example files was generated using [robocasa](https://robocasa.ai). Feel free to use any other
simulator for the generation of videos.

---

## Example Assets

Example inputs are included under:

```text
assets/
├── bt/
└── simulation_runs/
```

These can be used to explore the explanation generation pipeline without creating new datasets.


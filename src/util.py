from bt_parser import BTDict
def print_bt(bt_dict: BTDict) -> None:
    """
    Example output:
    [ROBOT] BehaviorTree
    └── Goal: AssemblePart
        │   Description: "I first grasp the object and the place it"
        ├── Subgoal: Grasp
        │   │   Need: "Pick up the object firmly without dropping it"
        │   │   Description: "Pick up the object firmly"
        │   ├── Step: Approach
        │   │   ├── Action: move_arm
        │   │   └── Action: open_gripper
        │   └── Step: Close
        │       └── Action: close_gripper
        └── Subgoal: Place
            └── Step: Release
                └── Action: open_gripper
    """
    for goal_name, goal_data in bt_dict.items():
        bt_type = goal_data.get("bt_type", "UNKNOWN")
        print(f"[{bt_type}] BehaviorTree")
        print(f"└── Goal: {goal_name}")
        description = goal_data.get("description")
        if description is not None:
            print(f'    │   Description: "{description}"')
        subgoals = goal_data["subgoals"]
        for i, (subgoal_name, subgoal_data) in enumerate(subgoals.items()):
            is_last_subgoal = i == len(subgoals) - 1
            subgoal_prefix = "    └──" if is_last_subgoal else "    ├──"
            subgoal_indent = "        " if is_last_subgoal else "    │   "
            print(f"{subgoal_prefix} Subgoal: {subgoal_name}")
            subgoal_need = subgoal_data.get("need")
            if subgoal_need is not None:
                print(f'{subgoal_indent}│   Need: "{subgoal_need}"')
            subgoal_description = subgoal_data.get("description")
            if subgoal_description is not None:
                print(f'{subgoal_indent}│   Description: "{subgoal_description}"')
            steps = subgoal_data["steps"]
            step_items = list(steps.items())
            for j, (step_name, step_data) in enumerate(step_items):
                is_last_step = j == len(step_items) - 1
                step_prefix = "└──" if is_last_step else "├──"
                step_indent = subgoal_indent + ("    " if is_last_step else "│   ")
                print(f"{subgoal_indent}{step_prefix} Step: {step_name}")
                actions = step_data["actions"]
                for k, action_name in enumerate(actions):
                    ac_prefix = "└──" if k == len(actions) - 1 else "├──"
                    print(f"{step_indent}{ac_prefix} Action: {action_name}")

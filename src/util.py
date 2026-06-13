from bt_parser import BTDict


def print_bt(bt_dict: BTDict) -> None:
    """
    Example output:
    [ROBOT] BehaviorTree
    └── Goal: AssemblePart
        │   Description: "I first grasp the object and the place it"
        ├── Subgoal: Grasp
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
        for i, (subgoal_name, steps) in enumerate(subgoals.items()):
            is_last_sg = i == len(subgoals) - 1
            sg_prefix = "    └──" if is_last_sg else "    ├──"
            sg_indent = "        " if is_last_sg else "    │   "

            print(f"{sg_prefix} Subgoal: {subgoal_name}")

            step_items = list(steps.items())
            for j, (step_name, step_data) in enumerate(step_items):
                is_last_st = j == len(step_items) - 1
                st_prefix = "└──" if is_last_st else "├──"
                st_indent = sg_indent + ("    " if is_last_st else "│   ")
                print(f"{sg_indent}{st_prefix} Step: {step_name}")

                actions = step_data["actions"]
                for k, action_name in enumerate(actions):
                    ac_prefix = "└──" if k == len(actions) - 1 else "├──"
                    print(f"{st_indent}{ac_prefix} Action: {action_name}")

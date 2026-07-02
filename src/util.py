from bt_parser import BTDict


def print_bt(bt_dict: BTDict) -> None:
    """
    Prints a behavior tree in a structured human-readable format.
    :param bt_dict: behavior tree dictionary to print
    :type bt_dict: BTDict

    Example output:
    BehaviorTree
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


def find_object(tree: dict | list, object_name: str) -> dict | None:
    """
    Recursively searches a nested dictionary for a key.

    :param tree: The dictionary (or list of dictionaries) to search.
    :type tree: dict | list
    :param object_name: The key to search for.
    :type object_name: str
    :return: The value associated with the first matching key
    :rtype: dict | None

    :raises ValueError: if the object_name does not exist
    """
    if isinstance(tree, dict):
        if object_name in tree:
            return tree[object_name]

        for value in tree.values():
            result = find_object(value, object_name)
            if result is not None:
                return result

    elif isinstance(tree, list):
        for item in tree:
            result = find_object(item, object_name)
            if result is not None:
                return result

    return None


def bt_to_frontend(bt: dict) -> dict:
    """
    Converts a parsed behavior tree into a frontend-compatible hierarchical structure.

    :param bt: behavior tree dictionary
    :type bt: dict
    :returns: tree in {name, children} format suitable for UI rendering
    :rtype: dict
    """

    root_name = next(iter(bt))
    root_content = bt[root_name]

    return convert_node(root_name, root_content)


def convert_node(name: str, node: dict) -> dict:
    """
    Recursively converts a behavior tree node into a frontend-compatible format.

    :param name: node identifier
    :type name: str
    :param node: node content containing subgoals and steps
    :type node: dict
    :returns: converted node with name and children fields
    :rtype: dict
    """
    result = {
        "name": name,
        "children": []
    }

    # Add subgoals
    for subgoal_name, subgoal in node.get("subgoals", {}).items():
        result["children"].append(
            convert_node(subgoal_name, subgoal)
        )

    # Add steps
    for step_name, step in node.get("steps", {}).items():
        result["children"].append(
            convert_node(step_name, step)
        )

    return result


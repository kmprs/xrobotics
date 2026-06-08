from bt import BehaviorTree

def print_bt(bt: BehaviorTree):
    print(f"[{bt.bt_type.name}] BehaviorTree")
    print(f"└── Goal: {bt.goal.name}")
    for i, subgoal in enumerate(bt.goal.subgoals):
        sg_prefix = "    └──" if i == len(bt.goal.subgoals) - 1 else "    ├──"
        print(f"{sg_prefix} Subgoal: {subgoal.name}")
        indent = "        " if i == len(bt.goal.subgoals) - 1 else "    │   "
        for j, step in enumerate(subgoal.steps):
            st_prefix = "└──" if j == len(subgoal.steps) - 1 else "├──"
            print(f"{indent}{st_prefix} Step: {step.name}")
            act_indent = indent + ("    " if j == len(subgoal.steps) - 1 else "│   ")
            for k, action in enumerate(step.actions):
                ac_prefix = "└──" if k == len(step.actions) - 1 else "├──"
                print(f"{act_indent}{ac_prefix} Action: {action.name}")


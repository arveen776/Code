from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import List

from recorder import Recorder
from replayer import replay
from workflows import add_workflow, find_best_workflow, load_workflows


def record_flow() -> None:
    recorder = Recorder()
    input("Press Enter to start recording...")
    recorder.start()
    input("Recording... perform your workflow, then press Enter to stop.")
    print("Stopping recorder...")
    events = recorder.stop()
    if not events:
        print("No events captured. Try again.")
        return

    print(f"Captured {len(events)} events.")
    name = input("Name this workflow: ").strip()
    description = input("Describe this workflow: ").strip()

    workflow = add_workflow(name, description, events)
    print(f"Saved workflow '{workflow['name']}' with id {workflow['id']}.")


def list_workflows() -> List[dict]:
    workflows = load_workflows()
    if not workflows:
        print("No workflows saved yet.")
        return workflows

    for idx, workflow in enumerate(workflows):
        print(f"[{idx}] {workflow['name']} — {workflow['description']}")
    return workflows


def replay_by_index() -> None:
    workflows = list_workflows()
    if not workflows:
        return

    choice = input("Select workflow index: ").strip()
    if not choice.isdigit():
        print("Please enter a valid number.")
        return

    idx = int(choice)
    if idx < 0 or idx >= len(workflows):
        print("Invalid index.")
        return

    _run_workflow(workflows[idx])


def replay_by_command() -> None:
    workflows = load_workflows()
    if not workflows:
        print("No workflows saved yet.")
        return

    command = input("What do you want me to do? ").strip()
    best = find_best_workflow(command, workflows)
    if not best:
        print("Could not find a matching workflow.")
        return

    print(
        f"Best match: {best['name']} — {best['description']}",
    )
    confirm = input("Run this workflow? (y/n): ").strip().lower()
    if confirm == "y":
        _run_workflow(best)


def _run_workflow(workflow: dict) -> None:
    print("Replaying in 3 seconds. Switch to the target window.")
    time.sleep(3)
    replay(workflow.get("events", []))
    print("Done.")


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="NAVI v0 CLI")
    parser.add_argument(
        "--mode",
        choices=["menu", "record", "list", "replay", "command"],
        default="menu",
        help="Choose how to interact with NAVI.",
    )
    return parser.parse_args(argv)


def run_menu() -> None:
    while True:
        print(
            "\nNAVI v0\n"
            "1) Record new workflow\n"
            "2) List workflows\n"
            "3) Replay by index\n"
            "4) Replay by natural language\n"
            "5) Exit"
        )
        choice = input("Select option: ").strip()
        if choice == "1":
            record_flow()
        elif choice == "2":
            list_workflows()
        elif choice == "3":
            replay_by_index()
        elif choice == "4":
            replay_by_command()
        elif choice == "5":
            print("Goodbye.")
            break
        else:
            print("Invalid option.")


def main() -> None:
    args = parse_args(sys.argv[1:])
    if args.mode == "record":
        record_flow()
    elif args.mode == "list":
        list_workflows()
    elif args.mode == "replay":
        replay_by_index()
    elif args.mode == "command":
        replay_by_command()
    else:
        run_menu()


if __name__ == "__main__":
    main()


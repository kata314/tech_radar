#!/usr/bin/env python3
"""Tech Radar CLI — validate, list, and add entries to radar.yaml.

IMPORTANT: This uses ruamel.yaml (not PyYAML) deliberately.
ruamel.yaml preserves comments, formatting, and block scalar style (the > markers)
when reading and writing YAML. PyYAML strips all of this on save, making the file
harder to read and producing noisy git diffs. Do not switch to PyYAML.

Install: pip install ruamel.yaml
"""

import argparse
import sys
from datetime import date
from pathlib import Path

from ruamel.yaml import YAML

RADAR_FILE = Path(__file__).parent / "radar.yaml"

VALID_QUADRANTS = {"models", "infrastructure", "libraries", "techniques"}
VALID_RINGS = {"adopt", "trial", "assess", "hold"}

# ruamel.yaml instance — preserves comments and formatting on round-trip
_yaml = YAML()
_yaml.preserve_quotes = True
_yaml.width = 90


def load_radar() -> dict:
    return _yaml.load(RADAR_FILE)


def save_radar(data: dict) -> None:
    _yaml.dump(data, RADAR_FILE)


def validate(args) -> int:
    data = load_radar()
    entries = data.get("entries", [])
    errors = []
    names_seen = set()

    for i, entry in enumerate(entries):
        label = entry.get("name", f"entry[{i}]")

        if not entry.get("name"):
            errors.append(f"  [{i}] missing 'name'")
        elif entry["name"].lower() in names_seen:
            errors.append(f"  [{i}] duplicate name: {entry['name']}")
        else:
            names_seen.add(entry["name"].lower())

        if entry.get("quadrant") not in VALID_QUADRANTS:
            errors.append(f"  {label}: invalid quadrant '{entry.get('quadrant')}' (valid: {VALID_QUADRANTS})")

        if entry.get("ring") not in VALID_RINGS:
            errors.append(f"  {label}: invalid ring '{entry.get('ring')}' (valid: {VALID_RINGS})")

        if not entry.get("description"):
            errors.append(f"  {label}: missing 'description'")

    if errors:
        print(f"FAIL — {len(errors)} error(s) in {len(entries)} entries:\n")
        print("\n".join(errors))
        return 1

    print(f"OK — {len(entries)} entries, all valid.")
    return 0


def list_entries(args) -> int:
    data = load_radar()
    entries = data.get("entries", [])

    for q in sorted(VALID_QUADRANTS):
        q_entries = [e for e in entries if e["quadrant"] == q]
        if not q_entries:
            continue
        print(f"\n{'─' * 40}")
        print(f"  {q.upper()}")
        print(f"{'─' * 40}")
        for ring in ["adopt", "trial", "assess", "hold"]:
            ring_entries = [e for e in q_entries if e["ring"] == ring]
            if ring_entries:
                print(f"  [{ring}]")
                for e in ring_entries:
                    print(f"    • {e['name']}")
    print()
    return 0


def add_entry(args) -> int:
    if args.quadrant not in VALID_QUADRANTS:
        print(f"Error: invalid quadrant '{args.quadrant}'. Valid: {VALID_QUADRANTS}")
        return 1
    if args.ring not in VALID_RINGS:
        print(f"Error: invalid ring '{args.ring}'. Valid: {VALID_RINGS}")
        return 1

    data = load_radar()
    entries = data.get("entries", [])

    existing_names = {e["name"].lower() for e in entries}
    if args.name.lower() in existing_names:
        print(f"Error: entry '{args.name}' already exists.")
        return 1

    entries.append({
        "name": args.name,
        "quadrant": args.quadrant,
        "ring": args.ring,
        "description": args.description,
    })
    data["entries"] = entries
    data["last_updated"] = date.today().isoformat()
    save_radar(data)
    print(f"Added '{args.name}' to {args.quadrant}/{args.ring}.")
    return 0


def move_entry(args) -> int:
    if args.ring not in VALID_RINGS:
        print(f"Error: invalid ring '{args.ring}'. Valid: {VALID_RINGS}")
        return 1

    data = load_radar()
    for entry in data.get("entries", []):
        if entry["name"].lower() == args.name.lower():
            old_ring = entry["ring"]
            entry["ring"] = args.ring
            data["last_updated"] = date.today().isoformat()
            save_radar(data)
            print(f"Moved '{entry['name']}' from {old_ring} → {args.ring}.")
            return 0

    print(f"Error: entry '{args.name}' not found.")
    return 1


def remove_entry(args) -> int:
    data = load_radar()
    entries = data.get("entries", [])

    for i, entry in enumerate(entries):
        if entry["name"].lower() == args.name.lower():
            name = entry["name"]
            del entries[i]
            data["last_updated"] = date.today().isoformat()
            save_radar(data)
            print(f"Removed '{name}'.")
            return 0

    print(f"Error: entry '{args.name}' not found.")
    return 1


def main():
    parser = argparse.ArgumentParser(description="Tech Radar CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("validate", help="Validate radar.yaml")
    sub.add_parser("list", help="List all entries")

    add_p = sub.add_parser("add", help="Add a new entry")
    add_p.add_argument("name")
    add_p.add_argument("--quadrant", "-q", required=True)
    add_p.add_argument("--ring", "-r", required=True)
    add_p.add_argument("--description", "-d", required=True)

    move_p = sub.add_parser("move", help="Move an entry to a different ring")
    move_p.add_argument("name")
    move_p.add_argument("--ring", "-r", required=True)

    remove_p = sub.add_parser("remove", help="Remove an entry")
    remove_p.add_argument("name")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1

    cmd = {"validate": validate, "list": list_entries, "add": add_entry, "move": move_entry, "remove": remove_entry}
    return cmd[args.command](args)


if __name__ == "__main__":
    sys.exit(main())

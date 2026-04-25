import argparse
import sys
import os
from uuid import uuid4
from dotenv import load_dotenv

from gcm.schema import GeometricNode, Link, RelationshipType
from gcm.registry import GeometricRegistry
from gcm.orchestrator import TimelineOrchestrator, DiscontinuityError
from gcm.observer import Observer


def display_voids(registry: GeometricRegistry):
    voids = registry.check_voids()
    if voids:
        print("\n[!] GEOMETRIC VOID DETECTED: BRIDGE REQUIRED")
        for void in voids:
            print(f"    Node {void.uid} has no outgoing edges.")
        print("-" * 50)


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Geometric Context Graph Middleware CLI")
    parser.add_argument("--add-dot", help="Add a new dot with the specified content", type=str)
    parser.add_argument("--simulate-llm", help="Simulate an LLM response", type=str)
    args = parser.parse_args()

    data_path = os.getenv("GCM_DATA_PATH", "geometric_registry.json")
    registry = GeometricRegistry(filepath=data_path)
    orchestrator = TimelineOrchestrator(registry)
    observer = Observer()

    if args.add_dot:
        node = GeometricNode(content=args.add_dot)
        registry.add_node(node)
        print(f"Added dot: {node.uid}")
        display_voids(registry)
        return

    # Current State coordinates (x, y, z)
    current_coords = [50.0, 50.0, 50.0]

    if args.simulate_llm:
        print("\n--- Intercepting Context ---")
        try:
            reference_dots = orchestrator.intercept(tuple(current_coords))
        except DiscontinuityError as e:
            print(str(e))
            return

        harness = orchestrator.construct_harness(reference_dots)
        print("Harness constructed:")
        print(harness)
        print("\n--- LLM Response ---")
        print(args.simulate_llm)

        print("\n--- Observer Evaluation ---")
        passed, missing_dots = observer.evaluate(args.simulate_llm, reference_dots)
        if passed:
            print("Evaluation Passed: The LLM referenced all required Dots.")
        else:
            print(observer.trigger_regrounding_maneuver(missing_dots))
            # Human in the loop prompt
            bridge_content = input("\nEnter Bridge Dot Content: ")
            if bridge_content:
                bridge_node = GeometricNode(
                    content=bridge_content,
                    links=[Link(target_uid=missing_dots[0].uid, relationship_type=RelationshipType.EXPANSION)]
                )
                registry.add_node(bridge_node)
                print(f"Added Bridge Dot: {bridge_node.uid}")
                registry.link_nodes(missing_dots[0].uid, bridge_node.uid, RelationshipType.EXPANSION)

        display_voids(registry)
        return

    # Default interactive mode
    print("GCM Interactive Shell")
    print("Commands: add <content> [x y z], list, simulate <response>, shift <axis> <value>, link <source> <target> [rel_type], exit")
    while True:
        try:
            cmd = input(f"gcm {tuple(current_coords)}> ").strip().split(" ", 1)
            if not cmd[0]:
                continue

            action = cmd[0].lower()

            if action == "exit":
                break
            elif action == "shift":
                if len(cmd) > 1:
                    # Example: "shift technical" -> increase y target by 20
                    # or "shift x 80"
                    args = cmd[1].split()
                    if args[0] == "technical":
                        current_coords[1] = min(100.0, current_coords[1] + 20.0)
                        print(f"Shifted Y (Resolution) to {current_coords[1]}")
                    elif len(args) == 2:
                        axis, val = args[0].lower(), float(args[1])
                        if axis == 'x': current_coords[0] = val
                        elif axis == 'y': current_coords[1] = val
                        elif axis == 'z': current_coords[2] = val
                        print(f"Shifted {axis.upper()} to {val}")
                else:
                    print("Usage: shift technical OR shift <x|y|z> <value>")
            elif action == "add":
                if len(cmd) > 1:
                    parts = cmd[1].rsplit(" ", 3)
                    if len(parts) == 4 and all(p.replace('.','',1).isdigit() for p in parts[1:]):
                        content = parts[0]
                        x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                        node = GeometricNode(content=content, x=x, y=y, z=z)
                    else:
                        content = cmd[1]
                        node = GeometricNode(content=content, x=current_coords[0], y=current_coords[1], z=current_coords[2])
                else:
                    node = GeometricNode(content="Empty dot", x=current_coords[0], y=current_coords[1], z=current_coords[2])

                registry.add_node(node)
                print(f"Added dot: {node.uid} at ({node.x}, {node.y}, {node.z})")
                display_voids(registry)
            elif action == "list":
                registry.decay_weights()
                nodes = registry.get_all_nodes()
                for node in nodes:
                    weight_val = int(node.weight)
                    heat_bar = f"[{'#' * weight_val}{'-' * (10 - weight_val)}]"
                    print(f"Dot: {node.uid} | Heat: {heat_bar} | Pos: ({node.x}, {node.y}, {node.z}) | Content: {node.content} | Links: {len(node.links)}")
                display_voids(registry)
            elif action == "simulate":
                response = cmd[1] if len(cmd) > 1 else ""
                if "shift to technical" in response.lower():
                    current_coords[1] = min(100.0, current_coords[1] + 20.0)
                    print(f"Programmatic Bend applied: Shifted Y to {current_coords[1]}")

                try:
                    reference_dots = orchestrator.intercept(tuple(current_coords))
                except DiscontinuityError as e:
                    print(str(e))
                    bridge_content = input("\nEnter Bridge Dot Content: ")
                    if bridge_content:
                        # Add at the missing coordinate region to bridge the gap
                        bridge_node = GeometricNode(
                            content=bridge_content,
                            x=current_coords[0], y=current_coords[1], z=current_coords[2]
                        )
                        registry.add_node(bridge_node)
                        print(f"Added Bridge Dot: {bridge_node.uid} at {tuple(current_coords)}")
                    continue

                harness = orchestrator.construct_harness(reference_dots)
                print("Harness:", harness)
                passed, missing_dots = observer.evaluate(response, reference_dots)
                if passed:
                    print("Observer: PASSED")
                else:
                    print(observer.trigger_regrounding_maneuver(missing_dots))
                    bridge_content = input("\nEnter Bridge Dot Content: ")
                    if bridge_content:
                        bridge_node = GeometricNode(
                            content=bridge_content,
                            links=[Link(target_uid=missing_dots[0].uid, relationship_type=RelationshipType.EXPANSION)],
                            x=current_coords[0], y=current_coords[1], z=current_coords[2]
                        )
                        registry.add_node(bridge_node)
                        print(f"Added Bridge Dot: {bridge_node.uid}")
                        registry.link_nodes(missing_dots[0].uid, bridge_node.uid, RelationshipType.EXPANSION)
                display_voids(registry)
            elif action == "link":
                parts = cmd[1].split() if len(cmd) > 1 else []
                if len(parts) >= 2:
                    source_prefix = parts[0]
                    target_prefix = parts[1]
                    rel_type_str = parts[2] if len(parts) > 2 else "EXPANSION"
                    try:
                        rel_type = RelationshipType(rel_type_str.capitalize())
                    except ValueError:
                        rel_type = RelationshipType.EXPANSION

                    source_node = None
                    target_node = None
                    for node in registry.get_all_nodes():
                        uid_str = str(node.uid)
                        if uid_str.startswith(source_prefix):
                            source_node = node
                        if uid_str.startswith(target_prefix):
                            target_node = node

                    if not source_node:
                        print(f"Could not find source node matching {source_prefix}")
                    elif not target_node:
                        print(f"Could not find target node matching {target_prefix}")
                    else:
                        registry.link_nodes(source_node.uid, target_node.uid, rel_type)
                        print(f"Weld Successful: {source_node.uid} -> {target_node.uid}")
                        display_voids(registry)
                else:
                    print("Usage: link <source_prefix> <target_prefix> [relationship]")
            else:
                print("Unknown command.")
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()

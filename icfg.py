import argparse
import os
import sys
import glob
from slither.slither import Slither


def find_sol_files(directory):
    # recursively find .sol files
    pattern = os.path.join(directory, "**", "*.sol")
    return glob.glob(pattern, recursive=True)


def has_project_indicators(directory):
    # Common files that indicate a Solidity project (Hardhat/Foundry/Truffle/Brownie)
    indicators = [
        "hardhat.config.js",
        "hardhat.config.ts",
        "foundry.toml",
        "remappings.txt",
        "truffle-config.js",
        "brownie-config.yaml",
        "package.json",
    ]
    for name in indicators:
        if os.path.exists(os.path.join(directory, name)):
            return True
    return False


def create_slither(target):
    # If target is a directory, try to be helpful: if it looks like a project, pass as-is;
    # otherwise, find .sol files and pass the list to Slither.
    if os.path.isdir(target):
        if has_project_indicators(target):
            return Slither(target)
        sol_files = find_sol_files(target)
        if not sol_files:
            print(f"No Solidity files found under '{target}'.\n"
                  "Either pass a specific .sol file or initialize a supported project (Hardhat/Foundry/Truffle/Brownie).")
            sys.exit(1)
        if len(sol_files) == 1:
            # single file — pass its path to Slither
            return Slither(sol_files[0])
        # multiple files found but no project indicators — be conservative and ask user to pick
        print(f"Multiple Solidity files found under '{target}':")
        for f in sol_files[:20]:
            print("  ", f)
        if len(sol_files) > 20:
            print(f"  ... and {len(sol_files)-20} more files")
        print("\nEither pass a single .sol file with --target, or run this inside a recognized project (Hardhat/Foundry/Truffle/Brownie).")
        sys.exit(1)
    else:
        # target is a file (or path to a single .sol). Let Slither handle validation.
        return Slither(target)


def main():
    parser = argparse.ArgumentParser(description="Build ICFG using Slither")
    parser.add_argument("--target", "-t", default=".", help="Path to a .sol file or project directory (default: .)")
    parser.add_argument("--export-json", help="Path to write ICFG JSON output (optional)")
    parser.add_argument("--export-dot", help="Path to write ICFG DOT output (optional)")
    args = parser.parse_args()

    sl = create_slither(args.target)

    all_functions = []
    for contract in sl.contracts_derived:      # derived contracts, ignore interfaces
        for f in contract.functions:
            if not f.is_implemented:           # skip abstract
                continue
            all_functions.append(f)

    from collections import defaultdict

    icfg_succ = defaultdict(set)  # Node -> set[Node]

    for f in all_functions:
        for n in f.nodes:
            print(f"node: {n}")  # Debug print to trace nodes
            for son in n.sons:
                icfg_succ[n].add(son)  # intra-procedural edge


    from slither.slithir.operations import InternalCall, HighLevelCall

    for f in all_functions:
        for n in f.nodes:
            for ir in n.all_slithir_operations():  # IR ops in this node
                # Internal (same-contract / inheritance) calls
                if isinstance(ir, InternalCall):
                    callee = ir.function
                    # Guard access: callee may be a StateVariable or other object
                    entry = getattr(callee, "entry_point", None)
                    if entry:
                        icfg_succ[n].add(entry)

                # High-level calls where Slither could resolve the target function
                elif isinstance(ir, HighLevelCall) and ir.function is not None:
                    callee = ir.function
                    entry = getattr(callee, "entry_point", None)
                    if entry:
                        icfg_succ[n].add(entry)


    # Print a small summary so the user knows we succeeded
    print(f"Discovered {len(all_functions)} implemented functions across {len(sl.contracts_derived)} derived contracts.")
    total_nodes = sum(len(f.nodes) for f in all_functions)
    total_edges = sum(len(s) for s in icfg_succ.values())
    print(f"ICFG: {total_nodes} nodes, {total_edges} intra-procedural edges.")

    # Export JSON / DOT if requested
    if args.export_json or args.export_dot:
        # Build node id mapping and serializable node info
        node_to_id = {}
        nodes = []
        nid = 0
        for f in all_functions:
            func_name = getattr(f, "full_name", None) or getattr(f, "canonical_name", None) or getattr(f, "name", None)
            contract_name = getattr(getattr(f, "contract", None), "name", None)
            for n in f.nodes:
                if n in node_to_id:
                    continue
                node_to_id[n] = nid
                # Use a concise label: function name + node index if available
                # `str(n)` often contains a readable representation; include it for diagnostics
                label = f"{contract_name or '?'}::{func_name or '?'}"
                nodes.append({
                    "id": nid,
                    "label": label,
                    "repr": str(n),
                })
                nid += 1

        edges = []
        for src, dsts in icfg_succ.items():
            if src not in node_to_id:
                # skip nodes outside the mapping (unlikely)
                continue
            for dst in dsts:
                if dst not in node_to_id:
                    continue
                edges.append({"src": node_to_id[src], "dst": node_to_id[dst]})

        # Write JSON
        if args.export_json:
            import json

            out = {"nodes": nodes, "edges": edges}
            with open(args.export_json, "w", encoding="utf-8") as fh:
                json.dump(out, fh, indent=2, ensure_ascii=False)
            print(f"Wrote ICFG JSON to {args.export_json}")

        # Write DOT
        if args.export_dot:
            def escape(s):
                return s.replace('"', '\\"')

            with open(args.export_dot, "w", encoding="utf-8") as fh:
                fh.write("digraph ICFG {\n")
                fh.write("  node [shape=box,fontname=\"DejaVu Sans\"];\n")
                for n in nodes:
                    label = escape(n["label"]) + "\\n" + escape(n["repr"])[:80]
                    fh.write(f"  n{n['id']} [label=\"{label}\"];\n")
                for e in edges:
                    fh.write(f"  n{e['src']} -> n{e['dst']};\n")
                fh.write("}\n")
            print(f"Wrote ICFG DOT to {args.export_dot}")


if __name__ == "__main__":
    main()

import argparse
import os
import sys
import glob
import json
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


def extract_function_info(func):
    """Extract detailed information about a function."""
    info = {
        "name": getattr(func, "name", None),
        "full_name": getattr(func, "full_name", None),
        "canonical_name": getattr(func, "canonical_name", None),
        "contract": getattr(getattr(func, "contract", None), "name", None) if hasattr(func, "contract") else None,
        "visibility": getattr(func, "visibility", None),
        "state_mutability": getattr(func, "state_mutability", None),
        "is_constructor": getattr(func, "is_constructor", False),
        "is_fallback": getattr(func, "is_fallback", False),
        "is_receive": getattr(func, "is_receive", False),
        "is_implemented": getattr(func, "is_implemented", False),
        "is_public": getattr(func, "is_public", False),
        "is_external": getattr(func, "is_external", False),
        "is_internal": getattr(func, "is_internal", False),
        "is_private": getattr(func, "is_private", False),
        "parameters": [],
        "return_values": [],
        "modifiers": [],
        "state_variables_read": [],
        "state_variables_written": [],
        "entry_point": None,
        "source_mapping": None,
    }
    
    # Extract parameters
    if hasattr(func, "parameters"):
        for param in func.parameters:
            param_info = {
                "name": getattr(param, "name", None),
                "type": str(getattr(param, "type", None)) if hasattr(param, "type") else None,
            }
            info["parameters"].append(param_info)
    
    # Extract return values
    if hasattr(func, "return_values"):
        for ret in func.return_values:
            ret_info = {
                "name": getattr(ret, "name", None),
                "type": str(getattr(ret, "type", None)) if hasattr(ret, "type") else None,
            }
            info["return_values"].append(ret_info)
    
    # Extract modifiers
    if hasattr(func, "modifiers"):
        for mod in func.modifiers:
            mod_info = {
                "name": getattr(mod, "name", None),
                "canonical_name": getattr(mod, "canonical_name", None),
            }
            info["modifiers"].append(mod_info)
    
    # Extract state variables read
    if hasattr(func, "state_variables_read"):
        for var in func.state_variables_read:
            var_info = {
                "name": getattr(var, "name", None),
                "type": str(getattr(var, "type", None)) if hasattr(var, "type") else None,
            }
            info["state_variables_read"].append(var_info)
    
    # Extract state variables written
    if hasattr(func, "state_variables_written"):
        for var in func.state_variables_written:
            var_info = {
                "name": getattr(var, "name", None),
                "type": str(getattr(var, "type", None)) if hasattr(var, "type") else None,
            }
            info["state_variables_written"].append(var_info)
    
    # Extract entry point
    if hasattr(func, "entry_point"):
        info["entry_point"] = str(func.entry_point) if func.entry_point else None
    
    # Extract source mapping
    if hasattr(func, "source_mapping"):
        sm = func.source_mapping
        if sm:
            info["source_mapping"] = {
                "filename": getattr(sm, "filename", None),
                "start": getattr(sm, "start", None),
                "length": getattr(sm, "length", None),
                "starting_line": getattr(sm, "starting_line", None),
                "ending_line": getattr(sm, "ending_line", None),
            }
    
    return info


def extract_node_info(node):
    """Extract detailed information about a node."""
    info = {
        "type": type(node).__name__,
        "string_representation": str(node),
        "expression": None,
        "source_mapping": None,
        "sons": [],
        "fathers": [],
        "ir_operations": [],
        "state_variables_read": [],
        "state_variables_written": [],
        "internal_calls": [],
        "high_level_calls": [],
        "low_level_calls": [],
    }
    
    # Extract expression
    if hasattr(node, "expression"):
        info["expression"] = str(node.expression) if node.expression else None
    
    # Extract source mapping
    if hasattr(node, "source_mapping"):
        sm = node.source_mapping
        if sm:
            info["source_mapping"] = {
                "filename": getattr(sm, "filename", None),
                "start": getattr(sm, "start", None),
                "length": getattr(sm, "length", None),
                "starting_line": getattr(sm, "starting_line", None),
                "ending_line": getattr(sm, "ending_line", None),
            }
    
    # Extract sons (successors)
    if hasattr(node, "sons"):
        info["sons"] = [str(son) for son in node.sons]
    
    # Extract fathers (predecessors)
    if hasattr(node, "fathers"):
        info["fathers"] = [str(father) for father in node.fathers]
    
    # Extract IR operations
    if hasattr(node, "all_slithir_operations"):
        for ir in node.all_slithir_operations():
            ir_info = {
                "type": type(ir).__name__,
                "string_representation": str(ir),
            }
            info["ir_operations"].append(ir_info)
    
    # Extract state variables read
    if hasattr(node, "state_variables_read"):
        for var in node.state_variables_read:
            var_info = {
                "name": getattr(var, "name", None),
                "type": str(getattr(var, "type", None)) if hasattr(var, "type") else None,
            }
            info["state_variables_read"].append(var_info)
    
    # Extract state variables written
    if hasattr(node, "state_variables_written"):
        for var in node.state_variables_written:
            var_info = {
                "name": getattr(var, "name", None),
                "type": str(getattr(var, "type", None)) if hasattr(var, "type") else None,
            }
            info["state_variables_written"].append(var_info)
    
    # Extract internal calls
    if hasattr(node, "internal_calls"):
        for call in node.internal_calls:
            call_info = {
                "name": getattr(call, "name", None),
                "full_name": getattr(call, "full_name", None),
            }
            info["internal_calls"].append(call_info)
    
    # Extract high-level calls
    if hasattr(node, "high_level_calls"):
        for call in node.high_level_calls:
            call_info = {
                "name": getattr(call, "name", None) if call else None,
                "full_name": getattr(call, "full_name", None) if call else None,
            }
            info["high_level_calls"].append(call_info)
    
    # Extract low-level calls
    if hasattr(node, "low_level_calls"):
        info["low_level_calls"] = [str(call) for call in node.low_level_calls]
    
    return info


def create_slither(target):
    # If target is a directory, try to be helpful: if it looks like a project, pass as-is;
    # otherwise, find .sol files and pass the list to Slither.
    if os.path.isdir(target):
        # Convert to absolute path so crytic_compile can find config files correctly
        target_abs = os.path.abspath(target)
        if has_project_indicators(target_abs):
            # crytic_compile looks for config files (like foundry.toml) in the current working directory
            # So we need to temporarily change to the target directory
            original_cwd = os.getcwd()
            try:
                os.chdir(target_abs)
                return Slither(target_abs)
            finally:
                os.chdir(original_cwd)
        sol_files = find_sol_files(target_abs)
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
        # target is a file (or path to a single .sol). Convert to absolute path.
        return Slither(os.path.abspath(target))


def main():
    parser = argparse.ArgumentParser(description="Build ICFG using Slither")
    parser.add_argument("--target", "-t", default=".", help="Path to a .sol file or project directory (default: .)")
    parser.add_argument("--export-json", nargs="?", const="icfg.json", help="Path to write ICFG JSON output (default: out/icfg.json)")
    parser.add_argument("--export-dot", nargs="?", const="icfg.dot", help="Path to write ICFG DOT output (default: out/icfg.dot)")
    args = parser.parse_args()
    
    # Ensure out/ directory exists
    os.makedirs("out", exist_ok=True)
    
    # Prepend out/ to export paths if they're relative paths (not absolute)
    if args.export_json and not os.path.isabs(args.export_json):
        args.export_json = os.path.join("out", args.export_json)
    if args.export_dot and not os.path.isabs(args.export_dot):
        args.export_dot = os.path.join("out", args.export_dot)

    sl = create_slither(args.target)

    all_functions = []
    for contract in sl.contracts_derived:      # derived contracts, ignore interfaces
        for f in contract.functions:
            if not f.is_implemented:           # skip abstract
                continue
            all_functions.append(f)

    # Extract and display function information
    print("\n" + "="*80)
    print("FUNCTION INFORMATION")
    print("="*80)
    functions_info = []
    for f in all_functions:
        func_info = extract_function_info(f)
        functions_info.append(func_info)
        print(f"\nFunction: {func_info['full_name'] or func_info['name']}")
        print(f"  Contract: {func_info['contract']}")
        print(f"  Visibility: {func_info['visibility']}")
        print(f"  State Mutability: {func_info['state_mutability']}")
        print(f"  Is Constructor: {func_info['is_constructor']}")
        print(f"  Parameters: {len(func_info['parameters'])}")
        for param in func_info['parameters']:
            print(f"    - {param['name']}: {param['type']}")
        print(f"  Return Values: {len(func_info['return_values'])}")
        for ret in func_info['return_values']:
            print(f"    - {ret['name']}: {ret['type']}")
        print(f"  Modifiers: {len(func_info['modifiers'])}")
        for mod in func_info['modifiers']:
            print(f"    - {mod['name']}")
        print(f"  State Variables Read: {len(func_info['state_variables_read'])}")
        for var in func_info['state_variables_read']:
            print(f"    - {var['name']}: {var['type']}")
        print(f"  State Variables Written: {len(func_info['state_variables_written'])}")
        for var in func_info['state_variables_written']:
            print(f"    - {var['name']}: {var['type']}")
        if func_info['source_mapping']:
            sm = func_info['source_mapping']
            print(f"  Source: {sm['filename']} (lines {sm['starting_line']}-{sm['ending_line']})")
        print(f"  Number of Nodes: {len(f.nodes)}")

    from collections import defaultdict

    icfg_succ = defaultdict(set)  # Node -> set[Node]

    # Extract and display node information
    print("\n" + "="*80)
    print("NODE INFORMATION")
    print("="*80)
    nodes_info = []
    node_obj_to_info = {}  # Map node objects to their info dicts for later ID assignment
    for f in all_functions:
        func_name = getattr(f, "full_name", None) or getattr(f, "name", None)
        contract_name = getattr(getattr(f, "contract", None), "name", None)
        print(f"\n--- Function: {contract_name}::{func_name} ---")
        for idx, n in enumerate(f.nodes):
            node_info = extract_node_info(n)
            node_info["function"] = func_name
            node_info["contract"] = contract_name
            node_info["node_index"] = idx
            nodes_info.append(node_info)
            node_obj_to_info[n] = node_info
            
            print(f"\n  Node {idx}: {node_info['type']}")
            print(f"    Expression: {node_info['expression']}")
            print(f"    IR Operations: {len(node_info['ir_operations'])}")
            for ir in node_info['ir_operations']:
                print(f"      - {ir['type']}: {ir['string_representation'][:80]}")
            print(f"    State Variables Read: {len(node_info['state_variables_read'])}")
            for var in node_info['state_variables_read']:
                print(f"      - {var['name']}")
            print(f"    State Variables Written: {len(node_info['state_variables_written'])}")
            for var in node_info['state_variables_written']:
                print(f"      - {var['name']}")
            print(f"    Internal Calls: {len(node_info['internal_calls'])}")
            for call in node_info['internal_calls']:
                print(f"      - {call['name']}")
            print(f"    High-Level Calls: {len(node_info['high_level_calls'])}")
            for call in node_info['high_level_calls']:
                print(f"      - {call['name']}")
            print(f"    Low-Level Calls: {len(node_info['low_level_calls'])}")
            for call in node_info['low_level_calls']:
                print(f"      - {call}")
            print(f"    Successors (sons): {len(node_info['sons'])}")
            print(f"    Predecessors (fathers): {len(node_info['fathers'])}")
            if node_info['source_mapping']:
                sm = node_info['source_mapping']
                print(f"    Source: {sm['filename']} (lines {sm['starting_line']}-{sm['ending_line']})")
            
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
        # First pass: assign IDs to all nodes
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
        
        # Second pass: add node IDs to nodes_info for linking
        for n, node_id in node_to_id.items():
            if n in node_obj_to_info:
                node_obj_to_info[n]["icfg_id"] = node_id

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
            # Include detailed function and node information in JSON export
            out = {
                "functions": functions_info,
                "nodes": nodes_info,
                "icfg": {
                    "nodes": nodes,
                    "edges": edges
                }
            }
            with open(args.export_json, "w", encoding="utf-8") as fh:
                json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
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

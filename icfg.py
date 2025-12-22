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
    parser = argparse.ArgumentParser(description="Build function-level call graph using Slither")
    parser.add_argument("--target", "-t", default=".", help="Path to a .sol file or project directory (default: .)")
    parser.add_argument("--export-json", nargs="?", const="icfg.json", help="Path to write call graph JSON output (default: out/icfg.json)")
    parser.add_argument("--export-dot", nargs="?", const="icfg.dot", help="Path to write call graph DOT output (default: out/icfg.dot)")
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
    from slither.slithir.operations import InternalCall, HighLevelCall
    
    # Try to import LibraryCall and LowLevelCall if they exist
    try:
        from slither.slithir.operations import LibraryCall, LowLevelCall
    except ImportError:
        # If they don't exist, we'll handle library calls via InternalCall
        LibraryCall = None
        LowLevelCall = None

    # Build function-level call graph with call sites
    # Map: caller_function -> list of (call_order, call_type, callee_func, call_site_info)
    call_sites = defaultdict(list)  # Function -> list of call site info
    
    # Also maintain a simpler structure for backward compatibility
    call_graph = defaultdict(lambda: defaultdict(set))  # Function -> Function -> set[call_type]
    
    # Track low-level calls separately (they don't have a specific callee function)
    low_level_calls_by_function = defaultdict(list)  # Function -> list of low-level call descriptions

    # Create a mapping from function objects to their identifiers
    func_to_id = {}
    func_id_to_info = {}
    func_id = 0
    tracked_functions = set()  # Track all functions we've seen (including called ones)
    
    # First, add all implemented functions
    for f in all_functions:
        func_name = getattr(f, "full_name", None) or getattr(f, "canonical_name", None) or getattr(f, "name", None)
        contract_name = getattr(getattr(f, "contract", None), "name", None)
        func_key = f"{contract_name}::{func_name}" if contract_name else func_name
        func_to_id[f] = func_id
        func_id_to_info[func_id] = {
            "id": func_id,
            "name": func_name,
            "full_name": getattr(f, "full_name", None),
            "canonical_name": getattr(f, "canonical_name", None),
            "contract": contract_name,
        }
        tracked_functions.add(f)
        func_id += 1
    
    # Helper to add a function to tracking if not already there
    def add_function_to_tracking(func):
        """Add a function to tracking dictionaries if not already present."""
        nonlocal func_id
        if func in tracked_functions:
            return func_to_id[func]
        tracked_functions.add(func)
        func_name = getattr(func, "full_name", None) or getattr(func, "canonical_name", None) or getattr(func, "name", None)
        contract_name = getattr(getattr(func, "contract", None), "name", None)
        func_to_id[func] = func_id
        func_id_to_info[func_id] = {
            "id": func_id,
            "name": func_name,
            "full_name": getattr(func, "full_name", None),
            "canonical_name": getattr(func, "canonical_name", None),
            "contract": contract_name,
        }
        current_id = func_id
        func_id += 1
        return current_id

    # Helper function to find function implementation
    def find_function_implementation(func):
        """Try to find the actual implementation of a function, even if it's from an interface."""
        if not func:
            return None
        
        # If function is already implemented, return it
        if hasattr(func, "is_implemented") and func.is_implemented:
            return func
        
        # Try to find implementation in derived contracts
        if hasattr(func, "contract") and func.contract:
            # Check if there's an implementation in derived contracts
            for contract in sl.contracts_derived:
                for f in contract.functions:
                    if (f.name == func.name and 
                        f.is_implemented):
                        # Try to match signatures if available
                        if (hasattr(f, "signature") and hasattr(func, "signature") and
                            f.signature == func.signature):
                            return f
                        # If signatures don't match or aren't available, still return if names match
                        # (this handles cases where signature comparison fails)
                        elif not (hasattr(f, "signature") and hasattr(func, "signature")):
                            return f
        
        # If no implementation found, return the function anyway (might be interface)
        # We'll still track it in the call graph
        return func
    
    # Helper to extract source mapping info
    def extract_source_mapping(obj):
        """Extract source mapping information from an object."""
        if hasattr(obj, "source_mapping") and obj.source_mapping:
            sm = obj.source_mapping
            
            # Try to get line numbers - Slither Source object might use different attributes
            starting_line = None
            ending_line = None
            
            # Try starting_line/ending_line first
            if hasattr(sm, "starting_line"):
                starting_line = getattr(sm, "starting_line", None)
            if hasattr(sm, "ending_line"):
                ending_line = getattr(sm, "ending_line", None)
            
            # If not found, try lines property
            if starting_line is None and hasattr(sm, "lines"):
                lines = getattr(sm, "lines", None)
                if lines:
                    if isinstance(lines, (list, tuple)) and len(lines) > 0:
                        starting_line = lines[0]
                        if len(lines) > 1:
                            ending_line = lines[-1]
                        else:
                            ending_line = starting_line
                    else:
                        starting_line = lines
                        ending_line = lines
            
            return {
                "filename": getattr(sm, "filename", None),
                "start": getattr(sm, "start", None),
                "length": getattr(sm, "length", None),
                "starting_line": starting_line,
                "ending_line": ending_line,
            }
        return None
    
    # Helper to get call site expression
    def get_call_site_expression(node, ir):
        """Get a readable representation of the call site."""
        # Try to get the node expression
        if hasattr(node, "expression") and node.expression:
            return str(node.expression)
        # Fall back to IR representation
        if hasattr(ir, "__str__"):
            return str(ir)
        return None

    # Traverse all functions and collect calls with order and call sites
    for caller_func in all_functions:
        call_order = 0  # Track call order within this function
        
        # Sort nodes by their source line to maintain execution order
        def get_node_line(n):
            """Safely get the starting line number from a node's source mapping."""
            if hasattr(n, "source_mapping") and n.source_mapping:
                sm = n.source_mapping
                # Try different ways to get line number
                # Try starting_line first
                if hasattr(sm, "starting_line"):
                    line = getattr(sm, "starting_line", None)
                    if line is not None:
                        return line
                # Try lines property
                if hasattr(sm, "lines"):
                    lines = getattr(sm, "lines", None)
                    if lines:
                        if isinstance(lines, (list, tuple)) and len(lines) > 0:
                            return lines[0]
                        else:
                            return lines
                # Fall back to start position (less accurate but works for sorting)
                if hasattr(sm, "start"):
                    return getattr(sm, "start", 999999)
            return 999999
        
        nodes_sorted = sorted(caller_func.nodes, key=get_node_line)
        
        for node in nodes_sorted:
            # Check IR operations for calls
            for ir in node.all_slithir_operations():
                call_type = None
                callee_func = None
                
                # Internal calls (same contract, inherited, or library)
                if isinstance(ir, InternalCall):
                    callee_func = ir.function
                    if callee_func and hasattr(callee_func, "contract"):
                        callee_contract = callee_func.contract
                        # Check if it's a library call
                        if callee_contract and hasattr(callee_contract, "is_library") and callee_contract.is_library:
                            call_type = "library"
                        else:
                            call_type = "internal"
                
                # High-level calls (external contract calls)
                elif isinstance(ir, HighLevelCall):
                    if ir.function is not None:
                        call_type = "high_level"
                        callee_func = ir.function
                
                # Library calls (if LibraryCall class exists)
                elif LibraryCall and isinstance(ir, LibraryCall):
                    call_type = "library"
                    callee_func = ir.function
                
                # Low-level calls (call, delegatecall, etc.)
                elif LowLevelCall and isinstance(ir, LowLevelCall):
                    # Low-level calls don't have a direct function target
                    # Store them separately with call site info
                    call_order += 1
                    source_mapping = extract_source_mapping(ir) or extract_source_mapping(node)
                    call_site_expr = get_call_site_expression(node, ir)
                    low_level_calls_by_function[caller_func].append({
                        "order": call_order,
                        "call_site": call_site_expr,
                        "source_mapping": source_mapping,
                        "description": str(ir)
                    })
                    continue
                
                # If we found a call with a resolvable callee function
                if call_type and callee_func:
                    # Try to find the actual implementation
                    impl_func = find_function_implementation(callee_func)
                    if impl_func and hasattr(impl_func, "name"):
                        # Add to tracking if not already there
                        add_function_to_tracking(impl_func)
                        
                        # Extract call site information
                        call_order += 1
                        source_mapping = extract_source_mapping(ir) or extract_source_mapping(node)
                        call_site_expr = get_call_site_expression(node, ir)
                        
                        # Store call site with order and metadata
                        call_sites[caller_func].append({
                            "order": call_order,
                            "call_type": call_type,
                            "callee_func": impl_func,
                            "call_site": call_site_expr,
                            "source_mapping": source_mapping,
                        })
                        
                        # Also maintain simple structure for backward compatibility
                        call_graph[caller_func][impl_func].add(call_type)
            
            # Also check node-level call information as fallback
            # This catches calls that might not be in IR operations
            if hasattr(node, "high_level_calls") and node.high_level_calls:
                for call_func in node.high_level_calls:
                    if call_func:  # Skip None entries
                        impl_func = find_function_implementation(call_func)
                        if impl_func and hasattr(impl_func, "name"):
                            # Check if we already tracked this call from IR
                            already_tracked = any(
                                cs["callee_func"] == impl_func and cs["call_type"] == "high_level"
                                for cs in call_sites[caller_func]
                            )
                            
                            if not already_tracked:
                                # Add to tracking if not already there
                                add_function_to_tracking(impl_func)
                                
                                # Extract call site information
                                call_order += 1
                                source_mapping = extract_source_mapping(node)
                                call_site_expr = get_call_site_expression(node, None)
                                
                                # Store call site with order and metadata
                                call_sites[caller_func].append({
                                    "order": call_order,
                                    "call_type": "high_level",
                                    "callee_func": impl_func,
                                    "call_site": call_site_expr,
                                    "source_mapping": source_mapping,
                                })
                                
                                call_graph[caller_func][impl_func].add("high_level")
            
            if hasattr(node, "internal_calls") and node.internal_calls:
                for call_func in node.internal_calls:
                    if call_func:  # Skip None entries
                        impl_func = find_function_implementation(call_func)
                        if impl_func and hasattr(impl_func, "name"):
                            # Determine call type
                            if hasattr(impl_func, "contract") and impl_func.contract:
                                if hasattr(impl_func.contract, "is_library") and impl_func.contract.is_library:
                                    call_type = "library"
                                else:
                                    call_type = "internal"
                            else:
                                call_type = "internal"
                            
                            # Check if we already tracked this call from IR
                            already_tracked = any(
                                cs["callee_func"] == impl_func and cs["call_type"] == call_type
                                for cs in call_sites[caller_func]
                            )
                            
                            if not already_tracked:
                                # Add to tracking if not already there
                                add_function_to_tracking(impl_func)
                                
                                # Extract call site information
                                call_order += 1
                                source_mapping = extract_source_mapping(node)
                                call_site_expr = get_call_site_expression(node, None)
                                
                                # Store call site with order and metadata
                                call_sites[caller_func].append({
                                    "order": call_order,
                                    "call_type": call_type,
                                    "callee_func": impl_func,
                                    "call_site": call_site_expr,
                                    "source_mapping": source_mapping,
                                })
                                
                                call_graph[caller_func][impl_func].add(call_type)
            
            # Check for low-level calls (already handled above in IR loop)

    # Print call graph summary with call sites
    print("\n" + "="*80)
    print("CALL GRAPH (Function-to-Function with Call Sites)")
    print("="*80)
    
    total_calls = 0
    for caller_func in all_functions:
        caller_name = getattr(caller_func, "full_name", None) or getattr(caller_func, "name", None)
        caller_contract = getattr(getattr(caller_func, "contract", None), "name", None)
        caller_label = f"{caller_contract}::{caller_name}" if caller_contract else caller_name
        
        # Get call sites for this function, sorted by order
        function_call_sites = call_sites.get(caller_func, [])
        function_call_sites.sort(key=lambda x: x["order"])
        
        # Get low-level calls
        function_low_level = low_level_calls_by_function.get(caller_func, [])
        if isinstance(function_low_level, list) and function_low_level and isinstance(function_low_level[0], dict):
            function_low_level.sort(key=lambda x: x.get("order", 0))
        
        has_any_calls = bool(function_call_sites) or bool(function_low_level)
        
        if has_any_calls:
            print(f"\n{caller_label}:")
            
            # Print function-to-function calls with order and call sites
            for call_site in function_call_sites:
                callee_func = call_site["callee_func"]
                callee_name = getattr(callee_func, "full_name", None) or getattr(callee_func, "name", None)
                callee_contract = getattr(getattr(callee_func, "contract", None), "name", None)
                callee_label = f"{callee_contract}::{callee_name}" if callee_contract else callee_name
                
                # Format source location
                sm = call_site.get("source_mapping")
                if sm and sm.get("starting_line"):
                    if sm.get("ending_line") and sm["ending_line"] != sm["starting_line"]:
                        location = f"lines {sm['starting_line']}-{sm['ending_line']}"
                    else:
                        location = f"line {sm['starting_line']}"
                    if sm.get("filename"):
                        location = f"{sm['filename']}:{location}"
                else:
                    location = "unknown location"
                
                # Format call site expression
                call_site_expr = call_site.get("call_site", "unknown call site")
                if call_site_expr and len(call_site_expr) > 100:
                    call_site_expr = call_site_expr[:100] + "..."
                
                print(f"  {call_site['order']}. [{call_site['call_type']}] {location}")
                print(f"     Call site: {call_site_expr}")
                print(f"     -> {callee_label}")
                total_calls += 1
            
            # Print low-level calls
            for ll_call in function_low_level:
                if isinstance(ll_call, dict):
                    order = ll_call.get("order", "?")
                    sm = ll_call.get("source_mapping", {})
                    if sm and sm.get("starting_line"):
                        if sm.get("ending_line") and sm["ending_line"] != sm["starting_line"]:
                            location = f"lines {sm['starting_line']}-{sm['ending_line']}"
                        else:
                            location = f"line {sm['starting_line']}"
                        if sm.get("filename"):
                            location = f"{sm['filename']}:{location}"
                    else:
                        location = "unknown location"
                    call_site_expr = ll_call.get("call_site", ll_call.get("description", "unknown"))
                    if call_site_expr and len(call_site_expr) > 100:
                        call_site_expr = call_site_expr[:100] + "..."
                    print(f"  {order}. [low_level] {location}")
                    print(f"     Call site: {call_site_expr}")
                else:
                    # Legacy format
                    print(f"  -> [low_level] {ll_call}")

    # Print summary
    print(f"\n" + "="*80)
    print(f"SUMMARY")
    print("="*80)
    print(f"Discovered {len(all_functions)} implemented functions across {len(sl.contracts_derived)} derived contracts.")
    total_low_level = sum(len(calls) if isinstance(calls, list) else 1 for calls in low_level_calls_by_function.values())
    print(f"Call graph: {len(all_functions)} functions, {total_calls} function-to-function call edges, {total_low_level} low-level calls.")

    # Build node-level ICFG
    def get_node_label(node, func):
        """Get a descriptive label for a node showing its expression/operation."""
        # Use full_name which includes signature, fall back to name
        func_name = getattr(func, "full_name", None) or getattr(func, "name", None)
        contract_name = getattr(getattr(func, "contract", None), "name", None)
        func_label = f"{contract_name}.{func_name}" if contract_name else func_name
        
        # Check if this is the entry point
        if hasattr(func, "entry_point") and func.entry_point == node:
            return f"{func_label}\\nENTRY_POINT"
        
        # Get node expression
        expression = None
        if hasattr(node, "expression") and node.expression:
            expression = str(node.expression)
        
        # Get IR operations to determine node type
        ir_ops = []
        if hasattr(node, "all_slithir_operations"):
            ir_ops = list(node.all_slithir_operations())
        
        # Determine node type based on IR operations
        node_type = "EXPRESSION"
        if ir_ops:
            # Check for specific operation types
            op_types = [type(op).__name__ for op in ir_ops]
            op_strs = [str(op) for op in ir_ops]
            
            # Check for return
            if "Return" in op_types:
                node_type = "RETURN"
                # Try to get return value from IR
                for op in ir_ops:
                    if type(op).__name__ == "Return":
                        if hasattr(op, "values") and op.values:
                            ret_val = str(op.values[0])
                            if len(ret_val) > 60:
                                ret_val = ret_val[:60] + "..."
                            return f"{func_label}\\n{node_type} {ret_val}"
            # Check for assignments
            elif "Assignment" in op_types:
                # Check if it's a new variable declaration
                for op in ir_ops:
                    if type(op).__name__ == "Assignment":
                        if hasattr(op, "lvalue") and op.lvalue:
                            lvalue_str = str(op.lvalue)
                            if "NEW VARIABLE" in lvalue_str.upper() or "TMP_" in lvalue_str:
                                node_type = "NEW VARIABLE"
                                # Try to get the assignment expression
                                if expression:
                                    # Extract variable name and value
                                    parts = expression.split("=", 1)
                                    if len(parts) == 2:
                                        var_name = parts[0].strip()
                                        var_value = parts[1].strip()
                                        if len(var_value) > 100:
                                            var_value = var_value[:100] + "..."
                                        return f"{func_label}\\n{node_type} {var_name} = {var_value}"
                            else:
                                node_type = "ASSIGNMENT"
            # Check for calls
            elif any(t in op_types for t in ["InternalCall", "HighLevelCall", "LibraryCall", "LowLevelCall"]):
                node_type = "EXPRESSION"  # Call expression
        
        # Build label
        if expression:
            # Clean up expression - remove extra whitespace and newlines
            expression = " ".join(expression.split())
            # Truncate long expressions
            if len(expression) > 120:
                expression = expression[:120] + "..."
            return f"{func_label}\\n{node_type} {expression}"
        else:
            # Try to get info from IR operations if no expression
            if ir_ops:
                ir_repr = str(ir_ops[0])
                # Clean up IR representation
                ir_repr = " ".join(ir_repr.split())
                if len(ir_repr) > 80:
                    ir_repr = ir_repr[:80] + "..."
                return f"{func_label}\\n{node_type} {ir_repr}"
            return f"{func_label}\\n{node_type}"
    
    # Build ICFG: node-level graph with intra and inter-procedural edges
    # Only include nodes that are call sites or entry points
    # Import call types for ICFG building
    from slither.slithir.operations import InternalCall as ICFG_InternalCall, HighLevelCall as ICFG_HighLevelCall
    try:
        from slither.slithir.operations import LibraryCall as ICFG_LibraryCall, LowLevelCall as ICFG_LowLevelCall
    except ImportError:
        ICFG_LibraryCall = None
        ICFG_LowLevelCall = None
    
    icfg_nodes = []  # List of node info dicts
    icfg_edges = []  # List of edge dicts
    node_to_id = {}  # Map node object -> node ID
    node_id = 0
    node_to_function = {}  # Map node -> function
    
    # Map function -> entry point node
    function_entry_points = {}  # Function -> Node (entry point)
    
    # Helper to check if a node is a call site
    def is_call_site(node):
        """Check if a node contains any calls (HighLevelCall, InternalCall, LibraryCall, LowLevelCall)."""
        if hasattr(node, "all_slithir_operations"):
            for ir in node.all_slithir_operations():
                if isinstance(ir, (ICFG_InternalCall, ICFG_HighLevelCall)):
                    return True
                if ICFG_LibraryCall and isinstance(ir, ICFG_LibraryCall):
                    return True
                if ICFG_LowLevelCall and isinstance(ir, ICFG_LowLevelCall):
                    return True
        # Also check node-level call information
        if hasattr(node, "high_level_calls") and node.high_level_calls:
            return True
        if hasattr(node, "internal_calls") and node.internal_calls:
            return True
        if hasattr(node, "low_level_calls") and node.low_level_calls:
            return True
        return False
    
    # First, identify all call sites and entry points
    call_site_nodes = set()
    for f in all_functions:
        entry = getattr(f, "entry_point", None)
        if entry:
            function_entry_points[f] = entry
            call_site_nodes.add(entry)  # Always include entry points
        
        for n in f.nodes:
            if is_call_site(n):
                call_site_nodes.add(n)
    
    # Create nodes only for call sites and entry points
    for f in all_functions:
        for n in f.nodes:
            if n not in call_site_nodes:
                continue
            if n in node_to_id:
                continue
            node_to_id[n] = node_id
            node_to_function[n] = f
            label = get_node_label(n, f)
            entry = getattr(f, "entry_point", None)
            icfg_nodes.append({
                "id": node_id,
                "label": label,
                "function": getattr(f, "full_name", None) or getattr(f, "name", None),
                "contract": getattr(getattr(f, "contract", None), "name", None),
                "is_entry_point": (entry == n) if entry else False,
            })
            node_id += 1
    
    # Add intra-procedural edges (within functions)
    # Connect call sites within the same function by following CFG paths
    for f in all_functions:
        # Get all call sites in this function
        func_call_sites = [n for n in f.nodes if n in call_site_nodes and n in node_to_id]
        
        # For each call site, find the next call site(s) reachable from it
        for src_node in func_call_sites:
            if src_node not in node_to_id:
                continue
            src_id = node_to_id[src_node]
            
            # BFS to find next call sites reachable from this node
            visited = set()
            queue = [(src_node, src_node)]  # (current_node, original_source)
            
            while queue:
                current, original_src = queue.pop(0)
                if current in visited:
                    continue
                visited.add(current)
                
                # Check if we reached another call site (and it's not the same as source)
                if current in call_site_nodes and current != original_src:
                    if current in node_to_id:
                        dst_id = node_to_id[current]
                        # Check if edge already exists
                        if not any(e["src"] == src_id and e["dst"] == dst_id and e["type"] == "intra_procedural" 
                                  for e in icfg_edges):
                            icfg_edges.append({
                                "src": src_id,
                                "dst": dst_id,
                                "type": "intra_procedural"
                            })
                    # Don't continue from this node (we found a call site)
                    continue
                
                # Continue BFS to find next call sites
                for son in current.sons:
                    if son not in visited:
                        queue.append((son, original_src))
    
    # Add inter-procedural edges (calls)
    for f in all_functions:
        for n in f.nodes:
            if n not in node_to_id:
                continue
            src_id = node_to_id[n]
            
            for ir in n.all_slithir_operations():
                callee_func = None
                
                # Internal calls
                if isinstance(ir, ICFG_InternalCall):
                    callee_func = ir.function
                
                # High-level calls
                elif isinstance(ir, ICFG_HighLevelCall):
                    if ir.function is not None:
                        callee_func = ir.function
                
                # Library calls
                elif ICFG_LibraryCall and isinstance(ir, ICFG_LibraryCall):
                    callee_func = ir.function
                
                # If we found a call, add edge to callee entry point
                if callee_func:
                    impl_func = find_function_implementation(callee_func)
                    if impl_func and hasattr(impl_func, "entry_point"):
                        entry = impl_func.entry_point
                        if entry and entry in node_to_id:
                            dst_id = node_to_id[entry]
                            icfg_edges.append({
                                "src": src_id,
                                "dst": dst_id,
                                "type": "inter_procedural",
                                "call_type": "internal" if isinstance(ir, ICFG_InternalCall) else 
                                            "high_level" if isinstance(ir, ICFG_HighLevelCall) else
                                            "library" if (ICFG_LibraryCall and isinstance(ir, ICFG_LibraryCall)) else "unknown"
                            })
            
            # Also check node-level call information
            if hasattr(n, "high_level_calls") and n.high_level_calls:
                for call_func in n.high_level_calls:
                    if call_func:
                        impl_func = find_function_implementation(call_func)
                        if impl_func and hasattr(impl_func, "entry_point"):
                            entry = impl_func.entry_point
                            if entry and entry in node_to_id:
                                dst_id = node_to_id[entry]
                                # Check if edge already exists
                                if not any(e["src"] == src_id and e["dst"] == dst_id and e["type"] == "inter_procedural" 
                                          for e in icfg_edges):
                                    icfg_edges.append({
                                        "src": src_id,
                                        "dst": dst_id,
                                        "type": "inter_procedural",
                                        "call_type": "high_level"
                                    })
            
            if hasattr(n, "internal_calls") and n.internal_calls:
                for call_func in n.internal_calls:
                    if call_func:
                        impl_func = find_function_implementation(call_func)
                        if impl_func and hasattr(impl_func, "entry_point"):
                            entry = impl_func.entry_point
                            if entry and entry in node_to_id:
                                dst_id = node_to_id[entry]
                                # Check if edge already exists
                                if not any(e["src"] == src_id and e["dst"] == dst_id and e["type"] == "inter_procedural" 
                                          for e in icfg_edges):
                                    call_type = "library" if (hasattr(impl_func, "contract") and 
                                                             impl_func.contract and 
                                                             hasattr(impl_func.contract, "is_library") and
                                                             impl_func.contract.is_library) else "internal"
                                    icfg_edges.append({
                                        "src": src_id,
                                        "dst": dst_id,
                                        "type": "inter_procedural",
                                        "call_type": call_type
                                    })

    # Export JSON / DOT if requested
    if args.export_json or args.export_dot:
        # Build function nodes and edges for call graph
        function_nodes = []
        function_edges = []
        
        # Create nodes for all functions
        for func_id, func_info in func_id_to_info.items():
            func_name = func_info["name"]
            contract_name = func_info["contract"]
            label = f"{contract_name}::{func_name}" if contract_name else func_name
            function_nodes.append({
                "id": func_id,
                "label": label,
                "name": func_name,
                "full_name": func_info["full_name"],
                "canonical_name": func_info["canonical_name"],
                "contract": contract_name,
            })
        
        # Create edges from call sites (with order and call site info)
        call_sites_info = []
        for caller_func, sites in call_sites.items():
            if caller_func not in func_to_id:
                continue
            caller_id = func_to_id[caller_func]
            
            # Sort by order
            sites_sorted = sorted(sites, key=lambda x: x["order"])
            
            for call_site in sites_sorted:
                callee_func = call_site["callee_func"]
                if callee_func not in func_to_id:
                    continue
                callee_id = func_to_id[callee_func]
                
                # Create edge with call site information
                edge_info = {
                    "src": caller_id,
                    "dst": callee_id,
                    "order": call_site["order"],
                    "call_type": call_site["call_type"],
                    "call_site": call_site.get("call_site"),
                    "source_mapping": call_site.get("source_mapping"),
                }
                function_edges.append(edge_info)
                call_sites_info.append(edge_info)

        # Collect low-level calls info for export
        low_level_calls_info = []
        for caller_func, ll_calls in low_level_calls_by_function.items():
            if caller_func in func_to_id:
                caller_id = func_to_id[caller_func]
                for ll_call in ll_calls:
                    if isinstance(ll_call, dict):
                        low_level_calls_info.append({
                            "caller_id": caller_id,
                            "order": ll_call.get("order"),
                            "call_site": ll_call.get("call_site"),
                            "source_mapping": ll_call.get("source_mapping"),
                            "description": ll_call.get("description"),
                        })
                    else:
                        # Legacy format
                        low_level_calls_info.append({
                            "caller_id": caller_id,
                            "call_description": str(ll_call),
                        })

        # Write JSON
        if args.export_json:
            out = {
                "functions": functions_info,
                "call_graph": {
                    "nodes": function_nodes,
                    "edges": function_edges,
                    "call_sites": call_sites_info,
                    "low_level_calls": low_level_calls_info
                },
                "icfg": {
                    "nodes": icfg_nodes,
                    "edges": icfg_edges
                }
            }
            with open(args.export_json, "w", encoding="utf-8") as fh:
                json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
            print(f"Wrote call graph JSON to {args.export_json}")

        # Write DOT
        if args.export_dot:
            def escape(s):
                if s is None:
                    return ""
                return str(s).replace('"', '\\"').replace('\n', '\\n').replace('\r', '')

            with open(args.export_dot, "w", encoding="utf-8") as fh:
                # Write ICFG (node-level graph)
                fh.write("digraph ICFG {\n")
                fh.write("  node [shape=box,fontname=\"DejaVu Sans\"];\n")
                fh.write("  edge [fontname=\"DejaVu Sans\"];\n")
                
                # Write ICFG nodes
                for node in icfg_nodes:
                    label = escape(node["label"])
                    fh.write(f"  n{node['id']} [label=\"{label}\"];\n")
                
                # Write ICFG edges
                for edge in icfg_edges:
                    fh.write(f"  n{edge['src']} -> n{edge['dst']};\n")
                
                fh.write("}\n")
            print(f"Wrote ICFG DOT to {args.export_dot}")


if __name__ == "__main__":
    main()

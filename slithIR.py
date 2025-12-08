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
    parser = argparse.ArgumentParser(description="Display SlithIR operations using Slither")
    parser.add_argument("--target", "-t", default=".", help="Path to a .sol file or project directory (default: .)")
    args = parser.parse_args()
    
    # Init slither
    slither = create_slither(args.target)

    # Iterate over all the contracts
    for contract in slither.contracts:

        # Iterate over all the functions
        for function in contract.functions:

            # Dont explore inherited functions
            if function.contract_declarer == contract:

                print(f"Function: {function.name}")

                # Iterate over the nodes of the function
                for node in function.nodes:

                    # Print the Solidity expression of the nodes
                    # And the SlithIR operations
                    if node.expression:

                        print(f"\tSolidity expression: {node.expression}")
                        print("\tSlithIR:")
                        for ir in node.irs:
                            print(f"\t\t\t{ir}")


if __name__ == "__main__":
    main()
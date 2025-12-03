# Slither ICFG

A tool to build Interprocedural Control Flow Graph (ICFG) from Solidity smart contracts using [Slither](https://github.com/crytic/slither).

## Features

- Analyzes Solidity contracts and builds ICFG (Interprocedural Control Flow Graph)
- Supports single files, directories, and project structures (Hardhat, Foundry, Truffle, Brownie)
- Exports ICFG in JSON and DOT formats for visualization
- Tracks intra-procedural edges and inter-procedural call edges

## Prerequisites

- Python 3.8 or higher
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management

## Setup

### 1. Install Poetry (if not already installed)

```sh
curl -sSL https://install.python-poetry.org | python3 -
```

Or follow the [official Poetry installation guide](https://python-poetry.org/docs/#installation).

### 2. Initialize Virtual Environment and Install Dependencies

```sh
# Initialize virtual environment and install dependencies
poetry install

# Activate the virtual environment
eval $(poetry env activate)  # or `source .venv/bin/activate`
```

Alternatively, you can use Poetry's shell:

```sh
poetry shell
```

### 3. Verify Installation

The setup will automatically install `slither-analyzer` and its dependencies. You can verify by running:

```sh
poetry run slither --version
```

## Quick Guide

### Scanning Projects in `dataset/scan_queue`

The `icfg.py` script can analyze Solidity projects located in the `dataset/scan_queue` directory.

#### Basic Usage

```sh
# Scan a single Solidity file
poetry run python icfg.py --target dataset/scan_queue/example.sol

# Scan a project directory (e.g., Foundry project)
poetry run python icfg.py --target dataset/scan_queue/min_slippage_example
```

#### Export ICFG Output

```sh
# Export JSON/DOT formats
poetry run python icfg.py --target dataset/scan_queue/example.sol \
    --export-json out/icfg.json \
    --export-dot out/icfg.dot
```

#### Examples

**Example 1: Scan a single Solidity file**
```sh
poetry run python icfg.py --target dataset/scan_queue/example.sol
```

**Example 2: Scan a Foundry project**
```sh
poetry run python icfg.py --target dataset/scan_queue/min_slippage_example \
    --export-json out/min_slippage_icfg.json \
    --export-dot out/min_slippage_icfg.dot
```

**Example 3: Visualize the DOT file**
```sh
# After generating the DOT file, you can visualize it using Graphviz
dot -Tpng out/icfg.dot -o out/icfg.png
```

### Command-Line Options

- `--target`, `-t`: Path to a `.sol` file or project directory (default: `.`)
- `--export-json`: Path to write ICFG JSON output (optional)
- `--export-dot`: Path to write ICFG DOT output (optional)

### Supported Project Types

The tool automatically detects and supports:
- **Hardhat** projects (detects `hardhat.config.js` or `hardhat.config.ts`)
- **Foundry** projects (detects `foundry.toml` or `remappings.txt`)
- **Truffle** projects (detects `truffle-config.js`)
- **Brownie** projects (detects `brownie-config.yaml`)
- **Standalone** Solidity files (`.sol` files)

## Output Format

### JSON Output

The JSON output contains:
- `nodes`: Array of ICFG nodes with `id`, `label`, and `repr` fields
- `edges`: Array of edges with `src` and `dst` node IDs

### DOT Output

The DOT format can be visualized using Graphviz tools:
- `dot` (command-line)
- Online tools like [Graphviz Online](https://dreampuf.github.io/GraphvizOnline/)
- Various Graphviz GUI applications

## Project Structure

```
slither-icfg/
├── icfg.py              # Main ICFG generation script
├── analyze.py           # Example analysis script
├── dataset/
│   └── scan_queue/      # Directory containing projects to scan
│       ├── example.sol
│       └── min_slippage_example/
├── out/                 # Output directory for ICFG files
│   ├── icfg.json
│   └── icfg.dot
└── pyproject.toml       # Poetry configuration
```

## Troubleshooting

### Common Issues

1. **"No Solidity files found"**
   - Ensure the target path contains `.sol` files
   - For project directories, ensure project configuration files are present

2. **"Multiple Solidity files found"**
   - Specify a single `.sol` file with `--target`
   - Or ensure the directory is a recognized project (Hardhat/Foundry/Truffle/Brownie)

3. **Import errors**
   - Make sure the virtual environment is activated
   - Run `poetry install` to ensure all dependencies are installed

## License

[Add your license information here]


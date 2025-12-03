from slither.slither import Slither

sl = Slither(".")  # or path to your main .sol, Hardhat/Foundry project root

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
        for son in n.sons:
            icfg_succ[n].add(son)  # intra-procedural edge

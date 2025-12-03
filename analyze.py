from slither.slither import Slither  
  
slither = Slither('call_graph.sol')  
  
for contract in slither.contracts:  
    print(f"Contract: {contract.name}")

    for function in contract.functions:
        print(f"  Function: {function.name}")
        print(f"    Read: {[v.name for v in function.state_variables_read]}")
        print(f"    Written: {[v.name for v in function.state_variables_written]}")
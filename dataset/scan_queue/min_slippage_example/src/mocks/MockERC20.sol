// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

contract MockERC20 {
    string public name;
    string public symbol;
    uint8  public decimals = 18;
    uint public totalSupply;
    mapping(address => uint) public balanceOf;
    mapping(address => mapping(address => uint)) public allowance;

    constructor(string memory n, string memory s, uint supply) {
        name = n; symbol = s;
        _mint(msg.sender, supply);
    }

    function _mint(address to, uint amt) internal {
        totalSupply += amt;
        balanceOf[to] += amt;
    }

    function transfer(address to, uint amt) external returns (bool) {
        require(balanceOf[msg.sender] >= amt, "bal");
        balanceOf[msg.sender] -= amt;
        balanceOf[to] += amt;
        return true;
    }

    function approve(address sp, uint amt) external returns (bool) {
        allowance[msg.sender][sp] = amt;
        return true;
    }

    function transferFrom(address f, address t, uint amt) external returns (bool) {
        require(balanceOf[f] >= amt, "bal");
        require(allowance[f][msg.sender] >= amt, "allow");
        allowance[f][msg.sender] -= amt;
        balanceOf[f] -= amt;
        balanceOf[t] += amt;
        return true;
    }
}

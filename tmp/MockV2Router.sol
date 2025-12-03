// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "../interfaces/IUniswapV2RouterLike.sol";
import "./MockERC20.sol";

contract MockV2Router is IUniswapV2RouterLike {
    // simplistic price model: amountOut = amountIn * rateNumer / rateDenom
    uint public rateNumer = 1;
    uint public rateDenom = 1;

    function setRate(uint numer, uint denom) external {
        require(denom != 0, "den");
        rateNumer = numer; rateDenom = denom;
    }

    function swapExactTokensForTokens(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint /*deadline*/
    ) external override returns (uint[] memory amounts) {
        require(path.length == 2, "path");
        MockERC20 inT = MockERC20(path[0]);
        MockERC20 outT = MockERC20(path[1]);

        require(inT.transferFrom(msg.sender, address(this), amountIn), "tf");

        uint outAmt = amountIn * rateNumer / rateDenom;
        require(outAmt >= amountOutMin, "INSUFFICIENT_OUTPUT_AMOUNT");

        outT.transfer(to, outAmt);

        
        amounts[0] = amountIn;
        amounts[1] = outAmt;
    }

    function addLiquidity(
        address tokenA, address tokenB,
        uint amountADesired, uint amountBDesired,
        uint amountAMin, uint amountBMin,
        address to, uint /*deadline*/
    ) external override returns (uint amountA, uint amountB, uint liquidity) {
        // Enforce mins like a real router would
        require(amountADesired >= amountAMin, "A<min");
        require(amountBDesired >= amountBMin, "B<min");

        MockERC20(tokenA).transferFrom(msg.sender, address(this), amountADesired);
        MockERC20(tokenB).transferFrom(msg.sender, address(this), amountBDesired);

        amountA = amountADesired;
        amountB = amountBDesired;
        liquidity = sqrt(amountA * amountB);
        MockERC20(address(0)); // noop
        // send “LP token” as plain accounting via tokenA to ‘to’ for demo omitted
        // no-op on ‘to’ to keep mock small
        to; 
    }

    function sqrt(uint x) internal pure returns (uint y) {
        uint z = (x + 1) / 2;
        y = x;
        while (z < y) { y = z; z = (x / z + z) / 2; }
    }
}

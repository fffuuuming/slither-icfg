// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "../interfaces/IUniswapV3PoolLike.sol";

contract MockV3Pool is IUniswapV3PoolLike {
    // Accept any swap. Record lastLimit for tests.
    uint160 public lastLimit;
    bool public zeroForOneLast;

    function swap(
        address /*recipient*/,
        bool zeroForOne,
        int256 amountSpecified,
        uint160 sqrtPriceLimitX96,
        bytes calldata /*data*/
    ) external override returns (int256 amount0, int256 amount1) {
        lastLimit = sqrtPriceLimitX96;
        zeroForOneLast = zeroForOne;

        // Adversarial fill: return worst direction payout
        if (zeroForOne) {
            // pay token0, receive token1 at poor rate
            amount0 = amountSpecified;      // spent
            amount1 = -int256(uint256(1));  // received tiny
        } else {
            amount0 = -int256(uint256(1));
            amount1 = amountSpecified;
        }
    }
}

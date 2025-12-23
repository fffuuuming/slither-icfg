// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

interface IUniswapV3PoolLike {
    // returns delta0, delta1
    function swap(
        address recipient,
        bool zeroForOne,
        int256 amountSpecified,
        uint160 sqrtPriceLimitX96,
        bytes calldata data
    ) external returns (int256, int256);
}

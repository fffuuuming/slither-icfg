// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "./interfaces/IUniswapV3PoolLike.sol";

/*
Thinking Process:
1) swap() on V3 pool -> yes.
2) Price limit param sqrtPriceLimitX96 exists.
3) Hardcoded to extreme ends -> disables price protection.
4) Confirmed.
Conclusion: Contains vulnerability.
*/
contract VulnerableV3HardcodedLimit {
    IUniswapV3PoolLike public pool;
    uint160 public constant MIN_SQRT_RATIO = 4295128739 + 1;
    uint160 public constant MAX_SQRT_RATIO = 1461446703485210103287273052203988822378723970342 - 1;

    constructor(IUniswapV3PoolLike p) { pool = p; }

    function swapAll_Hardcoded(bool zeroForOne, uint amount) external {
        // VULN: uses extreme hardcoded limits
        uint160 limit = zeroForOne ? MIN_SQRT_RATIO : MAX_SQRT_RATIO;
        pool.swap(address(this), zeroForOne, int256(amount), limit, abi.encode(msg.sender));
    }
}

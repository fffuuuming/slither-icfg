// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "./interfaces/IUniswapV2RouterLike.sol";
import "./mocks/MockERC20.sol";

/*
Thinking Process:
1) Adds liquidity -> yes.
2) Slippage params amountAMin, amountBMin exist in signature.
3) They are ignored and not forwarded to underlying router.
4) Confirmed: mins unused, no validation on callee.
Conclusion: Contains vulnerability.
*/
contract VulnerableIgnoreMinAddLiquidity {
    IUniswapV2RouterLike public router;

    constructor(IUniswapV2RouterLike r) { router = r; }

    function addLiquidity_IgnoreMin(
        address tokenA, address tokenB,
        uint amountADesired, uint amountBDesired,
        uint amountAMin, uint amountBMin, // declared but unused
        address to, uint deadline
    ) external returns (uint liq) {
        MockERC20(tokenA).approve(address(router), amountADesired);
        MockERC20(tokenB).approve(address(router), amountBDesired);

        // VULN: forwards a variant that drops mins by reusing same name
        // We "forget" to pass amountAMin/BMin. The mock enforces mins, so
        // ignoring them eliminates protection.
        (,,liq) = router.addLiquidity(
            tokenA, tokenB,
            amountADesired, amountBDesired,
            0, 0,                // <-- BUG: mins forced to 0
            to, deadline
        );
    }
}

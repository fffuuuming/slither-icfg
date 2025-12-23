// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "./interfaces/IUniswapV2RouterLike.sol";
import "./mocks/MockERC20.sol";

/*
Thinking Process:
1) Token swap via swapExactTokensForTokens -> yes.
2) Slippage param exists: amountOutMin at index 1.
3) Here it is hardcoded to 0 -> not validated by caller.
4) Confirmed: zero min allows arbitrary bad fills.
Conclusion: Contains vulnerability.
*/
contract VulnerableZeroMinSwap {
    IUniswapV2RouterLike public router;

    constructor(IUniswapV2RouterLike r) { router = r; }

    function swapAll_NoMin(address tokenIn, address tokenOut) external {
        uint bal = MockERC20(tokenIn).balanceOf(msg.sender);
        require(bal > 0, "no bal");
        MockERC20(tokenIn).approve(address(router), bal);

        address;
        path[0] = tokenIn; path[1] = tokenOut;

        // VULN: amountOutMin = 0
        router.swapExactTokensForTokens(
            bal,
            0,
            path,
            msg.sender,
            block.timestamp
        );
    }
}

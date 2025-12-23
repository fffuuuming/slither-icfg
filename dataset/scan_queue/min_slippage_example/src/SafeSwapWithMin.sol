// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "./interfaces/IUniswapV2RouterLike.sol";
import "./mocks/MockERC20.sol";

/*
Thinking Process:
1) Token swap -> yes.
2) Slippage param amountOutMin provided by user.
3) Validated by router and configurable.
4) Confirmed safe baseline.
Conclusion: No vulnerability.
*/
contract SafeSwapWithMin {
    IUniswapV2RouterLike public router;

    constructor(IUniswapV2RouterLike r) { router = r; }

    function swapWithMin(
        address tokenIn, address tokenOut,
        uint amountIn, uint amountOutMin
    ) external {
        MockERC20(tokenIn).transferFrom(msg.sender, address(this), amountIn);
        MockERC20(tokenIn).approve(address(router), amountIn);

        address;
        path[0] = tokenIn; path[1] = tokenOut;

        router.swapExactTokensForTokens(
            amountIn,
            amountOutMin,
            path,
            msg.sender,
            block.timestamp
        );
    }
}

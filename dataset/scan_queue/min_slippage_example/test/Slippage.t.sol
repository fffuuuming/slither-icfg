// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "forge-std/Test.sol";

import "../src/mocks/MockERC20.sol";
import "../src/mocks/MockV2Router.sol";
import "../src/mocks/MockV3Pool.sol";
import "../src/VulnerableZeroMinSwap.sol";
import "../src/VulnerableIgnoreMinAddLiquidity.sol";
import "../src/VulnerableV3HardcodedLimit.sol";
import "../src/SafeSwapWithMin.sol";

contract SlippageTest is Test {
    MockERC20 tokenA;
    MockERC20 tokenB;
    MockV2Router v2;
    MockV3Pool v3;

    address user = address(0xBEEF);

    function setUp() public {
        tokenA = new MockERC20("A","A",1e24);
        tokenB = new MockERC20("B","B",1e24);
        v2 = new MockV2Router();
        v3 = new MockV3Pool();

        tokenA.transfer(user, 1e21);
        tokenB.transfer(address(v2), 1e21); // router holds B for payouts
    }

    function test_VulnZeroMin_AllowsBadFill() public {
        vm.startPrank(user);
        tokenA.approve(address(v2), type(uint).max);

        // Adversarial price: output is tiny (1)
        v2.setRate(1, 1e18); // 1e-18 rate

        VulnerableZeroMinSwap vuln = new VulnerableZeroMinSwap(v2);

        uint balABefore = tokenA.balanceOf(user);
        uint balBBefore = tokenB.balanceOf(user);

        vuln.swapAll_NoMin(address(tokenA), address(tokenB));

        uint balAAfter = tokenA.balanceOf(user);
        uint balBAfter = tokenB.balanceOf(user);

        assertLt(balAAfter, balABefore, "spent A");
        assertEq(balBAfter, balBBefore + 1, "received tiny B due to no min");
        vm.stopPrank();
    }

    function test_SafeSwap_RevertsOnLowOut() public {
        vm.startPrank(user);
        SafeSwapWithMin safe = new SafeSwapWithMin(v2);
        tokenA.approve(address(safe), type(uint).max);

        // Adversarial price: output is tiny
        v2.setRate(1, 1e18);

        // User requires at least 1000 B -> should revert
        vm.expectRevert(bytes("INSUFFICIENT_OUTPUT_AMOUNT"));
        safe.swapWithMin(address(tokenA), address(tokenB), 1e18, 1000);
        vm.stopPrank();
    }

    function test_VulnIgnoreMin_AddLiquidity_ForcesZeroMins() public {
        vm.startPrank(user);
        VulnerableIgnoreMinAddLiquidity vuln = new VulnerableIgnoreMinAddLiquidity(v2);

        tokenA.approve(address(v2), type(uint).max);
        tokenB.approve(address(v2), type(uint).max);

        // User asks for strict mins, but contract forwards 0,0
        // Mock router would revert if mins enforced, but contract bypasses protection.
        // Here it succeeds because mins were zeroed in the forwarded call.
        (bool ok,) = address(vuln).call(
            abi.encodeWithSelector(
                vuln.addLiquidity_IgnoreMin.selector,
                address(tokenA), address(tokenB),
                1e18, 1e18,
                1e18, 1e18, // user intended mins (ignored)
                user, block.timestamp
            )
        );
        assertTrue(ok, "succeeds despite user mins request being ignored");
        vm.stopPrank();
    }

    function test_VulnV3_HardcodedLimit_Recorded() public {
        VulnerableV3HardcodedLimit vuln = new VulnerableV3HardcodedLimit(v3);
        vuln.swapAll_Hardcoded(true, 1e18);   // zeroForOne -> MIN limit used
        assertEq(v3.zeroForOneLast(), true, "dir");
        // limit equals one of extremes; check nonzero
        assertGt(v3.lastLimit(), 0, "limit set");
    }
}

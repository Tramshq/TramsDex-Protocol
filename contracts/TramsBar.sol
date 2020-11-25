//SPDX-License-Identifier: UNLICENSED
pragma solidity 0.6.12;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/math/SafeMath.sol";

// TramsBar is the coolest place in town. You come in with some Trams, and leave with more! The longer you stay, the more Trams you get.
//
// This contract handles swapping to and from xTrams, TramsDex's staking token.
contract TramsBar is ERC20("TramsBar", "xTRAMS"){
    using SafeMath for uint256;
    IERC20 public trams;

    // Define the Trams token contract
    constructor(IERC20 _trams) public {
        require(address(_trams) != address(0), "invalid address");
        trams = _trams;
    }

    // Enter the bar. Pay some TRAMS. Earn some shares.
    // Locks Trams and mints xTRAMS
    function enter(uint256 _amount) public {
        // Gets the amount of Trams locked in the contract
        uint256 totalTrams = trams.balanceOf(address(this));
        // Gets the amount of xTrams in existence
        uint256 totalShares = totalSupply();
        // If no xTrams exists, mint it 1:1 to the amount put in
        if (totalShares == 0 || totalTrams == 0) {
            _mint(msg.sender, _amount);
        } 
        // Calculate and mint the amount of xTrams the Trams is worth. The ratio will change overtime, as xTrams is burned/minted and Trams deposited + gained from fees / withdrawn.
        else {
            uint256 what = _amount.mul(totalShares).div(totalTrams);
            _mint(msg.sender, what);
        }
        // Lock the Trams in the contract
        trams.transferFrom(msg.sender, address(this), _amount);
    }

    // Leave the bar. Claim back your TRAMS.
    // Unclocks the staked + gained Trams and burns xTrams
    function leave(uint256 _share) public {
        // Gets the amount of xTrams in existence
        uint256 totalShares = totalSupply();
        // Calculates the amount of Trams the xTrams is worth
        uint256 what = _share.mul(trams.balanceOf(address(this))).div(totalShares);
        _burn(msg.sender, _share);
        trams.transfer(msg.sender, what);
    }
}
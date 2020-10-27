//SPDX-License-Identifier: MIT + WTFPL

pragma solidity 0.6.12;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
import "@openzeppelin/contracts/utils/EnumerableSet.sol";
import "@openzeppelin/contracts/math/SafeMath.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./TramsToken.sol";


interface IMigratorChef {
    // Perform LP token migration from legacy UniswapV2 to TramsDex.
    // Take the current LP token address and return the new LP token address.
    // Migrator should have full access to the caller's LP token.
    // Return the new LP token address.
    //
    // XXX Migrator must have allowance access to UniswapV2 LP tokens.
    // TramsDex must mint EXACTLY the same amount of TramsDex LP tokens or
    // else something bad will happen. Traditional UniswapV2 does not
    // do that so be careful!
    function migrate(IERC20 token) external returns (IERC20);
}


// TramsMaster is the master of Trams. He can make TRAMS .
//
// Note that it's ownable and the owner wields tremendous power. The ownership
// will be transferred to a governance smart contract once TRAMS is sufficiently
// distributed and the community can show to govern itself.
//
// Have fun reading it. Hopefully it's bug-free. God bless.
contract TramsMaster is Ownable {
    using SafeMath for uint256;
    using SafeERC20 for IERC20;

    // Info of each user.
    struct UserInfo {
        uint256 amount; // How many LP tokens the user has provided.
        uint256 rewardDebt; // Reward debt. See explanation below.
        //
        // We do some fancy math here. Basically, any point in time, the amount of TRAMS
        // entitled to a user but is pending to be distributed is:
        //
        //   pending reward = (user.amount * pool.accTramsPerShare) - user.rewardDebt
        //
        // Whenever a user deposits or withdraws LP tokens to a pool. Here's what happens:
        //   1. The pool's `accTramsPerShare` (and `lastRewardBlock`) gets updated.
        //   2. User receives the pending reward sent to his/her address.
        //   3. User's `amount` gets updated.
        //   4. User's `rewardDebt` gets updated.
    }

    // Info of each pool.
    struct PoolInfo {
        IERC20 lpToken; // Address of LP token contract.
        uint256 allocPoint; // How many allocation points assigned to this pool. TRAMS to distribute per block.
        uint256 lastRewardBlock; // Last block number that TRAMS distribution occurs.
        uint256 accTramsPerShare; // Accumulated TRAMS per share, times 1e12. See below.
    }

    // The TRAMS TOKEN!
    TramsToken public trams;
    // Dev address.
    address public devaddr;
    // Block number when beta test period ends.
    uint256 public betaTestEndBlock;
    // Block number when bonus TRAMS period ends.
    uint256 public bonusEndBlock;
    // Block number when mint TRAMS period ends.
    uint256 public mintEndBlock;
    // TRAMS tokens created per block.
    uint256 public tramsPerBlock;
    // Bonus muliplier for 7~22 days trams makers.
    uint256 public constant BONUSONE_MULTIPLIER = 20;
    // Bonus muliplier for 22 days onwards till mintend, trams makers.
    uint256 public constant BONUSTWO_MULTIPLIER = 2;
    // beta test block num,about 7 days.
    uint256 public constant BETATEST_BLOCKNUM = 46530;
    // Bonus block num,about 15 days.
    uint256 public constant BONUS_BLOCKNUM = 99750;
    // mint end block num,about 73+15 days.
    uint256 public constant MINTEND_BLOCKNUM = 585134;
    // The migrator contract. It has a lot of power. Can only be set through governance (owner).
    IMigratorChef public migrator;

    // Info of each pool.
    PoolInfo[] public poolInfo;
    // Info of each user that stakes LP tokens.
    mapping(uint256 => mapping(address => UserInfo)) public userInfo;
    // Record whether the pair has been added.
    mapping(address => uint256) public lpTokenPID;
    // Total allocation poitns. Must be the sum of all allocation points in all pools.
    uint256 public totalAllocPoint = 0;
    // The block number when TRAMS mining starts.
    uint256 public startBlock;

    event Deposit(address indexed user, uint256 indexed pid, uint256 amount);
    event Withdraw(address indexed user, uint256 indexed pid, uint256 amount);
    event EmergencyWithdraw(
        address indexed user,
        uint256 indexed pid,
        uint256 amount
    );

    constructor(
        TramsToken _trams,
        address _devaddr,
        uint256 _tramsPerBlock,
        uint256 _startBlock
    ) public {
        trams = _trams;
        devaddr = _devaddr;
        tramsPerBlock = _tramsPerBlock;
        startBlock = _startBlock;
        betaTestEndBlock = startBlock.add(BETATEST_BLOCKNUM);
        bonusEndBlock = startBlock.add(BONUS_BLOCKNUM).add(BETATEST_BLOCKNUM);
        mintEndBlock = startBlock.add(MINTEND_BLOCKNUM).add(BETATEST_BLOCKNUM);
    }

    function poolLength() external view returns (uint256) {
        return poolInfo.length;
    }

    // Add a new lp to the pool. Can only be called by the owner.
    // XXX DO NOT add the same LP token more than once. Rewards will be messed up if you do.
    function add(uint256 _allocPoint, IERC20 _lpToken, bool _withUpdate) public onlyOwner {
        if (_withUpdate) {
            massUpdatePools();
        }
        require(lpTokenPID[address(_lpToken)] == 0, "TramsMaster:duplicate add.");
        uint256 lastRewardBlock = block.number > startBlock ? block.number : startBlock;
        totalAllocPoint = totalAllocPoint.add(_allocPoint);
        poolInfo.push(
            PoolInfo({
                lpToken: _lpToken,
                allocPoint: _allocPoint,
                lastRewardBlock: lastRewardBlock,
                accTramsPerShare: 0
            })
        );
        lpTokenPID[address(_lpToken)] = poolInfo.length;
    }

    // Update the given pool's TRAMS allocation point. Can only be called by the owner.
    function set(uint256 _pid, uint256 _allocPoint, bool _withUpdate) public onlyOwner {
        if (_withUpdate) {
            massUpdatePools();
        }
        totalAllocPoint = totalAllocPoint.sub(poolInfo[_pid].allocPoint).add(_allocPoint);
        poolInfo[_pid].allocPoint = _allocPoint;
    }

    // Set the migrator contract. Can only be called by the owner.
    function setMigrator(IMigratorChef _migrator) public onlyOwner {
        migrator = _migrator;
    }

    // Handover the tramstoken mintage right.
    function handoverTramsMintage(address newOwner) public onlyOwner {
        trams.transferOwnership(newOwner);
    }

    // Migrate lp token to another lp contract. Can be called by anyone. We trust that migrator contract is good.
    function migrate(uint256 _pid) public {
        require(address(migrator) != address(0), "migrate: no migrator");
        PoolInfo storage pool = poolInfo[_pid];
        IERC20 lpToken = pool.lpToken;
        uint256 bal = lpToken.balanceOf(address(this));
        lpToken.safeApprove(address(migrator), bal);
        IERC20 newLpToken = migrator.migrate(lpToken);
        require(bal == newLpToken.balanceOf(address(this)), "migrate: bad");
        pool.lpToken = newLpToken;
    }

    // Return reward multiplier over the given _from to _to block.
    function getMultiplier(uint256 _from, uint256 _to) public view returns (uint256) {
        uint256 _toFinal = _to > mintEndBlock ? mintEndBlock : _to;
        if (_toFinal <= betaTestEndBlock) {
             return _toFinal.sub(_from);
        }else if (_from >= mintEndBlock) {
            return 0;
        } else if (_toFinal <= bonusEndBlock) {
            if (_from < betaTestEndBlock) {
                return betaTestEndBlock.sub(_from).add(_toFinal.sub(betaTestEndBlock).mul(BONUSONE_MULTIPLIER));
            } else {
                return _toFinal.sub(_from).mul(BONUSONE_MULTIPLIER);
            }
        } else {
            if (_from < betaTestEndBlock) {
                return betaTestEndBlock.sub(_from).add(bonusEndBlock.sub(betaTestEndBlock).mul(BONUSONE_MULTIPLIER)).add(
                    (_toFinal.sub(bonusEndBlock).mul(BONUSTWO_MULTIPLIER)));
            } else if (betaTestEndBlock <= _from && _from < bonusEndBlock) {
                return bonusEndBlock.sub(_from).mul(BONUSONE_MULTIPLIER).add(_toFinal.sub(bonusEndBlock).mul(BONUSTWO_MULTIPLIER));
            } else {
                return _toFinal.sub(_from).mul(BONUSTWO_MULTIPLIER);
            }
        } 
    }

    // View function to see pending TRAMS on frontend.
    function pendingTrams(uint256 _pid, address _user) external view returns (uint256) {
        PoolInfo storage pool = poolInfo[_pid];
        UserInfo storage user = userInfo[_pid][_user];
        uint256 accTramsPerShare = pool.accTramsPerShare;
        uint256 lpSupply = pool.lpToken.balanceOf(address(this));
        if (block.number > pool.lastRewardBlock && lpSupply != 0) {
            uint256 multiplier = getMultiplier(pool.lastRewardBlock, block.number);
            uint256 tramsReward = multiplier.mul(tramsPerBlock).mul(pool.allocPoint).div(totalAllocPoint);
            accTramsPerShare = accTramsPerShare.add(tramsReward.mul(1e12).div(lpSupply));
        }
        return user.amount.mul(accTramsPerShare).div(1e12).sub(user.rewardDebt);
    }

    // Update reward vairables for all pools. Be careful of gas spending!
    function massUpdatePools() public {
        uint256 length = poolInfo.length;
        for (uint256 pid = 0; pid < length; ++pid) {
            updatePool(pid);
        }
    }

    // Update reward variables of the given pool to be up-to-date.
    function updatePool(uint256 _pid) public {
        PoolInfo storage pool = poolInfo[_pid];
        if (block.number <= pool.lastRewardBlock) {
            return;
        }
        uint256 lpSupply = pool.lpToken.balanceOf(address(this));
        if (lpSupply == 0) {
            pool.lastRewardBlock = block.number;
            return;
        }
        uint256 multiplier = getMultiplier(pool.lastRewardBlock, block.number);
        if (multiplier == 0) {
            pool.lastRewardBlock = block.number;
            return;
        }
        uint256 tramsReward = multiplier.mul(tramsPerBlock).mul(pool.allocPoint).div(totalAllocPoint);
        trams.mint(devaddr, tramsReward.div(10));
        trams.mint(address(this), tramsReward);
        pool.accTramsPerShare = pool.accTramsPerShare.add(tramsReward.mul(1e12).div(lpSupply));
        pool.lastRewardBlock = block.number;
    }

    // Deposit LP tokens to TramsMaster for TRAMS allocation.
    function deposit(uint256 _pid, uint256 _amount) public {
        PoolInfo storage pool = poolInfo[_pid];
        UserInfo storage user = userInfo[_pid][msg.sender];
        updatePool(_pid);
        uint256 pending = user.amount.mul(pool.accTramsPerShare).div(1e12).sub(user.rewardDebt);
        user.amount = user.amount.add(_amount);
        user.rewardDebt = user.amount.mul(pool.accTramsPerShare).div(1e12);
        if (pending > 0) safeTramsTransfer(msg.sender, pending);
        pool.lpToken.safeTransferFrom(address(msg.sender), address(this), _amount);
        emit Deposit(msg.sender, _pid, _amount);
    }

    // Withdraw LP tokens from TramsMaster.
    function withdraw(uint256 _pid, uint256 _amount) public {
        PoolInfo storage pool = poolInfo[_pid];
        UserInfo storage user = userInfo[_pid][msg.sender];
        require(user.amount >= _amount, "withdraw: not good");
        updatePool(_pid);
        uint256 pending = user.amount.mul(pool.accTramsPerShare).div(1e12).sub(user.rewardDebt);
        user.amount = user.amount.sub(_amount);
        user.rewardDebt = user.amount.mul(pool.accTramsPerShare).div(1e12);
        safeTramsTransfer(msg.sender, pending);
        pool.lpToken.safeTransfer(address(msg.sender), _amount);
        emit Withdraw(msg.sender, _pid, _amount);
    }

    // Withdraw without caring about rewards. EMERGENCY ONLY.
    function emergencyWithdraw(uint256 _pid) public {
        PoolInfo storage pool = poolInfo[_pid];
        UserInfo storage user = userInfo[_pid][msg.sender];
        require(user.amount > 0, "emergencyWithdraw: not good");
        uint256 _amount = user.amount;
        user.amount = 0;
        user.rewardDebt = 0;
        pool.lpToken.safeTransfer(address(msg.sender), _amount);
        emit EmergencyWithdraw(msg.sender, _pid, _amount);
    }

    // Safe trams transfer function, just in case if rounding error causes pool to not have enough TRAMS.
    function safeTramsTransfer(address _to, uint256 _amount) internal {
        uint256 tramsBal = trams.balanceOf(address(this));
        if (_amount > tramsBal) {
            trams.transfer(_to, tramsBal);
        } else {
            trams.transfer(_to, _amount);
        }
    }

    // Update dev address by the previous dev.
    function dev(address _devaddr) public {
        require(msg.sender == devaddr, "dev: wut?");
        devaddr = _devaddr;
    }
}

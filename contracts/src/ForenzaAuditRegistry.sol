// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";

/**
 * @title ForenzaAuditRegistry
 * @notice FORENZA Forensic Evidence & Query Access Control Ledger
 * @dev High-security ISO/IEC 17025:2017 compliant audit trail and RBAC governance ledger.
 */
contract ForenzaAuditRegistry is AccessControl, Pausable {
    // ========================= Roles =========================

    bytes32 public constant LAB_ANALYST_ROLE   = keccak256("LAB_ANALYST_ROLE");
    bytes32 public constant LEGAL_AUDITOR_ROLE = keccak256("LEGAL_AUDITOR_ROLE");
    bytes32 public constant COURT_OFFICER_ROLE = keccak256("COURT_OFFICER_ROLE");

    // ========================= Types =========================

    enum InvestigatorStatus {
        UNREGISTERED,
        ACTIVE,
        SUSPENDED,
        REVOKED
    }

    struct InvestigatorProfile {
        string             name;
        string             agency;
        string             accreditation; // e.g., "ISO/IEC 17025:2017"
        InvestigatorStatus status;
        uint256            createdAt;
        uint256            sessionExpiry;
    }

    struct QueryLogEntry {
        address investigator;
        string  queryType;    // e.g., "STR_24_MATCH", "KINSHIP_LR", "ZKP_GROTH16_VERIFY"
        bytes32 profileHash;  // SHA-256 / Keccak-256 genomic profile commitment
        uint256 timestamp;
        uint256 blockNumber;
    }

    // ========================= State Variables =========================

    /// @notice Investigator address => Investigator Profile
    mapping(address => InvestigatorProfile) public investigators;

    /// @notice Investigator address => Active session token hash
    mapping(address => bytes32) private _sessionTokens;

    /// @notice Immutable on-chain audit trail
    QueryLogEntry[] public auditTrail;

    // Rate Limiting Security Configuration (5 calls / 60 seconds)
    uint256 public constant RATE_LIMIT_THRESHOLD = 5;
    uint256 public constant RATE_LIMIT_WINDOW    = 60; // seconds

    struct RateLimitState {
        uint256 count;
        uint256 windowStart;
    }
    mapping(address => RateLimitState) private _rateLimits;

    // ========================= Events =========================

    event InvestigatorEnrolled(address indexed investigator, string name, string agency);
    event InvestigatorStatusUpdated(address indexed investigator, InvestigatorStatus status);
    event SessionGranted(address indexed investigator, bytes32 sessionToken, uint256 expiry);
    event SessionRevoked(address indexed investigator);

    event QueryLogged(
        uint256 indexed logIndex,
        address indexed investigator,
        string  queryType,
        bytes32 profileHash,
        uint256 timestamp
    );

    event RateLimitExceeded(address indexed investigator, uint256 timestamp);
    event GlobalLockdownTriggered(address indexed triggeredBy, string reason, uint256 timestamp);
    event GlobalLockdownLifted(address indexed liftedBy, uint256 timestamp);

    // ========================= Modifiers =========================

    modifier onlyAuthorizedInvestigator(bytes32 _sessionToken) {
        require(!paused(), "ForenzaAuditRegistry: system is in LOCKDOWN mode");
        InvestigatorProfile storage prof = investigators[msg.sender];

        require(prof.status == InvestigatorStatus.ACTIVE, "ForenzaAuditRegistry: investigator not active");
        require(prof.sessionExpiry > 0 && block.timestamp <= prof.sessionExpiry, "ForenzaAuditRegistry: session token expired");
        require(_sessionTokens[msg.sender] == _sessionToken, "ForenzaAuditRegistry: invalid session token");
        _;
    }

    // ========================= Constructor =========================

    constructor(address rootAdmin) {
        address admin = (rootAdmin != address(0)) ? rootAdmin : msg.sender;
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(LAB_ANALYST_ROLE, admin);
        _grantRole(LEGAL_AUDITOR_ROLE, admin);
        _grantRole(COURT_OFFICER_ROLE, admin);
    }

    // ========================= IAM / RBAC Administration =========================

    /**
     * @notice Enrolls or updates an accredited forensic investigator in the registry.
     */
    function enrollInvestigator(
        address _investigator,
        string calldata _name,
        string calldata _agency,
        string calldata _accreditation,
        bytes32 _role
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(_investigator != address(0), "ForenzaAuditRegistry: invalid address");

        investigators[_investigator] = InvestigatorProfile({
            name: _name,
            agency: _agency,
            accreditation: bytes(_accreditation).length > 0 ? _accreditation : "ISO/IEC 17025:2017",
            status: InvestigatorStatus.ACTIVE,
            createdAt: block.timestamp,
            sessionExpiry: 0
        });

        if (_role != bytes32(0)) {
            _grantRole(_role, _investigator);
        }

        emit InvestigatorEnrolled(_investigator, _name, _agency);
    }

    /**
     * @notice Provisions a cryptographically bound session token for an investigator.
     */
    function grantSession(
        address _investigator,
        bytes32 _sessionToken,
        uint256 _durationSeconds
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(investigators[_investigator].status == InvestigatorStatus.ACTIVE, "ForenzaAuditRegistry: investigator not active");
        require(_sessionToken != bytes32(0), "ForenzaAuditRegistry: invalid session token");

        uint256 expiry = block.timestamp + (_durationSeconds > 0 ? _durationSeconds : 86400); // default 24h
        investigators[_investigator].sessionExpiry = expiry;
        _sessionTokens[_investigator] = _sessionToken;

        emit SessionGranted(_investigator, _sessionToken, expiry);
    }

    /**
     * @notice Revokes an investigator's access immediately.
     */
    function setInvestigatorStatus(
        address _investigator,
        InvestigatorStatus _status
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        investigators[_investigator].status = _status;
        if (_status != InvestigatorStatus.ACTIVE) {
            delete _sessionTokens[_investigator];
            investigators[_investigator].sessionExpiry = 0;
        }
        emit InvestigatorStatusUpdated(_investigator, _status);
    }

    // ========================= Core: Query Logging =========================

    /**
     * @notice Records an immutable forensic DNA query on the blockchain ledger.
     */
    function logQuery(
        string calldata _queryType,
        bytes32 _profileHash,
        bytes32 _sessionToken
    ) external onlyAuthorizedInvestigator(_sessionToken) {
        // Enforce sliding-window rate limit
        bool allowed = _enforceRateLimit(msg.sender);
        if (!allowed) {
            return;
        }

        QueryLogEntry memory entry = QueryLogEntry({
            investigator: msg.sender,
            queryType: _queryType,
            profileHash: _profileHash,
            timestamp: block.timestamp,
            blockNumber: block.number
        });

        auditTrail.push(entry);

        emit QueryLogged(
            auditTrail.length - 1,
            msg.sender,
            _queryType,
            _profileHash,
            block.timestamp
        );
    }

    // ========================= Emergency Circuit Breaker =========================

    /**
     * @notice Triggers emergency global lockdown halting all query operations.
     */
    function triggerLockdown(string calldata reason) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
        emit GlobalLockdownTriggered(msg.sender, reason, block.timestamp);
    }

    /**
     * @notice Lifts the emergency global lockdown.
     */
    function liftLockdown() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
        emit GlobalLockdownLifted(msg.sender, block.timestamp);
    }

    // ========================= Internal Helpers =========================

    function _enforceRateLimit(address investigator) internal returns (bool) {
        RateLimitState storage rl = _rateLimits[investigator];

        if (block.timestamp - rl.windowStart > RATE_LIMIT_WINDOW) {
            // New window
            rl.count = 1;
            rl.windowStart = block.timestamp;
            return true;
        } else {
            rl.count++;
            if (rl.count > RATE_LIMIT_THRESHOLD) {
                // Auto-suspend investigator on rate limit breach
                investigators[investigator].status = InvestigatorStatus.SUSPENDED;
                delete _sessionTokens[investigator];
                emit RateLimitExceeded(investigator, block.timestamp);
                emit InvestigatorStatusUpdated(investigator, InvestigatorStatus.SUSPENDED);
                return false;
            }
            return true;
        }
    }

    // ========================= View Helpers =========================

    function getLogCount() external view returns (uint256) {
        return auditTrail.length;
    }

    function getLog(uint256 index) external view returns (QueryLogEntry memory) {
        require(index < auditTrail.length, "ForenzaAuditRegistry: index out of bounds");
        return auditTrail[index];
    }

    function isInvestigatorAuthorized(address investigator) external view returns (bool) {
        if (paused()) return false;
        InvestigatorProfile storage prof = investigators[investigator];
        return (prof.status == InvestigatorStatus.ACTIVE && block.timestamp <= prof.sessionExpiry);
    }

    // Backward-compatible profiles mapping view for legacy Web3 service
    function profiles(address investigator) external view returns (string memory name, bool isAuthorized, uint256 createdAt) {
        InvestigatorProfile storage prof = investigators[investigator];
        name = prof.name;
        isAuthorized = (prof.status == InvestigatorStatus.ACTIVE && !paused());
        createdAt = prof.createdAt;
    }
}

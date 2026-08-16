// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ForensicMerkleLedger
 * @notice FORENZA Module 26: Cryptographic Chain of Custody (CoC) Immutable Merkle Tree Ledger
 * @dev Anchors case Merkle roots and verifies O(log2 N) Merkle inclusion proofs on-chain.
 *      Complies with ISO/IEC 17025:2017 Clause 7.6, NIST SP 800-106, and Federal Rules of Evidence Rule 702.
 */
contract ForensicMerkleLedger is Ownable {
    // ========================= Structs =========================

    struct CaseRecord {
        bytes32 merkleRoot;
        uint256 leafCount;
        uint256 timestamp;
        address registeredBy;
        string  metadataUri; // IPFS / LIMS reference URI
        bool    exists;
    }

    struct CustodyEventRecord {
        bytes32 caseId;
        bytes32 eventId;
        uint256 timestamp;
        address officer;
        string  officerId;
        string  sampleBarcode;
        string  locationId;
        bytes32 priorHash;
        bytes32 leafHash;
    }

    // ========================= State Variables =========================

    /// @notice Case ID => Case Merkle Commitment Record
    mapping(bytes32 => CaseRecord) public cases;

    /// @notice Case ID => Array of atomic custody events logged on-chain
    mapping(bytes32 => CustodyEventRecord[]) private _caseEvents;

    /// @notice Total registered case count
    uint256 public totalCasesRegistered;

    /// @notice Total custody transitions anchored across all cases
    uint256 public totalEventsAnchored;

    // ========================= Events =========================

    event CaseMerkleRootCommitted(
        bytes32 indexed caseId,
        bytes32 indexed merkleRoot,
        uint256 leafCount,
        address indexed registeredBy,
        string  metadataUri,
        uint256 timestamp
    );

    event CustodyEventAnchored(
        bytes32 indexed caseId,
        bytes32 indexed eventId,
        bytes32 indexed leafHash,
        address officer,
        string  officerId,
        string  sampleBarcode,
        uint256 timestamp
    );

    event ProofVerified(
        bytes32 indexed caseId,
        bytes32 indexed leafHash,
        bytes32 indexed merkleRoot,
        bool    isValid,
        uint256 timestamp
    );

    // ========================= Constructor =========================

    constructor() Ownable(msg.sender) {}

    // ========================= Core Ledger Operations =========================

    /**
     * @notice Commits an immutable Merkle root commitment for a forensic case file.
     * @param caseId Unique 32-byte identifier of the forensic casework dossier.
     * @param merkleRoot The 32-byte root hash of the binary Merkle tree over all custody events.
     * @param leafCount Number of atomic custody events encapsulated in the tree.
     * @param metadataUri URI pointing to canonical LIMS case metadata (e.g. ipfs://... or lims://...).
     */
    function commitCaseMerkleRoot(
        bytes32 caseId,
        bytes32 merkleRoot,
        uint256 leafCount,
        string calldata metadataUri
    ) external {
        require(caseId != bytes32(0), "ForensicMerkleLedger: invalid case ID");
        require(merkleRoot != bytes32(0), "ForensicMerkleLedger: invalid Merkle root");
        require(leafCount > 0, "ForensicMerkleLedger: leaf count must be > 0");
        require(!cases[caseId].exists, "ForensicMerkleLedger: case root already committed");

        cases[caseId] = CaseRecord({
            merkleRoot: merkleRoot,
            leafCount: leafCount,
            timestamp: block.timestamp,
            registeredBy: msg.sender,
            metadataUri: metadataUri,
            exists: true
        });

        totalCasesRegistered++;

        emit CaseMerkleRootCommitted(
            caseId,
            merkleRoot,
            leafCount,
            msg.sender,
            metadataUri,
            block.timestamp
        );
    }

    /**
     * @notice Records an atomic custody transition event on-chain.
     * @param caseId The casework identifier.
     * @param eventId Unique identifier for this custody state transition.
     * @param officerId Laboratory officer / technician identifier.
     * @param sampleBarcode Physical sample tube / evidence barcode.
     * @param locationId Laboratory extraction / cold-storage location ID.
     * @param priorHash Cryptographic hash of the immediately preceding custody event (or bytes32(0) for genesis).
     * @return leafHash The computed SHA-256 / Keccak-256 leaf hash for this custody event.
     */
    function recordCustodyEvent(
        bytes32 caseId,
        bytes32 eventId,
        string calldata officerId,
        string calldata sampleBarcode,
        string calldata locationId,
        bytes32 priorHash
    ) external returns (bytes32 leafHash) {
        require(caseId != bytes32(0), "ForensicMerkleLedger: invalid case ID");
        require(eventId != bytes32(0), "ForensicMerkleLedger: invalid event ID");

        leafHash = computeEventLeafHash(
            eventId,
            block.timestamp,
            officerId,
            sampleBarcode,
            locationId,
            priorHash
        );

        _caseEvents[caseId].push(CustodyEventRecord({
            caseId: caseId,
            eventId: eventId,
            timestamp: block.timestamp,
            officer: msg.sender,
            officerId: officerId,
            sampleBarcode: sampleBarcode,
            locationId: locationId,
            priorHash: priorHash,
            leafHash: leafHash
        }));

        totalEventsAnchored++;

        emit CustodyEventAnchored(
            caseId,
            eventId,
            leafHash,
            msg.sender,
            officerId,
            sampleBarcode,
            block.timestamp
        );
    }

    // ========================= Merkle Proof Verification =========================

    /**
     * @notice Pure mathematical verification of an O(log2 N) Merkle Inclusion Proof.
     * @param leafHash The hash of the target custody event being proven.
     * @param siblings Array of sibling hashes along the proof path from leaf to root.
     * @param pathBits Bitmask indicating the direction of each sibling (bit j = 0 -> sibling is RIGHT, bit j = 1 -> sibling is LEFT).
     * @param expectedRoot The expected Merkle root anchor.
     * @return isValid True if the proof path reduces exactly to expectedRoot.
     */
    function verifyInclusionProof(
        bytes32 leafHash,
        bytes32[] calldata siblings,
        uint256 pathBits,
        bytes32 expectedRoot
    ) public pure returns (bool isValid) {
        bytes32 current = leafHash;
        uint256 len = siblings.length;

        for (uint256 i = 0; i < len; ) {
            bytes32 sibling = siblings[i];
            bool siblingIsLeft = (pathBits & (1 << i)) != 0;

            if (siblingIsLeft) {
                // Sibling is LEFT: parent = hash(sibling || current)
                current = keccak256(abi.encodePacked(sibling, current));
            } else {
                // Sibling is RIGHT: parent = hash(current || sibling)
                current = keccak256(abi.encodePacked(current, sibling));
            }

            unchecked { ++i; }
        }

        isValid = (current == expectedRoot);
    }

    /**
     * @notice Verifies a custody event inclusion proof against a committed on-chain case root.
     * @param caseId The casework dossier identifier.
     * @param leafHash The custody event leaf hash.
     * @param siblings Array of sibling hashes from leaf to root.
     * @param pathBits Bitmask direction selector.
     * @return isValid True if the event is mathematically proven to exist in the case's committed root.
     */
    function verifyCaseInclusion(
        bytes32 caseId,
        bytes32 leafHash,
        bytes32[] calldata siblings,
        uint256 pathBits
    ) external returns (bool isValid) {
        require(cases[caseId].exists, "ForensicMerkleLedger: case not found");
        bytes32 root = cases[caseId].merkleRoot;

        isValid = verifyInclusionProof(leafHash, siblings, pathBits, root);

        emit ProofVerified(caseId, leafHash, root, isValid, block.timestamp);
    }

    // ========================= Helper Views =========================

    /**
     * @notice Canonical leaf hash calculation adhering to Research §1.1.
     */
    function computeEventLeafHash(
        bytes32 eventId,
        uint256 timestamp,
        string calldata officerId,
        string calldata sampleBarcode,
        string calldata locationId,
        bytes32 priorHash
    ) public pure returns (bytes32) {
        return keccak256(abi.encodePacked(
            eventId,
            timestamp,
            officerId,
            sampleBarcode,
            locationId,
            priorHash
        ));
    }

    /**
     * @notice Retrieves the count of recorded custody events for a specific case.
     */
    function getCaseEventCount(bytes32 caseId) external view returns (uint256) {
        return _caseEvents[caseId].length;
    }

    /**
     * @notice Retrieves a specific custody event record.
     */
    function getCaseEvent(bytes32 caseId, uint256 index) external view returns (CustodyEventRecord memory) {
        require(index < _caseEvents[caseId].length, "ForensicMerkleLedger: index out of bounds");
        return _caseEvents[caseId][index];
    }
}

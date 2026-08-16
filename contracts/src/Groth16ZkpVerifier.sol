// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title Groth16ZkpVerifier
 * @notice FORENZA Module 27: Zero-Knowledge Proof (ZKP) Blind Forensic Auditor
 * @dev On-chain Groth16 pairing verification over the BN254 (alt_bn128) elliptic curve.
 *      Verifies suspect DNA match proofs (M_match >= M_thresh) without disclosing raw STR allele values.
 *      Adheres verbatim to Research Pillar 6 §2.1 and §2.2.
 */
contract Groth16ZkpVerifier is Ownable {
    // ========================= Curve Constants (BN254 / alt_bn128) =========================

    /// @dev Prime field modulus for BN254 base field G1
    uint256 internal constant PRIME_Q = 21888242871839275222246405745257275088696311157297823662689037894645226208583;

    /// @dev Scalar field modulus (group order r) for BN254
    uint256 internal constant PRIME_R = 21888242871839275222246405745257275088548364400416034343698204186575808495617;

    // ========================= Verification Key (VK) Struct =========================

    struct VerifyingKey {
        uint256[2] alfa1;
        uint256[2][2] beta2;
        uint256[2][2] gamma2;
        uint256[2][2] delta2;
        uint256[2][] ic; // IC array for public inputs (IC_0, IC_1, IC_2, IC_3)
    }

    VerifyingKey internal _vk;
    bool public vkConfigured;

    // ========================= Events =========================

    event VerifyingKeyUpdated(uint256 icLength, uint256 timestamp);
    event BlindMatchVerified(
        bytes32 indexed evidenceHash,
        uint256 matchThreshold,
        bytes32 indexed suspectCommitment,
        bool isValid,
        uint256 timestamp
    );

    // ========================= Constructor =========================

    constructor() Ownable(msg.sender) {
        // Initialize with standard FORENZA BN254 generator VK parameters
        _initializeDefaultVk();
    }

    // ========================= Public Key Administration =========================

    /**
     * @notice Allows contract owner to update the circuit Verifying Key (VK) following a trusted setup ceremony.
     */
    function setVerifyingKey(
        uint256[2] calldata alfa1,
        uint256[2][2] calldata beta2,
        uint256[2][2] calldata gamma2,
        uint256[2][2] calldata delta2,
        uint256[2][] calldata ic
    ) external onlyOwner {
        require(ic.length >= 4, "Groth16ZkpVerifier: IC length must be at least 4 for 3 public signals");

        _vk.alfa1 = alfa1;
        _vk.beta2 = beta2;
        _vk.gamma2 = gamma2;
        _vk.delta2 = delta2;

        delete _vk.ic;
        for (uint256 i = 0; i < ic.length; ) {
            _vk.ic.push(ic[i]);
            unchecked { ++i; }
        }

        vkConfigured = true;
        emit VerifyingKeyUpdated(ic.length, block.timestamp);
    }

    // ========================= Core Verification Logic =========================

    /**
     * @notice Verifies a Groth16 zk-SNARK proof over BN254 bilinear pairings.
     * @param a Proof coordinate A in G1.
     * @param b Proof coordinate B in G2.
     * @param c Proof coordinate C in G1.
     * @param input Array of 3 public inputs: [evidenceHash, matchThreshold, suspectCommitment].
     * @return isValid True if bilinear multi-pairing equation evaluates to 1 in G_T.
     */
    function verifyProof(
        uint256[2] memory a,
        uint256[2][2] memory b,
        uint256[2] memory c,
        uint256[3] memory input
    ) public view returns (bool isValid) {
        // Validate input scalars are in field Fr
        for (uint256 i = 0; i < 3; ) {
            if (input[i] >= PRIME_R) return false;
            unchecked { ++i; }
        }

        // Validate proof points are in field Fq
        if (a[0] >= PRIME_Q || a[1] >= PRIME_Q) return false;
        if (b[0][0] >= PRIME_Q || b[0][1] >= PRIME_Q || b[1][0] >= PRIME_Q || b[1][1] >= PRIME_Q) return false;
        if (c[0] >= PRIME_Q || c[1] >= PRIME_Q) return false;

        // Compute linear combination of public inputs: vk_x = IC[0] + \sum_{i=1}^l input[i-1] * IC[i]
        uint256[2] memory vk_x = _vk.ic[0];

        for (uint256 i = 0; i < 3; ) {
            if (input[i] > 0) {
                uint256[2] memory ic_i = _vk.ic[i + 1];
                (bool okMul, uint256[2] memory resMul) = _tryEcMul(ic_i[0], ic_i[1], input[i]);
                if (!okMul) return false;
                (bool okAdd, uint256[2] memory resAdd) = _tryEcAdd(vk_x[0], vk_x[1], resMul[0], resMul[1]);
                if (!okAdd) return false;
                vk_x = resAdd;
            }
            unchecked { ++i; }
        }

        // Negate point A for pairing: -A = (A.x, PRIME_Q - A.y)
        uint256[2] memory negA = [a[0], PRIME_Q - (a[1] % PRIME_Q)];

        // Build 24-word pairing input buffer for 0x08 precompile:
        uint256[24] memory pInput;
        pInput[0]  = negA[0];
        pInput[1]  = negA[1];
        pInput[2]  = b[0][0];
        pInput[3]  = b[0][1];
        pInput[4]  = b[1][0];
        pInput[5]  = b[1][1];

        pInput[6]  = _vk.alfa1[0];
        pInput[7]  = _vk.alfa1[1];
        pInput[8]  = _vk.beta2[0][0];
        pInput[9]  = _vk.beta2[0][1];
        pInput[10] = _vk.beta2[1][0];
        pInput[11] = _vk.beta2[1][1];

        pInput[12] = vk_x[0];
        pInput[13] = vk_x[1];
        pInput[14] = _vk.gamma2[0][0];
        pInput[15] = _vk.gamma2[0][1];
        pInput[16] = _vk.gamma2[1][0];
        pInput[17] = _vk.gamma2[1][1];

        pInput[18] = c[0];
        pInput[19] = c[1];
        pInput[20] = _vk.delta2[0][0];
        pInput[21] = _vk.delta2[0][1];
        pInput[22] = _vk.delta2[0][1]; // Real BN254 G2 coordinates
        pInput[23] = _vk.delta2[1][1];

        return _executePairing(pInput);
    }

    /**
     * @notice Specialized high-level entrypoint for forensic blind DNA match validation.
     * @param evidenceHash Keccak-256 / Poseidon hash commitment of crime-scene evidence profile.
     * @param matchThreshold Minimum matching allele count required for inclusion (e.g. 20 of 20 loci).
     * @param suspectCommitment Blinded Poseidon commitment of suspect profile.
     * @param a Proof coordinate A.
     * @param b Proof coordinate B.
     * @param c Proof coordinate C.
     * @return isValid True if the blind match is mathematically proven.
     */
    function verifyDnaMatchProof(
        bytes32 evidenceHash,
        uint256 matchThreshold,
        bytes32 suspectCommitment,
        uint256[2] calldata a,
        uint256[2][2] calldata b,
        uint256[2] calldata c
    ) external returns (bool isValid) {
        uint256[3] memory input = [
            uint256(evidenceHash) % PRIME_R,
            matchThreshold,
            uint256(suspectCommitment) % PRIME_R
        ];

        isValid = verifyProof(a, b, c, input);

        emit BlindMatchVerified(
            evidenceHash,
            matchThreshold,
            suspectCommitment,
            isValid,
            block.timestamp
        );
    }

    // ========================= Internal Safe EVM Precompiles =========================

    function _tryEcAdd(uint256 x1, uint256 y1, uint256 x2, uint256 y2) internal view returns (bool success, uint256[2] memory r) {
        uint256[4] memory input = [x1, y1, x2, y2];
        assembly {
            success := staticcall(sub(gas(), 2000), 0x06, input, 0x80, r, 0x40)
        }
    }

    function _tryEcMul(uint256 x, uint256 y, uint256 s) internal view returns (bool success, uint256[2] memory r) {
        uint256[3] memory input = [x, y, s];
        assembly {
            success := staticcall(sub(gas(), 2000), 0x07, input, 0x60, r, 0x40)
        }
    }

    function _executePairing(uint256[24] memory pInput) internal view returns (bool) {
        uint256[1] memory out;
        bool success;
        assembly {
            success := staticcall(sub(gas(), 2000), 0x08, pInput, 0x300, out, 0x20)
        }
        return success && (out[0] == 1);
    }

    /**
     * @dev Initializes canonical default Verifying Key parameters with valid BN254 generator points.
     */
    function _initializeDefaultVk() internal {
        // G1 Generator: (1, 2) on y^2 = x^3 + 3 mod q
        _vk.alfa1 = [1, 2];

        // G2 Generator
        _vk.beta2 = [
            [
                10857046999023057135944570762232829481370756359578518086990519993285655852781,
                11559732032986387107991004021392285728898690649194833212880795412886948034023
            ],
            [
                8495653923123431417604973242340164883936601470124922497496826418193398762949,
                4082367875863433681332203403145435568310553707240800912007957011216009152814
            ]
        ];

        _vk.gamma2 = _vk.beta2;
        _vk.delta2 = _vk.beta2;

        // Valid G1 multiples
        _vk.ic.push([1, 2]);
        _vk.ic.push([1, 2]);
        _vk.ic.push([1, 2]);
        _vk.ic.push([1, 2]);

        vkConfigured = true;
    }
}

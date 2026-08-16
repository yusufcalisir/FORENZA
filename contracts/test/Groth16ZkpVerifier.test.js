const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Groth16ZkpVerifier (FORENZA Module 27)", function () {
    let verifier;
    let owner;

    beforeEach(async function () {
        [owner] = await ethers.getSigners();
        const Groth16ZkpVerifier = await ethers.getContractFactory("Groth16ZkpVerifier");
        verifier = await Groth16ZkpVerifier.deploy();
        await verifier.waitForDeployment();
    });

    describe("Verifying Key Configuration", function () {
        it("should initialize with default Verifying Key configured", async function () {
            expect(await verifier.vkConfigured()).to.be.true;
        });

        it("should reject inputs exceeding scalar field Fr", async function () {
            const PRIME_R = BigInt("21888242871839275222246405745257275088548364400416034343698204186575808495617");
            const invalidInput = [PRIME_R + 1n, 20n, 12345n];

            const a = [1n, 2n];
            const b = [
                [10857046999023057135944570762232829481370756359578518086990519993285655852781n, 11559732032986387107991004021392285728898690649194833212880795412886948034023n],
                [8495653923123431417604973242340164883936601470124922497496826418193398762949n, 4082367875863433681332203403145435568310553707240800912007957011216009152814n]
            ];
            const c = [1n, 2n];

            const isValid = await verifier.verifyProof(a, b, c, invalidInput);
            expect(isValid).to.be.false;
        });

        it("should allow owner to update verifying key", async function () {
            const alfa1 = [1n, 2n];
            const beta2 = [
                [10857046999023057135944570762232829481370756359578518086990519993285655852781n, 11559732032986387107991004021392285728898690649194833212880795412886948034023n],
                [8495653923123431417604973242340164883936601470124922497496826418193398762949n, 4082367875863433681332203403145435568310553707240800912007957011216009152814n]
            ];
            const gamma2 = beta2;
            const delta2 = beta2;
            const ic = [[1n, 2n], [1n, 2n], [1n, 2n], [1n, 2n]];

            const tx = await verifier.setVerifyingKey(alfa1, beta2, gamma2, delta2, ic);
            await tx.wait();

            expect(await verifier.vkConfigured()).to.be.true;
        });

        it("should revert if IC length is less than 4", async function () {
            const alfa1 = [1n, 2n];
            const beta2 = [
                [1n, 2n],
                [3n, 4n]
            ];
            const gamma2 = beta2;
            const delta2 = beta2;
            const shortIc = [[1n, 2n], [1n, 2n]];

            await expect(
                verifier.setVerifyingKey(alfa1, beta2, gamma2, delta2, shortIc)
            ).to.be.revertedWith("Groth16ZkpVerifier: IC length must be at least 4 for 3 public signals");
        });
    });

    describe("verifyDnaMatchProof Entrypoint", function () {
        it("should emit BlindMatchVerified event", async function () {
            const evidenceHash = ethers.keccak256(ethers.toUtf8Bytes("EVIDENCE_STR_24_LOCI"));
            const matchThreshold = 20n;
            const suspectCommitment = ethers.keccak256(ethers.toUtf8Bytes("SUSPECT_POSEIDON_COMMITMENT"));

            const a = [1n, 2n];
            const b = [
                [10857046999023057135944570762232829481370756359578518086990519993285655852781n, 11559732032986387107991004021392285728898690649194833212880795412886948034023n],
                [8495653923123431417604973242340164883936601470124922497496826418193398762949n, 4082367875863433681332203403145435568310553707240800912007957011216009152814n]
            ];
            const c = [1n, 2n];

            const tx = await verifier.verifyDnaMatchProof(
                evidenceHash,
                matchThreshold,
                suspectCommitment,
                a,
                b,
                c
            );
            const receipt = await tx.wait();

            const event = receipt.logs.find(log => log.fragment && log.fragment.name === "BlindMatchVerified");
            expect(event).to.not.be.undefined;
        });
    });
});

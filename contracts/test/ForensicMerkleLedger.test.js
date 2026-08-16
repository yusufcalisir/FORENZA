const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("ForensicMerkleLedger (FORENZA Module 26)", function () {
    let ledger;
    let owner;
    let officer1;
    let officer2;

    beforeEach(async function () {
        [owner, officer1, officer2] = await ethers.getSigners();
        const ForensicMerkleLedger = await ethers.getContractFactory("ForensicMerkleLedger");
        ledger = await ForensicMerkleLedger.deploy();
        await ledger.waitForDeployment();
    });

    describe("Case Merkle Root Commitments", function () {
        it("should commit a valid case Merkle root commitment", async function () {
            const caseId = ethers.keccak256(ethers.toUtf8Bytes("CASE-2026-EU-01"));
            const merkleRoot = ethers.keccak256(ethers.toUtf8Bytes("MERKLE_ROOT_HASH_VECTOR_26"));
            const leafCount = 8;
            const metadataUri = "ipfs://QmForensicCaseDossier2026";

            const tx = await ledger.commitCaseMerkleRoot(caseId, merkleRoot, leafCount, metadataUri);
            const receipt = await tx.wait();

            expect(await ledger.totalCasesRegistered()).to.equal(1);

            const caseRecord = await ledger.cases(caseId);
            expect(caseRecord.merkleRoot).to.equal(merkleRoot);
            expect(caseRecord.leafCount).to.equal(leafCount);
            expect(caseRecord.metadataUri).to.equal(metadataUri);
            expect(caseRecord.registeredBy).to.equal(owner.address);
            expect(caseRecord.exists).to.be.true;
        });

        it("should revert if caseId is zero", async function () {
            const root = ethers.keccak256(ethers.toUtf8Bytes("ROOT"));
            await expect(
                ledger.commitCaseMerkleRoot(ethers.ZeroHash, root, 4, "ipfs://uri")
            ).to.be.revertedWith("ForensicMerkleLedger: invalid case ID");
        });

        it("should revert if leafCount is zero", async function () {
            const caseId = ethers.keccak256(ethers.toUtf8Bytes("CASE-02"));
            const root = ethers.keccak256(ethers.toUtf8Bytes("ROOT"));
            await expect(
                ledger.commitCaseMerkleRoot(caseId, root, 0, "ipfs://uri")
            ).to.be.revertedWith("ForensicMerkleLedger: leaf count must be > 0");
        });

        it("should revert if case is already committed", async function () {
            const caseId = ethers.keccak256(ethers.toUtf8Bytes("CASE-DUPLICATE"));
            const root = ethers.keccak256(ethers.toUtf8Bytes("ROOT"));

            await ledger.commitCaseMerkleRoot(caseId, root, 2, "ipfs://uri1");
            await expect(
                ledger.commitCaseMerkleRoot(caseId, root, 2, "ipfs://uri2")
            ).to.be.revertedWith("ForensicMerkleLedger: case root already committed");
        });
    });

    describe("Atomic Custody Event Logging", function () {
        it("should record a custody transition event on-chain", async function () {
            const caseId = ethers.keccak256(ethers.toUtf8Bytes("CASE-2026-AA-02"));
            const eventId = ethers.keccak256(ethers.toUtf8Bytes("EVENT-001-EXTRACTION"));
            const officerId = "ANALYST-MORRISON-994";
            const barcode = "TUBE-DNA-992144";
            const location = "PCR-CLEAN-ROOM-B";
            const priorHash = ethers.ZeroHash;

            const tx = await ledger.connect(officer1).recordCustodyEvent(
                caseId,
                eventId,
                officerId,
                barcode,
                location,
                priorHash
            );
            await tx.wait();

            expect(await ledger.totalEventsAnchored()).to.equal(1);
            expect(await ledger.getCaseEventCount(caseId)).to.equal(1);

            const eventRec = await ledger.getCaseEvent(caseId, 0);
            expect(eventRec.caseId).to.equal(caseId);
            expect(eventRec.eventId).to.equal(eventId);
            expect(eventRec.officer).to.equal(officer1.address);
            expect(eventRec.officerId).to.equal(officerId);
            expect(eventRec.sampleBarcode).to.equal(barcode);
        });
    });

    describe("O(log2 N) Merkle Proof Verification", function () {
        it("should verify a 4-leaf balanced Merkle tree inclusion proof", async function () {
            // Construct a 4-leaf tree: H0, H1, H2, H3
            const h0 = ethers.keccak256(ethers.toUtf8Bytes("LEAF_0_CRIME_SCENE_COLLECTION"));
            const h1 = ethers.keccak256(ethers.toUtf8Bytes("LEAF_1_COLD_CHAIN_TRANSPORT"));
            const h2 = ethers.keccak256(ethers.toUtf8Bytes("LEAF_2_DNA_EXTRACTION"));
            const h3 = ethers.keccak256(ethers.toUtf8Bytes("LEAF_3_CE_ELECTROPHORESIS"));

            // Level 1 parents
            const p0 = ethers.keccak256(ethers.concat([h0, h1]));
            const p1 = ethers.keccak256(ethers.concat([h2, h3]));

            // Root
            const root = ethers.keccak256(ethers.concat([p0, p1]));

            // Target leaf: H0 (index 0). Siblings: H1 (right, bit 0 = 0), P1 (right, bit 1 = 0).
            const siblings = [h1, p1];
            const pathBits = 0; // both siblings on right

            const isValid = await ledger.verifyInclusionProof(h0, siblings, pathBits, root);
            expect(isValid).to.be.true;
        });

        it("should verify leaf H2 with sibling path bits", async function () {
            const h0 = ethers.keccak256(ethers.toUtf8Bytes("LEAF_0"));
            const h1 = ethers.keccak256(ethers.toUtf8Bytes("LEAF_1"));
            const h2 = ethers.keccak256(ethers.toUtf8Bytes("LEAF_2"));
            const h3 = ethers.keccak256(ethers.toUtf8Bytes("LEAF_3"));

            const p0 = ethers.keccak256(ethers.concat([h0, h1]));
            const p1 = ethers.keccak256(ethers.concat([h2, h3]));
            const root = ethers.keccak256(ethers.concat([p0, p1]));

            // Target leaf: H2 (index 2).
            // First sibling: H3 (right -> bit 0 = 0)
            // Second sibling: P0 (left -> bit 1 = 1)
            // pathBits = 0b10 = 2
            const siblings = [h3, p0];
            const pathBits = 2;

            const isValid = await ledger.verifyInclusionProof(h2, siblings, pathBits, root);
            expect(isValid).to.be.true;
        });

        it("should reject tampered leaf hash", async function () {
            const h0 = ethers.keccak256(ethers.toUtf8Bytes("LEAF_GENUINE"));
            const h1 = ethers.keccak256(ethers.toUtf8Bytes("LEAF_1"));
            const p0 = ethers.keccak256(ethers.concat([h0, h1]));
            const root = p0;

            const tamperedLeaf = ethers.keccak256(ethers.toUtf8Bytes("LEAF_TAMPERED"));
            const isValid = await ledger.verifyInclusionProof(tamperedLeaf, [h1], 0, root);
            expect(isValid).to.be.false;
        });

        it("should verify proof against on-chain committed case", async function () {
            const h0 = ethers.keccak256(ethers.toUtf8Bytes("EVIDENCE_A"));
            const h1 = ethers.keccak256(ethers.toUtf8Bytes("EVIDENCE_B"));
            const root = ethers.keccak256(ethers.concat([h0, h1]));

            const caseId = ethers.keccak256(ethers.toUtf8Bytes("CASE-CHAIN-01"));
            await ledger.commitCaseMerkleRoot(caseId, root, 2, "ipfs://audit");

            const isValid = await ledger.verifyCaseInclusion.staticCall(caseId, h0, [h1], 0);
            expect(isValid).to.be.true;
        });
    });
});

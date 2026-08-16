const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("ForenzaAuditRegistry (FORENZA Pillar 6 Governance)", function () {
    let registry;
    let owner;
    let analyst;
    let auditor;
    let unauthorized;

    beforeEach(async function () {
        [owner, analyst, auditor, unauthorized] = await ethers.getSigners();
        const ForenzaAuditRegistry = await ethers.getContractFactory("ForenzaAuditRegistry");
        registry = await ForenzaAuditRegistry.deploy(owner.address);
        await registry.waitForDeployment();
    });

    describe("Access Control & Enrollment", function () {
        it("should enroll an accredited laboratory analyst", async function () {
            const role = await registry.LAB_ANALYST_ROLE();
            await registry.enrollInvestigator(
                analyst.address,
                "Dr. Marcus Alvarez",
                "Forensic Science Ireland",
                "ISO/IEC 17025:2017",
                role
            );

            const profile = await registry.investigators(analyst.address);
            expect(profile.name).to.equal("Dr. Marcus Alvarez");
            expect(profile.agency).to.equal("Forensic Science Ireland");
            expect(profile.accreditation).to.equal("ISO/IEC 17025:2017");
            expect(profile.status).to.equal(1); // ACTIVE (enum: 0=UNREGISTERED, 1=ACTIVE, 2=SUSPENDED, 3=REVOKED)
            expect(await registry.hasRole(role, analyst.address)).to.be.true;
        });

        it("should grant and validate an active session token", async function () {
            const role = await registry.LAB_ANALYST_ROLE();
            await registry.enrollInvestigator(
                analyst.address,
                "Dr. Marcus Alvarez",
                "FSI",
                "ISO/IEC 17025:2017",
                role
            );

            const sessionToken = ethers.keccak256(ethers.toUtf8Bytes("SESSION_SEC_TOKEN_99182"));
            await registry.grantSession(analyst.address, sessionToken, 3600);

            expect(await registry.isInvestigatorAuthorized(analyst.address)).to.be.true;
        });
    });

    describe("Audit Trail & Query Logging", function () {
        let sessionToken;

        beforeEach(async function () {
            const role = await registry.LAB_ANALYST_ROLE();
            await registry.enrollInvestigator(
                analyst.address,
                "Dr. Chen",
                "Interpol Lyon",
                "ISO/IEC 17025:2017",
                role
            );

            sessionToken = ethers.keccak256(ethers.toUtf8Bytes("SESSION_TOKEN_CHEN"));
            await registry.grantSession(analyst.address, sessionToken, 3600);
        });

        it("should allow authorized analyst to log a forensic DNA query", async function () {
            const profileHash = ethers.keccak256(ethers.toUtf8Bytes("DNA_PROFILE_HASH_EU_01"));
            const queryType = "STR_24_AUTOSOMAL_MATCH";

            const tx = await registry.connect(analyst).logQuery(queryType, profileHash, sessionToken);
            await tx.wait();

            expect(await registry.getLogCount()).to.equal(1);

            const entry = await registry.getLog(0);
            expect(entry.investigator).to.equal(analyst.address);
            expect(entry.queryType).to.equal(queryType);
            expect(entry.profileHash).to.equal(profileHash);
        });

        it("should reject query logging from unauthorized address", async function () {
            const profileHash = ethers.keccak256(ethers.toUtf8Bytes("DNA_PROFILE_HASH_EU_01"));
            await expect(
                registry.connect(unauthorized).logQuery("STR_QUERY", profileHash, sessionToken)
            ).to.be.revertedWith("ForenzaAuditRegistry: investigator not active");
        });

        it("should enforce rate limiting and auto-suspend after 5 bursts in 60s", async function () {
            const profileHash = ethers.keccak256(ethers.toUtf8Bytes("DNA_PROFILE_BURST"));
            
            // 5 legitimate calls
            for (let i = 0; i < 5; i++) {
                await registry.connect(analyst).logQuery("STR_BURST_QUERY", profileHash, sessionToken);
            }
            expect(await registry.getLogCount()).to.equal(5);

            // 6th call exceeds threshold, suspends investigator, and does not append to audit trail
            await registry.connect(analyst).logQuery("STR_BURST_QUERY", profileHash, sessionToken);
            expect(await registry.getLogCount()).to.equal(5);

            const prof = await registry.investigators(analyst.address);
            expect(prof.status).to.equal(2); // SUSPENDED

            // 7th call will now be rejected by modifier
            await expect(
                registry.connect(analyst).logQuery("STR_BURST_QUERY", profileHash, sessionToken)
            ).to.be.revertedWith("ForenzaAuditRegistry: investigator not active");
        });
    });

    describe("Emergency Lockdown Circuit Breaker", function () {
        it("should allow admin to trigger and lift global lockdown", async function () {
            await registry.triggerLockdown("Suspicious anomaly detected in regional enclave");
            expect(await registry.paused()).to.be.true;

            await registry.liftLockdown();
            expect(await registry.paused()).to.be.false;
        });
    });
});

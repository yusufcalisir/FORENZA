const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
    const [deployer] = await hre.ethers.getSigners();
    console.log("==================================================================");
    console.log("FORENZA Forensic Evidence Operating System — Contract Deployment");
    console.log("Deployer account:", deployer.address);
    console.log("Network:", hre.network.name);
    console.log("==================================================================");

    // 1. Deploy ForenzaAuditRegistry
    console.log("\n[1/3] Deploying ForenzaAuditRegistry (ISO 17025 RBAC & Audit Trail)...");
    const ForenzaAuditRegistry = await hre.ethers.getContractFactory("ForenzaAuditRegistry");
    const auditRegistry = await ForenzaAuditRegistry.deploy(deployer.address);
    await auditRegistry.waitForDeployment();
    const auditRegistryAddress = await auditRegistry.getAddress();
    console.log("-> ForenzaAuditRegistry deployed to:", auditRegistryAddress);

    // 2. Deploy ForensicMerkleLedger (Module 26)
    console.log("\n[2/3] Deploying ForensicMerkleLedger (Module 26 Merkle Chain of Custody)...");
    const ForensicMerkleLedger = await hre.ethers.getContractFactory("ForensicMerkleLedger");
    const merkleLedger = await ForensicMerkleLedger.deploy();
    await merkleLedger.waitForDeployment();
    const merkleLedgerAddress = await merkleLedger.getAddress();
    console.log("-> ForensicMerkleLedger deployed to:", merkleLedgerAddress);

    // 3. Deploy Groth16ZkpVerifier (Module 27)
    console.log("\n[3/3] Deploying Groth16ZkpVerifier (Module 27 BN254 Pairings Verifier)...");
    const Groth16ZkpVerifier = await hre.ethers.getContractFactory("Groth16ZkpVerifier");
    const zkpVerifier = await Groth16ZkpVerifier.deploy();
    await zkpVerifier.waitForDeployment();
    const zkpVerifierAddress = await zkpVerifier.getAddress();
    console.log("-> Groth16ZkpVerifier deployed to:", zkpVerifierAddress);

    // Save deployed contract addresses to file
    const deploymentRecord = {
        network: hre.network.name,
        timestamp: new Date().toISOString(),
        deployer: deployer.address,
        contracts: {
            ForenzaAuditRegistry: auditRegistryAddress,
            ForensicMerkleLedger: merkleLedgerAddress,
            Groth16ZkpVerifier: zkpVerifierAddress
        }
    };

    const outPath = path.join(__dirname, "../deployed_addresses.json");
    fs.writeFileSync(outPath, JSON.stringify(deploymentRecord, null, 2));
    console.log("\nDeployment addresses saved to:", outPath);
    console.log("==================================================================");
    console.log("Deployment completed successfully.");
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});

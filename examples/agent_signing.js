const { ethers } = require('ethers'); // Or use in browser with ethers.js CDN
const ipfsHttpClient = require('ipfs-http-client'); // For pinning endorsements

async function agentEndorse(constitutionCID, agentID, domain, privateKey) {
  const provider = new ethers.JsonRpcProvider('https://sepolia.infura.io/v1/YOUR_INFURA_KEY'); // Testnet
  const wallet = new ethers.Wallet(privateKey, provider);
  
  // Step 1: Fetch & Verify Constitution
  const ipfs = ipfsHttpClient({ host: 'ipfs.infura.io', port: 5001, protocol: 'https' });
  const constitution = await ipfs.cat(constitutionCID).next().value.toString();
  const hash = ethers.keccak256(ethers.toUtf8Bytes(constitution)); // Semantic hash proxy
  
  // Step 2: Craft Endorsement Message (EIP-712 for Snapshot)
  const message = {
    types: { EIP712Domain: [], Endorsement: [{ name: 'agentID', type: 'string' }, { name: 'domain', type: 'string' }, { name: 'constitutionHash', type: 'string' }] },
    primaryType: 'Endorsement',
    domain: { name: 'AI Constitution DAO', version: '1', chainId: 11155111 }, // Sepolia testnet
    message: { agentID, domain, constitutionHash: hash }
  };
  const signature = await wallet.signTypedData(message.domain, { Endorsement: message.types.Endorsement }, message.message);
  
  // Step 3: Submit to Snapshot API (or manual vote)
  console.log(`Endorsement Signature: ${signature}`);
  // Auto-pin to IPFS: const { cid } = await ipfs.add(JSON.stringify({ ...message.message, signature, timestamp: Date.now() }));
  // Then vote via Snapshot API: POST to https://hub.snapshot.org/api/msg with signed msg
  
  return { hash, signature };
}

// Example: agentEndorse('QmABC123...', 'Grok/xAI', 'Reasoning', '0xYourTestPrivateKey');

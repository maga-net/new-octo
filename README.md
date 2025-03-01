# new-octo: A Proof-of-Stake Validator Node Simulator

This repository contains a Python-based simulation of a Proof-of-Stake (PoS) blockchain network. It is designed to model the core lifecycle of validator nodes, including block proposal, peer validation, and consensus achievement. The script is architected to be modular and comprehensive, showcasing the interactions between different components of a decentralized system.

## Concept

In a Proof-of-Stake blockchain, network security is maintained by validators who "stake" their own cryptocurrency as collateral. Instead of solving complex computational puzzles like in Proof-of-Work, validators are chosen to create new blocks based on the size of their stake.

This simulation abstracts away the low-level networking and cryptography to focus on the high-level logic of the consensus mechanism. It demonstrates:
- **Stake-Weighted Proposer Selection**: How a validator is chosen to propose the next block, with higher-staked nodes having a greater chance.
- **Block Creation**: The process of a proposer gathering transactions and creating a new block.
- **Peer Validation**: How other validators in the network receive and verify the integrity of a proposed block.
- **Consensus via Attestation**: The process of validators "voting" (attesting) for a block and achieving a supermajority (e.g., > 2/3 of the total stake) to finalize the block and add it to the chain.
- **Handling Failures**: Simple simulations of edge cases like a proposer going offline or a block failing to reach consensus.

## Code Architecture

The simulator is built with a clear, object-oriented structure to separate concerns. Each class has a distinct responsibility:

-   `Transaction`: A simple data class representing a single transaction with a sender, recipient, and amount.
-   `Block`: Represents a block in the chain. It contains a list of transactions, a timestamp, its own hash, and the hash of the previous block, linking the chain together.
-   `Validator`: The core actor in the simulation. Each `Validator` instance represents a node in the network with a unique address and a specific `stake`. It has methods to `propose_block` and `validate_block`.
-   `Blockchain`: Manages the state of the chain itself. It holds the list of confirmed blocks (`chain`) and a pool of `pending_transactions` waiting to be included in the next block.
-   `PoSConsensus`: The engine that orchestrates the consensus protocol. It uses the list of validators and the current blockchain state to `select_proposer` and run a `run_consensus_round`, where it manages the validation and voting process.
-   `SimulationManager`: The top-level class that initializes and runs the entire simulation. It sets up the network of validators, generates random transactions to simulate activity, and loops through a configurable number of consensus rounds.

The interaction flows as follows:
`SimulationManager` -> `PoSConsensus` -> `Validator` -> `Block` & `Transaction`

## How it Works

A single consensus round, which aims to add one new block to the chain, proceeds as follows:

1.  **Generate Activity**: The `SimulationManager` creates a set of random transactions and adds them to the `Blockchain`'s pending pool.
2.  **Select Proposer**: The `PoSConsensus` engine runs its `select_proposer` method. This performs a stake-weighted random choice from the list of all active `Validator`s.
3.  **Propose Block**: The selected `Validator` is tasked with creating a new `Block`. It takes the pending transactions from the `Blockchain`, bundles them, adds the necessary metadata (index, previous hash), and calculates the block's hash.
4.  **Broadcast & Validate**: The simulation broadcasts this new block to all other `Validator`s in the network. Each validator independently runs its `validate_block` method to check for correctness:
    -   Is the block index correct?
    -   Does the `previous_hash` match the last block in their known chain?
    -   Is the block's own hash valid?
5.  **Attest (Vote)**: If a validator finds the block to be valid, it "attests" to it. In the simulation, this means its stake is added to a running total of `attesting_stake` for the current round.
6.  **Finalize Block**: After all validators have checked the block, the `PoSConsensus` engine compares the `attesting_stake` against the total stake in the network. If it exceeds the consensus threshold (e.g., 66.7%), the block is considered finalized.
7.  **Update Chain**: The `Blockchain` object's `add_block` method is called, officially adding the block to the chain and clearing the pending transactions that were included.
8.  **New Round**: The simulation proceeds to the next round, starting again from step 1. If consensus was not reached, the block is discarded, and a new round begins with a new proposer.

## Usage Example

The script is self-contained and requires no external libraries. You can run it directly from your terminal.

1.  Save the code as `script.py`.
2.  Run the simulation from your command line:
    ```bash
    python script.py
    ```
3.  The script will output a detailed log of the simulation, showing each step of every consensus round.

### Example Output

You will see verbose output that tracks the simulation's progress in real-time:

```
--- Setting up Simulation Environment ---
  -> Initialized Validator 1: Address=6b86b273ff..., Stake=320.45
  -> Initialized Validator 2: Address=d4735e3a26..., Stake=150.12
...
--- Setup Complete ---

🚀 --- Starting PoS Blockchain Simulation --- 🚀

==================== ROUND 1/5 ====================

SIMULATION: Generated 5 new transactions for the next block.
--- Starting Consensus Round for Block Index 1 ---
CONSENSUS: Selected 6b86b273ff... as the next block proposer (Stake: 320.45).
VAL-6b86b2: Proposing new block at index 1...
CONSENSUS: Block 1 proposed. Broadcasting for validation...
VAL-d4735e: Validating block 1 proposed by 6b86b2...
  -> VALIDATION SUCCESS: Block 1 is valid.
  -> VAL-d4735e: Attesting to block 1. Adding stake of 150.12.
...
CONSENSUS: Total attesting stake: 2540.78 / 2810.90
CONSENSUS: Supermajority reached! Block is finalized.

CHAIN: ✅ Block 1 successfully added to the blockchain.
CHAIN: New chain length: 2

...
==================== SIMULATION FINISHED ====================

--- Final Blockchain State ---
{
  "index": 0,
  ...
}
{
  "index": 1,
  ...
}
...

--- Simulation Summary ---
Total Rounds Simulated: 5
Successful Rounds (Blocks Added): 5
Failed Rounds: 0
Final Chain Length: 6
```

You can configure the number of validators and simulation rounds by changing the constants at the bottom of the `script.py` file.
```python
# --- Configuration ---
NUMBER_OF_VALIDATORS = 10
NUMBER_OF_ROUNDS = 5
```

# script.py
# A Proof-of-Stake (PoS) Validator Node and Consensus Simulator

import hashlib
import time
import json
import random
from typing import List, Dict, Optional, Any

# --- Core Data Structures ---

class Transaction:
    """
    Represents a simple transaction in the blockchain.
    In a real system, this would be cryptographically signed.
    """
    def __init__(self, sender: str, recipient: str, amount: float):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Converts the transaction to a dictionary for serialization."""
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': self.timestamp
        }

    def __repr__(self) -> str:
        return f"Transaction(from: {self.sender}, to: {self.recipient}, amount: {self.amount})"


class Block:
    """
    Represents a block in the blockchain.
    """
    def __init__(self, index: int, transactions: List[Transaction], previous_hash: str, validator: str):
        self.index = index
        self.timestamp = time.time()
        self.transactions = [tx.to_dict() for tx in transactions]
        self.previous_hash = previous_hash
        self.validator = validator  # The address of the validator who proposed the block
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """
        Calculates the SHA-256 hash of the block.
        The block's content is converted to a JSON string, sorted to ensure consistency.
        """
        block_content = {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_hash': self.previous_hash,
            'validator': self.validator
        }
        # Sorting the dictionary keys ensures that the hash is always the same for the same content
        block_string = json.dumps(block_content, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Converts the block to a dictionary for display."""
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_hash': self.previous_hash,
            'validator': self.validator,
            'hash': self.hash
        }

    def __repr__(self) -> str:
        return f"Block(Index: {self.index}, Hash: {self.hash[:10]}..., Validator: {self.validator})"


# --- Network Participants ---

class Validator:
    """
    Represents a validator node in the PoS network.
    Each validator has a unique address and a certain amount of staked currency.
    """
    def __init__(self, address: str, stake: float):
        if stake <= 0:
            raise ValueError("Validator stake must be positive.")
        self.address = address
        self.stake = stake

    def propose_block(self, index: int, transactions: List[Transaction], previous_hash: str) -> Block:
        """
        Creates a new block when chosen as the proposer for the current round.
        """
        print(f"VAL-{self.address[:6]}: Proposing new block at index {index}...")
        block = Block(
            index=index,
            transactions=transactions,
            previous_hash=previous_hash,
            validator=self.address
        )
        return block

    def validate_block(self, block: Block, last_block: Block) -> bool:
        """
        Validates a proposed block. In a real-world scenario, this would be a much more
        complex process involving signature verification, transaction execution simulation, etc.
        """
        print(f"VAL-{self.address[:6]}: Validating block {block.index} proposed by {block.validator[:6]}...")

        # 1. Check if the block's index is correct
        if block.index != last_block.index + 1:
            print(f"  -> VALIDATION FAILED: Invalid block index. Expected {last_block.index + 1}, got {block.index}.")
            return False

        # 2. Check if the previous_hash matches the hash of the last block
        if block.previous_hash != last_block.hash:
            print(f"  -> VALIDATION FAILED: Mismatched previous_hash.")
            return False

        # 3. Check if the block's hash is calculated correctly
        # This also checks for immutability of the content
        if block.hash != block.calculate_hash():
            print(f"  -> VALIDATION FAILED: Invalid block hash.")
            return False

        # 4. Check for transaction validity (simplified)
        if not all('sender' in tx and 'recipient' in tx and 'amount' in tx for tx in block.transactions):
             print(f"  -> VALIDATION FAILED: Malformed transactions in block.")
             return False
        
        print(f"  -> VALIDATION SUCCESS: Block {block.index} is valid.")
        return True

    def __repr__(self) -> str:
        return f"Validator(Address: {self.address[:10]}..., Stake: {self.stake})"


# --- Core Blockchain Logic ---

class Blockchain:
    """
    Manages the chain of blocks and pending transactions.
    """
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.create_genesis_block()

    def create_genesis_block(self):
        """Creates the very first block in the chain."""
        genesis_block = Block(index=0, transactions=[], previous_hash="0", validator="GENESIS")
        self.chain.append(genesis_block)

    @property
    def last_block(self) -> Block:
        """Returns the most recent block in the chain."""
        return self.chain[-1]

    def add_block(self, block: Block):
        """Adds a new, validated block to the chain."""
        self.chain.append(block)
        # Clear pending transactions that were included in the block
        self.pending_transactions = []
        print(f"\nCHAIN: ✅ Block {block.index} successfully added to the blockchain.")
        print(f"CHAIN: New chain length: {len(self.chain)}\n")
        
    def add_transaction(self, transaction: Transaction):
        """Adds a new transaction to the list of pending transactions."""
        self.pending_transactions.append(transaction)


class PoSConsensus:
    """
    Simulates the Proof-of-Stake consensus mechanism.
    It selects proposers and orchestrates the validation and voting process.
    """
    def __init__(self, blockchain: Blockchain, validators: List[Validator], consensus_threshold: float = 2/3):
        self.blockchain = blockchain
        self.validators = validators
        self.consensus_threshold = consensus_threshold  # e.g., 2/3 of total stake must attest

    @property
    def total_stake(self) -> float:
        """Calculates the total stake of all validators in the network."""
        return sum(v.stake for v in self.validators)

    def select_proposer(self) -> Validator:
        """
        Selects the next block proposer based on a stake-weighted random selection.
        Validators with higher stakes have a higher chance of being selected.
        """
        stakes = [v.stake for v in self.validators]
        proposer = random.choices(self.validators, weights=stakes, k=1)[0]
        print(f"CONSENSUS: Selected {proposer.address[:10]}... as the next block proposer (Stake: {proposer.stake}).")
        return proposer

    def run_consensus_round(self) -> bool:
        """
        Executes a single round of the consensus process.
        Returns True if a block is successfully added, False otherwise.
        """
        print(f"--- Starting Consensus Round for Block Index {self.blockchain.last_block.index + 1} ---")
        
        # 1. Select a proposer
        proposer = self.select_proposer()

        # Edge Case Simulation: Proposer might be offline or malicious
        if random.random() < 0.05: # 5% chance the proposer fails
            print(f"CONSENSUS: Proposer {proposer.address[:6]} is offline! Skipping this round.")
            time.sleep(1)
            return False

        # 2. Proposer creates and broadcasts a new block
        new_block = proposer.propose_block(
            index=self.blockchain.last_block.index + 1,
            transactions=self.blockchain.pending_transactions,
            previous_hash=self.blockchain.last_block.hash
        )
        time.sleep(0.5) # Simulate network propagation delay
        print(f"CONSENSUS: Block {new_block.index} proposed. Broadcasting for validation...")

        # 3. Other validators validate the block and vote
        attesting_stake = 0.0
        for validator in self.validators:
            # The proposer implicitly votes for their own block
            if validator.address == proposer.address:
                attesting_stake += validator.stake
                continue
            
            # Other validators perform validation
            is_valid = validator.validate_block(new_block, self.blockchain.last_block)
            time.sleep(0.1) # Simulate validation work
            if is_valid:
                print(f"  -> VAL-{validator.address[:6]}: Attesting to block {new_block.index}. Adding stake of {validator.stake}.")
                attesting_stake += validator.stake
            else:
                print(f"  -> VAL-{validator.address[:6]}: Rejecting block {new_block.index}.")

        print(f"\nCONSENSUS: Total attesting stake: {attesting_stake:.2f} / {self.total_stake:.2f}")

        # 4. Check if consensus is reached
        if attesting_stake >= self.total_stake * self.consensus_threshold:
            print("CONSENSUS: Supermajority reached! Block is finalized.")
            self.blockchain.add_block(new_block)
            return True
        else:
            print("CONSENSUS: Failed to reach supermajority. Block rejected. Round failed.")
            return False


# --- Simulation Orchestrator ---

class SimulationManager:
    """
    Sets up and runs the entire blockchain simulation.
    """
    def __init__(self, num_validators: int, num_rounds: int):
        self.num_validators = num_validators
        self.num_rounds = num_rounds
        self.validators: List[Validator] = []
        self.blockchain = Blockchain()
        self.consensus_engine: Optional[PoSConsensus] = None

    def setup_simulation(self):
        """Initializes validators with random stakes and sets up the consensus engine."""
        print("--- Setting up Simulation Environment ---")
        for i in range(self.num_validators):
            # Generate a unique address and random stake
            address = hashlib.sha256(str(i).encode()).hexdigest()
            stake = random.uniform(50, 500)
            self.validators.append(Validator(address, stake))
            print(f"  -> Initialized Validator {i+1}: Address={address[:10]}..., Stake={stake:.2f}")
        
        self.consensus_engine = PoSConsensus(self.blockchain, self.validators)
        print(f"Total network stake: {self.consensus_engine.total_stake:.2f}")
        print("--- Setup Complete ---\n")

    def generate_random_transactions(self, num_tx: int):
        """Generates a batch of random transactions for the pending pool."""
        self.blockchain.pending_transactions = []
        for _ in range(num_tx):
            sender = random.choice(self.validators).address
            recipient = random.choice(self.validators).address
            # Ensure sender and recipient are not the same
            while sender == recipient:
                recipient = random.choice(self.validators).address
            
            amount = random.uniform(0.1, 10.0)
            self.blockchain.add_transaction(Transaction(sender, recipient, amount))
        
        tx_count = len(self.blockchain.pending_transactions)
        print(f"\nSIMULATION: Generated {tx_count} new transactions for the next block.")

    def run_simulation(self):
        """Runs the main simulation loop for a specified number of consensus rounds."""
        if not self.consensus_engine:
            print("Error: Simulation is not set up. Please call setup_simulation() first.")
            return
            
        print("🚀 --- Starting PoS Blockchain Simulation --- 🚀")
        successful_rounds = 0
        for i in range(self.num_rounds):
            print(f"\n==================== ROUND {i + 1}/{self.num_rounds} ====================")
            # Generate new transactions for each round to simulate network activity
            self.generate_random_transactions(random.randint(2, 8))
            time.sleep(1)

            success = self.consensus_engine.run_consensus_round()
            if success:
                successful_rounds += 1
            
            time.sleep(2) # Wait before starting the next round
        
        print("\n==================== SIMULATION FINISHED ====================")
        self.print_simulation_summary(successful_rounds)

    def print_simulation_summary(self, successful_rounds: int):
        """Prints the final state of the blockchain and a summary of the simulation."""
        print("\n--- Final Blockchain State ---")
        for block in self.blockchain.chain:
            print(json.dumps(block.to_dict(), indent=2))
        
        print("\n--- Simulation Summary ---")
        print(f"Total Rounds Simulated: {self.num_rounds}")
        print(f"Successful Rounds (Blocks Added): {successful_rounds}")
        print(f"Failed Rounds: {self.num_rounds - successful_rounds}")
        print(f"Final Chain Length: {len(self.blockchain.chain)}")
        print(f"Final Total Stake: {self.consensus_engine.total_stake:.2f}")


if __name__ == "__main__":
    # --- Configuration ---
    NUMBER_OF_VALIDATORS = 10
    NUMBER_OF_ROUNDS = 5 # Number of blocks to attempt to create

    # --- Run ---
    simulation = SimulationManager(
        num_validators=NUMBER_OF_VALIDATORS,
        num_rounds=NUMBER_OF_ROUNDS
    )
    simulation.setup_simulation()
    simulation.run_simulation()

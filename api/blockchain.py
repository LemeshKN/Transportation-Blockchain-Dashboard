# ------------------------------
# 1️⃣ Fix 1: Import missing libraries
# ------------------------------
import hashlib
import json
import os 
from time import time

# ------------------------------
# 2️⃣ Fix 2: Improved Block Class
# ------------------------------
class Block:
    def __init__(self, index, timestamp, delay_data, previous_hash):
        """
        ✅ Fixed: Now calculates hash BEFORE storing it in the block
        """
        self.index = index
        self.timestamp = timestamp
        self.delay_data = delay_data
        self.previous_hash = previous_hash
        self.hash = self.compute_hash()  # Hash calculation moved here

    def compute_hash(self):
        """
        ✅ Fixed: Removed self.hash from hashing calculation
        """
        # Create a copy of the object's dictionary without 'hash'
        block_data = self.__dict__.copy()
        block_data.pop('hash', None)  # Remove hash if exists
        
        return hashlib.sha256(
            json.dumps(block_data, sort_keys=True).encode()
        ).hexdigest()

    def __repr__(self):
        return f"Block #{self.index} | Hash: {self.hash[:10]}..."

# ------------------------------
# 3️⃣ Fix 3: Improved Blockchain Class
# ------------------------------

class TransportationBlockchain:
    def __init__(self):
        self.chain = []
        self.load_chain()  # Load existing blockchain data
        
        if not self.chain:
            self.create_genesis_block()

    def create_genesis_block(self):
        genesis_data = {
            "message": "Genesis Block - Start of Delay Tracking"
        }
        genesis_block_data = {
            "index": 0,
            "timestamp": time(),  # Use time() instead of time.time()
            "delay_data": genesis_data,
            "previous_hash": "0"
        }
        genesis_block = {
            **genesis_block_data,
            "hash": self.calculate_hash(genesis_block_data)
        }
        self.chain.append(genesis_block)
        self.save_chain()

    def save_chain(self):
        """Persist blockchain to file"""
        with open("blockchain_data.json", "w") as f:
            json.dump(self.chain, f, indent=4)

    def load_chain(self):
        """Load blockchain from file if exists"""
        if os.path.exists("blockchain_data.json"):
            with open("blockchain_data.json", "r") as f:
                self.chain = json.load(f)
            # Ensure it's a list, not a dictionary
            if not isinstance(self.chain, list):
                self.chain = []    

    def calculate_hash(self, block_data):
        """Generate SHA-256 hash for block data"""
        block_string = json.dumps(block_data, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def add_delay_record(self, delay_data):
        """Add new delay record with validation"""
        required_fields = ["location", "route", "delay_minutes"]
        if not all(field in delay_data for field in required_fields):
            raise ValueError(f"Missing required fields: {required_fields}")
        
        # Ensure there is at least one block
        if not self.chain:
            self.create_genesis_block()

        prev_block = self.chain[-1]
        
        new_block_data = {
            "index": len(self.chain),
            "timestamp": time(),  # Use time() instead of time.time()
            "delay_data": delay_data,
            "previous_hash": prev_block["hash"]
        }
        
        new_block = {
            **new_block_data,
            "hash": self.calculate_hash(new_block_data)
        }
        
        self.chain.append(new_block)
        self.save_chain()
        return new_block

    def is_chain_valid(self):
        """
          ✅ Checks if the blockchain is valid (no data has been tampered with).
        """
        for i in range(1, len(self.chain)):  # Start from second block (skip genesis)
            current_block = self.chain[i]  # Dictionary
            previous_block = self.chain[i - 1]  # Dictionary

             # Recalculate hash of current block using its data
            block_data = {
            "index": current_block["index"],
            "timestamp": current_block["timestamp"],
            "delay_data": current_block["delay_data"],
            "previous_hash": current_block["previous_hash"]
            }
            recalculated_hash = self.calculate_hash(block_data)

            # Check if stored hash matches recalculated hash
            if current_block["hash"] != recalculated_hash:
               return False  # Data has been tampered with!

            # Check if previous_hash matches actual hash of previous block
            if current_block["previous_hash"] != previous_block["hash"]:
                return False  # Blockchain is broken!

        return True  # Blockchain is valid 

# ------------------------------
# 4️⃣ Fix 4: Improved Testing Section
# ------------------------------
if __name__ == "__main__":
    # Initialize blockchain
    delay_chain = TransportationBlockchain()

    # Add sample records
    try:
        delay_chain.add_delay_record({
            "location": "Central Station",
            "route": "Bus-5A",
            "delay_minutes": 15
        })
        
        delay_chain.add_delay_record({
            "location": "North Terminal",
            "route": "Metro-Line-2",
            "delay_minutes": 8
        })
    except ValueError as e:
        print(f"Error: {e}")

    # Print blockchain
    print("\n🔗 Transportation Delay Blockchain:")
    for block in delay_chain.chain:
        print(f"""
        Block {block.index}
        Timestamp: {block.timestamp}
        Data: {block.delay_data}
        Previous Hash: {block.previous_hash[:8]}...
        Current Hash: {block.hash[:8]}...
        """)
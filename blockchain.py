from functools import reduce

import hashlib as hl
import json
import pickle

from utility.hash_util    import hash_block
from block        import Block
from transaction  import Transaction
from verification import Verification

# The reward we give to miners (for creating a new block)
MINING_REWARD = 10


class Blockchain:

    def __init__(self, hosting_node_id):
        genesis_block = Block(0, '', [], 0, 0)
        self.chain = [genesis_block]
        self.open_transactions = []
        self.load_data()
        self.hosting_node = hosting_node_id


    def load_data(self) -> None:
        try:
            with open('blockchain.txt', mode='r') as f:
                file_content = f.readlines()
                blockchain = json.loads(file_content[0][:-1])
                # convert transactions to OrderedDict
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(
                        tx['sender'], tx['recipient'], tx['amount']) for tx in block['transactions']]
                    updated_block = Block(
                        block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain
                open_transactions = json.loads(file_content[1])
                # again, convert transactions to OrderedDict
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(
                        tx['sender'], tx['recipient'], tx['amount'])
                    updated_transactions.append(updated_transaction)
                self.open_transactions = updated_transactions
        except (IOError, IndexError):
            pass


    def save_data(self) -> None:
        try:
            with open('blockchain.txt', mode='w') as f:
            	# cycle through all attribute for each block in chain
            	#	cycling through all transactions for each block
                saveable_chain = [block.__dict__ for block in 
                				 [Block(block_elt.index, block_elt.previous_hash, 
                				 	[tx.__dict__ for tx in block_elt.transactions], block_elt.proof, block_elt.timestamp) 
                				 		for block_elt in self.chain]]
                f.write(json.dumps(saveable_chain))
                f.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.open_transactions]
                f.write(json.dumps(saveable_tx))
        except IOError:
            print('Saving Failed!')


    def proof_of_work(self) -> int:
        '''
		Guess proof of work numbers until a valid proof is found.
        '''
        last_block = self.chain[-1]
        last_hash = hash_block(last_block)
        proof = 0

        while not Verification.valid_proof(self.open_transactions, last_hash, proof):
            proof += 1
        return proof


    def get_balance(self) -> float:
        user = self.hosting_node

        tx_sender = [[tx.amount for tx in block.transactions
                      if tx.sender == user] for block in self.chain]
        open_tx_sender = [tx.amount
                          for tx in self.open_transactions if tx.sender == user]
        tx_sender.append(open_tx_sender)

        amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt)
                             if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)

        tx_recipient = [[tx.amount for tx in block.transactions
                         if tx.recipient == user] for block in self.chain]

        amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt)
                                 if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)

        return amount_received - amount_sent


    def get_last_blockchain_value(self) -> Block:
        if len(self.chain) < 1:
            return None
        return self.chain[-1]


    def add_transaction(self, recipient: str, sender:str , amount: float=0.0) -> bool:
        # transaction = {
        #     'sender': sender,
        #     'recipient': recipient,
        #     'amount': amount
        # }
        transaction = Transaction(sender, recipient, amount)

        if Verification.verify_transaction(transaction, self.get_balance):
            self.open_transactions.append(transaction)
            self.save_data()

            return True

        return False


    def mine_block(self) -> bool:
        last_block = self.chain[-1]

        # include previous blocks hash
        hashed_block = hash_block(last_block)

        # generate proof of work
        proof = self.proof_of_work()
        # reward_transaction = {
        #     'sender': 'MINING',
        #     'recipient': owner,
        #     'amount': MINING_REWARD
        # }
        reward_transaction = Transaction(
            'MINING', self.hosting_node, MINING_REWARD)
        # Making a copy ensures tyhat if mining fails, reward isn't stored in the open transactions
        copied_transactions = self.open_transactions[:]
        copied_transactions.append(reward_transaction)

        block = Block(len(self.chain), hashed_block,
                      copied_transactions, proof)

        self.chain.append(block)
        # clear now processed transactions
        self.open_transactions = []
        # always save after mining new block
        self.save_data()

        return True

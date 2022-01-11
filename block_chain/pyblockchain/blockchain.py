import re
import sys
import logging
import time
import hashlib
import json

import utils

MINING_DIFFCULTY = 3
MINING_SENDER = 'THE BLOCKCHAIN'
MINING_REWARD = 1.0

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

class BlockChain(object):
    def __init__(self, blockchain_address=None) -> None:
        self.transaction_pool = []
        self.chain = []
        self.create_block(0, self.hash({}))
        self.blockchain_address = blockchain_address
    
    def create_block(self, nonce, previous_hash):
        block = utils.sorted_dict_by_key({
            'timestamp': time.time(),
            'transaction': self.transaction_pool,
            'nonce': nonce,
            'previous_hash': previous_hash,
        })
        self.chain.append(block)
        
        self.transaction_pool = []
        return block
    
    def hash(self, block):
        sorted_block = json.dumps(block, sort_keys=True)
        return hashlib.sha256(sorted_block.encode()).hexdigest()
    
    def add_transaction(self, sender_blockchain_address, recipient_blockchain_address, value):
        transaction = utils.sorted_dict_by_key({
            'sender_blockchain_address': sender_blockchain_address,
            'recipient_blockchain_address': recipient_blockchain_address,
            'value': float(value)
        })
        self.transaction_pool.append(transaction)
        return True
    
    def valid_proof(self, transaction, previous_hash, nonce, difficulty=MINING_DIFFCULTY):
        guess_block = utils.sorted_dict_by_key({
            'transaction': transaction,
            'previous_hash': previous_hash,
            'nonce': nonce 
        })
        
        guess_hash = self.hash(guess_block)
        return guess_hash[:difficulty] == '0'*difficulty
    
    def proof_of_work(self):
        transaction = self.transaction_pool.copy()
        previous_hash = self.hash(self.chain[-1])
        nonce = 0
        while self.valid_proof(transaction, previous_hash, nonce) == False:
            nonce += 1
        return nonce
    
    def mining(self):
        self.add_transaction(
            sender_blockchain_address=MINING_SENDER,
            recipient_blockchain_address=self.blockchain_address,
            value=MINING_REWARD)
        nonce = self.proof_of_work()
        previou_hash = self.hash(self.chain[-1])
        self.create_block(nonce, previou_hash)
        logger.info({'action': 'mining', 'state': 'success'})
        return True
    
    def calculate_total_amount(self, blockchain_address):
        total_amount = 0.0
        for block in self.chain:
            for transaction in block['transaction']:
                if transaction['recipient_blockchain_address'] == blockchain_address:
                    total_amount += transaction['value']
                elif transaction['sender_blockchain_address'] == blockchain_address:
                    total_amount -= transaction['value']
        
        return total_amount

if __name__ == '__main__':
    my_blockchain_address = 'my blockchain address'
    block_chain = BlockChain(blockchain_address=my_blockchain_address)
    
    block_chain.add_transaction('A', 'B', '1.0')
    block_chain.mining()
        
    block_chain.add_transaction('C', 'D', '2.0')
    block_chain.add_transaction('X', 'Y', '3.0')    
    block_chain.mining()
    
    utils.pprint(block_chain.chain)
    
    print('my', block_chain.calculate_total_amount(my_blockchain_address))
    print('C', block_chain.calculate_total_amount('C'))
    print('D', block_chain.calculate_total_amount('D'))
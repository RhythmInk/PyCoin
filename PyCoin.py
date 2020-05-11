from collections import OrderedDict

import hashlib
import json

from utility.hash_util import hash_string_512, hash_block

MINING_REWARD = 10

blockchain = []
open_transactions = []
owner = 'Aaron'
participants = {'Aaron'}


def load_data():
    '''
    Reinstantiates blockchain and open transactions.
    Loads all data from json file and then recreates ordered dictionaries for all
    transactions to ensure future hashes match previous ones.
    '''
    global blockchain
    global open_transactions

    try:
        with open('blockchain.txt', mode='r') as f:
            file_content = f.readlines()
            blockchain = json.loads(file_content[0][:-1])
            # Convert loaded data; Transactions should use OrderedDict for consistent hashing
            updated_blockchain = []
            for block in blockchain:
                updated_block = {
                    'previous_hash': block['previous_hash'],
                    'index': block['index'],
                    'proof': block['proof'],
                    'transactions': [OrderedDict(
                        [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])]) for tx in block['transactions']]
                }

                updated_blockchain.append(updated_block)

            blockchain = updated_blockchain

            open_transactions = json.loads(file_content[1])
            # Convert  loaded data; Transactions should use OrderedDict
            updated_transactions = []
            for tx in open_transactions:
                updated_transaction = OrderedDict(
                    [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])])
                updated_transactions.append(updated_transaction)

            open_transactions = updated_transactions
    except IOError:
        print('Loading Failed... \n Creating empty chain...')
        genesis_block = {
            'previous_hash': '',
            'index': 0,
            'transactions': [],
            'proof': 100
        }
        blockchain = [genesis_block]
        open_transactions = []


load_data()


def save_data():
    '''
    Writes blockchain to file in plaintext.
    '''
    try:
        with open('blockchain.txt', mode='w') as f:
            f.write(json.dumps(blockchain))
            f.write('\n')
            f.write(json.dumps(open_transactions))
            # save_data = {
            #     'chain': blockchain,
            #     'ot': open_transactions
            # }
            # f.write(pickle.dumps(save_data))
    except IOError:
        print('Saving failed!')


def valid_proof(transactions, last_hash, proof, verbose=True):
    '''
    Validate proof of work number

    Arguments:
        :transactions: 
        :last_hash:
        :proof: 
    '''
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = hash_string_512(guess)

    if verbose:
        print(guess_hash)

    # Only a hash (based on the above inputs) starting with 2 0s is considered valid
    return guess_hash[0:2] == '00'


def proof_of_work():
    '''
    Generate a proof of work for currently open transactions
    '''
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    # Try different PoW numbers and return first valid PoW
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof


def get_balance(user):
    '''
    Calculate and return the balance for a user.

    Arguments:
        :user:
    '''

    balance = 0

    for tx in open_transactions:
        if tx['sender'] == user:
            balance -= tx['amount']
        if tx['receipient'] == user:
            balance += tx['amount']

    for block in blockchain:
        for tx in block['transactions']:
            if tx['sender'] == user:
                balance -= tx['amount']
            if tx['recipient'] == user:
                balance += tx['amount']

    return balance


def get_last_blockchain_value():
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def verify_transaction(transaction):
    '''
    Retrieve sends balance to ensure sufficient number of coins.

    Arguments:
        :transaction:
    '''
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']


def add_transaction(recipient, sender=owner, amount=0.0):
    '''
    Append a new value as well as the last blockchain value to the blockchain.

    Arguments:
        :sender: 
        :recipient:
        :amount:
    '''

    # Transaction Template
    # Ordered Dictionary
    # transaction = {
    #     'sender': sender,
    #     'recipient': recipient,
    #     'amount': amount
    # }
    transaction = OrderedDict(
        [('sender', sender), ('recipient', recipient), ('amount', amount)])
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        save_data()
        return True
    return False


def mine_block():
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block)
    proof = proof_of_work()

    # Reward Transasction Template
    # reward_transaction = {
    #     'sender': 'MINING',
    #     'recipient': owner,
    #     'amount': MINING_REWARD
    # }
    reward_transaction = OrderedDict(
        [('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
    # Making a copy ensures tyhat is mining fails, reward isn't stored in the open transactions
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': copied_transactions,
        'proof': proof
    }
    blockchain.append(block)
    return True


def print_blockchain_elements():
    for block in blockchain:
        print('Outputting Block')
        print(block)
    else:
        print('-' * 20)


def verify_chain():
    '''
    Verify blockchain by rehashing all blocks.
    '''
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index - 1]):
            return False
        if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
            print('Proof of work is invalid')
            return False
    return True


def verify_transactions():
    '''
    Verifies all open transactions
    '''
    return all([verify_transaction(tx) for tx in open_transactions])


listening = True

while listening:
    print('Please choose')
    print('1: Add a new transaction')
    print('2: Mine a new block')
    print('3: Output the blockchain')
    print('4: Output participants')
    print('5: Check transaction validity')
    print('h: Manipulate the chain')
    print('q: Quit')

    user_choice = input()

    if user_choice == '1':
        recipient = input('Enter the recipient of the transaction: ')
        amount = float(input('Your transaction amount please: '))
        if add_transaction(recipient, amount=amount):
            print('Added transaction!')
        else:
            print('Transaction failed!')
        print(open_transactions)
    elif user_choice == '2':
        if mine_block():
            open_transactions = []
            save_data()
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == '4':
        print(participants)
    elif user_choice == '5':
        if verify_transactions():
            print('All transactions are valid.')
        else:
            print('There are invalid transactions!')
    # demonstrate chain integrity by manipulating it
    elif user_choice == 'h':
        if len(blockchain) >= 1:
            blockchain[0] = {
                'previous_hash': '',
                'index': 0,
                'transactions': [{'sender': 'Chris', 'recipient': 'Aaron', 'amount': 100.0}]
            }
    elif user_choice == 'q':
        listening = False
    else:
        print('Input was invalid, please pick a value from the list!')
    # if chain verification fails break loop and exit
    if not verify_chain():
        print_blockchain_elements()
        print('Invalid blockchain!')
        break
    print('Balance of {}: {:6.2f}'.format('Aaron', get_balance('Aaron')))
else:
    print('User left!')


print('Done!')

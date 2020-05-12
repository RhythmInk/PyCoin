from blockchain   import Blockchain
from verification import Verification

class Node:


    def __init__(self):

        self.id = 'Aaron'
        self.blockchain = Blockchain(self.id)


    def get_transaction_value(self):

        tx_recipient = input('Recipient: ')
        tx_amount    = float(input('Transaction amount: '))

        return tx_recipient, tx_amount


    def print_blockchain_elements(self):

        for block in self.blockchain.chain:
            print('Outputting Block')
            print(block)
        else:
            print('#' * 40)


    def listen(self):
        waiting_for_input = True


        while waiting_for_input:
            print('Please choose')
            print('1: Add a new transaction value')
            print('2: Mine a new block')
            print('3: Output the blockchain blocks')
            print('4: Check transaction validity')
            print('q: Quit')

            user_choice = input('Selection: ')

            if user_choice == '1':
                tx_data = self.get_transaction_value()
                recipient, amount = tx_data
                if self.blockchain.add_transaction(recipient, self.id, amount=amount):
                    print('Transaction Added')
                else:
                    print('Transaction Failed')
                print(self.blockchain.open_transactions)
            elif user_choice == '2':
                self.blockchain.mine_block()
            elif user_choice == '3':
                self.print_blockchain_elements()
            elif user_choice == '4':
                if Verification.verify_transactions(self.blockchain.open_transactions, self.blockchain.get_balance):
                    print('All transactions valid')
                else:
                    print('Invalid transaction found!')
                    print('Exiting!')
                    break
            elif user_choice == 'q':
                waiting_for_input = False
            else:
                print('Input was invalid, please pick a value from the list!')
            if not Verification.verify_chain(self.blockchain.chain):
                self.print_blockchain_elements()
                print('Invalid blockchain!')
                break
            print()
            print('Balance of {}: {:6.4f}'.format(self.id, self.blockchain.get_balance()))
        else:
            print('User left!')

        print('Done!')

node = Node()
node.listen()
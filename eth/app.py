import json
import argparse
import rlp

from web3 import Web3, HTTPProvider, TestRPCProvider
from web3.contract import ConciseContract
from ethereum.abi import ContractTranslator
from ethereum.transactions import Transaction

parser = argparse.ArgumentParser(description='Process smart-contract params.')
parser.add_argument('--owner', dest='owner',
                   help='address who will receive badge')
parser.add_argument('--tx', dest='tx',
                   help='Tx that owner sent for donation')
parser.add_argument('--title', dest='title',
                   help='Title of badge that user will receive')

args = parser.parse_args()

if args.title is None or args.tx is None or args.owner is None:
    parser.print_help()
    exit(0)

#Define who will receive badge
badge_owner = args.owner

#Define donation Tx what will be used to receive badge
donation_tx = args.tx

#Define badge title
badge_title = args.title


######### TEST RPC CONFIGURATION #########

# web3.py instance for Testrpc
# w3 = Web3(TestRPCProvider(host="localhost", port=8545))

#Define contract address
#Test RPC
#contract_address = '0x9c1a0c5c36ff75ed4c34475e9fc4e46b9523f26f'

#Sender address
#Test RPC
#sender_address = '0x0a79827632bf4356659d8740a6d301599473d6a3'
#sender_pk = bytes(bytearray.fromhex('03cbefb6c421b7f314bd74fb5e13275fca2f491eb33ca09555489bd5528846ee'))

##########################################

#########  INFURA CONFIGURATION  #########

w3 = Web3(HTTPProvider("https://rinkeby.infura.io/m6ecrmQM2b6CUWLkBCro"))
contract_address = '0x00a421dd2d39f49990e15922ffe28a92ef2acd85'
sender_address = '0x99a4572656eb49ffeefbe9588f8e7ab0f8d6eb5e'
sender_pk = bytes(bytearray.fromhex('1cf8c24523faceab6acc576c4a8eb36cbe2d42308260d95c301f5433002ac3f8'))

##########################################

#Define abi
abi = json.load(open('contracts/M8BadgeToken.json'))

#Define gas
gas = 123145

# Contract instance in concise mode
contract_instance = w3.eth.contract(abi['abi'], contract_address, ContractFactoryClass=ConciseContract)

# Contract creates new badge
transact = {
    "gas": gas,
    "from": sender_address
}

# Sending transaction
# contract_instance.create(donation_tx, badge_title, badge_owner, transact=transact)

# Send raw transaction
ct = ContractTranslator(abi['abi'])
txdata = ct.encode_function_call("create", [donation_tx, badge_title, badge_owner])


# Load data with configuration and nonce
data = json.load(open('data.txt', 'r'))

if 'nonce' not in data:
    data['nonce'] = w3.eth.getTransactionCount(sender_address)
else:
    nonce = data["nonce"] + 1

nonce = max(nonce, w3.eth.getTransactionCount(sender_address))

tx = Transaction(
    nonce=nonce,
    gasprice=gas,
    startgas=150000,
    to=contract_address,
    value=0,
    data=txdata,
)

# Save nonce to file
data['nonce'] = nonce
json.dump(data, open('data.txt', 'w'))

tx.sign(sender_pk)

raw_tx = rlp.encode(tx)
raw_tx_hex = w3.toHex(raw_tx)
result = w3.eth.sendRawTransaction(raw_tx_hex)

print(result)


# Just for testing

# Check who is owner of badge 0
# res = contract_instance.ownerOf(0)
# print('Contract value: {}'.format(res))

# Accounts list
# print('Accounts: {}'.format(w3.eth.accounts))

# Check that badge exists
# tokens = contract_instance.tokensOfOwner(badge_owner);
# print('Tokens: {}'.format(tokens))

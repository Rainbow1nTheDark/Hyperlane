import json

SUPPORTED_CHAINS = ['optimism', 'arbitrum', 'base', 'manta pacific']
START_CHAIN = 'arbitrum'

with open('./abi/erc20_abi.json') as file:
    ERC20_ABI = json.load(file)

with open('data/rpc.json') as file:
    RPC = json.load(file)

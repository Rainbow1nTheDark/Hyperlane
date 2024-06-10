import asyncio
import random
import sys
from decimal import Decimal

from web3 import Web3

import utils.sleeping as sleeping
from modules.account import Account
from modules.hyperlane import Hyperlane
from loguru import logger
from config import SUPPORTED_CHAINS, RPC, START_CHAIN
from data.contract_addresses import HYPERLANE_TOKEN_BRIDGE_ADDRESSES
from settings import MIN_TRANS, MAX_TRANS, SLEEP_FROM, SLEEP_TO


async def bridge():
    logger.info(f"[{wallet_num}]-[{account.address}][TX - {i + 1} / {num_of_trans}]")
    retries = 3

    try:
        j = 0
        fees = 0.001
        hp = Hyperlane(wallet_num, private_key, start_chain)
        amount_balance = await hp.get_balance_eth()

        while j < retries:
            if j > 0:
                fees += 0.0002

            amount = Web3.to_wei(amount_balance - Decimal(fees), 'ether')
            is_success = await hp.bride(chain_id, contract_address, amount, amount_balance)

            if is_success:
                break
            j += 1

    except Exception as error:
        logger.error(f"[{wallet_num}]-[{account.address}][TX - {i + 1} / {num_of_trans}] \nError: {error}")


if __name__ == '__main__':
    logger.add("logging.log")

    # get start chain
    start_chain = START_CHAIN
    # get wallet
    with open("./data/pk.txt", "r") as f:
        keys_list = [row.strip() for row in f if row.strip()]
    random.shuffle(keys_list)

    logger.info(f"Hyperlane has started. Number of accounts - {len(keys_list)}")
    num_keys = len(keys_list)
    wallet_num = 1

    while keys_list:
        private_key = keys_list.pop(0)
        num_of_trans = random.randint(MIN_TRANS, MAX_TRANS)
        account = Account(wallet_num, private_key, start_chain)

        for i in range(num_of_trans):

            if i < num_of_trans - 1:
                to_bridge_chain = random.choice([c for c in SUPPORTED_CHAINS if c != start_chain])
            else:
                to_bridge_chain = random.choice([c for c in START_CHAIN if c != start_chain])

            contract_address = HYPERLANE_TOKEN_BRIDGE_ADDRESSES[start_chain]
            chain_id = RPC[to_bridge_chain]['chain_id']

            logger.info(f"[{account.address}][{start_chain}][{chain_id}]-[{to_bridge_chain}] Bridging...")
            asyncio.run(bridge())

            start_chain = to_bridge_chain
            asyncio.run(sleeping.sleep(SLEEP_FROM, SLEEP_TO))

        wallet_num += 1



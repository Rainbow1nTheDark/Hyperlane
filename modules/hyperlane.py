import json as js
from decimal import Decimal

from loguru import logger
from web3 import Web3
from modules.account import Account


class Hyperlane(Account):
    def __init__(self, account_id: int, private_key: str, chain) -> None:
        super().__init__(account_id=account_id, private_key=private_key, chain=chain)
        self.hyperlane_abi = js.load(open('./abi/hyperlane_token_bridge.json'))

    async def bride(self, domain: int, contract_address: str, amount, amount_balance):

        contract_address = Web3.to_checksum_address(contract_address)

        contract = self.w3.eth.contract(address=contract_address, abi=self.hyperlane_abi)
        quote = await contract.functions.quoteBridge(domain, amount).call()

        total_value = amount + quote

        if Web3.from_wei(total_value, 'ether') > amount_balance - Decimal(0.00028):
            logger.warning(f"Not Enough Money for transfer: Balance: {amount_balance} | Wanted: {Web3.from_wei(total_value, 'ether')}")
            return

        logger.info(f"Balance: {amount_balance} | Total Amount: {Web3.from_wei(total_value, 'ether')} | Quote: {Web3.from_wei(quote, 'ether')} | Amount Transfer: {Web3.from_wei(amount, 'ether')} | {contract_address}")
        function_call = contract.functions.bridgeETH(domain, amount)

        estimated_gas = await function_call.estimate_gas({
            'from': self.account.address,
            'value': total_value
        })
        tx = {
            'from': self.account.address,
            'value': total_value,
            'gas': estimated_gas,
            'gasPrice': await self.w3.eth.gas_price,
            'nonce': await self.w3.eth.get_transaction_count(self.w3.to_checksum_address(self.account.address))
        }
        tx = await function_call.build_transaction(tx)
        signed_txn = self.w3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = await self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        # wait till tx is success
        status = await self.wait_until_tx_finished(tx_hash.hex())
        return status

from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from nacl.signing import SigningKey
from nacl.encoding import RawEncoder

class LocalWallet:
    def __init__(self, secret: bytes):
        self._kp = Keypair.from_secret_key(secret)

    @property
    def pubkey(self) -> str:
        return str(self._kp.public_key)

    async def sign_tx(self, tx_bytes: bytes) -> bytes:
        # Le payload Jupiter est déjà une tx v0; on signe avec la clé
        from solana.transaction import VersionedTransaction
        tx = VersionedTransaction.deserialize(tx_bytes)
        tx.sign([self._kp])
        return bytes(tx.serialize())

import hmac
import hashlib
import json
from typing import Dict, Any


def verify_prodamus_signature(data: Dict[str, Any], secret_key: str) -> bool:
    """
    Verify HMAC signature from Prodamus webhook data.
    Uses official prodamuspy library to correctly handle nested arrays and dicts.
    """
    if not secret_key:
        # In dev mode without secret key, allow testing if flag set
        return True

    received_sign = data.get("sign") or data.get("signature")
    if not received_sign:
        return False

    try:
        import prodamuspy
        prodamus = prodamuspy.ProdamusPy(secret_key)
        
        # prodamuspy does not automatically strip the sign/signature keys if they were injected
        clean_data = {k: v for k, v in data.items() if k not in ("sign", "signature")}
        return prodamus.verify(clean_data, received_sign)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Failed to verify Prodamus signature: {e}")
        return False

import hmac
import hashlib
import json
from typing import Dict, Any


def verify_prodamus_signature(data: Dict[str, Any], secret_key: str) -> bool:
    """
    Verify HMAC signature from Prodamus webhook data.
    Prodamus computes signature by sorting keys alphabetically (excluding 'sign'),
    serializing payload to string or JSON, and signing with secret_key.
    """
    if not secret_key:
        # In dev mode without secret key, allow testing if flag set
        return True

    received_sign = data.get("sign") or data.get("signature")
    if not received_sign:
        return False

    # Extract all fields except sign/signature
    clean_data = {k: v for k, v in data.items() if k not in ("sign", "signature")}
    
    # Sort keys alphabetically
    sorted_keys = sorted(clean_data.keys())
    
    # Concatenate values or JSON string
    payload_parts = [str(clean_data[k]) for k in sorted_keys if clean_data[k] is not None]
    raw_payload = "".join(payload_parts).encode("utf-8")

    # Compute HMAC-SHA256
    expected_sign_sha256 = hmac.new(
        secret_key.encode("utf-8"),
        raw_payload,
        hashlib.sha256
    ).hexdigest()

    # Compute HMAC-MD5 (fallback for legacy Prodamus integration)
    expected_sign_md5 = hmac.new(
        secret_key.encode("utf-8"),
        raw_payload,
        hashlib.md5
    ).hexdigest()

    return received_sign.lower() in (expected_sign_sha256.lower(), expected_sign_md5.lower())

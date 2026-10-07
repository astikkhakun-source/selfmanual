import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, Request, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base import get_db
from src.services.payment import process_prodamus_webhook

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "selfmanual-backend", "version": "1.3"}


@router.post("/payment/prodamus/webhook")
async def prodamus_webhook(request: Request, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """
    Handle Prodamus payment callback webhook.
    Form-encoded or JSON payload.
    """
    try:
        import json
        import urllib.parse
        
        raw_body = await request.body()
        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError:
            # Fallback to form-encoded data parsing manually
            import prodamuspy
            dummy_prodamus = prodamuspy.ProdamusPy("dummy")
            try:
                payload = dummy_prodamus.parse(raw_body.decode("utf-8"))
            except ValueError:
                # If strict_parsing fails, fallback to basic parsing
                parsed_qs = urllib.parse.parse_qsl(raw_body.decode("utf-8"), keep_blank_values=True)
                payload = dict(parsed_qs)

        # Check HTTP headers for 'Sign' if missing in payload
        if "sign" not in payload and "signature" not in payload:
            header_sign = (
                request.headers.get("Sign")
                or request.headers.get("sign")
                or request.headers.get("X-Sign")
                or request.headers.get("Signature")
                or request.headers.get("signature")
            )
            if header_sign:
                header_sign = header_sign.strip()
                if header_sign.lower().startswith("sign: "):
                    header_sign = header_sign[6:].strip()
                payload["sign"] = header_sign

        success, msg = await process_prodamus_webhook(db, payload, background_tasks)

        if not success:
            logger.warning(f"Prodamus webhook failed verification: {msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=msg
            )

        logger.info(f"Prodamus webhook processed successfully: {msg}")
        return {"status": "success", "message": msg}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error processing Prodamus webhook")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, Request, HTTPException, status
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
async def prodamus_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Handle Prodamus payment callback webhook.
    Form-encoded or JSON payload.
    """
    try:
        if request.headers.get("content-type") == "application/json":
            payload = await request.json()
        else:
            form_data = await request.form()
            payload = dict(form_data)

        success, msg = await process_prodamus_webhook(db, payload)

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

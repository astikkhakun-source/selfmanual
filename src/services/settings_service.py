from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.db.models import SystemSetting


ADMIN_REPORT_FORWARDING_KEY = "ADMIN_REPORT_FORWARDING"


async def get_setting(db: AsyncSession, key: str, default: str = "") -> str:
    """Fetch setting value by key or return default if not set."""
    result = await db.execute(select(SystemSetting).where(SystemSetting.key == key))
    setting = result.scalar_one_or_none()
    if setting:
        return setting.value
    return default


async def set_setting(db: AsyncSession, key: str, value: str) -> None:
    """Set setting value by key (create or update)."""
    result = await db.execute(select(SystemSetting).where(SystemSetting.key == key))
    setting = result.scalar_one_or_none()
    if setting:
        setting.value = value
    else:
        setting = SystemSetting(key=key, value=value)
        db.add(setting)
    await db.commit()


async def is_report_forwarding_enabled(db: AsyncSession) -> bool:
    """Check if report forwarding to admin is enabled (default True)."""
    val = await get_setting(db, ADMIN_REPORT_FORWARDING_KEY, default="true")
    return val.lower() in ("true", "1", "yes", "on")


async def toggle_report_forwarding(db: AsyncSession) -> bool:
    """Toggle report forwarding setting state. Returns new boolean state."""
    current = await is_report_forwarding_enabled(db)
    new_state = not current
    await set_setting(db, ADMIN_REPORT_FORWARDING_KEY, "true" if new_state else "false")
    return new_state

from aiogram.fsm.state import State, StatesGroup


class PromoCreateFSM(StatesGroup):
    waiting_for_code = State()
    waiting_for_uses = State()
    waiting_for_duration = State()


class UserPromoFSM(StatesGroup):
    waiting_for_promo = State()


class SupportFSM(StatesGroup):
    waiting_for_user_message = State()


class AdminReplyFSM(StatesGroup):
    waiting_for_admin_reply = State()


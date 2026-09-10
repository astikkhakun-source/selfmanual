from aiogram.fsm.state import State, StatesGroup


class PromoCreateFSM(StatesGroup):
    waiting_for_code = State()
    waiting_for_uses = State()
    waiting_for_duration = State()


class UserPromoFSM(StatesGroup):
    waiting_for_promo = State()

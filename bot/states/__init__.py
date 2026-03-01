"""FSM states for the conversion flow."""

from aiogram.fsm.state import State, StatesGroup


class ConvertStates(StatesGroup):
    waiting_file = State()

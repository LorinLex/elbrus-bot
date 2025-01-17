import re
from datetime import datetime
from dataclasses import asdict
from typing import Optional

from aiogram import html, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.methods import DeleteMessages
from aiogram.types import Message, CallbackQuery, InaccessibleMessage
from app import bot
from app.dal import Boy
from app.dal.events import Event, add_event, get_event_list
from app.handlers.events.utils import get_event_caption
from app.kb import confirm_event_inline_kb, confirm_inline_kb, \
    event_card_inline_kb, main_kb, stop_fsm_inline_kb
from app.states import CreateEventStates, FixEventStates, MainEventStates
from app.utils import bool2human


router = Router(name="event_update")


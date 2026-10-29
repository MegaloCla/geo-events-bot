from __future__ import annotations

import asyncio
from math import isfinite
from typing import TYPE_CHECKING
from uuid import uuid4

from cachetools import TTLCache
from pydantic import ValidationError
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from telegram.constants import ChatMemberStatus
from telegram.error import TelegramError

from geo_events_bot.models.location_filter import LocationFilter
from geo_events_bot.services.city_search import search_cities
from geo_events_bot.utils.logger import Logger

if TYPE_CHECKING:
    from geo_events_bot.controllers.event_poller import Poller

logger = Logger(__name__).get_logger()


class LocationController:
    def __init__(self, poller: Poller):
        self.poller = poller
        self._choices: TTLCache[str, LocationFilter] = TTLCache(
            maxsize=poller.settings.location_choice_cache_size,
            ttl=poller.settings.location_choice_ttl,
        )

    async def _can_configure(self, user_id: int) -> bool:
        chat_id = self.poller.settings.chat_id
        if str(user_id) == str(chat_id):
            return True
        try:
            member = await self.poller.bot.bot.get_chat_member(chat_id, user_id)
        except TelegramError:
            logger.exception("Unable to check location settings permissions")
            return False
        return member.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR)

    async def show(self, update, _context) -> None:
        if not await self._can_configure(update.effective_user.id):
            await update.effective_message.reply_text(
                "Non puoi modificare la zona di questa chat."
            )
            return
        location = self.poller.settings.location_filter
        text = (
            f"Zona attiva: {location.city}, entro {location.radius_km:g} km."
            if location is not None
            else "Ricevi gli eventi di tutte le zone."
        )
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Cerca città e raggio", switch_inline_query_current_chat=""
                    )
                ],
                [InlineKeyboardButton("Tutte le zone", callback_data="zone:off")],
            ]
        )
        await update.effective_message.reply_text(
            text + "\nCerca con il nome della città e il raggio, ad esempio: Roma 50."
            "\nRicerca città: Open-Meteo / GeoNames.",
            reply_markup=keyboard,
        )

    async def search(self, update, _context) -> None:
        query = update.inline_query
        parts = query.query.strip().rsplit(maxsplit=1)
        name = query.query.strip()
        radius = self.poller.settings.default_radius_km
        if len(parts) > 1:
            try:
                radius = float(parts[-1].replace(",", "."))
            except ValueError:
                pass  # The last word can be part of a multiword city name.
            else:
                name = parts[0]
        if not isfinite(radius) or radius <= 0:
            await query.answer([], cache_time=0, is_personal=True)
            return
        cities = await asyncio.to_thread(search_cities, name)
        results = []
        for city in cities:
            try:
                location = LocationFilter(
                    city=city.label,
                    latitude=city.latitude,
                    longitude=city.longitude,
                    radius_km=radius,
                )
            except ValidationError:
                continue
            choice_id = uuid4().hex
            self._choices[choice_id] = location
            results.append(
                InlineQueryResultArticle(
                    id=choice_id,
                    title=city.label,
                    description=f"Raggio: {radius:g} km · Seleziona e attiva il filtro",
                    input_message_content=InputTextMessageContent(
                        f"{city.label} · {radius:g} km\nPremi Attiva per usare questa zona."
                        "\nRicerca città: Open-Meteo / GeoNames."
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Attiva filtro", callback_data=f"zone:{choice_id}"
                                )
                            ]
                        ]
                    ),
                )
            )
        await query.answer(
            results, cache_time=self.poller.settings.inline_cache_time, is_personal=True
        )

    async def apply(self, update, _context) -> None:
        query = update.callback_query
        if not await self._can_configure(update.effective_user.id):
            await query.answer(
                "Solo il proprietario o gli amministratori possono cambiare zona.",
                show_alert=True,
            )
            return
        choice_id = query.data.removeprefix("zone:")
        location = None
        if choice_id != "off":
            location = self._choices.get(choice_id)
            if location is None:
                await query.answer(
                    "Ricerca scaduta. Cerca nuovamente la città.", show_alert=True
                )
                return
        self.poller.set_location_filter(location)
        await query.answer("Filtro aggiornato")
        text = (
            f"Filtro attivo: {location.city}, entro {location.radius_km:g} km."
            if location is not None
            else "Filtro disattivato: ricevi gli eventi di tutte le zone."
        )
        await query.edit_message_text(text)

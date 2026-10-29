from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram.constants import ChatMemberStatus
from telegram.error import TelegramError

from geo_events_bot.controllers.location_controller import LocationController
from geo_events_bot.models.city import City
from geo_events_bot.services.settings_store import SettingsStore

pytestmark = pytest.mark.asyncio()


def make_update(query="Roma 50", user_id=123):
    update = MagicMock()
    update.effective_user.id = user_id
    update.inline_query.query = query
    update.inline_query.answer = AsyncMock()
    update.callback_query.answer = AsyncMock()
    update.callback_query.edit_message_text = AsyncMock()
    update.effective_message.reply_text = AsyncMock()
    return update


async def test_search_then_activate_city(poller, event_cache):
    poller.settings.chat_id = "123"
    controller = LocationController(poller)
    update = make_update()
    city = City(
        id=1,
        name="Roma",
        latitude=41.9,
        longitude=12.5,
        admin1="Lazio",
        country="Italia",
    )
    with patch(
        "geo_events_bot.controllers.location_controller.search_cities",
        return_value=[city],
    ) as search:
        await controller.search(update, None)
    search.assert_called_once_with("Roma")
    result = update.inline_query.answer.call_args.args[0][0]
    assert result.title == "Roma, Lazio, Italia"  # noqa: S101
    update.callback_query.data = result.reply_markup.inline_keyboard[0][0].callback_data
    await controller.apply(update, None)
    assert poller.settings.location_filter.city == city.label  # noqa: S101
    assert poller.settings.location_filter.radius_km == 50  # noqa: S101, PLR2004
    assert (  # noqa: S101
        SettingsStore(event_cache.cache.directory).load_location_filter()
        == poller.settings.location_filter
    )


@pytest.mark.parametrize("query", ["Roma -5", "Roma 0", "Roma nan", "Roma inf"])
async def test_invalid_radius_does_not_search(poller, query):
    controller = LocationController(poller)
    update = make_update(query)
    with patch(
        "geo_events_bot.controllers.location_controller.search_cities"
    ) as search:
        await controller.search(update, None)
    search.assert_not_called()
    assert update.inline_query.answer.call_args.args[0] == []  # noqa: S101


async def test_multiword_city_and_default_radius(poller):
    controller = LocationController(poller)
    update = make_update("Reggio Emilia")
    with patch(
        "geo_events_bot.controllers.location_controller.search_cities", return_value=[]
    ) as search:
        await controller.search(update, None)
    search.assert_called_once_with("Reggio Emilia")


async def test_expired_choice_does_not_change_filter(poller):
    poller.settings.chat_id = "123"
    controller = LocationController(poller)
    update = make_update()
    update.callback_query.data = "zone:expired"
    await controller.apply(update, None)
    assert poller.settings.location_filter is None  # noqa: S101
    update.callback_query.edit_message_text.assert_not_called()


async def test_unauthorized_user_cannot_change_filter(poller):
    poller.settings.chat_id = "123"
    poller.bot.bot.get_chat_member = AsyncMock(
        return_value=MagicMock(status=ChatMemberStatus.MEMBER)
    )
    controller = LocationController(poller)
    update = make_update(user_id=999)
    update.callback_query.data = "zone:off"
    await controller.apply(update, None)
    update.callback_query.edit_message_text.assert_not_called()
    assert update.callback_query.answer.call_args.kwargs["show_alert"] is True  # noqa: S101


async def test_group_admin_can_disable_filter(poller):
    poller.settings.chat_id = "-100123"
    poller.bot.bot.get_chat_member = AsyncMock(
        return_value=MagicMock(status=ChatMemberStatus.ADMINISTRATOR)
    )
    controller = LocationController(poller)
    update = make_update()
    update.callback_query.data = "zone:off"
    await controller.apply(update, None)
    update.callback_query.edit_message_text.assert_awaited_once()


async def test_permission_check_failure_does_not_change_filter(poller):
    poller.settings.chat_id = "-100123"
    poller.bot.bot.get_chat_member = AsyncMock(side_effect=TelegramError("Unavailable"))
    controller = LocationController(poller)
    update = make_update()
    update.callback_query.data = "zone:off"
    await controller.apply(update, None)
    update.callback_query.edit_message_text.assert_not_called()


async def test_show_settings_offers_inline_city_search(poller):
    poller.settings.chat_id = "123"
    controller = LocationController(poller)
    update = make_update()
    await controller.show(update, None)
    keyboard = update.effective_message.reply_text.call_args.kwargs["reply_markup"]
    assert keyboard.inline_keyboard[0][0].switch_inline_query_current_chat == ""  # noqa: S101

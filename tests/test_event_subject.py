import asyncio

from geo_events_bot.services.event_subject import EventSubject


def test_event_subject(telegram_observer_mock):
    event_subject = EventSubject()

    event_subject.add_observer(telegram_observer_mock)

    asyncio.run(event_subject.notify_observers("tests message"))

    event_subject.remove_observer(telegram_observer_mock)

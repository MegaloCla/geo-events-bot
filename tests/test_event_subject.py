import pytest


def test_add_observer(subject, observer):
    subject.add_observer(observer)
    assert observer in subject._observers  # noqa: SLF001, S101


def test_add_observer_duplicate(subject, observer):
    subject.add_observer(observer)
    subject.add_observer(observer)
    assert subject._observers.count(observer) == 1  # noqa: SLF001, S101


def test_remove_observer(subject, observer):
    subject.add_observer(observer)
    subject.remove_observer(observer)
    assert observer not in subject._observers  # noqa: SLF001, S101


def test_remove_observer_not_present(subject, observer):
    subject.remove_observer(observer)
    assert observer not in subject._observers  # noqa: SLF001, S101


@pytest.mark.asyncio()
async def test_notify_observers(subject, observer):
    subject.add_observer(observer)

    message = "Test message"
    await subject.notify_observers(message)

    observer.send_message.assert_called_once_with(message, None)


@pytest.mark.asyncio()
async def test_notify_observers_with_photo(subject, observer):
    subject.add_observer(observer)

    message = "Test message"
    photo_bytes = b"fake_image_data"
    await subject.notify_observers(message, photo_bytes)

    observer.send_photo.assert_called_once_with(photo_bytes, message, None)
    observer.send_message.assert_not_called()


@pytest.mark.asyncio()
async def test_notify_observers_with_reply_markup(subject, observer):
    subject.add_observer(observer)

    message = "Test message"
    reply_markup = "fake_markup"
    await subject.notify_observers(message, reply_markup=reply_markup)

    observer.send_message.assert_called_once_with(message, reply_markup)

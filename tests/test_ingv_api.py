from unittest.mock import MagicMock, patch

from geo_events_bot.services.ingv_api import get_geo_events


@patch("geo_events_bot.services.ingv_api._get_earthquake_data")
@patch("geo_events_bot.services.ingv_api._json_to_model")
def test_get_geo_events_success(mock_json_to_model, mock_get_data):
    valid_json = {"some_key": "some_value"}
    model_instance = MagicMock()

    mock_get_data.return_value = valid_json
    mock_json_to_model.return_value = model_instance

    url = "http://dummyurl.com"
    result = get_geo_events(url)

    assert result == model_instance  # noqa: S101
    mock_get_data.assert_called_once_with(url)
    mock_json_to_model.assert_called_once_with(valid_json)


@patch("geo_events_bot.services.ingv_api._get_earthquake_data")
@patch("geo_events_bot.services.ingv_api._json_to_model")
def test_get_geo_events_failure(mock_json_to_model, mock_get_data):
    mock_get_data.return_value = None
    mock_json_to_model.return_value = None

    url = "http://dummyurl.com"
    result = get_geo_events(url)

    assert result is None  # noqa: S101
    mock_get_data.assert_called_once_with(url)
    mock_json_to_model.assert_called_once_with(None)

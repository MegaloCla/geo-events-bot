# geo-events-bot

Geo-events-bot is a Telegram bot that uses the APIs provided by INGV (Istituto Nazionale di Geofisica e Vulcanologia) to
receive updates on the latest seismic events.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Introduction

Geo-events-bot is designed to provide timely updates on seismic events directly on Telegram. It uses INGV APIs to fetch
information about earthquakes and send it to the bot users.

## Features

- 📅 Receive notifications about the latest seismic events
- 🌍 View detailed information about events
- 🗺️ Get geographical coordinates of earthquakes
- ⚠️ Receive near real-time updates (updates depend on the INGV API refresh rate)

The default thresholds set are:
- Minimum magnitude reported = 2
- Polling data interval = 5 seconds

## Prerequisites

Make sure you have the following software installed before proceeding with the installation:

- Python 3.12
- Poetry
- Docker (optional, for running the project in a container)
- A Telegram bot. Follow the instructions to create a bot on
  Telegram: [Telegram Bot Documentation](https://core.telegram.org/bots/tutorial)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/geo-events-bot.git
   cd geo-events-bot
2. Install dependencies using Poetry:

   ```bash
   poetry install

3. Configure environment variables (see Configuration).

4. Run the bot:

   ```bash
   cd src/
   poetry run python geo_events_bot

## Configuration

To run the program without Docker, you need to set the following environment variables:

   ```bash
   export TELEGRAM_TOKEN=your_telegram_bot_token
   export CHAT_TELEGRAM_ID=you_chat_telegram_id
   ```

Otherwise, to run the program with Docker, you need to create an `.env` file with the previous environment variables:
Example `.env` file:

   ```bash
   TELEGRAM_TOKEN=your_telegram_bot_token
   CHAT_TELEGRAM_ID=you_chat_telegram_id
   ```

## Running with Docker
1. Build a Docker image:

   ```bash
   docker build -t geo-events-bot .
   ```
2. Run the Docker container:

   ```bash
   docker run --env-file .env geo-events-bot
   ```

Make sure not to include the `.env` file in the repository by adding it to the `.dockerignore` file.

## Contributing
Contributions are welcome! Feel free to fork the project, create a new branch, and open a pull request. To report issues, you can open an issue in the repository.

## License
This project is licensed under the GNU General Public License v3.0. See the LICENSE file for details.

## Earthquakes near a city

The filter is configured directly in Telegram using a city name and a radius in km.

1. Enable inline queries for your bot with BotFather's `/setinline` command.
   Suggested placeholder: `Città e raggio in km, ad esempio Roma 50`.
2. Send `/zona` to your bot and tap **Cerca città e raggio**, or type
   `@your_bot Roma 50` directly in Telegram's message field.
3. Suggestions appear while typing (at least three characters). Select the city,
   checking its region and country, then tap **Attiva filtro**.

The radius defaults to 100 km if omitted and must be a positive finite number.
City search is provided by [Open-Meteo / GeoNames](https://open-meteo.com/en/docs/geocoding-api).
The configured private chat owner, or an administrator of the configured group/channel,
can activate or disable the filter. Settings apply to `CHAT_TELEGRAM_ID` and are saved
as `location_filter.json` in the event cache directory. They survive process restarts
while that directory is retained and are independent of event cache eviction.
Use `/zona` → **Tutte le zone** to remove the filter.

Both the minimum magnitude and the geographic radius apply. Distances are approximate
surface distances to the epicenter, shown in messages and image cards. Coordinates
are resolved internally; users enter only the city and radius. Already delivered
events remain deduplicated when the filter changes.

Map cards include local time (Europe/Rome), magnitude, depth when available and a
clear epicenter marker. Tiles use a seven-day local cache in the system temporary
directory, an application User-Agent and visible OpenStreetMap attribution.

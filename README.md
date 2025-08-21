# Table of Contents
- [Table of Contents](#table-of-contents)
- [Description](#description)
- [Maintainers Guide](#maintainers-guide)
  - [Requirements](#requirements)
  - [Running the Application](#running-the-application)
    - [Locally](#locally)
    - [Docker](#docker)
    - [Running the Full MTS Stack](#running-the-full-mts-stack)


# Description
event-mapper is a part of the MTS backend stack that infers locations using NER and geocode them using Google Maps API. 

event-mapper uses Redis streams to manage and process events in real-time from the [rss-aggregator][rss-aggregator].

The mapped events are then stored in a MongoDB database for further analysis and retrieval.

[rss-aggregator]: https://github.com/mts-monitor-the-situation/rss-aggregator

# Maintainers Guide

## Requirements

- Python >= 3.11
- Google Maps API key
- Docker(https://docs.docker.com/get-docker/)
- Redis >= 8.2.0
- MongoDB

## Running the Application
### Locally
1. Create a Python virtual environment:
   ```bash
   python -m venv venv
   ```
2. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```bash
     source venv/bin/activate # or venv/bin/activate.fish for fish shell
     ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start Redis and MongoDB services on default ports without authentication. You can run it locally or use Docker. This step is up to you.

5. Create the configuration file
    - The file should be named config.yaml and located in the root directory of the project.
    - You can refer to the content of [config.example.yaml](config.example.yaml)

6. Run the application:
   ```bash
   python main.py
   ```
### Docker
1. Build the Docker image:
   ```bash
   docker build -t event-mapper .
   ```
2. Create the configuration file
   - The file should be named config.yaml and located in the root directory of the project.
   - You can refer to the content of [config.example.yaml](config.example.yaml)

4. Start Redis and MongoDB services on default ports without authentication. You can run it locally or use Docker. This step is up to you.

5. Run the Docker container:
   ```bash
   docker run -v $(pwd)/config.yaml:/service/config.yaml event-mapper
   ```
### Running the Full MTS Stack
A docker-compose file is provided to run the full MTS backend stack.

This includes
- Redis
- MongoDB
- Event Mapper
- [RSS Aggregator][rss-aggregator]

1. Create 2 configuration files; 1 for the event-mapper and 1 for the rss-aggregator.
   - You can refer to the content of [config.example.yaml](config.example.yaml) for the required configuration for the event-mapper. The file needs to be named config.yaml and located in the root directory of the project.
   - You can refer to the content of [config.rss.example.yaml](config.rss.example.yaml) for the required configuration for the rss-aggregator. The file needs to be named config.rss.yaml and located in the root directory of the project.
2. Build the Docker images:
   ```bash
   docker-compose build
   ```
3. Start the services:
   ```bash
   docker-compose up
   ```
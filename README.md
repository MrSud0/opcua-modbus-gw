

# OPC UA to Modbus Gateway Project

## Description

This project is an OPC UA to Modbus gateway built with Python. It uses the `asyncua` and `pymodbus` libraries to create a gateway that translates OPC UA requests to Modbus TCP. The server is designed to run inside a Docker container.

## Project Structure

- `Dockerfile`: Defines the Docker image for the OPC UA to Modbus gateway.
- `entrypoint.sh`: The entry point script that starts the OPC UA to Modbus gateway.
- `opcua-modbus-gw.py`: The main Python script for the OPC UA to Modbus gateway.
- `requirements.txt`: Lists the Python dependencies required for the project.

## Prerequisites

- Docker
- Python 3.8+

## Getting Started

### Build the Docker Image

To build the Docker image, run the following command in the project directory:

```sh
docker build -t opcua-modbus-gw .
```

### Run the Docker Container

To run the Docker container, use the following command:

```sh
docker run -d -p 4840:4840 -p 5020:5020 opcua-modbus-gw
```

This will start the OPC UA to Modbus gateway and map ports 4840 (OPC UA) and 5020 (Modbus) of the container to ports 4840 and 5020 on your host machine, respectively.

### Accessing the Gateway

The OPC UA server will be accessible at `opc.tcp://localhost:4840`. The Modbus server will be accessible at `localhost:5020`. You can connect to these servers using any OPC UA and Modbus clients, respectively.

## Python Dependencies

The project requires the following Python packages:

- `asyncua==1.1.0`
- `pymodbus==3.6.8`

These dependencies are listed in the `requirements.txt` file and are installed during the Docker image build process.

## Scripts

### `opcua-modbus-gw.py`

This is the main script that initializes and runs the OPC UA to Modbus gateway. It leverages the `asyncua` and `pymodbus` libraries to handle OPC UA and Modbus TCP communications.

### `entrypoint.sh`

This shell script serves as the entry point for the Docker container. It simply runs the `opcua-modbus-gw.py` script:

```sh
#!/bin/sh
python /usr/src/app/opcua-modbus-gw.py "$@"
```

## Dockerfile

The `Dockerfile` is used to create the Docker image for the project. Below is a brief explanation of each step:

1. **Base Image**: Uses the official Python 3.8 image.
2. **Set Working Directory**: Sets the working directory to `/usr/src/app`.
3. **Copy Files**: Copies the project files into the container.
4. **Install Dependencies**: Installs the required Python packages using `pip`.
5. **Set Entrypoint**: Specifies `entrypoint.sh` as the entry point script.

```Dockerfile
# Use official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make ports 4840 and 5020 available to the world outside this container
EXPOSE 4840
EXPOSE 5020

# Run entrypoint.sh when the container launches
ENTRYPOINT ["sh", "entrypoint.sh"]
```

## Contributing

If you wish to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a new Pull Request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

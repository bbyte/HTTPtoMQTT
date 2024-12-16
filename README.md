# HTTP to MQTT Bridge

A lightweight service that bridges HTTP GET requests to MQTT messages. This project was created specifically to integrate Shelly Door/Window sensors with MQTT-based home automation systems, as Shelly door sensors only support HTTP callbacks but not direct MQTT communication.

## Why This Project?

While Shelly offers excellent IoT devices, their Door/Window sensors don't support direct MQTT communication, which is a common protocol in home automation setups. This bridge solves this limitation by:

1. Accepting HTTP callbacks from Shelly Door sensors
2. Converting these HTTP requests into MQTT messages
3. Publishing them to your MQTT broker

This enables you to:
- Integrate Shelly Door sensors with Home Assistant or other MQTT-based platforms
- Keep your home automation system consistent by using MQTT throughout
- Maintain a unified message bus for all your IoT devices

### Example Use Case

When setting up a Shelly Door sensor:
1. Configure the sensor's "Internet & Security → Actions" settings
2. Set the URL to: `http://your-server:8080/shelly/door/sensor1/state`
3. The bridge will publish to MQTT topic: `shelly/door/sensor1/state`

This way, your MQTT-based automation system can subscribe to these topics and react to door/window state changes.

## Features

- Converts HTTP GET requests to MQTT messages
- Configurable HTTP port and MQTT broker settings
- Runs as a system daemon (systemd service)
- Automatic reconnection to MQTT broker
- Logging with rotation
- URL path to MQTT topic conversion

## Requirements

- Python 3.6+
- MQTT Broker (e.g., Mosquitto)
- Linux system with systemd (for service installation)

## Installation

1. Create the installation directory and copy files:
   ```bash
   # Create directory
   sudo mkdir -p /opt/http_to_mqtt
   
   # Copy project files
   sudo cp -r * /opt/http_to_mqtt/
   
   # Create virtual environment
   cd /opt/http_to_mqtt
   sudo python3 -m venv venv
   
   # Install dependencies in virtual environment
   sudo ./venv/bin/pip install -r requirements.txt
   ```

2. Configure the service:
   ```bash
   # Create configuration directory
   sudo mkdir -p /etc/http_to_mqtt

   # Copy and edit configuration file
   sudo cp config.example.yaml /etc/http_to_mqtt/config.yaml
   sudo nano /etc/http_to_mqtt/config.yaml
   ```

3. Install and start the service:
   ```bash
   # Copy service file
   sudo cp http_to_mqtt.service /etc/systemd/system/

   # Reload systemd, enable and start service
   sudo systemctl daemon-reload
   sudo systemctl enable http_to_mqtt
   sudo systemctl start http_to_mqtt
   ```

4. Check service status:
   ```bash
   sudo systemctl status http_to_mqtt
   ```

5. View logs:
   ```bash
   # If logging is enabled in config.yaml
   sudo tail -f /var/log/http_to_mqtt.log
   
   # Or view systemd logs
   sudo journalctl -u http_to_mqtt -f
   ```

## Configuration

The configuration file can be specified in several ways (in order of precedence):

1. Command line argument:
   ```bash
   python run.py --config /path/to/config.yaml
   ```

2. Environment variable:
   ```bash
   export HTTP_TO_MQTT_CONFIG=/path/to/config.yaml
   python run.py
   ```

3. Default locations (checked in order):
   - `/etc/http_to_mqtt/config.yaml`
   - `./config.yaml` (in current directory)

To get started, copy the example configuration file:

```bash
cp config.example.yaml config.yaml
nano config.yaml
```

The configuration file supports the following options:

```yaml
mqtt:
  broker: "localhost"    # MQTT broker address
  port: 1883            # MQTT broker port
  username: ""          # Optional: MQTT username
  password: ""          # Optional: MQTT password

http:
  host: "0.0.0.0"      # Listen on all interfaces
  port: 8080           # HTTP port to listen on

logging:
  enabled: false       # Enable/disable logging
  path: "/var/log/http_to_mqtt.log"  # Log file path
  max_size: 100000    # Max log file size in bytes
  backup_count: 3     # Number of backup files to keep
```

## Usage

The service converts HTTP GET requests to MQTT messages. The URL path is converted to an MQTT topic by replacing slashes with dots.

Examples:
- `http://your-server:8080/home/temperature` → MQTT topic: `home.temperature`
- `http://your-server:8080/sensors/living-room/humidity` → MQTT topic: `sensors.living-room.humidity`

For Shelly Door sensors:
- HTTP URL: `http://your-server:8080/shelly/door/sensor1/state`
- Resulting MQTT topic: `shelly.door.sensor1.state`

You can then subscribe to these topics in your MQTT client:
- Specific sensor: `shelly/door/sensor1/#`
- All door sensors: `shelly/door/#`
- All Shelly devices: `shelly/#`

### Testing

1. Start the service:
   ```bash
   sudo systemctl start http_to_mqtt
   ```

2. Check service status:
   ```bash
   sudo systemctl status http_to_mqtt
   ```

3. Monitor logs:
   ```bash
   sudo tail -f /var/log/http_to_mqtt.log
   ```

4. Test with curl:
   ```bash
   curl http://localhost:8080/test/topic
   ```

## Troubleshooting

1. Check service status:
   ```bash
   sudo systemctl status http_to_mqtt
   ```

2. View logs:
   ```bash
   sudo journalctl -u http_to_mqtt
   tail -f /var/log/http_to_mqtt.log
   ```

3. Common issues:
   - Port already in use: Change the HTTP port in config.yaml
   - MQTT connection failed: Verify broker address and credentials
   - Permission denied: Ensure proper file permissions

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

#!/usr/bin/env python3

from flask import Flask, request
import paho.mqtt.client as mqtt
import yaml
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import json

# Setup logging
def setup_logging(config):
    logger = logging.getLogger(__name__)
    
    if not config.get('logging', {}).get('enabled', False):
        # If logging is disabled, use NullHandler
        logger.addHandler(logging.NullHandler())
        return logger

    log_path = config['logging'].get('path', '/var/log/http_to_mqtt.log')
    max_size = config['logging'].get('max_size', 100000)
    backup_count = config['logging'].get('backup_count', 3)

    # Ensure log directory exists
    log_dir = os.path.dirname(log_path)
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except PermissionError:
            print(f"Error: Cannot create log directory {log_dir}. Please check permissions.", file=sys.stderr)
            sys.exit(1)

    try:
        handler = RotatingFileHandler(log_path, maxBytes=max_size, backupCount=backup_count)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    except PermissionError:
        print(f"Error: Cannot write to log file {log_path}. Please check permissions.", file=sys.stderr)
        sys.exit(1)

    return logger

app = Flask(__name__)

# Load configuration
def load_config(config_path=None):
    # Try in this order:
    # 1. Provided config path
    # 2. Environment variable
    # 3. Default system path
    # 4. Local config
    
    paths = []
    if config_path:
        paths.append(config_path)
    
    if 'HTTP_TO_MQTT_CONFIG' in os.environ:
        paths.append(os.environ['HTTP_TO_MQTT_CONFIG'])
    
    paths.extend([
        '/etc/http_to_mqtt/config.yaml',
        os.path.join(os.getcwd(), 'config.yaml')
    ])
    
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as file:
                    config = yaml.safe_load(file)
                print(f"Using config file: {path}", file=sys.stderr)
                return config
            except Exception as e:
                print(f"Error loading config from {path}: {str(e)}", file=sys.stderr)
    
    print("No valid config file found", file=sys.stderr)
    sys.exit(1)

# Load config first
config = load_config()

# Setup logging with config
logger = setup_logging(config)

# MQTT client setup
def setup_mqtt(config):
    client = mqtt.Client()
    
    if config['mqtt'].get('username') and config['mqtt'].get('password'):
        client.username_pw_set(config['mqtt']['username'], config['mqtt']['password'])
    
    def on_connect(client, userdata, flags, rc):
        logger.info(f"Connected to MQTT broker with result code {rc}")
    
    def on_disconnect(client, userdata, rc):
        logger.warning(f"Disconnected from MQTT broker with result code {rc}")
        
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    
    client.connect(config['mqtt']['broker'], config['mqtt']['port'], 60)
    client.loop_start()
    return client

# Setup MQTT client
mqtt_client = setup_mqtt(config)

@app.route('/<path:topic>', methods=['GET', 'POST'])
def forward_to_mqtt(topic):
    try:
        # Use the URL path directly as MQTT topic
        mqtt_topic = topic
        
        # Prepare payload from different sources
        payload = {}
        
        # Add query parameters if any
        if request.args:
            payload.update(request.args.to_dict())
        
        # Add JSON body if present
        if request.is_json:
            payload.update(request.get_json())
        # Add form data if present
        elif request.form:
            payload.update(request.form.to_dict())
        # Add raw data if present
        elif request.data:
            try:
                payload.update(json.loads(request.data))
            except json.JSONDecodeError:
                payload['data'] = request.data.decode('utf-8')
        
        # If no payload was found, set a default value
        if not payload:
            payload = {"state": "triggered", "timestamp": request.timestamp}
        
        # Convert payload to JSON string
        mqtt_payload = json.dumps(payload)
        
        # Publish to MQTT
        mqtt_client.publish(mqtt_topic, mqtt_payload, qos=1)
        logger.info(f"Published message to topic: {mqtt_topic}, payload: {mqtt_payload}")
        
        return {"status": "success", "topic": mqtt_topic, "payload": payload}, 200
    except Exception as e:
        logger.error(f"Error publishing message: {str(e)}")
        return {"status": "error", "message": str(e)}, 500

if __name__ == '__main__':
    app.run(
        host=config['http']['host'],
        port=config['http']['port']
    )

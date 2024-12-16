#!/usr/bin/env python3

import yaml
import os
import sys
import subprocess
import argparse

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

def main():
    parser = argparse.ArgumentParser(description='HTTP to MQTT Bridge')
    parser.add_argument('--config', '-c', help='Path to config file')
    args = parser.parse_args()

    config = load_config(args.config)
    host = config['http']['host']
    port = config['http']['port']
    
    # Construct Gunicorn command
    cmd = [
        'gunicorn',
        'http_to_mqtt:app',
        '-b', f'{host}:{port}',
        '--log-level', 'info'
    ]
    
    # Execute Gunicorn
    try:
        subprocess.run(cmd)
    except Exception as e:
        print(f"Error starting server: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

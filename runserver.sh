#!/bin/bash

gunicorn hive_config_server.wsgi --bind 0.0.0.0:8000
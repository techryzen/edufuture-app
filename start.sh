#!/bin/bash
gunicorn wsgi:application --bind 0.0.0.0:$PORT 
#!/bin/bash

# Reload nginx daemon
sudo systemctl daemon-reload

# Remove default symlink in sites-enabled directory
sudo rm -f /etc/nginx/sites-enabled/default

# Copy nginx configuration file to sites-available directory
sudo cp /home/ubuntu/RideOnWay/nginx/nginx.conf /etc/nginx/sites-available/SoftwareEngg

# Create symlink to enable the nginx configuration
sudo ln -sf /etc/nginx/sites-available/SoftwareEngg /etc/nginx/sites-enabled/

# Add www-data user to ubuntu group
sudo usermod -aG ubuntu www-data

# Restart nginx service
sudo systemctl restart nginx

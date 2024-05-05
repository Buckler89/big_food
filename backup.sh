#!/bin/sh
# MongoDB Backup Script
# Set the environment variables if not set
MONGO_HOST=${MONGO_HOST:-mongo}
MONGO_PORT=${MONGO_PORT:-27017}
BACKUP_NAME="backup_$(date +%Y-%m-%d_%H-%M-%S).gz"

# Create backup
mongodump --host $MONGO_HOST --port $MONGO_PORT --archive=/backup/$BACKUP_NAME --gzip

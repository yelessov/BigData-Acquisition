#!/bin/bash

# Lab 3: Real-Time Traffic Monitoring with Kafka & Spark Streaming
# Quick start script to run the entire lab workflow

set -e

LAB_DIR="/Users/yelessov/Desktop/movie-hadoop-project/lab3"
SCRIPTS_DIR="$LAB_DIR/scripts"
DATA_DIR="$LAB_DIR/data"
PYTHON="/opt/homebrew/bin/python3.11"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}     LAB3: Smart City Traffic Monitor       ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}     Kafka + Real-time Data Streaming       ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Main workflow
print_header

# Step 1: Check Docker Services
print_step "Step 1: Checking Docker Services..."
if docker ps | grep -q "kafka"; then
    print_info "Kafka broker is running"
else
    print_error "Kafka broker not running. Starting docker-compose..."
    cd "$LAB_DIR"
    docker-compose up -d
    sleep 3
    print_info "Docker services started"
fi
echo ""

# Step 2: Verify Python environment
print_step "Step 2: Verifying Python environment..."
if ! $PYTHON -c "import confluent_kafka" 2>/dev/null; then
    print_info "Installing confluent-kafka..."
    $PYTHON -m pip install confluent-kafka -q
fi
print_info "Python 3.11 and confluent-kafka ready"
echo ""

# Step 3: Generate traffic data if needed
print_step "Step 3: Verifying traffic data..."
if [ ! -f "$DATA_DIR/traffic_sensors.csv" ] || [ $(wc -l < "$DATA_DIR/traffic_sensors.csv") -lt 100 ]; then
    print_info "Generating traffic sensor data..."
    mkdir -p "$DATA_DIR"
    cd "$SCRIPTS_DIR"
    $PYTHON generate_traffic.py
    print_info "Data generated: $(wc -l < $DATA_DIR/traffic_sensors.csv) records"
else
    print_info "Traffic data exists: $(wc -l < $DATA_DIR/traffic_sensors.csv) records"
fi
echo ""

# Step 4: Start Producer and Consumer
print_step "Step 4: Starting Kafka Producer and Consumer..."
print_info "Producer: Streaming traffic sensor data to Kafka..."

cd "$SCRIPTS_DIR"

# Start producer in background
$PYTHON producer.py > /tmp/producer_lab3.log 2>&1 &
PRODUCER_PID=$!
echo "   PID: $PRODUCER_PID"

sleep 2

# Start consumer
print_info "Consumer: Displaying real-time traffic statistics..."
echo "   Press Ctrl+C to stop"
echo ""

$PYTHON consumer_simple.py

# Cleanup on exit
trap "kill $PRODUCER_PID 2>/dev/null; exit" INT
wait

#!/bin/bash

# BigData-Acquisition Master Run Script
# Provides quick access to all lab workflows

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════════════════╗"
    echo "║        BigData-Acquisition Lab Runner                 ║"
    echo "║    Choose a lab to execute its workflow               ║"
    echo "╚═══════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_menu() {
    echo -e "${BLUE}Available Labs:${NC}"
    echo ""
    echo -e "${GREEN}1)${NC} Lab 1: Big Data Movie Analytics with Hadoop MapReduce"
    echo "   Files: movies.csv, ratings.csv"
    echo "   Output: Average ratings per movie"
    echo ""
    echo -e "${GREEN}2)${NC} Lab 2: Cyber Intrusion Detection with Apache Spark"
    echo "   Files: network_traffic.csv (synthetic)"
    echo "   Output: ML-based attack classification"
    echo ""
    echo -e "${GREEN}3)${NC} Lab 3: Real-Time Traffic Monitoring with Kafka"
    echo "   Files: traffic_sensors.csv (synthetic)"
    echo "   Output: Real-time speed aggregation per highway"
    echo ""
    echo -e "${GREEN}0)${NC} Exit"
    echo ""
}

run_lab1() {
    echo -e "${YELLOW}Starting Lab 1...${NC}"
    cd /Users/yelessov/Desktop/movie-hadoop-project/lab1 && bash run.sh
}

run_lab2() {
    echo -e "${YELLOW}Starting Lab 2...${NC}"
    cd /Users/yelessov/Desktop/movie-hadoop-project/lab2 && bash run.sh
}

run_lab3() {
    echo -e "${YELLOW}Starting Lab 3...${NC}"
    cd /Users/yelessov/Desktop/movie-hadoop-project/lab3 && bash run_lab3.sh
}

# Main loop
print_header
print_menu

while true; do
    echo -e "${BLUE}Enter your choice (0-3):${NC} "
    read -r choice
    
    case $choice in
        1)
            run_lab1
            ;;
        2)
            run_lab2
            ;;
        3)
            run_lab3
            ;;
        0)
            echo -e "${GREEN}Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Please enter 0-3.${NC}"
            echo ""
            ;;
    esac
done

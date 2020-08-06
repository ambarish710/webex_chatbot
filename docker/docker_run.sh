#!/usr/bin/env bash

# Make sure docker engine is installed on the machine
# And information.yaml is properly updated

# Creating ChatBot utility tar
tar -cvzf chatbot_utility.tar.gz --exclude="chatbot_utility.tar.gz" -C ../ .

# Building docker image from Dockerfile
docker build -t chatbot .

# Running newly created docker image
docker run -td -p 8012:8012 --name chatbot chatbot

# Starting Zookeeper and Kafka
docker exec -it --detach=true chatbot /root/CiscoWork/chatbot_utility/kafka_2.12-2.3.0/bin/zookeeper-server-start.sh /root/CiscoWork/chatbot_utility/kafka_2.12-2.3.0/config/zookeeper.properties
docker exec -it --detach=true chatbot /root/CiscoWork/chatbot_utility/kafka_2.12-2.3.0/bin/kafka-server-start.sh /root/CiscoWork/chatbot_utility/kafka_2.12-2.3.0/config/server.properties

# Stating ChatBot Utility
#docker exec -it --detach=true chatbot nohup sh run.sh

#!/bin/bash

# Prompt the user for input
read -p "Enter your Telegram API Token: " TELEGRAM_API_TOKEN
while [ -z "$TELEGRAM_API_TOKEN" ]; do
  echo "Telegram API Token cannot be empty. Please provide it:"
  read -p "Enter your Telegram API Token: " TELEGRAM_API_TOKEN
done

read -p "Enter your OpenAI API Key: " OPENAI_API_KEY
while [ -z "$OPENAI_API_KEY" ]; do
  echo "OpenAI API Key cannot be empty. Please provide it:"
  read -p "Enter your OpenAI API Key: " OPENAI_API_KEY
done

read -p "Enter your LangChain API Key [default: <your-langchain-api-key>]: " LANGCHAIN_API_KEY
LANGCHAIN_API_KEY=${LANGCHAIN_API_KEY:-<your-langchain-api-key>}
read -p "Enter your RabbitMQ username [default: user]: " RABBITMQ_USER
RABBITMQ_USER=${RABBITMQ_USER:-user}
read -p "Enter your RabbitMQ password [default: password]: " RABBITMQ_PASSWORD
RABBITMQ_PASSWORD=${RABBITMQ_PASSWORD:-password}
read -p "Enter your RabbitMQ Erlang Cookie [default: password]: " RABBITMQ_ERLANG_COOKIE
RABBITMQ_ERLANG_COOKIE=${RABBITMQ_ERLANG_COOKIE:-password}
read -p "Enter your Redis password [default: password]: " REDIS_PASSWORD
REDIS_PASSWORD=${REDIS_PASSWORD:-password}

# Ask if Google tools should be used
read -p "Do you want to use Google tools? (y/n): " USE_GOOGLE_TOOLS

# Define paths
CHATBOT_SECRETS_SRC=".kubernetes/converso_chatbot/secrets-example.yaml"
CHATBOT_SECRETS_DST=".kubernetes/converso_chatbot/secrets.yaml"
TELEGRAM_SECRETS_SRC=".kubernetes/converso_telegram_bot/secrets-example.yaml"
TELEGRAM_SECRETS_DST=".kubernetes/converso_telegram_bot/secrets.yaml"
RABBITMQ_SECRETS_SRC=".kubernetes/rabbitmq/secrets-example.yaml"
RABBITMQ_SECRETS_DST=".kubernetes/rabbitmq/secrets.yaml"
REDIS_SECRETS_SRC=".kubernetes/redis/secrets-example.yaml"
REDIS_SECRETS_DST=".kubernetes/redis/secrets.yaml"
DOCKERFILE=".docker/converso_chatbot.Dockerfile"

# Step 1: Copy the chatbot secrets file and adjust the values
echo "Setting up secrets for Converso Chatbot..."
cp $CHATBOT_SECRETS_SRC $CHATBOT_SECRETS_DST
sed -i "s/<your-token>/$TELEGRAM_API_TOKEN/" $CHATBOT_SECRETS_DST
sed -i "s/<your-openai-api-key>/$OPENAI_API_KEY/" $CHATBOT_SECRETS_DST
sed -i "s/<your-langchain-api-key>/$LANGCHAIN_API_KEY/" $CHATBOT_SECRETS_DST
sed -i "s/<rabbitmq-user>/$RABBITMQ_USER/" $CHATBOT_SECRETS_DST
sed -i "s/<rabbitmq-password>/$RABBITMQ_PASSWORD/" $CHATBOT_SECRETS_DST
sed -i "s/<redis-password>/$REDIS_PASSWORD/" $CHATBOT_SECRETS_DST

# Step 2: Copy the Telegram bot secrets file and adjust the values
echo "Setting up secrets for Converso Telegram Bot..."
cp $TELEGRAM_SECRETS_SRC $TELEGRAM_SECRETS_DST
sed -i "s/<your-token>/$TELEGRAM_API_TOKEN/" $TELEGRAM_SECRETS_DST
sed -i "s/<your-openai-api-key>/$OPENAI_API_KEY/" $TELEGRAM_SECRETS_DST
sed -i "s/<rabbitmq-user>/$RABBITMQ_USER/" $TELEGRAM_SECRETS_DST
sed -i "s/<rabbitmq-password>/$RABBITMQ_PASSWORD/" $TELEGRAM_SECRETS_DST

# Step 3: Create RabbitMQ secrets file
echo "Creating RabbitMQ secrets file..."
cp $RABBITMQ_SECRETS_SRC $RABBITMQ_SECRETS_DST
sed -i "s/<rabbitmq-user>/$RABBITMQ_USER/" $RABBITMQ_SECRETS_DST
sed -i "s/<rabbitmq-password>/$RABBITMQ_PASSWORD/" $RABBITMQ_SECRETS_DST
sed -i "s/<rabbitmq-erlang-cookie>/$RABBITMQ_ERLANG_COOKIE/" $RABBITMQ_SECRETS_DST

# Step 4: Create Redis secrets file
echo "Creating Redis secrets file..."
cp $REDIS_SECRETS_SRC $REDIS_SECRETS_DST
sed -i "s/<redis-password>/$REDIS_PASSWORD/" $REDIS_SECRETS_DST

# Step 5: Handle Google credentials and Dockerfile modification
if [[ "$USE_GOOGLE_TOOLS" == "y" || "$USE_GOOGLE_TOOLS" == "Y" ]]; then
  echo "Please generate your Google OAuth credentials by following this link: https://developers.google.com/identity/protocols/oauth2/web-server#creatingcred and place the client_secret.json in the root folder."
  echo "Ensuring 'COPY client_secret.json /' line is uncommented in Dockerfile..."
  sed -i 's/^#COPY client_secret.json /COPY client_secret.json /' $DOCKERFILE
else
  echo "Ensuring 'COPY client_secret.json /' line is commented in Dockerfile..."
  sed -i 's/^COPY client_secret.json /#COPY client_secret.json /' $DOCKERFILE
fi

echo "Setup completed successfully!"

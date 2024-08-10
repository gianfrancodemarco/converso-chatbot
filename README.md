Source code for the paper Converso: Improving LLM Chatbot Interfaces and Task
Execution via Conversational Forms.

The standalone python package is available at https://pypi.org/project/converso/ (source code: https://github.com/gianfrancodemarco/converso)

### How to run 

1) Create a copy of `.kubernetes/converso_chatbot/secrets-example.yaml` named `.kubernetes/converso_chatbot/secrets.yaml` and adjust the values
2) Create a copy of `.kubernetes/converso_telegram_bot/secrets-example.yaml` named `.kubernetes/converso_telegram_bot/secrets.yaml` and adjust the values
3) If using the Google tools, [generate credentials](https://developers.google.com/identity/protocols/oauth2/web-server#creatingcred) and place the `client_secret.json` file in the root of the project. Otherwise, comment out line 31 in `.docker/converso_chatbot.Dockerfile`
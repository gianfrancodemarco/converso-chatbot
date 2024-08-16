Source code for the paper Converso: Improving LLM Chatbot Interfaces and Task
Execution via Conversational Forms.

The standalone python package is available at https://pypi.org/project/converso/ (source code: https://github.com/g   ianfrancodemarco/converso)

## Setup the dev environment


To set up the development environment for the Converso project, run the setup script.

```bash
./setup-dev.sh
```

The script will prompt you for various configuration details and adjust your environment accordingly. You will be asked for:

- Telegram API Token
- OpenAI API Key
- LangChain API Key (default: \<your-langchain-api-key>)
- RabbitMQ credentials (username, password, Erlang cookie; default values are provided)
- Redis password (default: password)
- Whether to use Google tools (the script will guide you to generate OAuth credentials if yes)


## How to run

### Kubernetes + Helm + Kind + Skaffold

#### Prerequisites

Ensure you have the following dependencies installed (versions listed are those tested, but other versions should also work):

- [`docker`](https://www.docker.com/) ~v27.1.1
- [`helm`](https://helm.sh/docs/intro/install/) ~v3.15.3
- [`skaffold`](https://skaffold.dev/docs/install/) ~v2.12.0
- [`kubectl`](https://kubernetes.io/docs/tasks/tools/install-kubectl/) ~v1.29.4
- [`kind`](https://kind.sigs.k8s.io/) ~v0.23.0 or [`minikube`](https://minikube.sigs.k8s.io/docs/start/) ~v1.33.1

#### Run the project

### Docker Compose 
- [`docker`](https://www.docker.com/) ~v27.1.1

## Credits

- https://github.com/LuisFX
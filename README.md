# Desafio Técnico C2S - Agente Virtual de Venda de Veículos
# Augusto Aguiar Zambon -> https://www.linkedin.com/in/gutozambon/

Este projeto foi desenvolvido como parte do Desafio Técnico para a vaga de Desenvolvedor Python na C2S. O objetivo é criar uma aplicação de terminal com um agente virtual que auxilia usuários a encontrar veículos, consultando um banco de dados populado com dados fictícios através de um protocolo de comunicação cliente-servidor (MCP).

## Tecnologias Utilizadas

* **Python 3.9+**
* **FastAPI**: Para a criação do servidor MCP (backend RESTful API).
* **Uvicorn**: Servidor ASGI para rodar a aplicação FastAPI.
* **SQLAlchemy**: ORM para interação com o banco de dados PostgreSQL.
* **Pydantic**: Para validação de dados e schemas da API.
* **PostgreSQL (v12+)**: Banco de dados relacional. (O desenvolvimento usou v17)
* **Ollama**: Para execução local de Modelos de Linguagem Grandes (LLMs).
    * **Phi-3 Mini (`phi3:mini`)**: Modelo LLM específico utilizado pelo agente virtual.
* **Requests**: Biblioteca HTTP para o cliente MCP.
* **Pandas**: Para manipulação de dados (utilizado no script de população do banco).
* **Docker (Opcional, não implementado neste guia inicial)**: Para conteinerização futura.

## Pré-requisitos

Antes de começar, garanta que você tem os seguintes softwares instalados e configurados:

1.  **Python**: Versão 3.9 ou superior. Verifique com `python --version`.
2.  **Git**: Para clonar o repositório.
3.  **PostgreSQL**: Servidor de banco de dados. Certifique-se de que o serviço está rodando.
4.  **Ollama**:
    * Instale Ollama seguindo as instruções em [https://ollama.com/](https://ollama.com/).
    * Após a instalação, baixe o modelo `phi3:mini` executando no seu terminal:
        ```bash
        ollama pull phi3:mini
        ```
    * Certifique-se que o serviço do Ollama esteja em execução.

## Configuração do Ambiente

Siga os passos abaixo para configurar o projeto localmente:

### 1. Clonar o Repositório
```bash
git clone https://github.com/GutoZambon/desafio_c2s_automoveis.git
cd desafio_c2s_automoveis

2. Configurar Ambiente Virtual Python e Dependências
É altamente recomendado usar um ambiente virtual para isolar as dependências do projeto.


# Criar ambiente virtual (ex: .venv)
python -m venv .venv

# Ativar o ambiente virtual
# No Windows (PowerShell):
.venv\Scripts\Activate.ps1
# No Windows (CMD):
# .venv\Scripts\activate.bat
# No macOS/Linux:
# source .venv/bin/activate

# Instalar as dependências Python
pip install -r requirements.txt 

3. Configurar o Banco de Dados PostgreSQL
Conecte-se ao seu servidor PostgreSQL (usando pgAdmin, psql, DBeaver, etc.).
Crie um novo banco de dados. No desafio, usamos o nome TesteC2S:

    CREATE DATABASE "TesteC2S";
    Crie um novo usuário (role) para a aplicação. No desafio, usamos:
    Usuário: Teste
    Senha: teste123


    CREATE USER "Teste" WITH PASSWORD 'teste123';
    Conceda privilégios ao usuário no banco de dados:


    ALTER DATABASE "TesteC2S" OWNER TO "Teste";
    GRANT ALL PRIVILEGES ON DATABASE "TesteC2S" TO "Teste";
    GRANT ALL ON SCHEMA public TO "Teste"; 

4. Configurar Variáveis da Aplicação (Conexão com Banco)
    As credenciais de conexão com o banco de dados estão definidas no arquivo app/core/config.py. Atualmente, elas são (ou podem ser configuradas para usar variáveis de ambiente):
    DB_USER = "Teste"
    DB_PASSWORD = "teste123"
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "TesteC2S"
    Verifique se estas configurações correspondem ao seu ambiente PostgreSQL. O arquivo config.py está preparado para usar os.getenv, então você pode opcionalmente criar um arquivo .env na raiz do projeto para sobrescrever esses padrões de forma segura:

5. Criar Tabelas e Popular o Banco de Dados Inicialmente
    Este projeto inclui uma função para criar as tabelas no banco e populá-las com dados de um arquivo CSV.

    Execute app/main.py a partir da raiz do projeto (onde está a pasta .venv e app):


# Certifique-se que o ambiente virtual está ativado
python app/main.py
Após a execução bem-sucedida (verifique os logs no terminal, deve indicar que as tabelas foram criadas e dados populados), comente novamente a linha setup_inicial_do_banco() em app/main.py para evitar que o setup seja executado toda vez que o agente iniciar.
Executando a Aplicação
A aplicação consiste em dois componentes principais que precisam ser executados separadamente (em terminais diferentes): o Servidor MCP (backend) e o Agente Virtual no Terminal (frontend).

Passo 1: Iniciar o Servidor MCP (Backend FastAPI)
Este servidor lida com as requisições de busca de veículos.

Abra um terminal na raiz do projeto (desafio_c2s_automoveis/).
Certifique-se de que seu ambiente virtual Python esteja ativado.
Execute o comando:

python run_mcp_server.py
O servidor FastAPI/Uvicorn deverá iniciar. Você verá mensagens como:
Iniciando servidor MCP FastAPI em http://localhost:8000
Documentação da API (Swagger UI): http://localhost:8000/docs
...
Uvicorn running on [http://0.0.0.0:8000](http://0.0.0.0:8000)
Mantenha este terminal aberto enquanto utiliza a aplicação.
Passo 2: Iniciar o Agente Virtual no Terminal (Frontend)
Este é o programa com o qual o usuário interage.

Abra outro terminal na raiz do projeto (desafio_c2s_automoveis/).
Certifique-se de que seu ambiente virtual Python esteja ativado.
Certifique-se que o Servidor MCP (Passo 1) e o Ollama (com phi3:mini carregado e rodando) estejam em execução.
Execute o comando:
Bash

python app/main.py
O agente virtual "Alfred" iniciará a conversa no terminal.
Estrutura do Projeto (Principais Pastas)
desafio_c2s_automoveis/
├── .venv/                      # Ambiente virtual Python
├── app/                        # Código principal da aplicação
│   ├── agent/                  # Lógica do agente virtual de terminal
│   │   └── terminal_agent.py
│   ├── core/                   # Configurações centrais (config.py)
│   │   └── config.py
│   ├── database/               # Modelos SQLAlchemy e configuração de sessão
│   │   ├── models.py
│   │   └── session.py
│   ├── mcp/                    # Lógica do "Model Context Protocol"
│   │   ├── client.py           # Cliente MCP (usado pelo agente)
│   │   ├── schemas.py          # Schemas Pydantic para API
│   │   └── server.py           # Rotas FastAPI do servidor MCP
│   └── main.py                 # Ponto de entrada para o agente de terminal (e setup inicial do DB)
├── scripts/                    # Scripts auxiliares
│   ├── populate_db.py          # Contém a lógica de população (chamada pelo setup_inicial_do_banco)
│   └── veiculos_fabricados_brasil_reais.csv # Dados para popular o banco
├── tests/                      # Testes automatizados (espaço para desenvolvimento futuro)
├── .gitignore                  # Arquivos ignorados pelo Git
├── README.md                   # Este arquivo
├── requirements.txt            # Dependências Python
└── run_mcp_server.py           # Ponto de entrada para iniciar o servidor FastAPI

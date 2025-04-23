# CrewAI + MCP (Model Context Protocol) Integration Examples

Este repositório demonstra como integrar agentes CrewAI com ferramentas disponibilizadas por servidores MCP (Model Context Protocol), como o GitHub MCP, Context7 e Sequential Thinking.

## Descrição

O objetivo é mostrar como utilizar a classe `MCPServerAdapter` (obtida dos testes do `crewai-tools`) para conectar CrewAI a diferentes servidores MCP via STDIO, permitindo que os agentes utilizem as ferramentas desses servidores para realizar tarefas.

Os exemplos incluem:
- Testes isolados para conectar e usar ferramentas do Context7 e GitHub MCP.
- Um script combinado que utiliza CrewAI com agentes especializados para Sequential Thinking (planejamento) e GitHub MCP (execução).

## Pré-requisitos

- **Python**: Versão 3.12 ou superior (conforme `pyproject.toml`).
- **Docker**: Necessário para executar o servidor GitHub MCP. Certifique-se de que o Docker Desktop (ou equivalente) esteja instalado e em execução.
- **uv**: Gerenciador de pacotes Python usado neste projeto (`pip install uv`).
- **Tokens de API**:
    - `GITHUB_PERSONAL_ACCESS_TOKEN`: Um token de acesso pessoal do GitHub com escopos apropriados (ex: `repo`, `read:user`). [Como criar um PAT](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
    - `GEMINI_API_KEY` (ou outra LLM): Chave de API para o modelo de linguagem grande (LLM) usado pelo CrewAI (neste exemplo, Google Gemini).

## Instalação

1.  **Clone o repositório:**
    ```bash
    git clone [<URL_DO_SEU_REPOSITORIO>](https://github.com/matheus896/mcp-tool-crewai)
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    # Usando venv (padrão Python)
    python -m venv .venv
    source .venv/bin/activate # Linux/macOS
    # ou
    .\.venv\Scripts\activate # Windows

    # Ou usando conda, etc.
    ```

3.  **Instale as dependências com `uv`:**
    ```bash
    uv pip install -r requirements.txt # Se existir um requirements.txt gerado por uv
    # OU (recomendado se uv.lock estiver atualizado)
    uv sync
    # OU (para instalar do pyproject.toml)
    uv pip install .
    ```
    *Nota: O `pyproject.toml` especifica as dependências, incluindo `crewai`, `crewai-tools[mcp]`, `mcp`, e `mcpadapt`.*

## Configuração

1.  **Crie um arquivo `.env`:**
    Copie o arquivo `.env.example` para `.env`:
    ```bash
    cp .env.example .env
    ```

2.  **Edite o arquivo `.env`:**
    Substitua os valores de placeholder pelas suas chaves de API reais:
    ```
    GITHUB_PERSONAL_ACCESS_TOKEN="ghp_SEU_TOKEN_AQUI"
    GEMINI_API_KEY="SEU_GEMINI_API_KEY_AQUI"
    # OPENAI_API_KEY="SEU_OPENAI_API_KEY_AQUI" # Se usar OpenAI
    ```

## Arquivos Principais

-   **`mcp_tool.py`**: Contém a implementação da classe `MCPServerAdapter`, adaptada dos testes do repositório `crewai-tools`. Esta classe é crucial para a conexão com os servidores MCP. *Nota: O nome original no seu projeto pode ser `mcpadapter.py`, ajuste conforme necessário.*
-   **`test_mcp_context7.py`**: Script de teste isolado para conectar ao servidor Context7 MCP via `npx` e usar a ferramenta `resolve-library-id`.
-   **`test_mcp_github.py`**: Script de teste isolado para conectar ao servidor GitHub MCP via Docker e usar a ferramenta `get_me`.
-   **`crewai_mcp_combined.py`**: Script principal que demonstra a integração com CrewAI, utilizando dois servidores MCP (Sequential Thinking e GitHub) e dois agentes especializados (Planejador e Executor). Usa a abordagem de gerenciamento manual da conexão MCP (`.stop()` no `finally`).
-   **`pyproject.toml`**: Define as dependências do projeto e metadados.
-   **`.env.example`**: Arquivo de exemplo para as variáveis de ambiente necessárias.

## Como Executar

Certifique-se de que seu ambiente virtual está ativado e o Docker está rodando.

1.  **Testar Conexão Context7 (Isolado):**
    ```bash
    python test_mcp_context7.py
    ```

2.  **Testar Conexão GitHub (Isolado):**
    ```bash
    python test_mcp_github.py
    ```

3.  **Executar Exemplo Combinado CrewAI + Sequential Thinking + GitHub:**
    ```bash
    python crewai_mcp_combined.py
    ```
    Este script iniciará os adaptadores MCP, definirá os agentes e tarefas, e executará a `Crew`. A saída mostrará o processo de pensamento dos agentes e o resultado final.

## Observações

-   **`MCPServerAdapter`**: A classe `MCPServerAdapter` usada aqui foi obtida dos arquivos de teste do `crewai-tools`, pois não estava diretamente disponível na biblioteca no momento da criação deste exemplo. Se/quando for oficialmente incluída na `crewai-tools`, o import poderá ser ajustado (`from crewai_tools import MCPServerAdapter`).
-   **Erro Asyncio no Windows**: Pode incluir um erro comum do `asyncio` no Windows relacionado ao fechamento de subprocessos, geralmente ocorre no final da execução e não impede o funcionamento principal do script.
-   **Gerenciamento da Conexão MCP**: O script `crewai_mcp_combined.py` utiliza a abordagem de instanciar `MCPServerAdapter` e chamar `.stop()` manualmente em um bloco `finally`, conforme recomendado para garantir que a conexão permaneça ativa durante a execução da `Crew`.

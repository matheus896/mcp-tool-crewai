import os
from dotenv import load_dotenv
from mcp import StdioServerParameters
from mcp_tool import MCPServerAdapter
from crewai import Agent, Task, Crew, LLM

# Carrega variáveis de ambiente
load_dotenv()

llm = LLM(model="gemini/gemini-2.0-flash-001")

github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
if not github_token:
    raise ValueError("A variável de ambiente GITHUB_PERSONAL_ACCESS_TOKEN não está definida.")

# Parâmetros para o servidor MCP Github (STDIO via Docker)
github_mcp_params = StdioServerParameters(
    command="docker",
    args=[
        "run", "-i", "--rm",
        "-e", f"GITHUB_PERSONAL_ACCESS_TOKEN={github_token}",
        "ghcr.io/github/github-mcp-server"
    ],
    env={"GITHUB_PERSONAL_ACCESS_TOKEN": github_token, **os.environ}
)

try:
    # Conecta ao GitHub MCP e obtém suas ferramentas
    with MCPServerAdapter(github_mcp_params) as github_tools:
        print(f"Ferramentas carregadas do GitHub MCP: {[tool.name for tool in github_tools]}")

        # Define o agente CrewAI usando apenas as ferramentas do MCP Github
        researcher = Agent(
            role='Especialista GitHub',
            goal='Obter informações do usuário autenticado no GitHub usando MCP',
            backstory=(
                "Você é um especialista em interagir com o GitHub usando as ferramentas do MCP."
            ),
            verbose=True,
            llm=llm,
            allow_delegation=False,
            tools=github_tools
        )

        # Define uma tarefa simples usando a ferramenta get_me
        task1 = Task(
            description="Utilize a ferramenta 'get_me' para obter informações do usuário autenticado no GitHub.",
            expected_output="Um relatório com os dados do usuário autenticado.",
            agent=researcher
        )

        crew = Crew(
            agents=[researcher],
            tasks=[task1],
            verbose=True
        )

        print("\n--- Iniciando a Crew ---")
        result = crew.kickoff()
        print("\n--- Resultado da Crew ---")
        print(result)

except Exception as e:
    print(f"Ocorreu um erro: {e}")

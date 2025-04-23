import os
import traceback
from dotenv import load_dotenv
from mcp import StdioServerParameters
from mcp_tool import MCPServerAdapter
from crewai import Agent, Task, Crew, LLM

# Carrega variáveis de ambiente
load_dotenv()

llm = LLM(model="gemini/gemini-2.0-flash-001")

# --- Configuração dos Servidores MCP ---

# Sequential Thinking
sequential_thinking_params = StdioServerParameters(
    command="cmd",
    args=["/c", "npx", "@modelcontextprotocol/server-sequential-thinking", "-y"],
)

# GitHub MCP
github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
if not github_token:
    raise ValueError("A variável de ambiente GITHUB_PERSONAL_ACCESS_TOKEN não está definida.")

github_mcp_params = StdioServerParameters(
    command="docker",
    args=[
        "run", "-i", "--rm",
        "-e", f"GITHUB_PERSONAL_ACCESS_TOKEN={github_token}",
        "ghcr.io/github/github-mcp-server"
    ],
    env={"GITHUB_PERSONAL_ACCESS_TOKEN": github_token, **os.environ}
)

# --- Inicialização dos Adaptadores MCP (fora do try/finally principal) ---
# Isso garante que as variáveis existam no finally, mesmo se a inicialização falhar.
seq_adapter = None
github_adapter = None
seq_tools_list = []
github_tools_list = []

try:
    print("Inicializando adaptador Sequential Thinking MCP...")
    seq_adapter = MCPServerAdapter(sequential_thinking_params)
    seq_tools_list = seq_adapter.tools # Obtém ferramentas após start() implícito no __init__
    print(f"Ferramentas carregadas do Sequential Thinking: {[tool.name for tool in seq_tools_list]}")

    print("\nInicializando adaptador GitHub MCP...")
    github_adapter = MCPServerAdapter(github_mcp_params)
    github_tools_list = github_adapter.tools # Obtém ferramentas
    print(f"Ferramentas carregadas do GitHub MCP: {[tool.name for tool in github_tools_list]}")

    print(f"\nTotal de ferramentas MCP carregadas: {len(seq_tools_list) + len(github_tools_list)}")

    # --- Definição dos Agentes e Crew (dentro do try principal) ---
    print("\nDefinindo Agentes e Tarefas...")

    planner_agent = Agent(
        role='Planejador Estratégico',
        goal='Criar planos detalhados passo-a-passo para tarefas complexas usando Sequential Thinking',
        backstory=(
            "Você é um especialista em decompor problemas complexos em etapas acionáveis "
            "usando a ferramenta Sequential Thinking."
        ),
        verbose=True,
        llm=llm,
        allow_delegation=False,
        tools=seq_tools_list
    )

    github_executor_agent = Agent(
        role='Executor de Tarefas GitHub',
        goal='Executar ações específicas no GitHub conforme instruído, usando as ferramentas MCP',
        backstory=(
            "Você é um especialista em interagir com a API do GitHub através das ferramentas MCP, "
            "seguindo planos ou instruções diretas para realizar buscas, obter dados, etc."
        ),
        verbose=True,
        llm=llm,
        allow_delegation=False,
        tools=github_tools_list
    )

    task1_plan = Task(
        description="Crie um plano passo-a-passo detalhado para encontrar repositórios sobre 'crewai-tools' no GitHub.",
        expected_output="Um plano claro e sequencial em etapas para realizar a busca no GitHub.",
        agent=planner_agent
    )

    task2_search = Task(
        description="Siga o plano criado na tarefa anterior e execute a busca por repositórios chamados 'crewai-tools' no GitHub usando a ferramenta 'search_repositories'.",
        expected_output="Uma lista dos primeiros repositórios encontrados no GitHub chamados 'crewai-tools', conforme o plano.",
        agent=github_executor_agent,
        context=[task1_plan]
    )

    task3_get_user = Task(
        description="Utilize a ferramenta 'get_me' para obter informações do usuário autenticado no GitHub.",
        expected_output="Os dados JSON do usuário autenticado no GitHub.",
        agent=github_executor_agent
    )

    crew = Crew(
        agents=[planner_agent, github_executor_agent],
        tasks=[task1_plan, task2_search, task3_get_user],
        verbose=True
    )

    print("\n--- Iniciando a Crew ---")
    result = crew.kickoff()
    print("\n--- Resultado Final da Crew ---")
    print(result)

except Exception as e:
    print(f"\nOcorreu um erro durante a execução da Crew: {e}")
    traceback.print_exc()

finally:
    # --- Parada dos Adaptadores MCP ---
    print("\nParando adaptadores MCP...")
    if seq_adapter:
        try:
            print("Parando Sequential Thinking adapter...")
            seq_adapter.stop()
        except Exception as stop_e:
            print(f"Erro ao parar Sequential Thinking adapter: {stop_e}")
    if github_adapter:
        try:
            print("Parando GitHub adapter...")
            github_adapter.stop()
        except Exception as stop_e:
            print(f"Erro ao parar GitHub adapter: {stop_e}")
    print("\nScript finalizado.")

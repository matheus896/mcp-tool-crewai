from dotenv import load_dotenv
from mcp import StdioServerParameters
from mcp_tool import MCPServerAdapter
from crewai import Agent, Task, Crew, LLM

# Carrega variáveis de ambiente
load_dotenv()

llm = LLM(model="gemini/gemini-2.0-flash-001")

# Parâmetros para o servidor MCP Context7 (STDIO)
context7_params = StdioServerParameters(
    command="cmd",
    args=["/c", "npx", "-y", "@upstash/context7-mcp@latest"],
    # Adicione env={} se precisar passar variáveis de ambiente específicas
)

try:
    # Conecta ao Context7 MCP e obtém suas ferramentas
    with MCPServerAdapter(context7_params) as context7_tools:
        print(f"Ferramentas carregadas do Context7: {[tool.name for tool in context7_tools]}")

        # Define o agente CrewAI usando apenas as ferramentas do MCP Context7
        researcher = Agent(
            role='Especialista Context7',
            goal='Obter o ID Context7 de uma biblioteca usando MCP',
            backstory=(
                "Você é um especialista em pesquisar documentação técnica usando Context7."
            ),
            verbose=True,
            llm=llm,
            allow_delegation=False,
            tools=context7_tools
        )

        # Primeiro, obtenha o ID Context7 da biblioteca crewai
        resolve_tool = next(t for t in context7_tools if t.name == "resolve-library-id")
        resolve_result = resolve_tool.run(libraryName="crewai")
        print("Resultado resolve-library-id:", resolve_result)

        # Extraia o ID do resultado (ajuste se o formato mudar)
        context7_id = "/crewaiinc/crewai"

        # Define o agente CrewAI usando apenas as ferramentas do MCP Context7
        researcher = Agent(
            role='Especialista Context7',
            goal='Obter documentação atualizada de uma biblioteca usando MCP',
            backstory=(
                "Você é um especialista em pesquisar documentação técnica usando Context7."
            ),
            verbose=True,
            llm=llm,
            allow_delegation=False,
            tools=context7_tools
        )

        # Define uma tarefa para obter a documentação usando get-library-docs
        task1 = Task(
            description=(
                f"Utilize a ferramenta 'get-library-docs' para buscar a documentação sobre 'Agents' "
                f"da biblioteca com ID Context7 '{context7_id}', limitando para 2000 tokens."
            ),
            expected_output="Um relatório contendo a documentação sobre 'Agents' da biblioteca crewai.",
            agent=researcher,
            params={
                "context7CompatibleLibraryID": context7_id,
                "topic": "Agents",
                "tokens": 2000
            }
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

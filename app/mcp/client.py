import requests  
import json      
from typing import List, Dict, Any # Para tipagem

# URL base do nosso servidor MCP.
# No futuro, isso poderia vir de um arquivo de configuração ou variável de ambiente.
MCP_API_BASE_URL = "http://localhost:8000" # Servidor FastAPI rodando localmente na porta 8000

def consultar_veiculos_mcp(filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Envia uma requisição ao servidor MCP para buscar veículos com base nos filtros.

    Args:
        filtros (Dict[str, Any]): Um dicionário contendo os filtros.
            Exemplo: {"marca": "Toyota", "ano_producao_inicial_min": 2010}
            A estrutura deste dicionário deve ser compatível com o schema
            `VeiculoFiltros` definido no servidor.

    Returns:
        List[Dict[str, Any]]: Uma lista de dicionários, onde cada dicionário
                              representa um veículo conforme retornado pelo servidor.
                              Retorna uma lista vazia em caso de não encontrar resultados
                              ou alguns tipos de erro de comunicação.
    
    Raises:
        requests.exceptions.ConnectionError: Se não conseguir se conectar ao servidor.
    """
    endpoint_busca = f"{MCP_API_BASE_URL}/mcp/buscar_veiculos/"
    
    print(f"CLIENTE_MCP: Enviando filtros para {endpoint_busca}: {filtros}") # Log para depuração

    try:
        # Faz a requisição POST, enviando os filtros no corpo como JSON.
        # Timeout de 10 segundos para a requisição.
        response = requests.post(endpoint_busca, json=filtros, timeout=10)

        # Verifica se a resposta do servidor indica um erro HTTP (status code 4xx ou 5xx)
        response.raise_for_status()  # Se houver erro, levanta uma exceção HTTPError

        # Se a requisição foi bem-sucedida (status 2xx), converte a resposta JSON.
        # O servidor FastAPI já retorna uma lista de objetos VeiculoResposta.
        resultados = response.json()
        
        if not isinstance(resultados, list):
            print(f"CLIENTE_MCP AVISO: Resposta do servidor não é uma lista: {type(resultados)}")
            return [] # Ou trate como um erro mais sério

        print(f"CLIENTE_MCP: Recebidos {len(resultados)} veículos do servidor.") # Log para depuração
        return resultados

    except requests.exceptions.HTTPError as http_err:
        # Erros como 404 Not Found, 422 Unprocessable Entity, 500 Internal Server Error, etc.
        print(f"CLIENTE_MCP ERRO HTTP: {http_err}")
        print(f"CLIENTE_MCP ERRO HTTP: Status Code: {response.status_code}")
        try:
            # Tenta mostrar o corpo da resposta de erro, que pode conter detalhes do FastAPI
            print(f"CLIENTE_MCP ERRO HTTP: Detalhes: {response.json()}")
        except json.JSONDecodeError:
            print(f"CLIENTE_MCP ERRO HTTP: Corpo da resposta não é JSON: {response.text}")
        return [] # Retorna lista vazia para o agente tratar
        
    except requests.exceptions.ConnectionError as conn_err:
        print(f"CLIENTE_MCP ERRO DE CONEXÃO: Não foi possível conectar ao servidor em {endpoint_busca}.")
        print(f"CLIENTE_MCP ERRO DE CONEXÃO: Detalhe: {conn_err}")
        print("CLIENTE_MCP ERRO DE CONEXÃO: Verifique se o servidor MCP (run_mcp_server.py) está em execução.")
        raise # Relança a exceção para que a aplicação principal saiba da falha crítica
        
    except requests.exceptions.Timeout as timeout_err:
        print(f"CLIENTE_MCP ERRO: Timeout durante a requisição para {endpoint_busca}: {timeout_err}")
        return []
        
    except requests.exceptions.RequestException as req_err:
        # Outros erros da biblioteca requests (ex: JSON mal formado na resposta)
        print(f"CLIENTE_MCP ERRO DE REQUISIÇÃO: {req_err}")
        return []
    except Exception as e:
        print(f"CLIENTE_MCP ERRO INESPERADO: {e}")
        return []

# Bloco para testar este cliente diretamente (opcional)
if __name__ == "__main__":
    print("--- Iniciando teste do cliente MCP ---")
    print("IMPORTANTE: Certifique-se de que o servidor MCP (run_mcp_server.py) está rodando em outro terminal!")

    # Teste 1: Sem filtros
    print("\n[TESTE 1] Buscando todos os veículos (sem filtros)...")
    try:
        veiculos_todos = consultar_veiculos_mcp({})
        if veiculos_todos:
            print(f"Encontrados {len(veiculos_todos)} veículos.")
            print("Exemplo do primeiro veículo:", veiculos_todos[0])
        else:
            print("Nenhum veículo encontrado ou ocorreu um erro leve na comunicação.")
    except requests.exceptions.ConnectionError:
        print("Teste 1 falhou devido a erro de conexão. O servidor está rodando?")
    except Exception as e:
        print(f"Erro inesperado no Teste 1: {e}")

    # Teste 2: Com filtros
    filtros_exemplo = {
        "marca": "Volkswagen",
        "ano_producao_inicial_min": 2000,
        "transmissao_automatica": False # Lembre-se que no JSON é true/false (minúsculo)
    }
    print(f"\n[TESTE 2] Buscando veículos com filtros: {filtros_exemplo}...")
    try:
        veiculos_filtrados = consultar_veiculos_mcp(filtros_exemplo)
        if veiculos_filtrados:
            print(f"Encontrados {len(veiculos_filtrados)} veículos para os filtros.")
            for v in veiculos_filtrados[:3]: # Mostra os 3 primeiros
                print(f"  - {v.get('marca')} {v.get('modelo')} ({v.get('ano_producao_inicial')}), Transmissão Automática: {v.get('transmissao_automatica')}")
        else:
            print("Nenhum veículo encontrado para os filtros ou ocorreu um erro leve na comunicação.")
    except requests.exceptions.ConnectionError:
        print("Teste 2 falhou devido a erro de conexão. O servidor está rodando?")
    except Exception as e:
        print(f"Erro inesperado no Teste 2: {e}")
    
    print("\n--- Teste do cliente MCP finalizado ---")
# app/agent/terminal_agent.py
import ollama
import json
import re # Para expressões regulares na extração de filtros
from typing import List, Dict, Any, Optional

from app.mcp.client import consultar_veiculos_mcp # Cliente MCP
import requests # Para tratar exceção de conexão do cliente MCP

OLLAMA_MODEL = 'phi3:mini'

# Filtros conhecidos pelo nosso sistema/VeiculoFiltros.
# Isso ajuda a guiar o LLM e nossa lógica de extração.
FILTROS_CONHECIDOS = [
    "marca", "modelo", "ano_producao_inicial_min", "ano_producao_inicial_max",
    "ano_producao_final_especifico", "combustivel", "num_portas",
    "transmissao_automatica", "potencia_cv_min", "potencia_cv_max"
]

def interagir_com_llm(historico_conversa: List[Dict[str, str]]) -> Optional[str]:
    """Envia o histórico da conversa para o Ollama e retorna a resposta do assistente."""
    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=historico_conversa,
            # Options para tentar controlar a verbosidade e o formato, se necessário:
            # options={
            #     "temperature": 0.5, # Menor para respostas mais focadas
            # }
        )
        return response['message']['content']
    except Exception as e:
        print(f"\nALFRED (ERRO): Desculpe, não consegui pensar agora. (Erro Ollama: {e})")
        print("ALFRED (ERRO): Verifique se o Ollama está rodando e o modelo foi baixado: `ollama pull phi3:mini`")
        return None

def parse_filtros_da_resposta_llm(texto_llm: str) -> Dict[str, Any]:
    filtros_extraidos = {}
    # Encontra TODAS as ocorrências da tag 'FILTROS_COLETADOS:' e seus conteúdos na mesma linha.
    matches = list(re.finditer(r"FILTROS_COLETADOS:\s*([^\n]*)", texto_llm, re.IGNORECASE))

    if not matches:
        # print("ALFRED (INFO PARSER): Tag 'FILTROS_COLETADOS:' não encontrada na resposta do LLM.")
        return {} # Retorna vazio se a tag não for encontrada

    # Pega o conteúdo do ÚLTIMO match.
    filtros_str = matches[-1].group(1).strip()
    
    if not filtros_str or filtros_str.lower() == "nenhum":
        # print("ALFRED (INFO PARSER): LLM indicou 'nenhum' filtro ou string de filtros vazia na última tag.")
        return {} 
    
    pares = filtros_str.split(',')
    for par_raw in pares:
        par = par_raw.strip()
        if '=' not in par:
            continue
        
        chave_bruta, valor_bruto = par.split('=', 1)
        chave = chave_bruta.strip()
        valor = valor_bruto.strip()

        # Normaliza chaves com acentos que o LLM possa usar
        if chave == "potência_cv_min": chave = "potencia_cv_min"
        if chave == "potência_cv_max": chave = "potencia_cv_max"

        placeholders_nulos = ['nenhum', 'n/a', 'na', 'null', 'qualquer', '']
        if valor.lower() in placeholders_nulos:
            continue

        if chave not in FILTROS_CONHECIDOS:
            continue

        try:
            if chave in ["ano_producao_inicial_min", "ano_producao_inicial_max", 
                         "ano_producao_final_especifico", "num_portas", 
                         "potencia_cv_min", "potencia_cv_max"]:
                
                # Extrai apenas os dígitos para garantir que seja um número.
                # Isso removerá '>', '<', '.' de '1.8', etc.
                # O prompt deve instruir o LLM a fornecer o número correto.
                valor_numerico_str = re.sub(r"[^0-9]", "", valor)
                if not valor_numerico_str: # Se não sobrar nenhum dígito
                    print(f"ALFRED (AVISO PARSER): Valor '{valor}' não resultou em número válido para filtro '{chave}'. Ignorando.")
                    continue
                filtros_extraidos[chave] = int(valor_numerico_str)

            elif chave == "transmissao_automatica":
                if valor.lower() in ['true', 'sim', 'verdadeiro']:
                    filtros_extraidos[chave] = True
                elif valor.lower() in ['false', 'nao', 'não', 'falso']:
                    filtros_extraidos[chave] = False
                else:
                    continue 
            else: # marca, modelo, combustivel
                # Remove qualquer texto após uma quebra de linha no valor do filtro
                valor_limpo = valor.split('\n')[0].strip()
                if not valor_limpo or valor_limpo.lower() in placeholders_nulos:
                    continue
                filtros_extraidos[chave] = valor_limpo.capitalize() if chave in ["marca", "modelo", "combustivel"] else valor_limpo
        except ValueError:
            # print(f"ALFRED (AVISO PARSER): Não foi possível processar o valor '{valor}' para o filtro '{chave}'. Ignorando.")
            pass # Simplesmente não adiciona o filtro se a conversão/processamento falhar
            
    return filtros_extraidos

def exibir_resultados(veiculos: List[Dict[str, Any]]):
    """Formata e exibe os veículos encontrados."""
    # (Mantida a mesma função exibir_resultados da sua versão anterior, ela está boa)
    if not veiculos:
        print("\nALFRED: Puxa, não encontrei nenhum veículo com esses critérios no momento em nosso inventário.")
        return

    print("\nALFRED: Ótimo! Com base nos filtros, encontrei estes veículos em nosso inventário:")
    for i, v in enumerate(veiculos):
        print(f"\n--- Veículo {i+1} ---")
        print(f"  Marca: {v.get('marca')} | Modelo: {v.get('modelo')}")
        print(f"  Ano Fab.: {v.get('ano_producao_inicial')}", end="")
        if v.get('ano_producao_final'):
            print(f" (Modelo até: {v.get('ano_producao_final')})", end="")
        print(f"\n  Potência: {v.get('potencia_cv')} CV | Combustível: {v.get('combustivel')}")
        print(f"  Portas: {v.get('num_portas')} | Transmissão Automática: {'Sim' if v.get('transmissao_automatica') else 'Não'}")
        if v.get('porta_malas_litros') is not None:
            print(f"  Porta-malas: {v.get('porta_malas_litros')} L")
        # Adicione mais campos se necessário, conforme o VeiculoResposta
    print("\n--------------------")

def run_conversation_agent():
    print("--- Alfred: Seu Assistente Virtual de Veículos ---")
    print(f"Modelo LLM em uso: {OLLAMA_MODEL} (via Ollama)")
    print("Para começar, diga o que você procura ou simplesmente 'olá'.")
    print("Digite 'buscar' quando quiser que eu procure, ou 'sair' para terminar.")

    system_prompt = (
        "Você é Alfred, um assistente virtual especialista em ajudar usuários a encontrar veículos "
        "DENTRO DE UM INVENTÁRIO ESPECÍFICO da nossa concessionária. Você NÃO tem conhecimento sobre carros fora deste inventário. "
        "Seu objetivo principal é coletar informações (filtros) do usuário para realizar uma busca nesse inventário. "
        "Os ÚNICOS filtros válidos que você pode coletar e usar são: "
        "marca (ex: Fiat), modelo (ex: Strada), ano_producao_inicial_min (ex: 2019), "
        "ano_producao_inicial_max (ex: 2022), ano_producao_final_especifico (ex: 2021), "
        "combustivel (valores comuns: Flex, Diesel, Gasolina, Etanol, Elétrico, Híbrido), num_portas (ex: 2, 4), "
        "transmissao_automatica (boolean: true ou false), potencia_cv_min (ex: 70), potencia_cv_max (ex: 150). "
        
        "Se o usuário mencionar 'X cilindradas de potencia' ou 'motor X.Y litros', você DEVE ESCLARECER que filtra por POTÊNCIA em CV (cavalos). Pergunte: 'Qual a potência mínima em CV que você gostaria?' ou 'Qual a potência máxima em CV?'. "
        "NÃO use o valor de cilindradas ou litros diretamente como CV. Por exemplo, se o usuário disser 'mais de 150 de potencia' ou 'potencia acima de 150 CV', interprete isso como `potencia_cv_min=150` na sua lista de filtros. NÃO use símbolos como '>' ou '<' nos valores dos filtros. "
        
        "INSTRUÇÃO CRÍTICA PARA FILTROS: Ao final de CADA UMA das suas respostas, forneça a tag `FILTROS_COLETADOS:` APENAS UMA VEZ. "
        "Nesta tag, liste SOMENTE os filtros para os quais o USUÁRIO FORNECEU UM VALOR ESPECÍFICO E CONCRETO ou que você CONFIRMOU CLARAMENTE com ele nesta conversa ATUAL. "
        "Se o usuário NÃO especificou um valor para um filtro (ex: não falou de marca, não falou de ano), NÃO inclua essa chave de filtro na lista `FILTROS_COLETADOS:`. NÃO preencha filtros com valores padrão, 'nenhum', 'n/a', ou 'qualquer', ou valores que o usuário não pediu (como anos aleatórios). "
        "Exemplo CORRETO: Se o usuário apenas disse 'quero um carro flex com mais de 150cv', sua tag DEVE SER 'FILTROS_COLETADOS: combustivel=Flex, potencia_cv_min=150'. Não inclua `marca`, `ano`, etc., se não foram ditos. "
        "Se NENHUM filtro foi fornecido ou confirmado pelo usuário ATÉ O MOMENTO, escreva 'FILTROS_COLETADOS: nenhum'. "
        "A linha de FILTROS_COLETADOS deve ser a ÚLTIMA parte estruturada da sua resposta e não deve conter texto adicional depois dos filtros. "
        
        "Se o usuário disser 'buscar', o sistema Python usará os filtros da sua última tag 'FILTROS_COLETADOS:'. Se esta tag indicar 'nenhum', peça por critérios antes de o sistema buscar."
    )

    historico_conversa = [{'role': 'system', 'content': system_prompt}]
    filtros_para_busca = {} # Armazena o último conjunto de filtros válidos parseados do LLM

    while True:
        entrada_usuario = input("\nVocê: ").strip()

        if entrada_usuario.lower() == 'sair':
            print("\nALFRED: Entendido. Até a próxima!")
            break
        
        historico_conversa.append({'role': 'user', 'content': entrada_usuario})
        
        # Sempre interage com o LLM para obter a próxima resposta e a lista de filtros atualizada
        resposta_llm = interagir_com_llm(historico_conversa)

        if resposta_llm:
            print(f"\nALFRED: {resposta_llm}")
            historico_conversa.append({'role': 'assistant', 'content': resposta_llm})
            
            filtros_da_llm = parse_filtros_da_resposta_llm(resposta_llm)
            filtros_para_busca = filtros_da_llm 
            if filtros_para_busca:
                print(f"ALFRED (INFO): Filtros atuais (confirmados pelo LLM): {filtros_para_busca}")
            else:
                 print(f"ALFRED (INFO): Nenhum filtro ativo no momento (conforme LLM).")
            
            realizar_busca_agora = False
            entrada_usuario_lower = entrada_usuario.lower() # entrada_usuario é da iteração atual do loop

            # Palavras-chave explícitas de busca na fala do usuário
            palavras_gatilho_busca_usuario = ["buscar", "procure", "pesquise", "liste", "mostre", "encontre", "ache"]
            # Frases no início da fala do usuário que indicam busca
            frases_gatilho_inicio_usuario = [
                "me traga", "me retorne", "quero ver", "gostaria de ver", 
                "quais carros você tem com", "tem algum carro com", "procuro por carros com"
            ]

            if any(palavra in entrada_usuario_lower for palavra in palavras_gatilho_busca_usuario):
                realizar_busca_agora = True
                print(f"ALFRED (INFO): Usuário solicitou busca com palavra-gatilho: '{entrada_usuario}'")
            
            if not realizar_busca_agora:
                for frase_inicio in frases_gatilho_inicio_usuario:
                    if entrada_usuario_lower.startswith(frase_inicio):
                        realizar_busca_agora = True
                        print(f"ALFRED (INFO): Usuário solicitou busca com frase-gatilho: '{entrada_usuario}'")
                        break
            
            # Se o usuário não pediu explicitamente para buscar, vemos se o LLM sugeriu
            # e o usuário pode ter confirmado implicitamente ou explicitamente na sua última fala
            if not realizar_busca_agora and re.search(
                r"posso buscar|devo procurar|gostaria de ver as opções|realizar a busca|vamos ver o que encontro|posso prosseguir com a busca", 
                resposta_llm, re.IGNORECASE
            ):
                # Se o LLM sugere, e já temos filtros, podemos perguntar ao usuário para confirmar.
                # Ou, se a sugestão do LLM é forte e os filtros parecem bons, podemos arriscar.
                # Por agora, vamos ser um pouco mais diretos se o LLM sugere e temos filtros.
                if filtros_para_busca:
                    print("ALFRED (INFO): LLM sugeriu a busca e temos filtros.")
                    # Você pode adicionar uma confirmação explícita aqui se preferir:
                    # confirm_llm_sugestao = input("ALFRED: Notei que podemos ter filtros suficientes. Deseja buscar agora? (s/n): ").strip().lower()
                    # if confirm_llm_sugestao == 's':
                    #     realizar_busca_agora = True
                    # Por enquanto, vamos assumir que se o LLM sugeriu e temos filtros, é uma boa hora.
                    realizar_busca_agora = True 
                else:
                    print("ALFRED (INFO): LLM sugeriu busca, mas não há filtros claros para usar. Continuando a conversa.")
            
            if realizar_busca_agora:
                if not filtros_para_busca: 
                    print("\nALFRED: Para buscar, preciso de alguns filtros ou uma confirmação do que já conversamos. O que você gostaria de procurar?")
                else:
                    print(f"\nALFRED: Entendido! Buscando em nosso inventário com os filtros: {filtros_para_busca}")
                    try:
                        resultados = consultar_veiculos_mcp(filtros_para_busca)
                        exibir_resultados(resultados)
                        # (Opcional: lógica de feedback para LLM ou reset de filtros)
                    except requests.exceptions.ConnectionError:
                         print("\nALFRED: Não consegui me conectar ao servidor de veículos para buscar. Verifique se ele está ativo.")
                    except Exception as e:
                        print(f"\nALFRED: Ocorreu um erro inesperado durante a busca: {e}")
        else: # Erro ao falar com Ollama
            continue
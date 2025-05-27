import ollama # Biblioteca para interagir com o Ollama
import json   # Para o caso de tentarmos parsear JSON de filtros no futuro
from typing import List, Dict, Any

# Importa nosso cliente MCP
# (Certifique-se que o sys.path está ajustado no main.py para que 'app.' funcione)
from app.mcp.client import consultar_veiculos_mcp

# Modelo Ollama que escolhemos
OLLAMA_MODEL = 'phi3:mini'

# Filtros que o nosso agente tentará extrair (baseado no VeiculoFiltros)
# Isso ajuda a guiar o LLM e nossa lógica de extração.
FILTROS_CONHECIDOS = [
    "marca", "modelo", "ano_producao_inicial_min", "ano_producao_inicial_max",
    "ano_producao_final_especifico", "combustivel", "num_portas",
    "transmissao_automatica", "potencia_cv_min", "potencia_cv_max"
]

def interagir_com_llm(historico_conversa: List[Dict[str, str]]) -> str:
    """Envia o histórico da conversa para o Ollama e retorna a resposta do assistente."""
    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=historico_conversa,
            # stream=False # Mantenha False para respostas completas, True para streaming caractere a caractere
        )
        return response['message']['content']
    except Exception as e:
        print(f"\nALFRED (ERRO): Desculpe, não consegui pensar agora. (Erro Ollama: {e})")
        print("ALFRED (ERRO): Verifique se o Ollama está rodando e o modelo foi baixado: `ollama pull phi3:mini`")
        return None

def tentar_extrair_filtros_da_conversa(texto_llm: str, texto_usuario: str) -> Dict[str, Any]:
    """
    Tenta extrair filtros da resposta do LLM ou do input do usuário.
    Esta é uma função SIMPLIFICADA e pode ser bastante melhorada com técnicas de NLP ou
    instruindo o LLM a retornar filtros de forma estruturada.
    """
    filtros_extraidos = {}
    # Exemplo muito básico (e não muito robusto):
    # Você pode melhorar isso com regex, ou pedindo ao LLM para formatar os filtros.
    texto_combinado = (texto_llm + " " + texto_usuario).lower()

    # Marcas (exemplo)
    marcas_comuns = ["volkswagen", "fiat", "chevrolet", "ford", "hyundai", "toyota", "renault", "honda", "jeep", "nissan"]
    for marca_candidata in marcas_comuns:
        if marca_candidata in texto_combinado:
            filtros_extraidos["marca"] = marca_candidata.capitalize() # Capitaliza para o filtro

    # Combustível (exemplo)
    combustiveis_comuns = ["gasolina", "etanol", "flex", "diesel", "elétrico", "híbrido"]
    for comb_candidato in combustiveis_comuns:
        if comb_candidato in texto_combinado:
            filtros_extraidos["combustivel"] = comb_candidato.capitalize()
            
    # Transmissão Automática (exemplo)
    if "automático" in texto_combinado or "automatica" in texto_combinado:
        filtros_extraidos["transmissao_automatica"] = True
    elif "manual" in texto_combinado:
        filtros_extraidos["transmissao_automatica"] = False
        
    # Ano (exemplo simplificado - buscaria por 4 dígitos)
    import re
    match_ano = re.search(r'\b(19\d{2}|20\d{2})\b', texto_combinado)
    if match_ano:
        # Decide se é min ou max baseado no contexto (aqui simplificamos para min)
        filtros_extraidos["ano_producao_inicial_min"] = int(match_ano.group(0))

    return filtros_extraidos


def exibir_resultados(veiculos: List[Dict[str, Any]]):
    """Formata e exibe os veículos encontrados."""
    if not veiculos:
        print("\nALFRED: Puxa, não encontrei nenhum veículo com esses critérios no momento.")
        return

    print("\nALFRED: Ótimo! Encontrei estes veículos que podem te interessar:")
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
        if v.get('capacidade_carga_kg') is not None:
            print(f"  Cap. Carga: {v.get('capacidade_carga_kg')} kg")
        if v.get('tanque_litros') is not None:
            print(f"  Tanque: {v.get('tanque_litros')} L")
        if v.get('autonomia_km_l') is not None:
            print(f"  Autonomia: {v.get('autonomia_km_l')} km/l")
    print("\n--------------------")


def run_conversation_agent():
    """Função principal que roda o loop de conversa com o agente Alfred."""
    print("--- Alfred: Seu Assistente Virtual de Veículos ---")
    print(f"Modelo LLM em uso: {OLLAMA_MODEL} (via Ollama)")
    print("Para começar, diga o que você procura ou simplesmente 'olá'.")
    print("Digite 'buscar' quando quiser que eu procure com os filtros coletados, ou 'sair' para terminar.")

    # Prompt inicial do sistema para guiar o LLM
    system_prompt = (
        "Você é Alfred, um assistente virtual amigável e vendedor de carros. "
        "Seu objetivo é conversar com o usuário para entender que tipo de veículo ele procura. "
        "Faça perguntas sobre marca, modelo, ano de fabricação, tipo de combustível, número de portas, e se quer transmissão automática. Não pergunte sobre preço. "
        "Conduza a conversa de forma natural. Quando o usuário indicar que quer buscar, ou você achar que tem filtros suficientes, "
        "confirme os filtros que entendeu e pergunte se pode prosseguir com a busca. "
        "Tente ser conciso e objetivo nas suas respostas e perguntas."
    )
    historico_conversa = [{'role': 'system', 'content': system_prompt}]
    filtros_coletados = {}

    while True:
        entrada_usuario = input("\nVocê: ").strip()

        if entrada_usuario.lower() == 'sair':
            print("\nALFRED: Entendido. Até a próxima!")
            break
        
        historico_conversa.append({'role': 'user', 'content': entrada_usuario})
        
        # Se o usuário explicitamente pede para buscar
        if entrada_usuario.lower() == 'buscar':
            if not filtros_coletados:
                print("\nALFRED: Ainda não coletamos nenhum filtro. Pode me dizer o que procura?")
                historico_conversa.append({'role': 'assistant', 'content': "Ainda não coletamos nenhum filtro. Pode me dizer o que procura?"})
                continue

            print(f"\nALFRED: Entendido! Buscando veículos com os filtros: {filtros_coletados}")
            try:
                resultados = consultar_veiculos_mcp(filtros_coletados)
                exibir_resultados(resultados)
                # Opcional: Resetar filtros e conversa após uma busca bem-sucedida?
                # filtros_coletados = {}
                # historico_conversa = [{'role': 'system', 'content': system_prompt}]
            except requests.exceptions.ConnectionError:
                 print("\nALFRED: Não consegui me conectar ao servidor de veículos para buscar. Verifique se ele está ativo.")
            except Exception as e:
                print(f"\nALFRED: Ocorreu um erro inesperado durante a busca: {e}")
            continue # Volta para o input do usuário após a busca

        # Interage com o LLM para obter a próxima resposta/pergunta
        resposta_llm = interagir_com_llm(historico_conversa)

        if resposta_llm:
            print(f"\nALFRED: {resposta_llm}")
            historico_conversa.append({'role': 'assistant', 'content': resposta_llm})
            
            # Tenta extrair/atualizar filtros da conversa (abordagem simplificada)
            novos_filtros = tentar_extrair_filtros_da_conversa(resposta_llm, entrada_usuario)
            if novos_filtros:
                filtros_coletados.update(novos_filtros)
                print(f"ALFRED (INFO): Filtros atualizados: {filtros_coletados}")
        else:
            # Se interagir_com_llm retornou None (erro de comunicação com Ollama)
            # A mensagem de erro já foi impressa dentro de interagir_com_llm
            # Podemos apenas continuar o loop para o usuário tentar de novo ou sair
            pass
import sys # Importe o módulo sys
from pathlib import Path

script_file_path = Path(__file__).resolve()
app_dir = script_file_path.parent
project_root = app_dir.parent
sys.path.append(str(project_root))

from app.agent.terminal_agent import run_conversation_agent
from scripts.populate_db import popula_dados, criar_tabelas_se_nao_existirem
import os 

def inicia_dados():
    criar_tabelas_se_nao_existirem()
    
    # Caminho para o diretório onde o main.py está (a pasta 'app')
    diretorio_atual_script = Path(__file__).resolve().parent

    # Caminho para a raiz do projeto (um nível acima da pasta 'app')
    raiz_do_projeto = diretorio_atual_script.parent

    # Nome do arquivo CSV
    nome_arquivo_csv = "veiculos_fabricados_brasil_reais.csv"

    # Monta o caminho completo para o arquivo CSV
    csv_path = raiz_do_projeto / "scripts" / nome_arquivo_csv
      
    # Se a função popula_dados espera uma string como caminho:
    if csv_path.exists():
        popula_dados(str(csv_path)) # Converte o objeto Path para string        
    else:
        print(f"ERRO: Arquivo CSV não encontrado em: {str(csv_path)}")
    

if __name__ == "__main__":        
    inicia_dados()
    run_conversation_agent()
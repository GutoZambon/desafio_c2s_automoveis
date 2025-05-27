import pandas as pd
from sqlalchemy.orm import Session
from app.database.session import SessionLocal, engine
from app.database.models import Veiculo, Base

def criar_tabelas_se_nao_existirem():
    """
    Cria todas as tabelas definidas nos modelos SQLAlchemy (herdadas de Base)
    no banco de dados conectado pelo engine, caso ainda não existam.
    """
    try:
        print("Verificando e criando tabelas, se necessário...")
        Base.metadata.create_all(bind=engine)
        print("Tabelas prontas.")
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")        
        raise

def popula_dados(csv_file_path: str) -> str:
    """
    Popula o banco de dados com dados de veículos de um arquivo CSV.
    Verifica a existência de veículos antes de inserir para evitar duplicatas.

    Args:
        csv_file_path (str): O caminho para o arquivo CSV contendo os dados dos veículos.

    Returns:
        str: Mensagem indicando o resultado da operação.
    """
    db: Session = SessionLocal()
    novos_veiculos_adicionados = 0

    try:
        # Lê o arquivo CSV para um DataFrame do Pandas
        # 'na_values' garante que strings vazias sejam tratadas como NaN (Not a Number)
        # 'sep' especifica o delimitador do CSV
        df = pd.read_csv(csv_file_path, sep=',', na_values=['', 'NA', 'N/A'])

        # Converte a coluna 'transmissao_automatica' de string para booleanos
        # O CSV contém 'True'/'False' como strings [cite: 1]
        if 'transmissao_automatica' in df.columns:
            df['transmissao_automatica'] = df['transmissao_automatica'].astype(str).str.strip().str.lower().map(
                {'true': True, 'false': False, 'nan': None}
            ).astype(pd.BooleanDtype()) # Usa BooleanDtype para permitir <NA>

        for _, row in df.iterrows():
            # Tratamento de valores que podem ser nulos ou precisam de conversão de tipo
            marca_veiculo = row['marca']
            modelo_veiculo = row['modelo']
            ano_inicial_veiculo = int(row['ano_producao_inicial'])
            potencia_veiculo = int(row['potencia_cv']) # O CSV parece ter CV como inteiro [cite: 1]

            # Para ano_producao_final, que pode ser nulo ou um float como "2021.0" [cite: 1]
            ano_final_val = row.get('ano_producao_final')
            ano_final = None if pd.isna(ano_final_val) else int(float(ano_final_val))

            # Para porta_malas_litros, que pode ser nulo ou float como "470.0" [cite: 1]
            porta_malas_val = row.get('porta_malas_litros')
            porta_malas = None if pd.isna(porta_malas_val) else int(float(porta_malas_val))

            # Para capacidade_carga_kg, que pode ser nulo [cite: 1]
            capacidade_carga_val = row.get('capacidade_carga_kg')
            capacidade_carga = None if pd.isna(capacidade_carga_val) else float(capacidade_carga_val)
            
            # Para tanque_litros
            tanque_val = row.get('tanque_litros')
            tanque = None if pd.isna(tanque_val) else int(float(tanque_val))

            # Para autonomia_km_l
            autonomia_val = row.get('autonomia_km_l')
            autonomia = None if pd.isna(autonomia_val) else float(autonomia_val)
            
            # Para transmissao_automatica (já convertida para Booleano ou pd.NA)
            transmissao_auto_val = row.get('transmissao_automatica')
            transmissao_auto = None if pd.isna(transmissao_auto_val) else bool(transmissao_auto_val)


            # Critério de verificação de duplicidade: marca, modelo, ano_producao_inicial e potencia_cv
            veiculo_existente = db.query(Veiculo).filter(
                Veiculo.marca == marca_veiculo,
                Veiculo.modelo == modelo_veiculo,
                Veiculo.ano_producao_inicial == ano_inicial_veiculo,
                Veiculo.potencia_cv == potencia_veiculo
            ).first()

            if not veiculo_existente:
                novo_veiculo = Veiculo(
                    marca=marca_veiculo,
                    modelo=modelo_veiculo,
                    ano_producao_inicial=ano_inicial_veiculo,
                    ano_producao_final=ano_final,
                    potencia_cv=potencia_veiculo,
                    combustivel=row['combustivel'],
                    num_portas=int(row['num_portas']), # O CSV parece ter num_portas como inteiro [cite: 1]
                    porta_malas_litros=porta_malas,
                    transmissao_automatica=transmissao_auto,
                    capacidade_carga_kg=capacidade_carga,
                    tanque_litros=tanque,
                    autonomia_km_l=autonomia
                )
                db.add(novo_veiculo)
                novos_veiculos_adicionados += 1
        
        if novos_veiculos_adicionados > 0:
            db.commit()
            return f"{novos_veiculos_adicionados} novos veículos incluídos com sucesso."
        else:
            return "Base já populada (nenhum novo veículo do CSV precisou ser adicionado)."

    except FileNotFoundError:
        return f"Erro: Arquivo CSV não encontrado em '{csv_file_path}'."
    except pd.errors.EmptyDataError:
        return f"Erro: Arquivo CSV '{csv_file_path}' está vazio."
    except KeyError as e:
        db.rollback()
        return f"Erro: Coluna esperada não encontrada no CSV: {e}. Verifique o cabeçalho do arquivo."
    except Exception as e:
        db.rollback()
        print(f"Ocorreu um erro inesperado: {e}") # Logar o erro
        # Em um cenário de produção, seria ideal logar o traceback completo.
        # raise e # Re-levantar a exceção pode ser útil para depuração mais profunda.
        return f"Erro ao popular dados: {e}"
    finally:
        db.close()

# Exemplo de como chamar esta função (pode ser de um script main.py ou para teste direto)
if __name__ == "__main__":
    # Este bloco só será executado se o script populate_db.py for chamado diretamente.
    
    # 1. Garante que as tabelas existem no banco de dados.
    #    Isso é importante especialmente na primeira vez que rodar ou em um ambiente de teste.
    criar_tabelas_se_nao_existirem()

    # 2. Define o caminho para o arquivo CSV.
    #    Certifique-se de que o arquivo 'veiculos_fabricados_brasil_reais.csv' esteja no
    #    local correto ou forneça o caminho completo.
    #    Para este exemplo, vamos supor que ele está na pasta raiz do projeto.
    #    Se o script está em 'scripts/' e o CSV na raiz, o caminho seria '../veiculos_fabricados_brasil_reais.csv'
    #    Ou, se o CSV estiver na mesma pasta que este script:
    caminho_do_csv = "veiculos_fabricados_brasil_reais.csv" 
    # Se preferir, pode colocar o CSV na pasta 'scripts' também para facilitar o teste direto.
    # Ou, para um caminho mais robusto a partir da raiz do projeto, se você tiver uma estrutura conhecida:
    # import os
    # project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Vai para duas pastas acima de 'scripts'
    # caminho_do_csv = os.path.join(project_root, "veiculos_fabricados_brasil_reais.csv")


    print(f"Tentando popular o banco de dados com o arquivo: {caminho_do_csv}")
    resultado_populacao = popula_dados(caminho_do_csv)
    print(resultado_populacao)
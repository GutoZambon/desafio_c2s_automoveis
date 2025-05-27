from pydantic import BaseModel, ConfigDict 
from typing import Optional, List

# --------------------
# Schema para os Filtros da Requisição MCP
# --------------------
# Define os campos que o cliente pode enviar para filtrar a busca de veículos.
# Todos os campos são opcionais, o cliente pode enviar quantos quiser (ou nenhum).
class VeiculoFiltros(BaseModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    # Para o ano, podemos permitir um range para o ano_producao_inicial
    ano_producao_inicial_min: Optional[int] = None
    ano_producao_inicial_max: Optional[int] = None
    # Ou um ano específico de produção final (se o modelo já saiu de linha)
    ano_producao_final_especifico: Optional[int] = None
    
    combustivel: Optional[str] = None
    num_portas: Optional[int] = None
    transmissao_automatica: Optional[bool] = None
    potencia_cv_min: Optional[int] = None
    potencia_cv_max: Optional[int] = None
    # Podemos adicionar mais filtros conforme a necessidade, como:
    porta_malas_litros_min: Optional[int] = None
    autonomia_km_l_min: Optional[float] = None

    class Config:
        # Comportamento para campos extras enviados pelo cliente que não estão definidos aqui
        extra = 'forbid' # Rejeita a requisição se campos desconhecidos forem enviados


# --------------------
# Schema para a Resposta MCP (Detalhes do Veículo)
# --------------------
# Define a estrutura de um veículo individual que será retornado pela API.
# Baseado nos campos que temos atualmente no nosso modelo SQLAlchemy `Veiculo`.
class VeiculoResposta(BaseModel):
    id: int                  # ID do veículo no banco
    marca: str
    modelo: str
    ano_producao_inicial: int
    ano_producao_final: Optional[int] = None
    potencia_cv: int         # Conforme modelo SQLAlchemy, não é opcional
    combustivel: str         # Conforme modelo SQLAlchemy, não é opcional
    num_portas: int          # Conforme modelo SQLAlchemy, não é opcional
    porta_malas_litros: Optional[int] = None
    transmissao_automatica: bool # Conforme modelo SQLAlchemy, tem default
    capacidade_carga_kg: Optional[float] = None
    tanque_litros: Optional[int] = None
    autonomia_km_l: Optional[float] = None
   

    class Config:
        model_config = ConfigDict(from_attributes=True)


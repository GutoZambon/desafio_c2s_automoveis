from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List # Para especificar o tipo de retorno como uma lista

# Importações dos nossos módulos
from app.database.session import get_db # Nossa dependência de sessão do banco
from app.database.models import Veiculo  # Nosso modelo SQLAlchemy
from app.mcp.schemas import VeiculoFiltros, VeiculoResposta # Nossos schemas Pydantic

# Cria um APIRouter. Podemos adicionar prefixos e tags se tivermos muitos endpoints.
router = APIRouter(
    prefix="/mcp", # Adiciona um prefixo a todas as rotas definidas neste router
    tags=["MCP - Veículos"], # Agrupa as rotas na documentação Swagger/OpenAPI
)

@router.post("/buscar_veiculos/", response_model=List[VeiculoResposta])
async def buscar_veiculos_endpoint(
    filtros: VeiculoFiltros,        # Corpo da requisição, validado pelo Pydantic
    db: Session = Depends(get_db)   # Injeção de dependência da sessão do banco
):
    """
    Endpoint para buscar veículos com base nos filtros fornecidos.
    O cliente envia um JSON com os filtros, e o servidor retorna
    uma lista de veículos que correspondem.
    """
    query = db.query(Veiculo) # Começa com uma query base para todos os veículos

    # Aplica os filtros dinamicamente
    if filtros.marca:
        # Usamos ilike para busca case-insensitive e parcial (contém)
        query = query.filter(Veiculo.marca.ilike(f"%{filtros.marca}%"))
    
    if filtros.modelo:
        query = query.filter(Veiculo.modelo.ilike(f"%{filtros.modelo}%"))
    
    if filtros.ano_producao_inicial_min is not None:
        query = query.filter(Veiculo.ano_producao_inicial >= filtros.ano_producao_inicial_min)
    
    if filtros.ano_producao_inicial_max is not None:
        query = query.filter(Veiculo.ano_producao_inicial <= filtros.ano_producao_inicial_max)

    if filtros.ano_producao_final_especifico is not None:
        query = query.filter(Veiculo.ano_producao_final == filtros.ano_producao_final_especifico)
        
    if filtros.combustivel:
        query = query.filter(Veiculo.combustivel.ilike(f"%{filtros.combustivel}%"))
        
    if filtros.num_portas is not None:
        query = query.filter(Veiculo.num_portas == filtros.num_portas)
        
    if filtros.transmissao_automatica is not None:
        query = query.filter(Veiculo.transmissao_automatica == filtros.transmissao_automatica)
        
    if filtros.potencia_cv_min is not None:
        query = query.filter(Veiculo.potencia_cv >= filtros.potencia_cv_min)

    if filtros.potencia_cv_max is not None:
        query = query.filter(Veiculo.potencia_cv <= filtros.potencia_cv_max)

    # Execute a query para obter os resultados
    resultados = query.all()

    # O FastAPI cuidará da conversão dos objetos 'Veiculo' (SQLAlchemy)
    # para o schema 'VeiculoResposta' (Pydantic) devido ao `response_model`
    # e `orm_mode = True` no schema.
    # Se nenhum resultado for encontrado, uma lista vazia `[]` será retornada,
    # o que é o comportamento HTTP correto (200 OK com corpo vazio).
    
    return resultados


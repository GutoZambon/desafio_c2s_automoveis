# run_mcp_server.py
from fastapi import FastAPI
import uvicorn

import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path: # Evita adicionar repetidamente se já estiver
    sys.path.append(str(project_root))

from app.mcp.server import router as mcp_router

app = FastAPI(
    title="Servidor MCP - Desafio C2S Veículos",
    description="Este servidor implementa o 'Model Context Protocol' para busca de veículos.",
    version="0.1.0"
)

app.include_router(mcp_router)

if __name__ == "__main__":
    print("Iniciando servidor MCP FastAPI em http://localhost:8000")
    print("Documentação da API (Swagger UI): http://localhost:8000/docs")
    print("Documentação alternativa (ReDoc): http://localhost:8000/redoc")
    uvicorn.run(
        "run_mcp_server:app", 
        host="0.0.0.0",
        port=8000,
        reload=True
    )
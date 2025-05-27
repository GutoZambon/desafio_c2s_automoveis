from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db  # Fornece a sessão para o endpoint
    finally:
        db.close() # Garante que a sessão seja fechada após o uso

# Funções para criar e fechar sessões de banco de dados
# (Útil especialmente se você estiver construindo uma API com FastAPI, por exemplo)
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Para criar as tabelas no banco de dados (se elas não existirem)
# Importamos Base do arquivo models.py
from app.database.models import Base
def init_db():
    try:
        print("Tentando criar tabelas no banco de dados...")
        Base.metadata.create_all(bind=engine)
        print("Tabelas verificadas/criadas com sucesso.")
    except Exception as e:
        print(f"Erro ao tentar criar tabelas: {e}")
        print("Certifique-se de que o servidor PostgreSQL está rodando e as credenciais em config.py estão corretas.")
        print(f"String de conexão utilizada: {DATABASE_URL}")

# Se você quiser executar init_db() ao iniciar a aplicação,
# você pode chamá-lo de um script principal ou do seu __main__.py
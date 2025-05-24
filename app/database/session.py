from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importa a string de conexão do nosso arquivo de configuração
from app.core.config import DATABASE_URL

# Cria o engine do SQLAlchemy.
# O engine é o ponto de partida para qualquer aplicação SQLAlchemy.
# Ele "sabe" como se comunicar com um banco de dados específico através da DATABASE_URL.
# O argumento pool_pre_ping=True verifica as conexões antes de usá-las,
# o que pode ajudar a evitar problemas com conexões que foram fechadas pelo servidor do banco.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Cria uma classe SessionLocal.
# Cada instância de SessionLocal será uma sessão de banco de dados.
# Uma sessão é a interface primária para o seu código Python "conversar" com o banco de dados.
# Ela permite que você consulte, adicione, atualize e delete registros.
# autocommit=False e autoflush=False são configurações comuns;
# você controlará o commit das transações manualmente.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
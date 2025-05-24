import os

DB_USER = os.getenv("DB_USER", "Teste")
DB_PASSWORD = os.getenv("DB_PASSWORD", "teste123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "TesteC2S")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "SUA_CHAVE_API_AQUI_SE_NECESSARIO")
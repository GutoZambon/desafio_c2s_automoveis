from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy.orm import declarative_base # Correção para SQLAlchemy >= 1.4, antes era sqlalchemy.ext.declarative
from sqlalchemy import create_engine

# Base declarativa para nossos modelos SQLAlchemy.
# Em projetos maiores, isso pode ficar em um arquivo separado, como app/database/base_class.py
Base = declarative_base()

class Veiculo(Base):
    __tablename__ = "veiculos"  # Nome da tabela no banco de dados

    # Chave primária e identificador único para cada veículo
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Atributos que você especificou:
    marca = Column(String(100), index=True, nullable=False) # Ex: "Volkswagen", "Ford"
    modelo = Column(String(100), index=True, nullable=False) # Ex: "Golf GTI", "Mustang"
    ano_producao_inicial = Column(Integer, nullable=False) # Ano em que o modelo começou a ser produzido
    ano_producao_final = Column(Integer, nullable=True) # Ano em que o modelo deixou de ser produzido (pode ser nulo se ainda em produção)
    potencia_cv = Column(Integer) # Potência do motor em cavalos (CV)
    combustivel = Column(String(50)) # Ex: "Gasolina", "Diesel", "Etanol", "Elétrico", "Híbrido"
    num_portas = Column(Integer) # Ex: 2, 4
    porta_malas_litros = Column(Integer, nullable=True) # Capacidade do porta-malas em litros
    transmissao_automatica = Column(Boolean, default=False) # True se for automático, False se manual
    capacidade_carga_kg = Column(Float, nullable=True) # Capacidade de carga em quilogramas (para picapes, utilitários)
    tanque_litros = Column(Integer, nullable=True) # Capacidade do tanque de combustível em litros
    autonomia_km_l = Column(Float, nullable=True) # Autonomia em km/l (ou km por carga para elétricos)    

    def __repr__(self):
        return f"<Veiculo(id={self.id}, marca='{self.marca}', modelo='{self.modelo}', ano_inicial={self.ano_producao_inicial})>"




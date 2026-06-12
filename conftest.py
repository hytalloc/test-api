import pytest
from fastapi.testclient import TestClient
from src.tarefas.app import app, _tarefas, _proximo_id

@pytest.fixture
def client():
    """Cria um cliente de teste limpando o estado da API antes de cada execução."""
    # Limpa o banco em memória para garantir a independência dos testes
    _tarefas.clear()
    
    # Reseta o contador de IDs de volta para 1
    global _proximo_id
    import src.tarefas.app
    src.tarefas.app._proximo_id = 1
    
    with TestClient(app) as c:
        yield c

@pytest.fixture
def token(client):
    """Obtém um token JWT válido para os testes autenticados."""
    response = client.post(
        "/auth/login",
        data={
            "username": "aluno",
            "password": "senha123"
        }
    )
    return response.json()["access_token"]
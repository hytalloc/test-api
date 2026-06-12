import pytest

# Testes do Módulo de Autenticação
def test_ct01_login_valido(client):
    """Verifica login com credenciais válidas."""
    response = client.post("/auth/login", data={"username": "aluno", "password": "senha123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_ct02_login_sem_username(client):
    """Verifica erro ao logar sem username."""
    response = client.post("/auth/login", data={"password": "senha123"})
    assert response.status_code == 422

def test_ct03_login_sem_password(client):
    """Verifica erro ao logar sem password."""
    response = client.post("/auth/login", data={"username": "aluno"})
    assert response.status_code == 422

# Testes do Módulo de Criar Tarefa
def test_ct04_criar_tarefa_valida(client):
    """Verifica criação de tarefa com dados válidos."""
    payload = {"titulo": "Estudar pytest", "descricao": "Ler documentação"}
    response = client.post("/tarefas", json=payload)
    assert response.status_code == 201
    assert response.json()["status"] == "pendente"

def test_ct05_criar_tarefa_sem_descricao(client):
    """Verifica criação de tarefa sem descrição."""
    payload = {"titulo": "Tarefa sem descricao"}
    response = client.post("/tarefas", json=payload)
    assert response.status_code == 201
    assert response.json()["descricao"] is None

def test_ct06_criar_tarefa_titulo_vazio(client):
    """Verifica rejeição de título vazio."""
    response = client.post("/tarefas", json={"titulo": ""})
    assert response.status_code == 422

def test_ct07_criar_tarefa_sem_titulo(client):
    """Verifica rejeição sem campo título."""
    response = client.post("/tarefas", json={"descricao": "sem titulo"})
    assert response.status_code == 422

def test_ct08_criar_tarefa_titulo_longo(client):
    """Verifica limite de 200 caracteres no título."""
    response = client.post("/tarefas", json={"titulo": "A" * 201})
    assert response.status_code == 422

def test_ct09_status_inicial_pendente(client):
    """Verifica se status inicial é sempre pendente."""
    response = client.post("/tarefas", json={"titulo": "Nova", "status": "concluida"})
    assert response.status_code == 201
    assert response.json()["status"] == "pendente"

# Testes do Módulo de Listar Tarefas
def test_ct10_listar_tarefas_vazio(client):
    """Verifica listagem vazia inicial."""
    response = client.get("/tarefas")
    assert response.status_code == 200
    assert response.json() == []

def test_ct11_listar_tarefas_apos_criacao(client):
    """Verifica listagem após criar uma tarefa."""
    client.post("/tarefas", json={"titulo": "Tarefa Teste"})
    response = client.get("/tarefas")
    assert response.status_code == 200
    assert len(response.json()) == 1

# Testes do Módulo de Buscar por ID
def test_ct12_buscar_tarefa_existente(client):
    """Verifica busca de tarefa por ID existente."""
    res = client.post("/tarefas", json={"titulo": "Buscar"})
    tarefa_id = res.json()["id"]
    response = client.get(f"/tarefas/{tarefa_id}")
    assert response.status_code == 200

def test_ct13_buscar_id_inexistente(client):
    """Verifica erro ao buscar ID que não existe."""
    response = client.get("/tarefas/99999")
    assert response.status_code == 404

def test_ct14_buscar_id_nao_numerico(client):
    """Verifica erro ao passar ID de texto."""
    response = client.get("/tarefas/abc")
    assert response.status_code == 422

# Testes do Módulo de Deletar Tarefa
def test_ct15_deletar_sem_token(client):
    """Verifica bloqueio de deleção sem autenticação."""
    response = client.delete("/tarefas/1")
    assert response.status_code == 401

def test_ct16_deletar_token_invalido(client):
    """Verifica bloqueio com token corrompido."""
    response = client.delete("/tarefas/1", headers={"Authorization": "Bearer invalido"})
    assert response.status_code == 401

def test_ct17_deletar_com_sucesso(client, token):
    """Verifica deleção com token correto."""
    res = client.post("/tarefas", json={"titulo": "Deletar"})
    tarefa_id = res.json()["id"]
    response = client.delete(f"/tarefas/{tarefa_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204

def test_ct18_deletar_inexistente(client, token):
    """Verifica erro ao deletar ID inexistente com token válido."""
    response = client.delete("/tarefas/99999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404

def test_ct19_tarefa_deletada_nao_encontrada(client, token):
    """Verifica se tarefa sumiu após ser deletada."""
    res = client.post("/tarefas", json={"titulo": "Sumiu"})
    tarefa_id = res.json()["id"]
    client.delete(f"/tarefas/{tarefa_id}", headers={"Authorization": f"Bearer {token}"})
    response = client.get(f"/tarefas/{tarefa_id}")
    assert response.status_code == 404
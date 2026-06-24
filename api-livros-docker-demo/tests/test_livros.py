import os
import sys

# Isso faz o Python enxergar o main.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
import main

client = TestClient(main.app)



def test_criar_livro():
    payload = {
        "titulo": "Teste",
        "autor": "Teste",
        "ano": 2000,
        "isbn": "1234567890"
    }

    response = client.post("/livros", json=payload)

    assert response.status_code == 201


def test_listar_livros():
    response = client.get("/livros")
    assert response.status_code == 200


def test_buscar_nao_existente():
    response = client.get("/livros/9999")
    assert response.status_code == 404

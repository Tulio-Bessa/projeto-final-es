import os
import sys
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

# Isso faz o Python enxergar o main.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import main
from models import LivroCriar
from repository import RepositorioEmMemoria


client = TestClient(main.app)


@pytest.fixture(autouse=True)
def ambiente_isolado(monkeypatch):
    """Reinicia os dados e evita chamadas reais para a Open Library."""
    main.servico = main.ServicoLivros(RepositorioEmMemoria())

    resposta = Mock(status_code=200)
    resposta.json.return_value = {
        "ISBN:1234567890": {
            "title": "Livro vindo da Open Library",
            "authors": [{"name": "Autor da Open Library"}],
        }
    }
    mock_get = Mock(return_value=resposta)
    monkeypatch.setattr(main.requests, "get", mock_get)
    return mock_get


def criar_payload(isbn="1234567890"):
    return {
        "titulo": "Teste",
        "autor": "Teste",
        "ano": 2000,
        "isbn": isbn,
    }


def test_criar_livro_com_dados_da_open_library(ambiente_isolado):
    response = client.post("/livros", json=criar_payload())

    assert response.status_code == 201
    assert response.json()["titulo"] == "Livro vindo da Open Library"
    assert response.json()["autor"] == "Autor da Open Library"
    ambiente_isolado.assert_called_once()


def test_impedir_isbn_duplicado():
    dados = LivroCriar(**criar_payload())
    main.servico.criar(dados)

    with pytest.raises(ValueError, match="ISBN já cadastrado"):
        main.servico.criar(LivroCriar(**criar_payload()))


def test_listar_livros():
    client.post("/livros", json=criar_payload())

    response = client.get("/livros")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_buscar_por_titulo_ignora_maiusculas_e_minusculas():
    main.servico._repo.adicionar(LivroCriar(**criar_payload()))

    response = client.get("/livros/busca", params={"titulo": "teste"})

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["titulo"] == "Teste"


def test_buscar_nao_existente():
    response = client.get("/livros/9999")

    assert response.status_code == 404


def test_atualizar_livro():
    livro = main.servico._repo.adicionar(LivroCriar(**criar_payload()))
    dados_atualizados = criar_payload("0987654321")
    dados_atualizados["titulo"] = "Título atualizado"

    response = client.put(f"/livros/{livro.id}", json=dados_atualizados)

    assert response.status_code == 200
    assert response.json()["titulo"] == "Título atualizado"


def test_remover_livro():
    livro = main.servico._repo.adicionar(LivroCriar(**criar_payload()))

    response = client.delete(f"/livros/{livro.id}")

    assert response.status_code == 200
    assert client.get(f"/livros/{livro.id}").status_code == 404

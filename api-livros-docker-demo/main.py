"""
API REST de catalogo de livros (FastAPI).

Estrutura em camadas:
  - Rotas (este arquivo): recebem a requisicao, chamam o service, devolvem a resposta
  - Service: regras de negocio
  - Repository (repository.py): guarda e recupera os dados

Para rodar:
  pip install fastapi uvicorn
  uvicorn main:app --reload

Documentacao interativa: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException, status

from models import Livro, LivroCriar, LivroAtualizar
from repository import RepositorioEmMemoria, RepositorioLivros
import requests


# ----------------------------------------------------------------------
# Camada de servico (regras de negocio)
# ----------------------------------------------------------------------

class ServicoLivros:
    """
    Onde mora a logica de negocio. Recebe um RepositorioLivros pela
    interface --- nao sabe se e em memoria, SQLite ou outra coisa.
    """

    def __init__(self, repositorio: RepositorioLivros) -> None:
        self._repo = repositorio

    def listar(self) -> list[Livro]:
        return self._repo.listar()

    def buscar(self, livro_id: int) -> Livro | None:
        return self._repo.buscar_por_id(livro_id)

    def criar(self, dados: LivroCriar) -> Livro:
    # Regra de negócio: impedir ISBN duplicado
        livros = self._repo.listar()

        for livro in livros:
            if livro.isbn == dados.isbn:
                raise ValueError("ISBN já cadastrado")

        
    # CHAMADA API EXTERNA (OPEN LIBRARY)
        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{dados.isbn}&format=json&jscmd=data"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            key = f"ISBN:{dados.isbn}"

            if key in data:
                livro_data = data[key]

                # preenchendo automaticamente
                dados.titulo = livro_data.get("title", dados.titulo)

                autores = livro_data.get("authors", [])
                if autores:
                    dados.autor = autores[0].get("name", dados.autor)

        return self._repo.adicionar(dados)

    def atualizar(self, livro_id: int, dados: LivroAtualizar) -> Livro | None:
        return self._repo.atualizar(livro_id, dados)

    def remover(self, livro_id: int) -> bool:
        return self._repo.remover(livro_id)


# ----------------------------------------------------------------------
# Montagem da aplicacao
# ----------------------------------------------------------------------

app = FastAPI(title="Catalogo de Livros", version="1.0.0")

# Injecao de dependencia simples: trocar a linha abaixo por outra
# implementacao de RepositorioLivros nao exige mudar mais nada.
servico = ServicoLivros(RepositorioEmMemoria())


# ----------------------------------------------------------------------
# Rotas (camada de API)
# ----------------------------------------------------------------------

@app.get("/livros", response_model=list[Livro])
def listar_livros():
    return servico.listar()


@app.get("/livros/busca", response_model=list[Livro])
def buscar_por_titulo(titulo: str):
    livros = servico._repo.listar()

    resultado = [
        livro for livro in livros
        if titulo.lower() in livro.titulo.lower()
    ]

    return resultado


@app.get("/livros/{livro_id}", response_model=Livro)
def buscar_livro(livro_id: int):
    livro = servico.buscar(livro_id)
    if livro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livro nao encontrado",
        )
    return livro

@app.get("/livros")
def listar_livros(ordenar_por: str = None):
    livros = servico.listar()

    if ordenar_por == "titulo":
        livros.sort(key=lambda l: l.titulo)
    elif ordenar_por == "ano":
        livros.sort(key=lambda l: l.ano)

    return livros

@app.post("/livros", response_model=Livro, status_code=status.HTTP_201_CREATED)
def criar_livro(dados: LivroCriar):
    try:
        return servico.criar(dados)
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro),
        )



@app.put("/livros/{livro_id}", response_model=Livro)
def atualizar_livro(livro_id: int, dados: LivroAtualizar):
    livro = servico.atualizar(livro_id, dados)
    if livro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livro nao encontrado",
        )
    return livro


@app.delete("/livros/{livro_id}", status_code=status.HTTP_200_OK)
def remover_livro(livro_id: int):
    removido = servico.remover(livro_id)
    if not removido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livro nao encontrado",
        )
    return {"mensagem": "Livro removido com sucesso"}

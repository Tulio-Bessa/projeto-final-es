#  API de Catálogo de Livros#  API de Catálogo gerenciamento de livros, com aplicação de regras de negócio, integração com API externa, testes automatizados, pipeline CI e deploy em ambiente cloud.

---

##  Integrantes

- **007225** - Túlio Menezes Bessa  
- **003540** - Thalison de Oliveira Santos  
- **007217** - Julia Sudário Silva  
- **007194** - Adryan Ryan Santos  

---

##  Funcionalidades

- ✅ Cadastro de livros  
- ✅ Listagem de livros  
- ✅ Busca por ID  
- ✅ Atualização de dados  
- ✅ Remoção de livros  
- ✅ Validação de ISBN único (*regra de negócio*)  
- ✅ Integração com a API **Open Library** (enriquecimento automático)  
- ✅ Testes automatizados com cobertura > 70%  
- ✅ Pipeline CI com GitHub Actions  
- ✅ Containerização com Docker  
- ✅ Deploy na AWS Academy  

---

##  Arquitetura

O projeto segue arquitetura em camadas para melhor organização e manutenção:

### 🔹 API (FastAPI)

Responsável por expor os endpoints HTTP e receber as requisições.

### 🔹 Service

Implementa as regras de negócio (ex: validação de ISBN único).

### 🔹 Repository

Gerencia o armazenamento dos dados em memória.

---

##  Execução com Docker

```bash
docker build -t api-livros .
docker run -p 8000:8000 api-livros



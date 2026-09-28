# 🐄 Romaneio de Pesagem de Bovinos

Aplicação web para organizar registros de pesagem de bovinos, desenvolvida em **Python + Flask + SQLite**.

## 🎯 Objetivo

Facilitar o cadastro e o acompanhamento das pesagens dos animais, centralizando as informações em um sistema simples.

## ⚙️ Funcionalidades

- Cadastro e login de usuário
- Cadastro, consulta, edição e exclusão de pesagens
- Cálculo do peso total
- API REST dos registros
- Validação de dados
- Proteção CSRF nos formulários
- Senhas armazenadas com hash
- Banco SQLite

## 💻 Tecnologias

Python, Flask, Flask-SQLAlchemy, SQLite, HTML5, CSS3, Git, GitHub e PlantUML.

## 🏗️ Arquitetura

- C4 Contexto: `contexto.puml`
- C4 Contêiner: `conteiner.puml`
- Banco de Dados: `banco.puml`
- Fluxo do processo: `fluxo_calculo.puml`
- Esquema SQL: `schema.sql`

## 🚀 Como executar

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Depois, acesse `http://127.0.0.1:5000`.

## 🔐 Configuração

Crie um arquivo `.env` baseado em `.env.example` e defina uma `SECRET_KEY`. O arquivo `.env` não deve ser enviado ao GitHub.

## 👤 Integrante

**Heloina Lorena Santana Marinho**  
GitHub: **@helo987**  
Projeto individual.

## 📌 Status

Projeto preparado para a entrega do 4º bimestre, com aplicação Flask, banco SQLite, CRUD, autenticação, API, documentação e diagramas.

# Sistema de Fretamento - Project IDX

Este projeto foi configurado para rodar no Google Project IDX com suporte a Django (Monolito) e FastAPI (Bot WhatsApp).

## Estrutura do Projeto

- `/monolito`: Código fonte do sistema Django.
- `/bot_whatsapp`: Código fonte da API FastAPI.
- `.idx/dev.nix`: Configuração do ambiente (Nix, serviços, previews).
- `setup_projeto.sh`: Script para inicializar o ambiente, instalar dependências e criar a estrutura inicial.

## Como Iniciar

1. Ao abrir o projeto no Project IDX, o ambiente será construído.
2. O script `setup_projeto.sh` deve rodar automaticamente na criação do workspace (`onCreate`), criando as pastas e instalando dependências.
3. Se necessário, rode manualmente:
   - **No Project IDX (Linux)**:
     ```bash
     bash setup_projeto.sh
     ```
   - **No Windows Local**:
     ```powershell
     .\setup_projeto.ps1
     ```
4. Os previews devem iniciar automaticamente:
   - **Django**: Porta 8000
   - **FastAPI**: Porta 8001 (Pública)

## Serviços Configurados

- **Banco de Dados**: PostgreSQL 15 com extensão PostGIS.
- **Cache**: Redis.
- **Docker**: Habilitado (Docker Compose disponível).
- **Linguagem**: Python 3.11.

## Comandos Úteis

- Rodar servidor Django:
  ```bash
  python monolito/manage.py runserver
  ```
- Rodar FastAPI:
  ```bash
  uvicorn bot_whatsapp.main:app --host 0.0.0.0 --port 8001 --reload
  ```

# Desafio MBA Engenharia de Software com IA - Full Cycle

## Sistema de Ingestão e Busca Semântica com LangChain e PostgreSQL

## 🚀 Comandos para Executar

### 1. Configurar APIs
Crie arquivo `.env` com suas chaves:
```bash
# Configurações do banco de dados
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=rag

# Configurações da OpenAI
OPENAI_API_KEY=sua_chave_api_aqui

# Configurações do PDF
PDF_PATH=document.pdf

# Configurações dos modelos OpenAI
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-5-nano
```

### 2. Subir Banco de Dados
```bash
docker-compose up -d
```

### 3. Ambiente Python
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 4. Executar Sistema
```bash
python src/ingest.py    # Ingestão do PDF
python src/chat.py      # Chat para perguntas
```

## 📁 Estrutura
- `docker-compose.yml` - PostgreSQL + pgVector
- `src/ingest.py` - Ingestão do PDF
- `src/search.py` - Busca semântica  
- `src/chat.py` - Interface CLI
- `document.pdf` - Arquivo para processar

## 🔧 Tecnologias
- Python + LangChain
- PostgreSQL + pgVector
- Docker
- OpenAI (GPT-5-nano + text-embedding-3-small)
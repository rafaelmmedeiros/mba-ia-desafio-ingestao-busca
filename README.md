# Desafio MBA Engenharia de Software com IA - Full Cycle

## Sistema de Ingestão e Busca Semântica com LangChain e PostgreSQL

## 🚀 Comandos para Executar

### 1. Configurar APIs
Crie arquivo `.env` com suas chaves:
```bash
OPENAI_API_KEY=sua_chave_aqui
GOOGLE_API_KEY=sua_chave_aqui
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
- OpenAI ou Google Gemini
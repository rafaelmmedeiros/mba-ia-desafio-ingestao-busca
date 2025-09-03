import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import PGVector
from langchain_core.prompts import PromptTemplate

# Carrega variáveis de ambiente
load_dotenv()

# Template do prompt conforme especificado no desafio
PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

def get_database_connection():
    """Cria conexão com o banco PostgreSQL para busca"""
    try:
        # Parâmetros de conexão
        connection_string = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
        
        # Cria a conexão com pgvector para busca
        db = PGVector(
            connection_string=connection_string,
            embedding_function=GoogleGenerativeAIEmbeddings(
                model=os.getenv("EMBEDDING_MODEL", "models/embedding-001"),
                google_api_key=os.getenv("GOOGLE_API_KEY")
            ),
            collection_name="pdf_documents"
        )
        
        return db
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None

def search_similar_documents(query, db, k=10):
    """Busca documentos similares no banco de dados"""
    try:
        print(f"🔍 Buscando documentos similares para: '{query[:50]}...'")
        
        # Busca os k documentos mais similares
        similar_docs = db.similarity_search_with_score(query, k=k)
        
        print(f"✅ Encontrados {len(similar_docs)} documentos relevantes")
        
        # Extrai apenas o conteúdo dos documentos (sem scores)
        documents = [doc[0] for doc in similar_docs]
        
        return documents
        
    except Exception as e:
        print(f"❌ Erro na busca: {e}")
        return []

def create_context_from_documents(documents):
    """Cria o contexto concatenando os documentos encontrados"""
    try:
        if not documents:
            return "Nenhum documento relevante encontrado."
        
        # Concatena o conteúdo dos documentos
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"DOCUMENTO {i}:\n{doc.page_content}\n")
        
        context = "\n".join(context_parts)
        
        print(f"📝 Contexto criado com {len(documents)} documentos")
        return context
        
    except Exception as e:
        print(f"❌ Erro ao criar contexto: {e}")
        return "Erro ao processar documentos."

def generate_response(query, context):
    """Gera resposta usando Google Gemini"""
    try:
        print("🤖 Gerando resposta com Google Gemini...")
        
        # Cria o modelo de chat
        llm = ChatGoogleGenerativeAI(
            model=os.getenv("LLM_MODEL", "gemini-2.0-flash-exp"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.1  # Baixa temperatura para respostas mais precisas
        )
        
        # Cria o prompt
        prompt = PromptTemplate(
            template=PROMPT_TEMPLATE,
            input_variables=["contexto", "pergunta"]
        )
        
        # Monta o prompt final
        final_prompt = prompt.format(contexto=context, pergunta=query)
        
        # Gera a resposta
        response = llm.invoke(final_prompt)
        
        print("✅ Resposta gerada com sucesso!")
        return response.content
        
    except Exception as e:
        print(f"❌ Erro ao gerar resposta: {e}")
        return f"Erro ao processar resposta: {e}"

def search_prompt(question=None):
    """Função principal de busca e resposta"""
    if not question:
        return None
    
    try:
        # 1. Conecta ao banco
        db = get_database_connection()
        if not db:
            return "Erro: Não foi possível conectar ao banco de dados."
        
        # 2. Busca documentos similares
        similar_docs = search_similar_documents(question, db)
        if not similar_docs:
            return "Não tenho informações necessárias para responder sua pergunta."
        
        # 3. Cria o contexto
        context = create_context_from_documents(similar_docs)
        
        # 4. Gera a resposta
        response = generate_response(question, context)
        
        return response
        
    except Exception as e:
        print(f"❌ Erro na busca: {e}")
        return f"Erro interno: {e}"

def test_search_functionality():
    """Testa a funcionalidade de busca"""
    print("🧪 TESTANDO FUNCIONALIDADE DE BUSCA")
    print("=" * 50)
    
    # Testa com uma pergunta simples
    test_question = "Qual é o tema principal deste documento?"
    
    print(f"Pergunta de teste: {test_question}")
    print("\n" + "=" * 50)
    
    response = search_prompt(test_question)
    
    print(f"Resposta: {response}")
    
    return response is not None

if __name__ == "__main__":
    test_search_functionality()
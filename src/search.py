import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import PGVector
from langchain_core.prompts import PromptTemplate

load_dotenv()

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
    try:
        connection_string = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
        
        db = PGVector(
            connection_string=connection_string,
            embedding_function=OpenAIEmbeddings(
                model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
                openai_api_key=os.getenv("OPENAI_API_KEY")
            ),
            collection_name="pdf_documents"
        )
        
        return db
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None

def search_similar_documents(query, db, k=10):
    try:
        print(f"🔍 Buscando documentos similares para: '{query[:50]}...'")
        
        similar_docs = db.similarity_search_with_score(query, k=k)
        
        print(f"✅ Encontrados {len(similar_docs)} documentos relevantes")
        
        documents = [doc[0] for doc in similar_docs]
        
        return documents
        
    except Exception as e:
        print(f"❌ Erro na busca: {e}")
        return []

def create_context_from_documents(documents):
    try:
        if not documents:
            return "Nenhum documento relevante encontrado."
        
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
    try:
        print("🤖 Gerando resposta com OpenAI...")
        
        llm = ChatOpenAI(
            model=os.getenv("LLM_MODEL", "gpt-5-nano"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.1
        )
        
        prompt = PromptTemplate(
            template=PROMPT_TEMPLATE,
            input_variables=["contexto", "pergunta"]
        )
        
        final_prompt = prompt.format(contexto=context, pergunta=query)
        
        response = llm.invoke(final_prompt)
        
        print("✅ Resposta gerada com sucesso!")
        return response.content
        
    except Exception as e:
        print(f"❌ Erro ao gerar resposta: {e}")
        return f"Erro ao processar resposta: {e}"

def search_prompt(question=None):
    if not question:
        return None
    
    try:
        db = get_database_connection()
        if not db:
            return "Erro: Não foi possível conectar ao banco de dados."
        
        similar_docs = search_similar_documents(question, db)
        if not similar_docs:
            return "Não tenho informações necessárias para responder sua pergunta."
        
        context = create_context_from_documents(similar_docs)
        
        response = generate_response(question, context)
        
        return response
        
    except Exception as e:
        print(f"❌ Erro na busca: {e}")
        return f"Erro interno: {e}"

def test_search_functionality():
    print("🧪 TESTANDO FUNCIONALIDADE DE BUSCA")
    print("=" * 50)
    
    test_question = "Qual é o tema principal deste documento?"
    
    print(f"Pergunta de teste: {test_question}")
    print("\n" + "=" * 50)
    
    response = search_prompt(test_question)
    
    print(f"Resposta: {response}")
    
    return response is not None

if __name__ == "__main__":
    test_search_functionality()
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
- Responda SOMENTE com base no CONTEXTO fornecido.
- Para todas as perguntas, analise TODOS os dados relevantes no contexto. 
- Siga um método de analise ao qual eu tenho que olhar todos para saber qual é a resposta. Por exemplo: Eu somente posso saber quem é o maior, se olhar todos os dados relevantes no contexto.
- Sempre que tiver um ranking, faça uma pós analise, exemplo: para os 5 maiores, procure o maior, depois procure o segundo maior, e assim por diante (o segundo maior é o maior excluindo o primeiro). Siga tal regra para outros rankings.
- Se a informação não estiver no CONTEXTO, responda: "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente dados ou use conhecimento externo.

EXEMPLOS DE ANÁLISE COMPLEXA:
Pergunta: "Quais são os 5 maiores faturamentos?"
Resposta: Com base no contexto, os 5 maiores faturamentos são: 1) Empresa A - R$ 10 milhões, 2) Empresa B - R$ 8 milhões, 3) Empresa C - R$ 6 milhões, 4) Empresa D - R$ 4 milhões, 5) Empresa E - R$ 2 milhões.

Pergunta: "Compare as empresas com maior e menor faturamento"
Resposta: A empresa com maior faturamento é [nome] com R$ [valor], e a com menor faturamento é [nome] com R$ [valor].

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO" analisando e organizando as informações do contexto quando necessário.
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

def search_similar_documents(query, db, k=67):
    try:
        print(f"🔍 Buscando TODOS os documentos para: '{query[:50]}...'")
        
        # BUSCAR TODOS os documentos usando busca por similaridade com query genérica
        # Usar uma query que retorna todos os documentos
        all_docs = db.similarity_search_with_score("", k=k)
        
        print(f"✅ Encontrados {len(all_docs)} documentos (TODOS os chunks)")
        documents = [doc[0] for doc in all_docs]
        
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
            # Adicionar separador mais claro entre documentos
            context_parts.append(f"=== DOCUMENTO {i} ===\n{doc.page_content}\n")
        
        context = "\n".join(context_parts)
        
        print(f"📝 Contexto criado com {len(documents)} documentos ({len(context)} caracteres)")
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
        
        # SEMPRE buscar TODOS os documentos para máxima precisão
        print("🔍 Buscando TODOS os documentos para máxima precisão...")
        
        similar_docs = search_similar_documents(question, db, k=67)
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
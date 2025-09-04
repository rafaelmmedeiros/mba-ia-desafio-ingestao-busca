import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import PGVector

load_dotenv()

def get_database_connection():
    try:
        connection_string = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
        
        db = PGVector(
            connection_string=connection_string,
            embedding_function=GoogleGenerativeAIEmbeddings(
                model=os.getenv("EMBEDDING_MODEL", "models/embedding-001"),
                google_api_key=os.getenv("GOOGLE_API_KEY")
            ),
            collection_name="pdf_documents"
        )
        
        print("✅ Conexão com banco estabelecida!")
        return db
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None

def load_pdf(pdf_path):
    try:
        print(f"📖 Carregando PDF: {pdf_path}")
        
        if not os.path.exists(pdf_path):
            print(f"❌ Arquivo não encontrado: {pdf_path}")
            return None
        
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        print(f"✅ PDF carregado! {len(documents)} páginas encontradas")
        return documents
        
    except Exception as e:
        print(f"❌ Erro ao carregar PDF: {e}")
        return None

def split_documents(documents):
    try:
        print("✂️  Dividindo documentos em chunks...")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        
        print(f"✅ Documentos divididos em {len(chunks)} chunks!")
        print(f"   Tamanho médio: {sum(len(chunk.page_content) for chunk in chunks) // len(chunks)} caracteres")
        
        return chunks
        
    except Exception as e:
        print(f"❌ Erro ao dividir documentos: {e}")
        return None

def save_to_database(db, chunks):
    try:
        print("💾 Salvando chunks no banco de dados...")
        
        for i, chunk in enumerate(chunks):
            print(f"   Salvando chunk {i+1}/{len(chunks)}...")
            
            db.add_documents([chunk])
        
        print("✅ Todos os chunks foram salvos no banco!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao salvar no banco: {e}")
        return False

def ingest_pdf():
    print("🚀 INICIANDO PROCESSO DE INGESTÃO")
    print("=" * 50)
    
    db = get_database_connection()
    if not db:
        return False
    
    pdf_path = os.getenv("PDF_PATH", "document.pdf")
    documents = load_pdf(pdf_path)
    if not documents:
        return False
    
    chunks = split_documents(documents)
    if not chunks:
        return False
    
    success = save_to_database(db, chunks)
    
    if success:
        print("\n🎉 INGESTÃO CONCLUÍDA COM SUCESSO!")
        print(f"📊 Resumo:")
        print(f"   - PDF processado: {pdf_path}")
        print(f"   - Páginas: {len(documents)}")
        print(f"   - Chunks criados: {len(chunks)}")
        print(f"   - Chunks salvos no banco: {len(chunks)}")
    else:
        print("\n❌ INGESTÃO FALHOU!")
    
    return success

if __name__ == "__main__":
    ingest_pdf()
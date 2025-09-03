import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import PGVector

# Carrega variáveis de ambiente
load_dotenv()

def get_database_connection():
    """Cria conexão com o banco PostgreSQL"""
    try:
        # Parâmetros de conexão
        connection_string = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
        
        # Cria a conexão com pgvector
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
    """Carrega o PDF e extrai o texto"""
    try:
        print(f"📖 Carregando PDF: {pdf_path}")
        
        # Verifica se o arquivo existe
        if not os.path.exists(pdf_path):
            print(f"❌ Arquivo não encontrado: {pdf_path}")
            return None
        
        # Carrega o PDF
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        print(f"✅ PDF carregado! {len(documents)} páginas encontradas")
        return documents
        
    except Exception as e:
        print(f"❌ Erro ao carregar PDF: {e}")
        return None

def split_documents(documents):
    """Divide os documentos em chunks menores"""
    try:
        print("✂️  Dividindo documentos em chunks...")
        
        # Configura o divisor de texto
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,      # Tamanho de cada chunk
            chunk_overlap=150,     # Overlap entre chunks
            length_function=len,   # Função para medir tamanho
            separators=["\n\n", "\n", " ", ""]  # Separadores para divisão
        )
        
        # Divide os documentos
        chunks = text_splitter.split_documents(documents)
        
        print(f"✅ Documentos divididos em {len(chunks)} chunks!")
        print(f"   Tamanho médio: {sum(len(chunk.page_content) for chunk in chunks) // len(chunks)} caracteres")
        
        return chunks
        
    except Exception as e:
        print(f"❌ Erro ao dividir documentos: {e}")
        return None

def save_to_database(db, chunks):
    """Salva os chunks no banco de dados"""
    try:
        print("💾 Salvando chunks no banco de dados...")
        
        # Salva cada chunk no banco
        for i, chunk in enumerate(chunks):
            print(f"   Salvando chunk {i+1}/{len(chunks)}...")
            
            # Adiciona o chunk ao banco
            db.add_documents([chunk])
        
        print("✅ Todos os chunks foram salvos no banco!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao salvar no banco: {e}")
        return False

def ingest_pdf():
    """Função principal de ingestão"""
    print("🚀 INICIANDO PROCESSO DE INGESTÃO")
    print("=" * 50)
    
    # 1. Conecta ao banco
    db = get_database_connection()
    if not db:
        return False
    
    # 2. Carrega o PDF
    pdf_path = os.getenv("PDF_PATH", "document.pdf")
    documents = load_pdf(pdf_path)
    if not documents:
        return False
    
    # 3. Divide em chunks
    chunks = split_documents(documents)
    if not chunks:
        return False
    
    # 4. Salva no banco
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
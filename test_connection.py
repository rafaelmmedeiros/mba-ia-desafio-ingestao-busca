import os
import psycopg2
from dotenv import load_dotenv

def test_database_connection():
    """Testa a conexão com o banco PostgreSQL"""
    try:
        # Carrega as variáveis de ambiente
        load_dotenv()
        
        # Parâmetros de conexão
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "postgres")
        database = os.getenv("POSTGRES_DB", "rag")
        
        print(f"🔌 Tentando conectar ao banco...")
        print(f"   Host: {host}")
        print(f"   Porta: {port}")
        print(f"   Usuário: {user}")
        print(f"   Banco: {database}")
        
        # Tenta conectar
        connection = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        # Testa se a extensão pgvector está instalada
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        vector_extension = cursor.fetchone()
        
        if vector_extension:
            print("✅ Conexão com o banco estabelecida com sucesso!")
            print("✅ Extensão pgvector está instalada!")
        else:
            print("⚠️  Conexão OK, mas extensão pgvector não encontrada!")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        print("\n💡 Dicas para resolver:")
        print("   1. Verifique se o Docker está rodando")
        print("   2. Execute: docker compose up -d")
        print("   3. Aguarde alguns segundos para o banco inicializar")
        return False

def test_api_keys():
    """Testa se as chaves de API estão configuradas"""
    load_dotenv()
    
    # Testa chave da OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key != "sua_chave_api_aqui":
        print("✅ Chave da OpenAI configurada!")
        openai_ok = True
    else:
        print("⚠️  Chave da OpenAI não configurada (opcional)")
        openai_ok = False
    
    # Testa chave da Google
    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key and google_key != "sua_chave_api_aqui":
        print("✅ Chave da Google configurada!")
        google_ok = True
    else:
        print("❌ Chave da Google não configurada!")
        google_ok = False
    
    return openai_ok, google_ok

if __name__ == "__main__":
    print("🧪 TESTANDO CONFIGURAÇÕES DO PROJETO")
    print("=" * 50)
    
    # Testa conexão com banco
    db_ok = test_database_connection()
    
    print("\n" + "=" * 50)
    
    # Testa chaves de API
    openai_ok, google_ok = test_api_keys()
    
    print("\n" + "=" * 50)
    
    if db_ok and google_ok:
        print("🎉 TUDO PRONTO! Pode prosseguir para a próxima etapa.")
        print("🚀 Usando Google Gemini para embeddings e respostas!")
    else:
        print("⚠️  Alguns problemas foram encontrados. Resolva antes de continuar.")

import os
import sys
from dotenv import load_dotenv
from search import search_prompt

# Carrega variáveis de ambiente
load_dotenv()

def print_banner():
    """Exibe o banner de boas-vindas"""
    print("🚀" + "=" * 60 + "🚀")
    print("           SISTEMA DE BUSCA SEMÂNTICA COM IA")
    print("           Baseado no documento: " + os.getenv("PDF_PATH", "document.pdf"))
    print("🚀" + "=" * 60 + "🚀")
    print()

def print_help():
    """Exibe a ajuda do sistema"""
    print("\n📚 COMANDOS DISPONÍVEIS:")
    print("   /help     - Mostra esta ajuda")
    print("   /quit     - Sai do sistema")
    print("   /clear    - Limpa a tela")
    print("   /status   - Mostra status do sistema")
    print("   /about    - Informações sobre o projeto")
    print()
    print("💡 DICAS:")
    print("   - Faça perguntas específicas para melhores respostas")
    print("   - O sistema responde apenas com base no documento")
    print("   - Perguntas fora do contexto receberão resposta padrão")
    print()

def print_status():
    """Exibe o status do sistema"""
    print("\n📊 STATUS DO SISTEMA:")
    print(f"   📄 Documento: {os.getenv('PDF_PATH', 'document.pdf')}")
    print(f"   🤖 Modelo LLM: {os.getenv('LLM_MODEL', 'gemini-2.0-flash-exp')}")
    print(f"   🔍 Modelo Embedding: {os.getenv('EMBEDDING_MODEL', 'models/embedding-001')}")
    print(f"   🗄️  Banco: {os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}")
    print()

def print_about():
    """Exibe informações sobre o projeto"""
    print("\nℹ️  SOBRE O PROJETO:")
    print("   Este é um sistema de busca semântica que utiliza:")
    print("   - LangChain para processamento de documentos")
    print("   - Google Gemini para embeddings e respostas")
    print("   - PostgreSQL com pgVector para busca vetorial")
    print("   - Processamento de PDF com divisão em chunks")
    print()

def clear_screen():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def process_command(command):
    """Processa comandos especiais"""
    command = command.lower().strip()
    
    if command == "/help":
        print_help()
        return True
    elif command == "/quit":
        print("\n👋 Obrigado por usar o sistema! Até logo!")
        return False
    elif command == "/clear":
        clear_screen()
        print_banner()
        return True
    elif command == "/status":
        print_status()
        return True
    elif command == "/about":
        print_about()
        return True
    elif command.startswith("/"):
        print(f"❌ Comando desconhecido: {command}")
        print("💡 Digite /help para ver os comandos disponíveis")
        return True
    
    return None  # Não é um comando, é uma pergunta

def chat_loop():
    """Loop principal do chat"""
    print_banner()
    print_help()
    
    question_count = 0
    
    while True:
        try:
            # Pega a pergunta do usuário
            question = input(f"\n🔍 PERGUNTA {question_count + 1}: ").strip()
            
            # Verifica se é um comando
            if question.startswith("/"):
                should_continue = process_command(question)
                if should_continue is False:
                    break
                continue
            
            # Verifica se é uma pergunta vazia
            if not question:
                print("❌ Por favor, digite uma pergunta válida.")
                continue
            
            # Processa a pergunta
            print(f"\n🤔 Processando sua pergunta...")
            print("-" * 60)
            
            response = search_prompt(question)
            
            if response:
                print(f"📝 RESPOSTA:")
                print(response)
            else:
                print("❌ Erro ao processar a pergunta. Tente novamente.")
            
            print("-" * 60)
            question_count += 1
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupção detectada. Use /quit para sair.")
            continue
        except EOFError:
            print("\n\n👋 Encerrando o sistema...")
            break
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            print("💡 Tente novamente ou use /quit para sair.")

def main():
    """Função principal"""
    try:
        # Verifica se o sistema está configurado
        if not os.getenv("GOOGLE_API_KEY"):
            print("❌ ERRO: Chave da Google API não configurada!")
            print("💡 Configure a variável GOOGLE_API_KEY no arquivo .env")
            return False
        
        # Inicia o chat
        chat_loop()
        return True
        
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        return False

if __name__ == "__main__":
    main()
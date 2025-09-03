from src.search import search_prompt

def test_specific_questions():
    """Testa perguntas específicas para verificar o funcionamento"""
    print("🧪 TESTANDO PERGUNTAS ESPECÍFICAS")
    print("=" * 60)
    
    # Lista de perguntas para testar
    test_questions = [
        "Qual é o nome da empresa mencionada no documento?",
        "Quais são os principais produtos ou serviços?",
        "Qual é o faturamento mencionado?",
        "Quantos funcionários a empresa tem?",
        "Qual é a data de fundação?",
        "O que é inteligência artificial?",
        "Qual é a capital da França?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🔍 PERGUNTA {i}: {question}")
        print("-" * 60)
        
        # Faz a busca
        response = search_prompt(question)
        
        print(f"📝 RESPOSTA: {response}")
        print("=" * 60)
        
        # Pausa entre perguntas para não sobrecarregar a API
        if i < len(test_questions):
            input("Pressione Enter para continuar...")

if __name__ == "__main__":
    test_specific_questions()

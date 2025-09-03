"""
UTILITÁRIOS PARA GEMINI COM RATE LIMITING
==========================================

Este módulo contém a classe RateLimitedModel que pode ser importada
em qualquer código para evitar problemas de quota.

Como usar:
from utils_gemini import RateLimitedModel

model = RateLimitedModel()
result = model.invoke("Seu prompt aqui")
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import time
import random

# Carrega as variáveis de ambiente (API key do Gemini)
load_dotenv()

class RateLimitedModel:
    """
    Modelo Gemini com rate limiting automático para evitar exceder quotas.
    
    Características:
    - Delays automáticos de 4.5s entre chamadas
    - Tratamento automático de erros de quota
    - Retry automático com backoff
    - Compatível com todos os códigos LangChain
    """
    
    def __init__(self, model_name="gemini-2.5-flash-lite", temperature=0):
        """
        Inicializa o modelo com rate limiting.
        
        Args:
            model_name (str): Nome do modelo Gemini (padrão: gemini-2.5-flash-lite)
            temperature (float): Temperatura do modelo (padrão: 0)
        """
        self.model = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
        self.last_call_time = 0
        self.min_delay = 4.5  # Mínimo 4.5 segundos entre chamadas
        self.request_count = 0
        
    def invoke(self, prompt):
        """
        Invoca o modelo com rate limiting automático.
        
        Args:
            prompt: O prompt ou mensagem para enviar ao modelo
            
        Returns:
            Resposta do modelo
            
        Raises:
            Exception: Se houver erro não relacionado à quota
        """
        # Aguarda o tempo necessário para respeitar o rate limit
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.min_delay:
            sleep_time = self.min_delay - time_since_last_call + random.uniform(0, 1)
            print(f"⏳ Aguardando {sleep_time:.1f}s para respeitar rate limit...")
            time.sleep(sleep_time)
        
        try:
            result = self.model.invoke(prompt)
            self.last_call_time = time.time()
            self.request_count += 1
            print(f"✅ Requisição {self.request_count} processada com sucesso")
            return result
        except Exception as e:
            if "quota" in str(e).lower() or "429" in str(e):
                print(f"🚫 Quota excedida! Aguardando 60 segundos...")
                time.sleep(60)
                # Tenta novamente
                return self.invoke(prompt)
            else:
                raise e
    
    def get_stats(self):
        """Retorna estatísticas de uso"""
        return {
            "total_requests": self.request_count,
            "last_call_time": self.last_call_time,
            "min_delay": self.min_delay
        }

# Função de conveniência para criar modelo rapidamente
def create_gemini_model(model_name="gemini-2.5-flash-lite", temperature=0):
    """
    Função rápida para criar um modelo Gemini com rate limiting.
    
    Args:
        model_name (str): Nome do modelo
        temperature (float): Temperatura
        
    Returns:
        RateLimitedModel: Modelo configurado
    """
    return RateLimitedModel(model_name, temperature)

# Exemplo de uso
if __name__ == "__main__":
    print("🧪 Testando RateLimitedModel...")
    
    model = RateLimitedModel()
    
    # Teste simples
    result = model.invoke("Diga 'Olá, mundo!' em português")
    print(f"Resposta: {result.content}")
    
    # Estatísticas
    stats = model.get_stats()
    print(f"Estatísticas: {stats}")

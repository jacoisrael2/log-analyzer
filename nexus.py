import paramiko
import time
from datetime import datetime
import json
from getpass import getpass
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import os
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuração da API OpenAI com validação
try:
    api_key = input("Digite sua chave API da OpenAI: ").strip()
    if not api_key:
        raise ValueError("A chave API não pode estar vazia")
    os.environ["OPENAI_API_KEY"] = api_key
except Exception as e:
    logger.error(f"Erro ao configurar API key: {e}")
    raise

def connect_switch(ip, username, password):
    """
    Estabelece conexão SSH com o switch Nexus
    
    Args:
        ip (str): Endereço IP do switch
        username (str): Nome de usuário
        password (str): Senha
        
    Returns:
        paramiko.SSHClient: Objeto de conexão SSH ou None se falhar
    """
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, look_for_keys=False, timeout=10)
        logger.info(f"Conexão estabelecida com {ip}")
        return ssh
    except Exception as e:
        logger.error(f"Erro ao conectar ao switch {ip}: {e}")
        return None

def execute_command(ssh, command, timeout=30):
    """
    Executa comando no switch e retorna a saída
    
    Args:
        ssh (paramiko.SSHClient): Conexão SSH
        command (str): Comando a ser executado
        timeout (int): Tempo máximo de espera em segundos
        
    Returns:
        str: Saída do comando ou None se falhar
    """
    try:
        stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if error:
            logger.warning(f"Erro ao executar {command}: {error}")
        return output
    except Exception as e:
        logger.error(f"Erro ao executar comando {command}: {e}")
        return None

def collect_switch_data(ip, username, password):
    """
    Coleta dados do switch
    
    Args:
        ip (str): Endereço IP do switch
        username (str): Nome de usuário
        password (str): Senha
        
    Returns:
        dict: Dados coletados do switch ou None se falhar
    """
    ssh = connect_switch(ip, username, password)
    if not ssh:
        return None
    
    data = {}
    commands = [
        "show version",
        "show system resources", 
        "show environment",
        "show logging log | last 100",  # Limitando logs para melhor performance
        "show interface status",
        "show ip interface brief",
        "show processes cpu history"
    ]
    
    try:
        for cmd in commands:
            logger.info(f"Executando comando: {cmd}")
            output = execute_command(ssh, cmd)
            if output is not None:
                data[cmd] = output
            else:
                logger.warning(f"Comando {cmd} falhou")
    finally:
        ssh.close()
        logger.info("Conexão SSH fechada")
    
    return data if data else None

def truncate_text(text, max_chars=3000):
    """
    Trunca texto para um tamanho máximo
    
    Args:
        text (str): Texto a ser truncado
        max_chars (int): Número máximo de caracteres
        
    Returns:
        str: Texto truncado
    """
    if len(text) > max_chars:
        return text[:max_chars] + "\n\n[TRUNCADO: dados demais para análise completa]"
    return text

def analyze_with_ai(data, problem_description):
    """
    Analisa os dados coletados usando OpenAI
    
    Args:
        data (dict): Dados coletados do switch
        problem_description (str): Descrição do problema
        
    Returns:
        str: Análise gerada pela IA
    """
    template = """
    Você é um engenheiro de redes especialista em switches Cisco Nexus.
    Analise os seguintes dados coletados do switch e o problema relatado:
    
    Problema relatado: {problem}
    
    Dados do switch:
    {switch_data}
    
    Por favor, forneça:
    1. Análise detalhada do problema
    2. Possíveis causas
    3. Recomendações para resolução
    4. Ações preventivas para evitar problemas similares
    5. Sugestões de monitoramento
    """
    
    try:
        prompt = PromptTemplate(
            input_variables=["problem", "switch_data"],
            template=template
        )
        
        llm = OpenAI(temperature=0.7)
        chain = prompt | llm
        
        formatted_data = "\n".join([f"{cmd}:\n{output}\n" for cmd, output in data.items()])
        formatted_data = truncate_text(formatted_data)
        
        response = chain.invoke({
            "problem": problem_description,
            "switch_data": formatted_data
        })
        return response
    except Exception as e:
        logger.error(f"Erro na análise com IA: {e}")
        return "Erro ao realizar análise. Por favor, tente novamente."

def main():
    """Função principal do programa"""
    logger.info("Iniciando Analisador de Logs Nexus com IA")
    print("=== Analisador de Logs Nexus com IA ===")
    
    try:
        # Coleta credenciais com validação básica
        switch_ip = input("Digite o IP do switch Nexus: ").strip()
        username = input("Digite o usuário: ").strip()
        password = getpass("Digite a senha: ")
        
        if not all([switch_ip, username, password]):
            raise ValueError("Todos os campos são obrigatórios")
        
        logger.info("Iniciando coleta de dados...")
        print("\nColetando dados do switch...")
        switch_data = collect_switch_data(switch_ip, username, password)
        
        if not switch_data:
            raise Exception("Falha ao coletar dados do switch")
        
        # Salva dados com tratamento de erro
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"switch_data_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(switch_data, f, indent=4)
        logger.info(f"Dados salvos em {filename}")
        
        print("\nDados coletados com sucesso!")
        problem = input("\nDescreva o problema que você está enfrentando: ").strip()
        
        if not problem:
            raise ValueError("A descrição do problema é obrigatória")
        
        print("\nAnalisando dados com IA...")
        analysis = analyze_with_ai(switch_data, problem)
        
        print("\n=== Análise da IA ===")
        print(analysis)
        logger.info("Análise concluída com sucesso")
        
    except Exception as e:
        logger.error(f"Erro durante execução: {e}")
        print(f"\nErro: {e}")
        print("Por favor, verifique os logs para mais detalhes.")

if __name__ == "__main__":
    main()

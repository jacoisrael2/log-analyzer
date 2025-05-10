# log-analyzer

Ferramenta para análise de logs e automação de diagnósticos em switches Cisco Nexus utilizando Python, SSH e IA (OpenAI).

## Funcionalidades
- Conexão SSH automatizada com switches Cisco Nexus
- Execução de comandos de diagnóstico e coleta de informações do equipamento
- Análise dos dados coletados usando modelos de linguagem (OpenAI)
- Geração de relatório analítico com possíveis causas, recomendações e ações preventivas
- Salvamento dos dados coletados em arquivo JSON para auditoria

## Como usar
1. Clone o repositório:
   ```bash
   git clone https://github.com/jacoisrael2/log-analyzer.git
   cd log-analyzer
   ```
2. Instale as dependências necessárias (recomenda-se uso de ambiente virtual):
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o script principal:
   ```bash
   python nexus.py
   ```
4. Siga as instruções no terminal para inserir as credenciais e descrever o problema.

## Exemplo de comandos coletados
- show version
- show system resources
- show environment
- show logging log | last 100
- show interface status
- show ip interface brief
- show processes cpu history

## Requisitos
- Python 3.8+
- Acesso SSH ao switch Nexus
- Chave de API da OpenAI

## Licença
MIT

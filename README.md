# Automação Auditoria CFTV - Via API

Este repositório contém uma solução robusta para automatizar o monitoramento diário do status das gravações de CFTV em múltiplos clientes, utilizando uma arquitetura de API central para garantir a confiabilidade dos dados.

## Problemática: Fragilidade da Sincronização de Arquivos

Em um ambiente de monitoramento de CFTV, é crucial garantir que as gravações de todos os clientes estejam ocorrendo sem interrupções. A primeira versão desta automação, disponível em [n33miaz/automacao_monitoramento_de_gravacoes](https://github.com/n33miaz/automacao_monitoramento_de_gravacoes), utilizava um fluxo baseado em arquivos de texto:

1.  Cada cliente gerava um relatório (`.txt`) localmente.
2.  Esse arquivo era salvo em uma pasta sincronizada via OneDrive.
3.  Um script central aguardava a sincronização para ler os arquivos e enviar um relatório por e-mail.

O principal ponto de falha era a **dependência da sincronização do OneDrive**. Atrasos ou falhas de rede frequentemente resultavam em relatórios incompletos, minando a confiança na auditoria.

## Resolução: Migração para uma Arquitetura de API

Este projeto representa a evolução da solução anterior, eliminando completamente a necessidade de arquivos e sincronização. A nova arquitetura é baseada em comunicação direta e em tempo real:

1.  **Servidor API (`api_servidor.pyw`):** Um microsserviço web (Flask) roda no computador central, atuando como um ponto de coleta de dados.
2.  **Clientes (`gerar_relatorio_api_*.pyw`):** Scripts nos computadores clientes analisam o status das gravações e enviam os dados diretamente para a API via requisição HTTP POST.
3.  **Centralizador (`enviar_relatorios_api.pyw`):** Um script agendado no servidor central busca os dados coletados pela API, monta um relatório consolidado em HTML e o envia por e-mail.

Esta abordagem garante que os dados sejam transacionados instantaneamente, tornando o sistema de monitoramento muito mais robusto e confiável.

## Estrutura do Projeto

O repositório está dividido em duas partes principais:

### `raíz do projeto`
Contém os scripts que rodam na máquina principal.
*   **`api_servidor.pyw`**: O servidor Flask/Waitress que recebe os dados. Projetado para rodar como um serviço contínuo do Windows.
*   **`enviar_relatorios_api.pyw`**: O script que busca os dados da API, monta e envia o e-mail diário.
*   **`.env.example`**: Um arquivo de exemplo para as variáveis de ambiente. A senha do e-mail é carregada a partir de um arquivo `.env` real, que não deve ser versionado.

### `/gerar_relatorios`
Contém os scripts que são implantados nas máquinas dos clientes (local).
*   **`gerar_relatorio_api_intelbras.pyw`**: Script de exemplo para coletar dados de um sistema Intelbras.
*   **`gerar_relatorio_api_digifort.pyw`**: Script de exemplo para coletar dados de um sistema Digifort.
*   **`gerar_relatorio_api_ivms.pyw`**: Script de exemplo para coletar dados de um sistema iVMS.

## Como Colocar para Funcionar

### Pré-requisitos
*   [Python 3.x](https://www.python.org/downloads/)
*   Acesso de administrador para instalar o serviço no Windows.

### 1. Configuração do Servidor Central

1.  Clone [este repositório](https://github.com/n33miaz/relatorio-auditoria_gravacoes_cftv) para uma pasta na máquina central.
2.  Instale as dependências:
    ```bash
    pip install flask waitress requests python-dotenv
    ```
3.  Crie um arquivo `.env` na `raíz do projeto`, baseado no `.env.example`, e preencha com a senha do e-mail configurado em `api_servidor.pyw`:
    ```
    VALID="senha_do_email"
    ```
4.  Execute o `api_servidor.pyw`. Na primeira vez, o Firewall do Windows pode solicitar permissão para a rede. Permita o acesso para redes privadas.
5.  **Para produção**, transforme o `api_servidor.pyw` em um serviço do Windows para garantir que ele inicie automaticamente e rode em segundo plano. A ferramenta [NSSM (Non-Sucking Service Manager)](https://nssm.cc/) é altamente recomendada para isso.
    *   **Comando de instalação de exemplo:** `nssm install APICFTV`
    *   **Path:** `C:\pasta\onde\está\instalado\seu\python.exe`
    *   **Startup directory:** `C:\pasta\onde\você\deixou\a\automacao`
    *   **Arguments:** `api_servidor.pyw`
6.  Agende a execução do `enviar_relatorios_api.pyw` em algum Agendador de Tarefas (ex: o nativo do Windows) para rodar uma vez por dia, em um horário de baixa atividade.

### 2. Configuração dos Clientes

1.  Em cada máquina cliente, copie o script correspondente à tecnologia de CFTV utilizada (ex: `gerar_relatorio_api_intelbras.pyw`).
2.  Instale a dependência:
    ```bash
    pip install requests
    ```
3.  Edite o script e configure as seguintes variáveis:
    *   `CLIENTE`: Nome do cliente.
    *   `CAMINHO_BASE`: Caminho para a pasta raiz das gravações.
    *   `TECNOLOGIA`: Nome da tecnologia de monitoramento.
    *   `API_URL`: O endereço IP e a porta do seu servidor central.
4.  Agende a execução do script em algum Agendador de Tarefas para rodar uma vez por dia, **pelo menos uma hora antes** da execução do script centralizador.

Com isso, o sistema estará totalmente operacional, fornecendo auditorias diárias confiáveis e em tempo real sobre o estado das gravações.
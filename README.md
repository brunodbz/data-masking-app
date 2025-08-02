# Data Masking App - README

## Descrição

O Data Masking App é uma solução completa para mascaramento e restauração de informações sensíveis em documentos. Desenvolvida com Flask e Docker, a aplicação oferece uma interface web intuitiva e APIs RESTful para proteger dados como e-mails, CPFs, CNPJs e outras informações personalizadas. A solução inclui autenticação com Microsoft Entra ID (antigo Azure Active Directory), suporte a autenticação multifator (MFA), controle de acesso baseado em perfis de usuário, e histórico completo de operações.

## Funcionalidades Principais

### 🛡️ Mascaramento de Documentos
- **Suporte a múltiplos formatos**: Word (.docx), Excel (.xlsx) e PDF
- **Detecção automática**: Identifica e mascara automaticamente:
  - E-mails (padrão `nome.sobrenome@`)
  - CPFs (formato XXX.XXX.XXX-XX)
  - CNPJs (formato XX.XXX.XXX/XXXX-XX)
- **Mascaramento personalizado**: Permite adicionar palavras específicas para mascarar
- **Tokens únicos**: Cada informação mascarada recebe um token UUID para evitar conflitos

### 🔓 Restauração de Documentos
- **Restauração segura**: Utiliza IDs de sessão para restaurar documentos originais
- **Controle de acesso**: Apenas o usuário que mascarou o documento (ou administradores) pode restaurá-lo
- **Preservação de formato**: Mantém o formato original do documento após restauração

### 🔐 Autenticação e Segurança
- **Microsoft Entra ID**: Integração completa com o ecossistema Microsoft
- **Autenticação Multifator (MFA)**: Suporte a MFA via Microsoft Entra ID
- **Controle de acesso baseado em perfis**:
  - **Usuários comuns**: Acesso apenas aos próprios documentos
  - **Administradores**: Visualização de metadados de todos os documentos sem acesso aos arquivos
- **Sessões persistentes**: Armazenamento seguro de mapeamentos entre tokens e valores originais

### 📊 Histórico e Auditoria
- **Histórico de operações**: Registra todas as operações de mascaramento e restauração
- **IDs de sessão**: Armazena e exibe IDs de sessão para facilitar a restauração
- **Visão do administrador**: Permite visualizar todas as operações realizadas por todos os usuários
- **Últimos 10 documentos**: Usuários comuns veem seus últimos 10 documentos processados

### 🗂️ Gerenciamento de Arquivos
- **Armazenamento temporário**: Arquivos são excluídos automaticamente após 48 horas
- **Limpeza programada**: Scheduler para remoção de arquivos temporários
- **Upload seguro**: Validação de tipos de arquivo e nomes seguros

## Arquitetura

### Tecnologias Utilizadas
- **Backend**: Python com Flask
- **Banco de Dados**: PostgreSQL
- **Autenticação**: Microsoft Entra ID (Azure Active Directory)
- **Processamento de Documentos**:
  - python-docx para documentos Word
  - openpyxl para planilhas Excel
  - pdfplumber e reportlab para PDFs
- **Containerização**: Docker e Docker Compose
- **Agendamento de Tarefas**: APScheduler
- **Frontend**: HTML5, CSS3 e JavaScript

### Estrutura do Projeto
```
data-masking-app/
├── app.py                    # Aplicação Flask principal
├── requirements.txt          # Dependências Python
├── Dockerfile               # Configuração do contêiner Docker
├── docker-compose.yml       # Orquestração de serviços
├── .env.example             # Exemplo de variáveis de ambiente
├── .dockerignore           # Arquivos ignorados no build
├── models/                  # Modelos de banco de dados
│   ├── __init__.py
│   ├── user.py             # Modelo de usuário
│   ├── session.py          # Modelo de sessão de mascaramento
│   └── document_history.py # Modelo de histórico de documentos
├── auth/                    # Módulo de autenticação
│   ├── __init__.py
│   └── entra_id.py         # Integração com Microsoft Entra ID
├── utils/                   # Utilitários
│   ├── __init__.py
│   ├── database.py         # Configuração do banco de dados
│   ├── file_processor.py   # Processamento de documentos
│   └── cleanup.py         # Limpeza de arquivos temporários
├── static/                  # Arquivos estáticos
│   └── css/
│       └── style.css       # Estilos CSS
└── templates/              # Templates HTML
    ├── base.html           # Template base
    ├── login.html          # Página de login
    ├── user_dashboard.html  # Dashboard do usuário
    └── admin_dashboard.html # Dashboard do administrador
```

### Fluxo de Dados
1. **Autenticação**: Usuário faz login via Microsoft Entra ID (com ou sem MFA)
2. **Mascaramento**:
   - Usuário envia documento e palavras para mascarar
   - Sistema detecta automaticamente e-mails, CPFs e CNPJs
   - Sistema substitui informações sensíveis por tokens únicos
   - Sistema armazena mapeamentos no banco de dados
   - Sistema registra operação no histórico
   - Sistema retorna documento mascarado e ID da sessão
3. **Processamento Externo**: Usuário utiliza documento mascarado em outro sistema
4. **Restauração**:
   - Usuário envia documento mascarado e ID da sessão
   - Sistema valida permissões de acesso
   - Sistema restaura informações originais
   - Sistema registra operação no histórico
   - Sistema retorna documento original

## Instalação

### Pré-requisitos
- Docker (versão 20.10 ou superior)
- Docker Compose (versão 1.29 ou superior)
- Conta Microsoft com acesso ao Azure Portal
- Permissões de Administrador no Microsoft Entra ID

### Configuração do Microsoft Entra ID
1. Acesse o [Portal do Azure](https://portal.azure.com)
2. Navegue para **Microsoft Entra ID** > **Registros de aplicativo**
3. Crie um novo registro:
   - Nome: `Data Masking App`
   - Tipos de conta: `Contas em qualquer diretório organizacional`
   - URI de redirecionamento: `http://localhost:5000/auth/entra-id/callback`
4. Copie o **ID do aplicativo (cliente)** e o **ID do diretório (locatário)**
5. Vá para **Certificados e segredos** e crie um novo segredo do cliente
6. Configure o MFA:
   - Vá para **Segurança** > **Métodos de autenticação** e habilite os métodos desejados
   - Vá para **Segurança** > **Acesso condicional** e crie uma política para exigir MFA

### Configuração da Aplicação
1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/data-masking-app.git
   cd data-masking-app
   ```

2. Copie e configure as variáveis de ambiente:
   ```bash
   cp .env.example .env
   ```
   Edite o arquivo `.env` com suas credenciais do Microsoft Entra ID e configurações do banco de dados.

3. Construa e inicie os contêineres:
   ```bash
   docker-compose up --build -d
   ```

4. Configure o primeiro administrador:
   ```bash
   docker exec -it data-masking-app_db_1 psql -U postgres -d masking_app
   UPDATE users SET is_admin = true WHERE username = 'seu-username';
   ```

## Uso

### Para Usuários Comuns
1. Acesse `http://localhost:5000` e faça login com sua conta Microsoft
2. No dashboard do usuário:
   - **Mascarar documento**: Selecione um arquivo, adicione palavras opcionais para mascarar e clique em "Mascarar Documento"
   - Copie o ID da sessão exibido após o processamento
   - **Restaurar documento**: Selecione o arquivo mascarado, informe o ID da sessão e clique em "Restaurar Documento"
3. Na seção "Seus Últimos Documentos", visualize seu histórico e copie IDs de sessão

### Para Administradores
1. Após o login, você será redirecionado para o dashboard do administrador
2. **Gerenciar usuários**: Promova ou rebaixe usuários entre perfis comum e administrador
3. **Visualizar histórico**: Acesse o histórico de todos os documentos processados (apenas metadados)

## API Endpoints

### Autenticação
- `GET /login` - Inicia o processo de login com Microsoft Entra ID
- `GET /auth/entra-id/callback` - Callback para processamento do login
- `GET /logout` - Encerra a sessão do usuário

### Operações com Documentos
- `POST /mask` - Mascara um documento
  - Parâmetros: `file` (arquivo), `mask_words` (palavras para mascarar, opcional)
  - Retorna: Arquivo mascarado e ID da sessão no cabeçalho `X-Session-ID`
  
- `POST /unmask` - Restaura um documento
  - Parâmetros: `file` (arquivo mascarado), `session_id` (ID da sessão)
  - Retorna: Arquivo original

### Administração
- `POST /admin/promote/<user_id>` - Promove um usuário a administrador
- `POST /admin/demote/<user_id>` - Rebaixa um administrador a usuário comum

## Segurança

### Proteção de Dados
- Tokens únicos para cada informação mascarada
- Sessões persistentes com tempo de vida limitado
- Validação de permissões para restauração de documentos
- Exclusão automática de arquivos temporários após 48 horas

### Autenticação e Autorização
- Integração completa com Microsoft Entra ID
- Suporte a autenticação multifator (MFA)
- Controle de acesso baseado em perfis de usuário
- Sessões seguras com Flask

### Boas Práticas
- Uso de variáveis de ambiente para credenciais
- Validação de tipos de arquivo
- Nomes de arquivo seguros com `secure_filename`
- Proteção contra CSRF

## Manutenção

### Backup do Banco de Dados
```bash
docker exec -t data-masking-app_db_1 pg_dump -U postgres masking_app > backup.sql
```

### Restauração do Banco de Dados
```bash
docker exec -i data-masking-app_db_1 psql -U postgres -d masking_app < backup.sql
```

### Atualização da Aplicação
```bash
docker-compose pull
docker-compose up --build -d
```

## Contribuição

Contribuições são bem-vindas! Por favor, sinta-se à vontade para abrir uma issue para relatar bugs ou sugerir melhorias.

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Suporte

Se você encontrar algum problema ou tiver alguma dúvida, por favor, abra uma issue no repositório ou entre em contato com a equipe de suporte.

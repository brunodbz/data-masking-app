# Data Masking App - README

## Descrição

O Data Masking App é uma solução completa para mascaramento e restauração de informações sensíveis em documentos. Desenvolvida com Flask e Docker, a aplicação oferece uma interface web intuitiva e APIs RESTful para proteger dados como e-mails, CPFs, CNPJs e outras informações personalizadas. A solução inclui autenticação com Microsoft Entra ID (antigo Azure Active Directory), suporte a autenticação local com MFA obrigatório, controle de acesso baseado em perfis de usuário, e histórico completo de operações.

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
- **Autenticação Local com MFA Obrigatório**: 
  - Registro de usuários locais com MFA obrigatório
  - Compatibilidade com Microsoft Authenticator, Google Authenticator e Authy
  - Configuração simplificada com QR Code
- **Controle de acesso baseado em perfis**:
  - **Usuários comuns**: Acesso apenas aos próprios documentos
  - **Administradores**: Visualização de metadados de todos os documentos sem acesso aos arquivos
- **Sessões persistentes**: Armazenamento seguro de mapeamentos entre tokens e valores originais

### 👥 Gestão de Usuários
- **Primeiro usuário como administrador**: A primeira conta local criada é automaticamente definida como administrador
- **Aprovação de usuários**: Demais contas locais precisam ser aprovadas por um administrador
- **Recuperação de senha**: Sistema de recuperação de senha via e-mail com token seguro
- **Gerenciamento de perfis**: Administradores podem promover ou rebaixar usuários

### 📧 Sistema de E-mails
- **Configuração SMTP**: Painel administrativo para configurar servidor de e-mails
- **Notificações automáticas**: Envio de e-mail para cada documento processado
  - Informações do documento (nome e ID da sessão)
  - Formatos em texto e HTML
- **Recuperação de senha**: Envio de e-mail com link seguro para redefinição de senha

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
│   ├── document_history.py # Modelo de histórico de documentos
│   └── email_config.py     # Modelo de configuração de e-mail
├── auth/                    # Módulo de autenticação
│   ├── __init__.py
│   ├── entra_id.py         # Integração com Microsoft Entra ID
│   └── local_auth.py       # Autenticação local
├── utils/                   # Utilitários
│   ├── __init__.py
│   ├── database.py         # Configuração do banco de dados
│   ├── file_processor.py   # Processamento de documentos
│   ├── cleanup.py         # Limpeza de arquivos temporários
│   ├── mfa.py             # Utilitários MFA
│   ├── auth.py            # Utilitários de autenticação
│   └── email_sender.py    # Envio de e-mails
├── static/                  # Arquivos estáticos
│   └── css/
│       └── style.css       # Estilos CSS
└── templates/              # Templates HTML
    ├── base.html           # Template base
    ├── login.html          # Página de login
    ├── login_choice.html   # Escolha do método de login
    ├── register.html       # Registro de usuário local
    ├── setup_mfa.html      # Configuração do MFA
    ├── local_login.html    # Login local
    ├── verify_mfa.html     # Verificação do MFA
    ├── forgot_password.html # Recuperação de senha
    ├── reset_password.html  # Redefinição de senha
    ├── user_dashboard.html  # Dashboard do usuário
    └── admin_dashboard.html # Dashboard do administrador
```

### Fluxo de Dados
1. **Autenticação**: Usuário faz login via Microsoft Entra ID ou autenticação local com MFA
2. **Mascaramento**:
   - Usuário envia documento e palavras para mascarar
   - Sistema detecta automaticamente e-mails, CPFs e CNPJs
   - Sistema substitui informações sensíveis por tokens únicos
   - Sistema armazena mapeamentos no banco de dados
   - Sistema registra operação no histórico
   - Sistema envia e-mail com informações do documento
   - Sistema retorna documento mascarado e ID da sessão
3. **Processamento Externo**: Usuário utiliza documento mascarado em outro sistema
4. **Restauração**:
   - Usuário envia documento mascarado e ID da sessão
   - Sistema valida permissões de acesso
   - Sistema restaura informações originais
   - Sistema registra operação no histórico
   - Sistema envia e-mail com informações do documento
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
   git clone https://github.com/brunodbz/data-masking-app.git
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

4. Execute as migrações do banco de dados:
   ```bash
   docker exec -it data-masking-app_web_1 python migrate_db.py
   ```

5. Configure o primeiro administrador:
   - Crie uma conta local através da interface web
   - A primeira conta local será automaticamente definida como administrador

## Uso

### Para Usuários Locais
1. Na página de login, clique em "Login Local"
2. Se não tiver uma conta, clique em "Registre-se" para criar uma
3. Durante o registro, você será orientado a configurar o MFA
4. Escaneie o QR Code com seu aplicativo de autenticação preferido
5. Digite o código de verificação para concluir o registro
6. Se não for o primeiro usuário, aguarde a aprovação de um administrador
7. Para fazer login, digite seu nome de usuário, senha e o código MFA
8. Para recuperar sua senha, clique em "Esqueceu a senha" e siga as instruções

### Para Usuários do Microsoft Entra ID
1. Na página de login, clique em "Login com Microsoft"
2. Faça login com sua conta Microsoft
3. Se o MFA estiver configurado no Microsoft Entra ID, você será solicitado a fornecer o segundo fator
4. Após a autenticação, você será redirecionado para o dashboard

### Para Administradores
1. No dashboard do administrador, você pode visualizar todos os usuários
2. É possível identificar usuários locais e usuários do Microsoft Entra ID
3. É possível verificar se o MFA está habilitado para usuários locais
4. É possível aprovar ou rejeitar novos usuários locais
5. Você pode promover ou rebaixar usuários conforme necessário
6. Configure o servidor SMTP para envio de e-mails

### Mascaramento de Documentos
1. No dashboard do usuário, clique em "Mascarar Documento"
2. Selecione um arquivo (Word, Excel ou PDF)
3. Opcionalmente, adicione palavras adicionais para mascarar
4. Clique em "Mascarar Documento"
5. O sistema enviará um e-mail com as informações do documento
6. Copie o ID da sessão exibido após o processamento

### Restauração de Documentos
1. No dashboard do usuário, clique em "Restaurar Documento"
2. Selecione o arquivo mascarado
3. Informe o ID da sessão obtido no mascaramento
4. Clique em "Restaurar Documento"
5. O sistema enviará um e-mail com as informações do documento

## API Endpoints

### Autenticação
- `GET /login` - Inicia o processo de login
- `GET /auth/entra-id/callback` - Callback para processamento do login com Microsoft Entra ID
- `GET /logout` - Encerra a sessão do usuário
- `POST /local_auth/register` - Registra um novo usuário local
- `POST /local_auth/login` - Login de usuário local
- `POST /local_auth/verify-mfa` - Verificação do MFA
- `POST /local_auth/forgot-password` - Solicitação de recuperação de senha
- `POST /local_auth/reset-password/<token>` - Redefinição de senha

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
- `POST /admin/approve-user/<user_id>` - Aprova um usuário local
- `POST /admin/reject-user/<user_id>` - Rejeita e exclui um usuário local
- `GET/POST /admin/email-config` - Configuração do servidor SMTP

## Segurança

### Proteção de Dados
- Tokens únicos para cada informação mascarada
- Sessões persistentes com tempo de vida limitado
- Validação de permissões para restauração de documentos
- Exclusão automática de arquivos temporários após 48 horas
- Tokens seguros para recuperação de senha com expiração

### Autenticação e Autorização
- Integração completa com Microsoft Entra ID
- Suporte a autenticação multifator (MFA) para ambos os métodos de login
- Controle de acesso baseado em perfis de usuário
- Sessões seguras com Flask
- Aprovação obrigatória para novos usuários locais

### Boas Práticas
- Uso de variáveis de ambiente para credenciais
- Validação de tipos de arquivo
- Nomes de arquivo seguros com `secure_filename`
- Proteção contra CSRF
- Senhas hasheadas com algoritmo seguro
- Tokens de recuperação de senha com expiração

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

### Migrações do Banco de Dados
```bash
docker exec -it data-masking-app_web_1 python migrate_db.py
```

### Logs da Aplicação
```bash
docker-compose logs -f web
```

## Contribuição

Contribuições são bem-vindas! Por favor, sinta-se à vontade para abrir uma issue para relatar bugs ou sugerir melhorias.

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Suporte

Se você encontrar algum problema ou tiver alguma dúvida, por favor, abra uma issue no repositório ou entre em contato com a equipe de suporte.

---

**Data Masking App** - Protegendo informações sensíveis com tecnologia de ponta desde 2025.

[🔗 GitHub Repository](https://github.com/brunodbz/data-masking-app) | [📖 Documentação](https://github.com/brunodbz/data-masking-app/blob/main/README.md) | [🐛 Reportar Issues](https://github.com/brunodbz/data-masking-app/issues)

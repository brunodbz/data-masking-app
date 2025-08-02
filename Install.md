# Passo a Passo para Instalação, Configuração e Uso da Aplicação de Mascaramento de Dados

## Índice
1. [Pré-requisitos](#pré-requisitos)
2. [Configuração do Microsoft Entra ID](#configuração-do-microsoft-entra-id)
3. [Preparação do Ambiente](#preparação-do-ambiente)
4. [Instalação e Configuração da Aplicação](#instalação-e-configuração-da-aplicação)
5. [Configuração do Banco de Dados](#configuração-do-banco-de-dados)
6. [Inicialização da Aplicação](#inicialização-da-aplicação)
7. [Configuração do Primeiro Administrador](#configuração-do-primeiro-administrador)
8. [Uso da Aplicação](#uso-da-aplicação)
9. [Manutenção e Backup](#manutenção-e-backup)
10. [Solução de Problemas Comuns](#solução-de-problemas-comuns)

---

## 1. Pré-requisitos

### Software Necessário
- **Docker** (versão 20.10 ou superior)
- **Docker Compose** (versão 1.29 ou superior)
- **Git** (para clonar o repositório)

### Contas Necessárias
- **Conta Microsoft** com acesso ao Azure Portal
- **Permissões de Administrador** no Microsoft Entra ID (antigo Azure Active Directory)

### Conhecimentos Básicos
- Linha de comando (terminal)
- Conceitos básicos de Docker
- Noções de bancos de dados relacionais

---

## 2. Configuração do Microsoft Entra ID

### 2.1 Criar um Novo Registro de Aplicação
1. Acesse o [Portal do Azure](https://portal.azure.com)
2. Navegue para **Microsoft Entra ID** (antigo Azure Active Directory)
3. Selecione **Registros de aplicativo** e clique em **Novo registro**
4. Preencha as informações:
   - **Nome**: `Data Masking App`
   - **Tipos de conta suportados**: `Contas em qualquer diretório organizacional`
   - **URI de redirecionamento**: `http://localhost:5000/auth/entra-id/callback`
5. Clique em **Registrar**

### 2.2 Obter Credenciais da Aplicação
1. Anote os seguintes valores:
   - **ID do aplicativo (cliente)**
   - **ID do diretório (locatário)**

2. Vá para **Certificados e segredos**:
   - Clique em **Novo segredo do cliente**
   - Descrição: `Data Masking App Secret`
   - Expira: Escolha uma opção (recomendado 24 meses)
   - Clique em **Adicionar**
   - **Copie imediatamente o Valor do segredo** (ele não será exibido novamente)

### 2.3 Configurar Autenticação Multifator (MFA)
1. No Microsoft Entra ID, vá para **Segurança** > **Métodos de autenticação**
2. Habilite os métodos desejados (ex: Aplicativo autenticador, SMS)
3. Vá para **Segurança** > **Acesso condicional**
4. Clique em **Nova política**:
   - **Nome**: `Exigir MFA para Data Masking App`
   - **Atribuições**:
     - **Usuários e grupos**: Selecione os usuários que devem usar MFA
     - **Aplicativos na nuvem**: Selecione o aplicativo "Data Masking App"
   - **Controles de acesso**:
     - **Conceder**: Marque "Exigir autenticação multifator"
   - **Ativar política**: Sim
5. Clique em **Criar**

---

## 3. Preparação do Ambiente

### 3.1 Clonar o Repositório
```bash
git clone https://github.com/brunodbz/data-masking-app.git
cd data-masking-app
```

### 3.2 Estrutura de Diretórios
Verifique se a estrutura está correta:
```
data-masking-app/
├── app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── models/
├── auth/
├── utils/
└── static/
```

---

## 4. Instalação e Configuração da Aplicação

### 4.1 Configurar Variáveis de Ambiente
1. Copie o arquivo de exemplo:
```bash
cp .env.example .env
```

2. Edite o arquivo `.env` com suas informações:
```env
# Configurações do Banco de Dados
POSTGRES_USER=postgres
POSTGRES_PASSWORD=sua-senha-segura-aqui
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=masking_app

# Configurações do Microsoft Entra ID
ENTRA_ID_CLIENT_ID=seu-client-id
ENTRA_ID_CLIENT_SECRET=seu-client-secret
ENTRA_ID_TENANT_ID=seu-tenant-id
ENTRA_ID_REDIRECT_URI=http://localhost:5000/auth/entra-id/callback

# Configurações da Aplicação
SECRET_KEY=uma-chave-secreta-muito-longa-e-aleatoria
FLASK_ENV=development
```

### 4.2 Construir a Imagem Docker
```bash
docker-compose build
```

---

## 5. Configuração do Banco de Dados

### 5.1 Iniciar o Banco de Dados
```bash
docker-compose up -d db
```

### 5.2 Verificar Status do Banco
```bash
docker-compose ps
```
O contêiner `db` deve estar com status `Up`.

### 5.3 Conectar ao Banco (Opcional)
```bash
docker-compose exec db psql -U postgres -d masking_app
```
Digite `\q` para sair.

---

## 6. Inicialização da Aplicação

### 6.1 Iniciar Todos os Serviços
```bash
docker-compose up -d
```

### 6.2 Verificar Status dos Serviços
```bash
docker-compose ps
```
Ambos os contêineres (`web` e `db`) devem estar com status `Up`.

### 6.3 Verificar Logs
```bash
docker-compose logs -f web
```
Pressione `Ctrl+C` para sair.

---

## 7. Configuração do Primeiro Administrador

### 7.1 Acessar a Aplicação
Abra seu navegador e acesse: `http://localhost:5000`

### 7.2 Fazer Login
1. Clique em "Login com Microsoft"
2. Faça login com uma conta Microsoft que tenha permissão no Entra ID
3. O primeiro usuário será criado como usuário comum

### 7.3 Promover a Administrador
1. Acesse o terminal e execute:
```bash
# Acessar o contêiner do banco de dados
docker exec -it data-masking-app_db_1 psql -U postgres -d masking_app

# No prompt do PostgreSQL, execute:
UPDATE users SET is_admin = true WHERE username = 'seu-username';

# Saia do PostgreSQL com \q
```

### 7.4 Verificar Promoção
1. Faça logout e login novamente
2. Você deve ser redirecionado para o dashboard do administrador

---

## 8. Uso da Aplicação

### 8.1 Para Usuários Comuns

#### 8.1.1 Dashboard do Usuário
Após o login, você será redirecionado para o dashboard do usuário, onde poderá:
- Visualizar seus últimos 10 documentos processados
- Mascarar novos documentos
- Restaurar documentos previamente mascarados

#### 8.1.2 Mascarar um Documento
1. Clique em "Mascarar Documento"
2. Selecione um arquivo (Word, Excel ou PDF)
3. Opcionalmente, adicione palavras para mascarar (separadas por vírgula)
4. Clique em "Mascarar Documento"
5. O arquivo será baixado automaticamente
6. O ID da sessão será exibido na tela - copie este ID para uso posterior

#### 8.1.3 Restaurar um Documento
1. Clique em "Restaurar Documento"
2. Selecione o arquivo mascarado
3. Cole o ID da sessão obtido no passo anterior
4. Clique em "Restaurar Documento"
5. O arquivo original será baixado

#### 8.1.4 Histórico de Documentos
Na seção "Seus Últimos Documentos", você pode:
- Ver os últimos 10 documentos processados
- Copiar o ID da sessão de qualquer documento
- Ver a data e hora de cada operação

### 8.2 Para Administradores

#### 8.2.1 Dashboard do Administrador
Após o login, você será redirecionado para o dashboard do administrador, onde poderá:
- Gerenciar usuários (promover/rebaixar)
- Visualizar histórico de todos os documentos
- Acessar apenas metadados dos documentos (sem acesso aos arquivos)

#### 8.2.2 Gerenciar Usuários
1. Na seção "Gerenciar Usuários", você verá todos os usuários cadastrados
2. Use os botões "Promover" ou "Rebaixar" para alterar o perfil dos usuários
3. Usuários promovidos terão acesso ao dashboard do administrador

#### 8.2.3 Visualizar Histórico
Na seção "Histórico de Documentos", você pode:
- Ver todos os documentos processados por todos os usuários
- Ver o nome do arquivo, o usuário, a operação e o ID da sessão
- **Importante**: Você não tem acesso aos arquivos, apenas aos metadados

---

## 9. Manutenção e Backup

### 9.1 Parar a Aplicação
```bash
docker-compose down
```

### 9.2 Reiniciar a Aplicação
```bash
docker-compose restart
```

### 9.3 Atualizar a Aplicação
```bash
docker-compose pull
docker-compose up --build -d
```

### 9.4 Backup do Banco de Dados
```bash
docker exec -t data-masking-app_db_1 pg_dump -U postgres masking_app > backup.sql
```

### 9.5 Restaurar Banco de Dados
```bash
docker exec -i data-masking-app_db_1 psql -U postgres -d masking_app < backup.sql
```

### 9.6 Limpeza de Arquivos Temporários
A aplicação exclui automaticamente arquivos temporários com mais de 48 horas. Para forçar uma limpeza:
```bash
docker exec data-masking-app_web_1 python -c "from utils.cleanup import cleanup_old_files; cleanup_old_files('/app/uploads')"
```

---

## 10. Solução de Problemas Comuns

### 10.1 Problema: Erro ao conectar ao banco de dados
**Solução:**
- Verifique se o contêiner do banco de dados está rodando: `docker ps`
- Verifique as variáveis de ambiente no arquivo `.env`
- Verifique os logs do banco de dados: `docker-compose logs db`

### 10.2 Problema: Erro de autenticação com Microsoft Entra ID
**Solução:**
- Verifique se as configurações do Entra ID estão corretas
- Verifique se o URI de redirecionamento está correto
- Verifique se o segredo do cliente é válido
- Verifique se o usuário tem permissão para acessar o aplicativo

### 10.3 Problema: MFA não está funcionando
**Solução:**
- Verifique se a política de acesso condicional está configurada corretamente
- Verifique se o usuário tem métodos de autenticação configurados
- Verifique se o usuário está incluído na política de MFA

### 10.4 Problema: Arquivos não são mascarados corretamente
**Solução:**
- Verifique se o formato do arquivo é suportado (docx, xlsx, pdf)
- Verifique se as palavras para mascarar estão corretas
- Verifique os logs da aplicação: `docker-compose logs web`

### 10.5 Problema: ID da sessão não é exibido
**Solução:**
- Verifique se o JavaScript está habilitado no navegador
- Verifique os logs do navegador para erros de JavaScript
- Verifique os logs da aplicação: `docker-compose logs web`

### 10.6 Problema: Não consigo promover o primeiro usuário a administrador
**Solução:**
- Verifique se você está usando o nome de usuário correto no comando SQL
- Verifique se o usuário foi criado no banco de dados
- Tente reiniciar os contêineres: `docker-compose restart`

---

## Configuração para Produção

Para uso em produção, considere as seguintes alterações:

### 1. Segurança
- Use HTTPS com certificado SSL/TLS válido
- Use variáveis de ambiente seguras (não o arquivo `.env`)
- Use um proxy reverso (Nginx, Apache)
- Configure um firewall para restringir acesso

### 2. Banco de Dados
- Use um serviço de banco de dados gerenciado (Azure Database for PostgreSQL, AWS RDS)
- Configure backups automáticos
- Use senhas fortes e rotativas

### 3. Microsoft Entra ID
- Use um locatário dedicado para produção
- Configure políticas de acesso condicional mais restritivas
- Use grupos do Azure AD para gerenciar permissões

### 4. Monitoramento
- Configure monitoramento de logs e métricas
- Configure alertas para erros e anomalias
- Use ferramentas como Prometheus, Grafana ou Azure Monitor

### 5. Escalabilidade
- Configure múltiplas instâncias da aplicação
- Use um balanceador de carga
- Considere usar Kubernetes para orquestração

---


Este passo a passo cobre todo o ciclo de vida da aplicação, desde a instalação até o uso e manutenção. Se você tiver alguma dúvida ou encontrar algum problema, consulte os logs ou entre em contato com o suporte.

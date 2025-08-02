# Data Masking App - Notas de Atualização v1.1.0

Estamos muito felizes em anunciar a versão 1.1.0 do Data Masking App! Esta atualização traz uma das funcionalidades mais solicitadas pela comunidade: **suporte completo a autenticação local com MFA obrigatório**, mantendo toda a robustez da integração com Microsoft Entra ID.

## 🚀 Novas Funcionalidades

### 🔐 Autenticação Local com MFA Obrigatório
- **Registro de usuários locais**: Agora é possível criar contas diretamente na aplicação, sem depender do Microsoft Entra ID
- **MFA obrigatório para todos os usuários locais**: Todas as contas locais devem configurar autenticação de dois fatores durante o registro
- **Compatibilidade múltipla**: Suporte total para Microsoft Authenticator, Google Authenticator e Authy
- **Configuração simplificada**: QR Code para fácil configuração do MFA, com opção de digitação manual da chave secreta

### 🔑 Sistema de Autenticação Híbrido
- **Escolha do método de login**: Interface unificada que permite ao usuário escolher entre login local ou com Microsoft Entra ID
- **Gestão unificada de usuários**: Administradores podem visualizar e gerenciar todos os usuários, independentemente do método de autenticação
- **Identificação visual clara**: Badges que distinguem usuários locais de usuários do Microsoft Entra ID

### 🛡️ Segurança Reforçada
- **Segredos MFA únicos**: Cada usuário recebe um segredo MFA gerado aleatoriamente
- **Validação tolerante**: Sistema de validação de códigos MFA com janela de tempo para evitar problemas de sincronização
- **Armazenamento seguro**: Segredos MFA armazenados de forma segura no banco de dados

## ✨ Melhorias

### 🎨 Interface do Usuário Aprimorada
- **Novo design da página de login**: Interface moderna com opções claras para escolha do método de autenticação
- **Página de registro intuitiva**: Fluxo simplificado para criação de contas locais
- **Assistente de configuração do MFA**: Interface passo a passo para configuração do autenticador
- **Dashboard do administrador expandido**: Agora exibe informações sobre o tipo de autenticação e status do MFA de cada usuário

### 🔧 Melhorias Técnicas
- **Arquitetura modular**: Separação clara entre autenticação local e Microsoft Entra ID usando Blueprints
- **Validações aprimoradas**: Validação robusta de formulários e dados de entrada
- **Gerenciamento de sessões**: Melhor controle sobre sessões temporárias durante o processo de autenticação

### 📱 Responsividade
- **Design mobile-first**: Interface totalmente responsiva para todos os dispositivos
- **Melhor experiência em tablets**: Layout otimizado para telas de tamanho intermediário

## 🐛 Correções de Bugs

- Corrigido problema de exibição de IDs de sessão em dispositivos móveis
- Melhorada a validação de formatos de CPF e CNPJ em documentos PDF
- Corrigido bug que impedia a cópia de IDs de sessão em alguns navegadores
- Resolvido problema de redirecionamento após logout em cenários específicos

## 🔄 Como Atualizar

### Para instalações novas:
Siga o passo a passo completo no README.md do projeto.

### Para atualizar instalações existentes:

1. **Faça backup do seu banco de dados:**
   ```bash
   docker exec -t data-masking-app_db_1 pg_dump -U postgres masking_app > backup.sql
   ```

2. **Atualize o código:**
   ```bash
   git pull origin main
   ```

3. **Atualize as dependências:**
   ```bash
   docker-compose build --no-cache
   ```

4. **Reinicie os serviços:**
   ```bash
   docker-compose up -d
   ```

5. **Verifique a atualização:**
   Acesse a aplicação e confirme que a nova página de login está disponível.

## 📝 Notas Importantes

- **Migração de usuários**: Usuários existentes do Microsoft Entra ID não são afetados por esta atualização
- **Primeiro administrador**: Se esta é uma nova instalação, lembre-se de promover o primeiro usuário a administrador conforme as instruções do README
- **Configuração do MFA**: O MFA é obrigatório apenas para novos usuários locais. Usuários do Microsoft Entra ID continuam utilizando o MFA configurado no Microsoft Entra ID

## 🙏 Agradecimentos

Gostaríamos de agradecer a toda a comunidade que contribuiu com feedback e sugestões para esta versão. Um agradecimento especial aos usuários que solicitaram a funcionalidade de autenticação local e ajudaram a testar as versões preliminares.

## 📋 Próximas Passos

Estamos trabalhando ativamente nas seguintes melhorias para futuras versões:

- Integração com outros provedores de autenticação (Google, GitHub)
- API REST completa para automação de processos
- Interface de administração avançada com relatórios e auditoria
- Suporte a mais formatos de documento (PowerPoint, imagens)

---

**Data Masking App** - Protegendo informações sensíveis com tecnologia de ponta.

[🔗 GitHub Repository](https://github.com/brunodbz/data-masking-app) | [📖 Documentação](https://github.com/brunodbz/data-masking-app/blob/main/README.md) | [🐛 Reportar Issues](https://github.com/brunodbz/data-masking-app/issues)
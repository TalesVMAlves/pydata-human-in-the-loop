## Configuração de Ambiente GCP
- Acesse console.cloud.google.com/
- Faça o login na sua conta do google
- Crie um novo projeto
- No menu de seleção, no canto superior esquerdo navegue APIs e Serviços > Biblioteca.
- Ative o Gmail API
## Configurando as Credenciais
- No menu de navegação, vá em APIs e Serviços > Tela de permissão OAuth
- Preencha os campos obrigatórios, como: nome do app, email de suporte
- Público externo, assim qualquer conta Gmail será capaz de acessar ao publicar o app
- Adicione usuário de teste, esses serão os únicos usuários que terão acesso ao aplicativo em desenvolvimento
- Navegue novamente no menu, vá em APIs e Serviços > Credenciais
- No topo da tela, clique em + Criar Credenciais e selecione ID do cliente OAuth
- Para o agente de Gmail o tipo de aplicativo será App para computador
- Crie o ID do cliente OAuth e faça o download do Json

Mova o json da sua pasta de downloads para dentro do projeto que irá utilizar o serviço, uma boa prática é renomear esse arquivo para "credentials.json" por exemplo e adicioná-lo ao .gitignore ou .dockerignore
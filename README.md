# Extrator de Clientes do Stripe

Um script Python simples para extrair dados de clientes do Stripe e salvá-los em um arquivo CSV.

## Funcionalidades

- Extrai nome, e-mail, telefone e assinaturas ativas dos clientes
- Salva os dados em um arquivo CSV com timestamp no diretório `outputs`
- Gerencia paginação para obter todos os clientes
- Trata dados ausentes marcando campos como "Vazio"

## Instalação

### Instalação Automática

Execute o script de instalação para configurar automaticamente o ambiente:

```
./setup.sh
```

Este script irá:
1. Verificar e instalar Python se necessário
2. Configurar um ambiente virtual
3. Instalar todas as dependências
4. Criar um arquivo `.env` modelo

### Instalação Manual

1. Clone este repositório
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
   Ou instale manualmente:
   ```
   pip install stripe python-dotenv pandas
   ```
3. Crie um arquivo `.env` na pasta raiz com sua chave API do Stripe:
   ```
   STRIPE_API_KEY=sua_chave_api_stripe
   ```
   Alternativamente, você pode inserir a chave API quando solicitado pelo script.

## Uso

Execute o script:
```
python stripe_extractor.py
```

O script irá:
1. Conectar-se à API do Stripe usando sua chave API
2. Buscar todos os clientes com seus dados de assinatura
3. Extrair informações de nome, e-mail, telefone e assinaturas ativas
4. Salvar os dados em um arquivo CSV no diretório `outputs`

O arquivo CSV contém as seguintes colunas:
- name (mostra "Vazio" se ausente)
- email (mostra "Vazio" se ausente)
- phone (mostra "Vazio" se ausente)
- active_subscriptions (mostra "Vazio" se não houver assinaturas ativas)

O arquivo de saída será nomeado `outputs/stripe_customers_AAAAMMDD_HHMMSS.csv` com o timestamp atual.

## Nota de Segurança

Nunca cometa o erro de incluir sua chave API do Stripe no controle de versão. O arquivo `.env` está incluído no `.gitignore` para ajudar a prevenir a exposição acidental de credenciais sensíveis.
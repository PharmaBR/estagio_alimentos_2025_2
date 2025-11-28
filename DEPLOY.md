# 🚀 Guia de Deploy no Streamlit Cloud

## Pré-requisitos
- Conta no GitHub (já configurada ✅)
- Repositório: `PharmaBR/estagio_alimentos_2025_2` (já criado ✅)
- Código commitado e pushed (já feito ✅)

## Passo a Passo

### 1. Acessar Streamlit Cloud

Acesse: [share.streamlit.io](https://share.streamlit.io)

### 2. Fazer login com GitHub

Clique em "Sign in with GitHub" e autorize o Streamlit Cloud

### 3. Deploy das 3 Aplicações

Você precisará criar **3 apps separados** no Streamlit Cloud:

#### 📱 App 1: Interface dos Estudantes

1. Clique em "New app"
2. Selecione:
   - **Repository**: `PharmaBR/estagio_alimentos_2025_2`
   - **Branch**: `main`
   - **Main file path**: `app.py`
3. **App URL**: escolha algo como `estagio-alimentos-estudantes`
4. Clique em "Deploy"

#### 📱 App 2: Configuração do Supervisor

1. Clique em "New app" novamente
2. Selecione:
   - **Repository**: `PharmaBR/estagio_alimentos_2025_2`
   - **Branch**: `main`
   - **Main file path**: `supervisor_config.py`
3. **App URL**: escolha algo como `estagio-alimentos-supervisor`
4. Clique em "Deploy"

#### 📱 App 3: Gerenciamento de Feriados (Admin)

1. Clique em "New app" novamente
2. Selecione:
   - **Repository**: `PharmaBR/estagio_alimentos_2025_2`
   - **Branch**: `main`
   - **Main file path**: `manage_holidays.py`
3. **App URL**: escolha algo como `estagio-alimentos-admin`
4. Clique em "Deploy"

### 4. Aguardar o Deploy

- O Streamlit Cloud irá:
  1. Clonar o repositório
  2. Instalar dependências do `requirements.txt`
  3. Instalar pacotes do sistema do `packages.txt`
  4. Iniciar a aplicação

- O processo leva aproximadamente 2-5 minutos

### 5. Verificar o Deploy

Após o deploy, você terá 3 URLs:
- `https://estagio-alimentos-estudantes.streamlit.app` (ou o nome que escolheu)
- `https://estagio-alimentos-supervisor.streamlit.app`
- `https://estagio-alimentos-admin.streamlit.app`

## 🔄 Atualizações Futuras

Sempre que você fizer mudanças no código:

```bash
git add .
git commit -m "Descrição das mudanças"
git push origin main
```

O Streamlit Cloud detecta automaticamente e redesploya a aplicação!

## 🎯 Fluxo de Uso Recomendado

1. **Supervisor** acessa o app de configuração e cria o template
2. **Admin** acessa o app de feriados e cadastra as datas especiais
3. **Estudantes** acessam o app principal e geram seus documentos

## ⚠️ Importante

- Os arquivos `custom_holidays.json` e `internship_template.json` são criados em runtime
- Cada app mantém seus próprios arquivos (não compartilhados entre deploys)
- Para produção, considere usar um banco de dados ou storage compartilhado

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'fitz'"
- Solução: O `packages.txt` já está configurado com as dependências necessárias

### Erro: "File not found: templates/"
- Certifique-se de que a pasta `templates/` com os PDFs está no repositório

### App não carrega
- Verifique os logs no Streamlit Cloud (botão "Manage app" → "Logs")
- Confirme que todos os arquivos necessários estão no repositório

## 📞 Suporte

Em caso de problemas, verifique:
1. Logs do Streamlit Cloud
2. Issues do repositório no GitHub
3. Documentação oficial: [docs.streamlit.io](https://docs.streamlit.io)

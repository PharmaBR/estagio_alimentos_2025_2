# Sistema de Preenchimento de Documentos de Estágio

Sistema automatizado para preenchimento de documentos de estágio em PDF com interface web usando Streamlit.

## 📋 Funcionalidades

- ✅ Preenchimento automático de checklist
- ✅ Geração de folhas de frequência (máximo 3)
- ✅ Declaração de realização de estágio
- ✅ Declaração de atividade obrigatória
- ✅ Interface web amigável com 3 módulos separados
- ✅ Gerenciamento de feriados personalizados
- ✅ Configuração de template pelo supervisor
- ✅ Seleção de dias da semana do estágio
- ✅ Detecção automática de feriados brasileiros
- ✅ Cálculo automático de atividades complementares
- ✅ Download em ZIP de todos os documentos

## 🚀 Deploy no Streamlit Cloud

### Passo 1: Preparar o repositório
✅ Repositório GitHub: `PharmaBR/estagio_alimentos_2025_2`
✅ Arquivos necessários criados:
- `requirements.txt` - Dependências Python
- `packages.txt` - Dependências do sistema
- `.streamlit/config.toml` - Configuração do tema

### Passo 2: Deploy das aplicações

Acesse [share.streamlit.io](https://share.streamlit.io) e faça o deploy de 3 apps separados:

#### 1. 🎓 App dos Estudantes
- **Arquivo**: `app.py`
- **URL sugerida**: `estagio-alimentos-estudantes`
- **Descrição**: Interface simplificada para estudantes preencherem seus dados

#### 2. 👨‍🏫 App do Supervisor
- **Arquivo**: `supervisor_config.py`
- **URL sugerida**: `estagio-alimentos-supervisor`
- **Descrição**: Configuração de templates de estágio pelo supervisor

#### 3. ⚙️ App Administrativo
- **Arquivo**: `manage_holidays.py`
- **URL sugerida**: `estagio-alimentos-admin`
- **Descrição**: Gerenciamento de feriados personalizados

## 💻 Como usar localmente

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar template de estágio (Supervisor)

```bash
streamlit run supervisor_config.py
```

Configure:
- Período do estágio
- Carga horária diária
- Dias da semana
- Descrição de atividades por encontro

### 3. Configurar feriados (Responsável pelo Estágio)

```bash
streamlit run manage_holidays.py
```

Cadastre feriados municipais, pontos facultativos e datas especiais.

### 4. Gerar documentos (Estudantes)

```bash
streamlit run app.py
```

Preencha seus dados pessoais e gere automaticamente todos os documentos.

### 5. Acessar no navegador

As aplicações abrirão automaticamente em `http://localhost:8501`

## 👥 Três módulos do sistema

### 👨‍🏫 Módulo Supervisor (`supervisor_config.py`)
- Configuração de templates de estágio
- Define período, carga horária e dias da semana
- Cria descrições de atividades por encontro
- Template salvo automaticamente para todos os estudantes

### ⚙️ Módulo Administrativo (`manage_holidays.py`)
- Para responsáveis pelo estágio
- Cadastro de feriados personalizados
- Visualização de feriados oficiais
- Feriados salvos em arquivo JSON compartilhado

### 🎓 Módulo Estudante (`app.py`)
- Interface simplificada para estudantes
- Auto-carrega template do supervisor
- Coleta apenas dados pessoais
- Geração automática de todos os documentos
- Download em ZIP

## 📁 Estrutura do projeto

```
estagio_filler/
├── app.py                    # Aplicação estudantes
├── supervisor_config.py      # Configuração supervisor
├── manage_holidays.py        # Gerenciamento feriados (admin)
├── models.py                 # Modelos de dados
├── docs_filler.py            # Lógica de preenchimento
├── date_utils.py             # Utilitários de datas e feriados
├── requirements.txt          # Dependências Python
├── packages.txt              # Dependências do sistema (deploy)
├── custom_holidays.json      # Feriados personalizados (gerado)
├── internship_template.json  # Template do supervisor (gerado)
├── .streamlit/
│   └── config.toml          # Configurações do Streamlit
├── templates/               # Templates PDF
└── filled_docs/            # Documentos gerados
```

## 🔧 Configuração

### Templates

Coloque os templates PDF na pasta `templates/`:
- `1_checklist.pdf`
- `2_freq1.pdf` até `8_freq7.pdf`
- `9_realizacao_estagio.pdf`
- `10_declaracao_atividade_obrigatoria.pdf`

### Saída

Os documentos preenchidos são salvos em `filled_docs/`

## 📝 Uso Programático

Você também pode usar o sistema sem interface:

```python
from models import UserData, InternshipData, ShiftData, DocumentData
from docs_filler import DocFiller

# Criar dados
user = UserData(nome="João", ra="123", ...)
internship = InternshipData(disciplina_estagio="Est I", ...)
shifts = [ShiftData("08:00", "12:00", "01/10/2024", "Atividade")]

# Gerar documentos
document_data = DocumentData(user=user, internship=internship, shifts=shifts)
filler = DocFiller(document_data)
filler.fill_all_documents()
```

## 🧰 Utilitários opcionais

Há alguns scripts de inspeção (`inspect_docx_mergefields.py`) que usam `docx-mailmerge`. Essa biblioteca é opcional para a geração principal de documentos e, devido a limitações da versão publicada, não está no `requirements.txt`. Instale manualmente com:

```
pip install "docx-mailmerge<=0.5.0"
```

Esses scripts são úteis para investigar campos de mesclagem nos templates DOCX, mas não são necessários em tempo de execução da aplicação Streamlit.

## 🛠️ Tecnologias

- **Python 3.12+**
- **Streamlit** - Interface web
- **PyMuPDF (fitz)** - Manipulação de PDFs
- **holidays** - Detecção de feriados brasileiros
- **Dataclasses** - Estruturação de dados

## 🔒 Segurança

- Os arquivos `custom_holidays.json` e `internship_template.json` não são versionados (`.gitignore`)
- Cada deploy no Streamlit Cloud mantém seus próprios arquivos de configuração
- PDFs gerados são temporários e não ficam persistidos no servidor

## 📄 Licença

MIT License

# Sistema de Preenchimento de Documentos de Estágio

Sistema automatizado para preenchimento de documentos de estágio em PDF com interface web usando Streamlit.

## 📋 Funcionalidades

- ✅ Preenchimento automático de checklist
- ✅ Geração de folhas de frequência
- ✅ Declaração de realização de estágio
- ✅ Declaração de atividade obrigatória
- ✅ Interface web amigável
- ✅ Gerenciamento de feriados personalizados
- ✅ Seleção de dias da semana do estágio
- ✅ Detecção automática de feriados brasileiros
- ✅ Download em ZIP de todos os documentos

## 🚀 Como usar

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar feriados (Responsável pelo Estágio)

```bash
streamlit run manage_holidays.py
```

Acesse a interface administrativa para cadastrar feriados municipais, pontos facultativos e datas especiais que serão aplicados a todos os estagiários.

### 3. Executar a aplicação principal (Estagiários)

```bash
streamlit run app.py
```

### 4. Acessar no navegador

As aplicações abrirão automaticamente em `http://localhost:8501`

## 👥 Dois modos de uso

### 🔧 Modo Administrativo (`manage_holidays.py`)
- Para responsáveis pelo estágio
- Cadastro de feriados personalizados
- Visualização de feriados oficiais
- Feriados salvos em arquivo JSON compartilhado

### 📝 Modo Estagiário (`app.py`)
- Para estagiários gerarem documentos
- Visualização de feriados cadastrados (somente leitura)
- Seleção de dias da semana do estágio
- Geração automática de turnos por período
- Download de todos os documentos

## 📁 Estrutura do projeto

```
estagio_filler/
├── app.py                    # Aplicação principal (estagiários)
├── manage_holidays.py        # Gerenciamento de feriados (admin)
├── models.py                 # Modelos de dados
├── docs_filler.py            # Lógica de preenchimento
├── date_utils.py             # Utilitários de datas e feriados
├── requirements.txt          # Dependências
├── custom_holidays.json      # Feriados personalizados (gerado)
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

## 🛠️ Tecnologias

- **Python 3.8+**
- **Streamlit** - Interface web
- **PyMuPDF (fitz)** - Manipulação de PDFs
- **Dataclasses** - Estruturação de dados

## 📄 Licença

MIT License

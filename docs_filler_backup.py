import fitz  # PyMuPDF
import os
from dataclasses import dataclass, asdict
from typing import Dict, Tuple, Optional


@dataclass
class UserData:
    """Dados do usuário/estudante"""
    nome: str
    ra: str
    polo: str
    turma: str
    telefone_ddd: str
    telefone_numero: str
    email: str
    semestre: str
    data: str


@dataclass
class InternshipData:
    """Dados do estágio"""
    disciplina_estagio: str
    codigo_disciplina: str
    local_estagio: str
    supervisor_estagio: str
    carga_horaria: int
    titulo_atividade_obrigatoria: str


@dataclass
class ShiftData:
    """Dados de turno/atividade"""
    horario_inicio: str
    horario_fim: str
    data: str
    atividade_realizada: str


class PDFConfig:
    """Configurações de caminhos e templates"""
    TEMPLATE_PATH = "./templates/"
    OUTPUT_PATH = "./filled_docs/"
    DEFAULT_FONT_SIZE = 12
    
    @classmethod
    def get_template_file(cls, filename: str) -> str:
        return os.path.join(cls.TEMPLATE_PATH, filename)
    
    @classmethod
    def get_output_file(cls, filename: str) -> str:
        return os.path.join(cls.OUTPUT_PATH, filename)


class ChecklistPDFFiller:
    """Preenche o PDF de checklist"""
    
    FIELD_COORDS: Dict[str, Tuple[float, float]] = {
        "nome":             (94.6, 160.9),
        "ra":               (423.8, 160.9),
        "polo":             (89.7, 177.9),
        "turma":            (432.3, 177.9),
        "telefone_ddd":     (108.8, 195.9),
        "telefone_numero":  (130.4, 195.9),
        "email":            (99.7, 210.7),
        "semestre":         (482.3, 195.9),
        "data":             (105.8, 702.0),
    }
    
    def __init__(self, user_data: UserData, font_size: int = PDFConfig.DEFAULT_FONT_SIZE):
        self.user_data = user_data
        self.font_size = font_size
    
    def fill(self) -> str:
        """Preenche o PDF e retorna o caminho do arquivo gerado"""
        template_file = PDFConfig.get_template_file("1_checklist.pdf")
        output_file = PDFConfig.get_output_file(f"checklist_{self.user_data.ra}.pdf")
        
        doc = fitz.open(template_file)
        page = doc[0]
        
        print("Preenchendo checklist PDF...")
        
        # Converter dataclass para dicionário
        user_dict = asdict(self.user_data)
        
        # Preencher campos
        for field_name, coords in self.FIELD_COORDS.items():
            if field_name in user_dict:
                text = str(user_dict[field_name])
                print(f"Campo '{field_name}': {text}")
                x, y = coords
                page.insert_text((x, y), text, fontsize=self.font_size)
        
        # Campo fixo de carga horária
        page.insert_text((460.9, 603.3), "100 HORAS", fontsize=self.font_size)
        
        doc.save(output_file)
        doc.close()
        
        print(f"PDF salvo em: {output_file}")
        return output_file


class DocFiller:
    """Classe principal para gerenciar o preenchimento de documentos"""
    
    def __init__(self, user_data: UserData, internship_data: Optional[InternshipData] = None, shift_data: Optional[ShiftData] = None):
        self.user_data = user_data
        self.internship_data = internship_data
        self.shift_data = shift_data
    
    def fill_checklist(self) -> str:
        """Preenche o checklist PDF"""
        filler = ChecklistPDFFiller(self.user_data)
        return filler.fill()
    
    def fill_all_documents(self):
        """Preenche todos os documentos necessários"""
        # Por enquanto apenas o checklist
        self.fill_checklist()
        # Adicionar outros documentos conforme necessário


# Exemplo de uso
if __name__ == "__main__":
    sample_user_data = UserData(
        nome="João Silva",
        ra="123456789",
        polo="Polo Central",
        turma="Turma A",
        telefone_ddd="11",
        telefone_numero="987654321",
        email="joao.silva@example.com",
        semestre="2024.1",
        data="Brasília,          28      10    2025"
    )
    
    doc_filler = DocFiller(user_data=sample_user_data)
    doc_filler.fill_checklist()
"""
Sistema de preenchimento automático de documentos de estágio em PDF.
"""
import fitz  # PyMuPDF
import os
from dataclasses import asdict
from typing import Dict, Tuple, List
from abc import ABC, abstractmethod

from models import UserData, InternshipData, ShiftData, DocumentData


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
        os.makedirs(cls.OUTPUT_PATH, exist_ok=True)
        return os.path.join(cls.OUTPUT_PATH, filename)


class BasePDFFiller(ABC):
    """Classe base abstrata para todos os fillers de PDF"""
    
    def __init__(self, font_size: int = PDFConfig.DEFAULT_FONT_SIZE):
        self.font_size = font_size
    
    @abstractmethod
    def get_template_name(self) -> str:
        """Retorna o nome do arquivo template"""
        pass
    
    @abstractmethod
    def get_output_name(self, identifier: str) -> str:
        """Retorna o nome do arquivo de saída"""
        pass
    
    @abstractmethod
    def fill_page(self, page, doc) -> None:
        """Preenche a página do PDF com os dados"""
        pass
    
    def fill(self) -> str:
        """Preenche o PDF e retorna o caminho do arquivo gerado"""
        template_file = PDFConfig.get_template_file(self.get_template_name())
        output_file = PDFConfig.get_output_file(self.get_output_name(self._get_identifier()))
        
        doc = fitz.open(template_file)
        
        print(f"Preenchendo {self.__class__.__name__}...")
        self.fill_page(doc[0], doc)
        
        doc.save(output_file)
        doc.close()
        
        print(f"PDF salvo em: {output_file}")
        return output_file
    
    @abstractmethod
    def _get_identifier(self) -> str:
        """Retorna o identificador único para o arquivo (ex: RA do aluno)"""
        pass


class ChecklistPDFFiller(BasePDFFiller):
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
        super().__init__(font_size)
        self.user_data = user_data
    
    def get_template_name(self) -> str:
        return "1_checklist.pdf"
    
    def get_output_name(self, identifier: str) -> str:
        return f"checklist_{identifier}.pdf"
    
    def _get_identifier(self) -> str:
        return self.user_data.ra
    
    def fill_page(self, page, doc) -> None:
        """Preenche a página do checklist"""
        user_dict = asdict(self.user_data)
        
        # Preencher campos dinâmicos
        for field_name, coords in self.FIELD_COORDS.items():
            if field_name in user_dict:
                text = str(user_dict[field_name])
                print(f"  Campo '{field_name}': {text}")
                x, y = coords
                page.insert_text((x, y), text, fontsize=self.font_size)
        
        # Campo fixo de carga horária
        page.insert_text((460.9, 603.3), "100 HORAS", fontsize=self.font_size)


class FrequencySheetPDFFiller(BasePDFFiller):
    """Preenche PDFs de folha de frequência (freq1-freq7)"""
    
    def __init__(self, user_data: UserData, internship_data: InternshipData, 
                 shifts: List[ShiftData], sheet_number: int, 
                 font_size: int = PDFConfig.DEFAULT_FONT_SIZE):
        super().__init__(font_size)
        self.user_data = user_data
        self.internship_data = internship_data
        self.shifts = shifts
        self.sheet_number = sheet_number
    
    def get_template_name(self) -> str:
        return f"{self.sheet_number}_freq{self.sheet_number - 1}.pdf"
    
    def get_output_name(self, identifier: str) -> str:
        return f"freq{self.sheet_number - 1}_{identifier}.pdf"
    
    def _get_identifier(self) -> str:
        return self.user_data.ra
    
    def fill_page(self, page, doc) -> None:
        """Preenche a folha de frequência"""
        print(f"  Preenchendo frequência {self.sheet_number - 1}")
        
        # Coordenadas para nome e matrícula (RA)
        FIELD_COORDS = {
            'nome': (85, 155),      # Coordenadas do campo nome
            'matricula': (420, 155)  # Coordenadas do campo matrícula/RA
        }
        
        # Preenche nome
        page.insert_text(FIELD_COORDS['nome'], self.user_data.nome, 
                        fontsize=self.font_size)
        
        # Preenche matrícula (RA)
        page.insert_text(FIELD_COORDS['matricula'], self.user_data.ra, 
                        fontsize=self.font_size)


class InternshipDeclarationPDFFiller(BasePDFFiller):
    """Preenche o PDF de realização de estágio"""
    
    def __init__(self, user_data: UserData, internship_data: InternshipData,
                 font_size: int = PDFConfig.DEFAULT_FONT_SIZE):
        super().__init__(font_size)
        self.user_data = user_data
        self.internship_data = internship_data
    
    def get_template_name(self) -> str:
        return "9_realizacao_estagio.pdf"
    
    def get_output_name(self, identifier: str) -> str:
        return f"realizacao_estagio_{identifier}.pdf"
    
    def _get_identifier(self) -> str:
        return self.user_data.ra
    
    def fill_page(self, page, doc) -> None:
        """Preenche a declaração de realização de estágio"""
        print(f"  Preenchendo declaração de realização de estágio")
        
        # Coordenadas para nome e matrícula (RA)
        FIELD_COORDS = {
            'nome': (125, 237),      # Coordenadas do campo nome
            'matricula': (450, 237)  # Coordenadas do campo matrícula/RA
        }
        
        # Preenche nome
        page.insert_text(FIELD_COORDS['nome'], self.user_data.nome, 
                        fontsize=self.font_size)
        
        # Preenche matrícula (RA)
        page.insert_text(FIELD_COORDS['matricula'], self.user_data.ra, 
                        fontsize=self.font_size)


class MandatoryActivityPDFFiller(BasePDFFiller):
    """Preenche o PDF de declaração de atividade obrigatória"""
    
    def __init__(self, user_data: UserData, internship_data: InternshipData,
                 font_size: int = PDFConfig.DEFAULT_FONT_SIZE):
        super().__init__(font_size)
        self.user_data = user_data
        self.internship_data = internship_data
    
    def get_template_name(self) -> str:
        return "10_declaracao_atividade_obrigatoria.pdf"
    
    def get_output_name(self, identifier: str) -> str:
        return f"atividade_obrigatoria_{identifier}.pdf"
    
    def _get_identifier(self) -> str:
        return self.user_data.ra
    
    def fill_page(self, page, doc) -> None:
        """Preenche a declaração de atividade obrigatória"""
        print(f"  Preenchendo declaração de atividade obrigatória")
        
        # Coordenadas para nome e matrícula (RA)
        FIELD_COORDS = {
            'nome': (280, 235),      # Coordenadas do campo nome
            'matricula': (80, 265)  # Coordenadas do campo matrícula/RA
        }
        
        # Preenche nome
        page.insert_text(FIELD_COORDS['nome'], self.user_data.nome, 
                        fontsize=self.font_size)
        
        # Preenche matrícula (RA)
        page.insert_text(FIELD_COORDS['matricula'], self.user_data.ra, 
                        fontsize=self.font_size)


class DocFiller:
    """Classe principal para gerenciar o preenchimento de todos os documentos"""
    
    def __init__(self, document_data: DocumentData):
        self.data = document_data
    
    def fill_checklist(self) -> str:
        """Preenche o checklist PDF"""
        filler = ChecklistPDFFiller(self.data.user)
        return filler.fill()
    
    def fill_frequency_sheets(self) -> List[str]:
        """Preenche todas as folhas de frequência necessárias (máximo 3)"""
        output_files = []
        # Divide os turnos em grupos (assumindo ~10 turnos por folha)
        shifts_per_sheet = 6
        num_sheets = (len(self.data.shifts) + shifts_per_sheet - 1) // shifts_per_sheet
        
        # Limita a 3 folhas de frequência
        num_sheets = min(num_sheets, 3)
        
        for i in range(num_sheets):
            start_idx = i * shifts_per_sheet
            end_idx = min(start_idx + shifts_per_sheet, len(self.data.shifts))
            shifts_subset = self.data.shifts[start_idx:end_idx]
            
            filler = FrequencySheetPDFFiller(
                self.data.user,
                self.data.internship,
                shifts_subset,
                sheet_number=i + 2  # freq1 é template 2_freq1.pdf
            )
            output_files.append(filler.fill())
        
        return output_files
    
    def fill_internship_declaration(self) -> str:
        """Preenche a declaração de realização de estágio"""
        filler = InternshipDeclarationPDFFiller(self.data.user, self.data.internship)
        return filler.fill()
    
    def fill_mandatory_activity(self) -> str:
        """Preenche a declaração de atividade obrigatória"""
        filler = MandatoryActivityPDFFiller(self.data.user, self.data.internship)
        return filler.fill()
    
    def fill_all_documents(self) -> Dict[str, List[str]]:
        """Preenche todos os documentos necessários"""
        print("\n" + "="*60)
        print("INICIANDO PREENCHIMENTO DE TODOS OS DOCUMENTOS")
        print("="*60 + "\n")
        
        results = {
            "checklist": [self.fill_checklist()],
            "frequency_sheets": self.fill_frequency_sheets(),
            "internship_declaration": [self.fill_internship_declaration()],
            "mandatory_activity": [self.fill_mandatory_activity()]
        }
        
        print("\n" + "="*60)
        print("TODOS OS DOCUMENTOS FORAM PREENCHIDOS COM SUCESSO!")
        print("="*60 + "\n")
        
        return results


# Exemplo de uso
if __name__ == "__main__":
    # Dados do usuário
    sample_user_data = UserData(
        nome="João Silva",
        ra="123456789",
        polo="Polo Central",
        turma="Turma A",
        telefone_ddd="11",
        telefone_numero="987654321",
        email="joao.silva@example.com",
        semestre="2024.1",
        data="Brasília, 28 de outubro de 2025"
    )
    
    # Dados do estágio
    sample_internship_data = InternshipData(
        disciplina_estagio="Estágio Supervisionado I",
        codigo_disciplina="EST001",
        local_estagio="Hospital Central",
        supervisor_estagio="Dr. Maria Santos",
        carga_horaria=100,
        titulo_atividade_obrigatoria="Atividades de Assistência Farmacêutica"
    )
    
    # Dados de turnos (exemplo com alguns turnos)
    sample_shifts = [
        ShiftData("08:00", "12:00", "01/10/2024", "Dispensação de medicamentos"),
        ShiftData("14:00", "18:00", "02/10/2024", "Controle de estoque"),
        ShiftData("08:00", "12:00", "03/10/2024", "Atendimento ao público"),
    ]
    
    # Criar documento completo
    document_data = DocumentData(
        user=sample_user_data,
        internship=sample_internship_data,
        shifts=sample_shifts
    )
    
    # Preencher apenas o checklist (exemplo)
    doc_filler = DocFiller(document_data)
    doc_filler.fill_checklist()
    
    # Ou preencher todos os documentos
    # doc_filler.fill_all_documents()
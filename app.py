"""
Aplicação Streamlit para preenchimento automático de documentos de estágio.
"""
import streamlit as st
from datetime import date, time
from typing import List, Tuple
import os
import json
import fitz  # PyMuPDF

from models import UserData, InternshipData, ShiftData, DocumentData, ActivityStorage
from docs_filler import DocFiller
from mid_internship_fillers import CompanyActivitiesDocxFiller, SupervisionReportDocxFiller
import datetime
import zipfile
from date_utils import (
    generate_date_range, is_brazilian_holiday, get_holiday_name, 
    get_weekday_name, get_custom_holidays
)


TEMPLATE_CONFIG_FILE = "./internship_template.json"


def load_template_config() -> dict:
    """Carrega a configuração do template de estágio"""
    if os.path.exists(TEMPLATE_CONFIG_FILE):
        try:
            with open(TEMPLATE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def generate_mid_internship_documents(document_data: DocumentData, ra: str) -> Tuple[str, bool]:
    """Gera os documentos intermediários e retorna o caminho do ZIP e se faltou conversão para PDF"""
    fillers = (
        CompanyActivitiesDocxFiller,
        SupervisionReportDocxFiller,
    )
    generated_paths: list[str] = []
    for filler_cls in fillers:
        filler = filler_cls(document_data)
        generated_paths.append(filler.fill())

    mid_zip = f"./filled_docs/mid_documents_{ra}.zip"
    os.makedirs(os.path.dirname(mid_zip), exist_ok=True)
    with zipfile.ZipFile(mid_zip, "w") as zf:
        for path in generated_paths:
            if path and os.path.exists(path):
                zf.write(path, os.path.basename(path))

    missing_pdf = all(p.lower().endswith('.docx') for p in generated_paths if p)
    return mid_zip, missing_pdf


def init_session_state():
    """Inicializa o estado da sessão"""
    if 'shifts' not in st.session_state:
        st.session_state.shifts = []
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'custom_holidays_initialized' not in st.session_state:
        st.session_state.custom_holidays_initialized = False
    if 'activity_descriptions' not in st.session_state:
        st.session_state.activity_descriptions = {}


def add_shift(shift: ShiftData):
    """Adiciona um turno à lista"""
    st.session_state.shifts.append(shift)


def remove_shift(index: int):
    """Remove um turno da lista"""
    st.session_state.shifts.pop(index)


def merge_pdfs_to_single_file(files: dict, ra: str) -> str:
    """Mescla todos os PDFs gerados em um único arquivo"""
    output_path = f"./filled_docs/documentos_estagio_{ra}.pdf"
    
    # Criar documento PDF final
    merged_pdf = fitz.open()
    
    # Ordem desejada dos documentos
    order = ["checklist", "frequency_sheets", "internship_declaration", "mandatory_activity"]
    
    for category in order:
        if category in files:
            for file_path in files[category]:
                if os.path.exists(file_path):
                    # Abrir e adicionar cada PDF
                    pdf_document = fitz.open(file_path)
                    merged_pdf.insert_pdf(pdf_document)
                    pdf_document.close()
    
    # Salvar PDF mesclado
    merged_pdf.save(output_path)
    merged_pdf.close()
    
    return output_path


def render_user_data_form():
    """Renderiza o formulário de dados do usuário"""
    st.header("📋 Dados do Estudante")
    
    col1, col2 = st.columns(2)
    
    with col1:
        nome = st.text_input("Nome completo*", placeholder="João Silva")
        ra = st.text_input("RA*", placeholder="123456789")
        polo = st.text_input("Polo*", placeholder="Polo Central")
        turma = st.text_input("Turma*", placeholder="Turma A")
    
    with col2:
        telefone_ddd = st.text_input("DDD*", placeholder="11", max_chars=2)
        telefone_numero = st.text_input("Telefone*", placeholder="987654321", max_chars=9)
        email = st.text_input("E-mail*", placeholder="joao.silva@aluno.unip.br")
        semestre = st.text_input("Semestre*", placeholder="2025/2")
    
    data_assinatura = st.text_input(
        "Data de assinatura*",
        value="Brasília, 12 de Junho de 2026",
        help="Formato livre, ex: 'Brasília, 12 de Junho de 2026'"
    )
    
    return {
        "nome": nome,
        "ra": ra,
        "polo": polo,
        "turma": turma,
        "telefone_ddd": telefone_ddd,
        "telefone_numero": telefone_numero,
        "email": email,
        "semestre": semestre,
        "data": data_assinatura
    }


def render_internship_data_form():
    """Renderiza o formulário de dados do estágio"""
    st.header("🏥 Dados do Estágio")
    
    col1, col2 = st.columns(2)
    
    with col1:
        disciplina_estagio = st.text_input(
            "Disciplina de Estágio*",
            value="Alimentos"
        )
        codigo_disciplina = st.text_input(
            "Código da Disciplina*",
            value="7433-100"
        )
        local_estagio = st.text_input(
            "Local do Estágio*",
            value="UNIP"
        )
    
    with col2:
        supervisor_estagio = st.text_input(
            "Supervisor do Estágio*",
            value="Breno Silva de Abreu"
        )
        carga_horaria = st.number_input(
            "Carga Horária Total*",
            min_value=1,
            value=100,
            step=10
        )
        titulo_atividade = st.text_input(
            "Título da Atividade Obrigatória*",
            value="Análise de Rotulagem"
        )
    
    return {
        "disciplina_estagio": disciplina_estagio,
        "codigo_disciplina": codigo_disciplina,
        "local_estagio": local_estagio,
        "supervisor_estagio": supervisor_estagio,
        "carga_horaria": int(carga_horaria),
        "titulo_atividade_obrigatoria": titulo_atividade
    }


def render_shifts_form():
    """Renderiza o formulário de turnos/atividades"""
    st.header("⏰ Turnos e Atividades")
    
    # Mostrar feriados personalizados cadastrados (somente leitura)
    custom_holidays = get_custom_holidays()
    if custom_holidays:
        with st.expander(f"🎉 Feriados Cadastrados pelo Responsável ({len(custom_holidays)})", expanded=False):
            st.info("ℹ️ Estes feriados foram configurados pelo responsável do estágio e serão aplicados automaticamente.")
            
            sorted_holidays = sorted(custom_holidays.items(), key=lambda x: x[0])
            
            cols = st.columns(3)
            for idx, (holiday_date, holiday_name) in enumerate(sorted_holidays):
                with cols[idx % 3]:
                    st.write(f"📅 **{holiday_date.strftime('%d/%m/%Y')}**")
                    st.caption(holiday_name)
    
    st.markdown("---")
    
    # Tabs para escolher modo de entrada
    tab1, tab2 = st.tabs(["📅 Range de Datas", "➕ Turno Individual"])
    
    # Tab 1: Range de datas
    with tab1:
        st.write("Adicione múltiplos turnos selecionando um período:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Data Inicial",
                value=date.today(),
                key="range_start",
                format="DD/MM/YYYY"
            )
            horario_inicio_range = st.time_input(
                "Horário de Início",
                value=time(8, 0),
                key="range_time_start"
            )
        
        with col2:
            end_date = st.date_input(
                "Data Final",
                value=date.today(),
                key="range_end",
                format="DD/MM/YYYY"
            )
            horario_fim_range = st.time_input(
                "Horário de Fim",
                value=time(12, 0),
                key="range_time_end"
            )
        
        # Seleção de dias da semana
        st.write("**Dias da semana do estágio:**")
        
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        
        weekday_selection = {}
        with col1:
            weekday_selection[0] = st.checkbox("Seg", value=True, key="wd_mon")
        with col2:
            weekday_selection[1] = st.checkbox("Ter", value=True, key="wd_tue")
        with col3:
            weekday_selection[2] = st.checkbox("Qua", value=True, key="wd_wed")
        with col4:
            weekday_selection[3] = st.checkbox("Qui", value=True, key="wd_thu")
        with col5:
            weekday_selection[4] = st.checkbox("Sex", value=True, key="wd_fri")
        with col6:
            weekday_selection[5] = st.checkbox("Sáb", value=False, key="wd_sat")
        with col7:
            weekday_selection[6] = st.checkbox("Dom", value=False, key="wd_sun")
        
        selected_weekdays = [day for day, selected in weekday_selection.items() if selected]
        
        if not selected_weekdays:
            st.warning("⚠️ Selecione pelo menos um dia da semana")
        
        st.write("")
        
        atividade_range = st.text_area(
            "Atividade Padrão",
            placeholder="Atividade que será aplicada a todos os dias (exceto feriados)...",
            height=100,
            key="range_activity"
        )
        
        # Opção adicional
        auto_detect_holidays = st.checkbox("Detectar feriados automaticamente", value=True)
        
        if st.button("📅 Adicionar Turnos do Período", use_container_width=True, type="primary", disabled=not selected_weekdays):
            if start_date > end_date:
                st.error("❌ Data inicial deve ser anterior à data final!")
            elif not atividade_range.strip():
                st.error("❌ Por favor, descreva a atividade padrão.")
            else:
                try:
                    # Gerar lista de datas
                    date_list = generate_date_range(start_date, end_date)
                    added_count = 0
                    skipped_days = 0
                    holidays_count = 0
                    
                    for current_date in date_list:
                        # Filtrar por dias da semana selecionados
                        if current_date.weekday() not in selected_weekdays:
                            skipped_days += 1
                            continue
                        
                        # Verificar feriado
                        atividade_dia = atividade_range
                        if auto_detect_holidays and is_brazilian_holiday(current_date):
                            atividade_dia = "FERIADO"
                            holidays_count += 1
                        
                        # Adicionar turno
                        shift = ShiftData(
                            horario_inicio=horario_inicio_range.strftime("%H:%M"),
                            horario_fim=horario_fim_range.strftime("%H:%M"),
                            data=current_date.strftime("%d/%m/%Y"),
                            atividade_realizada=atividade_dia
                        )
                        add_shift(shift)
                        added_count += 1
                    
                    # Mensagem de sucesso
                    success_msg = f"✅ {added_count} turno(s) adicionado(s) com sucesso!"
                    if skipped_days > 0:
                        success_msg += f" ({skipped_days} dia(s) não selecionado(s) ignorado(s))"
                    if holidays_count > 0:
                        success_msg += f" ({holidays_count} feriado(s) detectado(s))"
                    
                    st.success(success_msg)
                    st.rerun()
                    
                except ValueError as e:
                    st.error(f"❌ Erro: {str(e)}")
    
    # Tab 2: Turno individual
    with tab2:
        st.write("Adicione um turno específico:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            horario_inicio = st.time_input("Horário de Início", value=time(8, 0), key="single_time_start")
            horario_fim = st.time_input("Horário de Fim", value=time(12, 0), key="single_time_end")
        
        with col2:
            data_turno = st.date_input("Data", value=date.today(), key="single_date", format="DD/MM/YYYY")
            
            # Verificar se é feriado
            if is_brazilian_holiday(data_turno):
                holiday_name = get_holiday_name(data_turno)
                st.warning(f"⚠️ Esta data é feriado: **{holiday_name}**")
        
        atividade = st.text_area(
            "Atividade Realizada",
            placeholder="Descreva as atividades realizadas neste turno...",
            height=100,
            key="single_activity"
        )
        
        # Botão para preencher automaticamente "FERIADO"
        col1, col2 = st.columns([1, 1])
        with col1:
            if is_brazilian_holiday(data_turno):
                if st.button("🎉 Marcar como Feriado", use_container_width=True):
                    st.session_state.single_activity_override = "FERIADO"
                    st.rerun()
        
        with col2:
            if st.button("➕ Adicionar Turno", use_container_width=True):
                atividade_final = st.session_state.get('single_activity_override', atividade)
                
                if atividade_final.strip():
                    shift = ShiftData(
                        horario_inicio=horario_inicio.strftime("%H:%M"),
                        horario_fim=horario_fim.strftime("%H:%M"),
                        data=data_turno.strftime("%d/%m/%Y"),
                        atividade_realizada=atividade_final
                    )
                    add_shift(shift)
                    st.session_state.pop('single_activity_override', None)
                    st.success("✅ Turno adicionado com sucesso!")
                    st.rerun()
                else:
                    st.error("Por favor, descreva a atividade realizada.")
    st.markdown("---")
    
    # Mostrar turnos adicionados
    if st.session_state.shifts:
        st.subheader(f"📋 Turnos Cadastrados ({len(st.session_state.shifts)})")
        
        # Opção de ordenar
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            sort_option = st.selectbox(
                "Ordenar por:",
                ["Data (crescente)", "Data (decrescente)", "Ordem de adição"],
                key="sort_option"
            )
        with col3:
            if st.button("🗑️ Limpar Todos", type="secondary"):
                st.session_state.shifts = []
                st.rerun()
        
        # Ordenar turnos
        display_shifts = st.session_state.shifts.copy()
        if sort_option == "Data (crescente)":
            display_shifts.sort(key=lambda x: tuple(reversed(x.data.split('/'))))
        elif sort_option == "Data (decrescente)":
            display_shifts.sort(key=lambda x: tuple(reversed(x.data.split('/'))), reverse=True)
        
        # Mostrar turnos
        for idx, shift in enumerate(display_shifts):
            original_idx = st.session_state.shifts.index(shift)
            
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    # Destacar feriados
                    if shift.atividade_realizada == "FERIADO":
                        st.write(f"🎉 **{shift.data}** | {shift.horario_inicio} - {shift.horario_fim}")
                        st.caption("⚠️ FERIADO")
                    else:
                        st.write(f"**{shift.data}** | {shift.horario_inicio} - {shift.horario_fim}")
                        st.caption(shift.atividade_realizada)
                
                with col2:
                    horas = (
                        int(shift.horario_fim.split(':')[0]) - 
                        int(shift.horario_inicio.split(':')[0])
                    )
                    st.metric("Horas", f"{horas}h")
                
                with col3:
                    if st.button("🗑️", key=f"remove_{original_idx}", help="Remover turno"):
                        remove_shift(original_idx)
                        st.rerun()
                
                st.divider()
        
        # Estatísticas
        total_horas = sum([
            int(shift.horario_fim.split(':')[0]) - int(shift.horario_inicio.split(':')[0])
            for shift in st.session_state.shifts
        ])
        feriados_count = sum([1 for shift in st.session_state.shifts if shift.atividade_realizada == "FERIADO"])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Horas", f"{total_horas}h")
        with col2:
            st.metric("Total de Turnos", len(st.session_state.shifts))
        with col3:
            st.metric("Feriados", feriados_count)
    else:
        st.warning("⚠️ Nenhum turno cadastrado ainda. Adicione pelo menos um turno para continuar.")


def render_activity_descriptions_form(internship_data: dict):
    """Renderiza o formulário para descrições detalhadas de atividades"""
    st.header("📝 Descrições de Atividades por Encontro")
    
    if not st.session_state.shifts:
        st.info("ℹ️ Adicione turnos primeiro para poder descrever as atividades de cada encontro.")
        return
    
    # Agrupar turnos por data (excluindo feriados)
    unique_dates = sorted(set([
        shift.data for shift in st.session_state.shifts 
        if shift.atividade_realizada != "FERIADO"
    ]), key=lambda x: tuple(reversed(x.split('/'))))
    
    if not unique_dates:
        st.info("ℹ️ Todos os turnos cadastrados são feriados. Não é necessário adicionar descrições.")
        return
    
    st.write("Adicione descrições detalhadas para cada dia de atividade:")
    
    # Calcular horas e mostrar previsão
    total_shift_hours = sum([shift.get_hours() for shift in st.session_state.shifts])
    carga_horaria = internship_data.get("carga_horaria", 100)
    missing_hours = max(0, carga_horaria - total_shift_hours)
    
    with st.expander("📊 Resumo de Carga Horária", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Carga Horária Total", f"{carga_horaria}h")
        
        with col2:
            st.metric("Horas de Turnos", f"{total_shift_hours:.1f}h")
        
        with col3:
            if missing_hours > 0:
                st.metric("Horas Faltantes", f"{missing_hours:.1f}h", delta=f"-{missing_hours:.1f}h")
            else:
                st.metric("Status", "✅ Completo", delta="0h")
        
        with col4:
            complementary_hours = 0
            if missing_hours > 0:
                atividade_obrigatoria_hours = min(20, missing_hours)
                remaining = missing_hours - atividade_obrigatoria_hours
                complementary_hours = atividade_obrigatoria_hours + remaining
                st.metric("Horas Complementares", f"{complementary_hours:.1f}h")
            else:
                st.metric("Horas Complementares", "0h")
        
        # Explicação
        if missing_hours > 0:
            st.info(
                f"⚙️ **Cálculo Automático:** Faltam {missing_hours:.1f}h para completar a carga horária. "
                f"Serão adicionadas automaticamente:\n"
                f"- **{min(20, missing_hours):.1f}h** de '{internship_data.get('titulo_atividade_obrigatoria', 'Atividade Obrigatória')}'\n" +
                (f"- **{max(0, missing_hours - 20):.1f}h** de 'Preenchimento de Documentos'" if missing_hours > 20 else "")
            )
    
    st.write("---")
    
    # Tabs ou accordion para cada data
    for date_str in unique_dates:
        with st.expander(f"📅 {date_str}", expanded=False):
            # Mostrar turnos deste dia
            day_shifts = [s for s in st.session_state.shifts if s.data == date_str]
            
            st.write("**Turnos neste dia:**")
            for shift in day_shifts:
                st.caption(f"⏰ {shift.horario_inicio} - {shift.horario_fim} | {shift.atividade_realizada}")
            
            st.write("")
            
            # Campo de descrição
            current_description = st.session_state.activity_descriptions.get(date_str, "")
            
            description = st.text_area(
                "Descrição detalhada das atividades realizadas:",
                value=current_description,
                height=150,
                key=f"activity_desc_{date_str}",
                placeholder="Descreva em detalhes as atividades, aprendizados e experiências deste encontro..."
            )
            
            if st.button("💾 Salvar Descrição", key=f"save_desc_{date_str}"):
                if description and description.strip():
                    st.session_state.activity_descriptions[date_str] = description.strip()
                    st.success(f"✅ Descrição salva para {date_str}")
                    st.rerun()
                else:
                    # Remover se vazio
                    if date_str in st.session_state.activity_descriptions:
                        del st.session_state.activity_descriptions[date_str]
                        st.info("Descrição removida")
                        st.rerun()
    
    # Resumo de descrições
    st.write("---")
    descriptions_count = len(st.session_state.activity_descriptions)
    total_dates = len(unique_dates)
    
    if descriptions_count == 0:
        st.warning(f"⚠️ Nenhuma descrição detalhada adicionada ainda. ({total_dates} data(s) disponível(is))")
    elif descriptions_count < total_dates:
        st.warning(f"⚠️ {descriptions_count}/{total_dates} datas com descrição. Considere adicionar descrições para todas as datas.")
    else:
        st.success(f"✅ Todas as {total_dates} datas possuem descrição!")


def validate_form_data(user_data: dict, internship_data: dict) -> tuple[bool, List[str]]:
    """Valida os dados do formulário"""
    errors = []
    
    # Validar dados do usuário
    required_user_fields = ["nome", "ra", "polo", "turma", "telefone_ddd", "telefone_numero", "email", "semestre", "data"]
    for field in required_user_fields:
        if not user_data.get(field, "").strip():
            errors.append(f"Campo '{field}' é obrigatório")
    
    # Validar dados do estágio
    required_internship_fields = ["disciplina_estagio", "codigo_disciplina", "local_estagio", "supervisor_estagio", "titulo_atividade_obrigatoria"]
    for field in required_internship_fields:
        if not internship_data.get(field, "").strip():
            errors.append(f"Campo '{field}' é obrigatório")
    
    # Validar turnos (devem ter sido carregados do template)
    if not st.session_state.shifts:
        errors.append("Nenhum turno encontrado. Certifique-se de que o supervisor configurou o template.")
    
    return len(errors) == 0, errors


def main():
    """Função principal da aplicação"""
    st.set_page_config(
        page_title="Preenchedor de Documentos de Estágio",
        page_icon="📄",
        layout="wide"
    )
    
    init_session_state()
    
    # Cabeçalho
    st.title("📄 Sistema de Preenchimento de Documentos de Estágio")
    st.markdown("---")
    
    # Carregar template do supervisor silenciosamente
    template_config = load_template_config()
    
    if template_config:
        # Auto-carregar template se ainda não foi carregado
        if not st.session_state.shifts:
            # Gerar turnos baseado no template
            all_dates = generate_date_range(
                date.fromisoformat(template_config['start_date']),
                date.fromisoformat(template_config['end_date'])
            )
            
            filtered_dates = [
                d for d in all_dates 
                if d.weekday() in template_config['weekdays'] and not is_brazilian_holiday(d)
            ]
            
            # Adicionar turnos automaticamente
            for date_obj in filtered_dates:
                date_str = date_obj.strftime("%d/%m/%Y")
                
                # Pegar descrição do template ou usar "FERIADO" se for feriado
                if is_brazilian_holiday(date_obj):
                    activity = "FERIADO"
                else:
                    activity = template_config.get('activity_descriptions', {}).get(
                        date_str,
                        template_config.get('default_activity', 'Atividade de estágio')
                    )
                
                shift = ShiftData(
                    horario_inicio=template_config['start_time'],
                    horario_fim=template_config['end_time'],
                    data=date_str,
                    atividade_realizada=activity
                )
                st.session_state.shifts.append(shift)
                
                # Adicionar descrição detalhada se existir
                if date_str in template_config.get('activity_descriptions', {}):
                    st.session_state.activity_descriptions[date_str] = template_config['activity_descriptions'][date_str]
        
        # Mostrar apenas informação resumida
        st.info(f"✅ Template de estágio carregado: {len(st.session_state.shifts)} encontros configurados pelo supervisor.")
    else:
        st.warning("⚠️ Nenhum template configurado pelo supervisor. Entre em contato com seu supervisor.")
    
    st.markdown("---")
    
    # Formulários
    user_data = render_user_data_form()
    st.markdown("---")
    
    internship_data = render_internship_data_form()
    
    # Auto-preencher data do documento se existir no template
    template_config = load_template_config()
    if template_config and 'document_date' in template_config:
        if not user_data.get('data'):
            user_data['data'] = template_config['document_date']
    
    st.markdown("---")
    
    # Mostrar resumo dos turnos (somente visualização)
    if st.session_state.shifts:
        st.header("📋 Turnos Cadastrados pelo Supervisor")
        
        with st.expander("Ver Detalhes dos Turnos", expanded=False):
            # Ordenar turnos por data
            display_shifts = sorted(
                st.session_state.shifts, 
                key=lambda x: tuple(reversed(x.data.split('/')))
            )
            
            for shift in display_shifts:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if shift.atividade_realizada == "FERIADO":
                        st.write(f"🎉 **{shift.data}** | {shift.horario_inicio} - {shift.horario_fim}")
                        st.caption("⚠️ FERIADO")
                    else:
                        st.write(f"**{shift.data}** | {shift.horario_inicio} - {shift.horario_fim}")
                        st.caption(shift.atividade_realizada)
                
                with col2:
                    horas = shift.get_hours()
                    st.metric("Horas", f"{horas:.1f}h")
                
                st.divider()
            
            # Estatísticas
            total_horas = sum([shift.get_hours() for shift in st.session_state.shifts])
            feriados_count = sum([1 for shift in st.session_state.shifts if shift.atividade_realizada == "FERIADO"])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Horas", f"{total_horas:.1f}h")
            with col2:
                st.metric("Total de Turnos", len(st.session_state.shifts))
            with col3:
                st.metric("Feriados", feriados_count)
    
    st.markdown("---")
    
    # Mostrar resumo de carga horária
    if st.session_state.shifts and internship_data.get('carga_horaria'):
        st.header("📊 Resumo de Carga Horária")
        
        total_shift_hours = sum([shift.get_hours() for shift in st.session_state.shifts])
        carga_horaria = internship_data.get("carga_horaria", 100)
        missing_hours = max(0, carga_horaria - total_shift_hours)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Carga Horária Total", f"{carga_horaria}h")
        
        with col2:
            st.metric("Horas de Turnos", f"{total_shift_hours:.1f}h")
        
        with col3:
            if missing_hours > 0:
                st.metric("Horas Faltantes", f"{missing_hours:.1f}h", delta=f"-{missing_hours:.1f}h")
            else:
                st.metric("Status", "✅ Completo", delta="0h")
        
        with col4:
            if missing_hours > 0:
                atividade_obrigatoria_hours = min(20, missing_hours)
                remaining = missing_hours - atividade_obrigatoria_hours
                complementary_hours = atividade_obrigatoria_hours + remaining
                st.metric("Horas Complementares", f"{complementary_hours:.1f}h")
            else:
                st.metric("Horas Complementares", "0h")
        
        # Explicação
        if missing_hours > 0:
            st.info(
                f"⚙️ **Cálculo Automático:** Faltam {missing_hours:.1f}h para completar a carga horária. "
                f"Serão adicionadas automaticamente:\n"
                f"- **{min(20, missing_hours):.1f}h** de '{internship_data.get('titulo_atividade_obrigatoria', 'Atividade Obrigatória')}'\n" +
                (f"- **{max(0, missing_hours - 20):.1f}h** de 'Preenchimento de Documentos'" if missing_hours > 20 else "")
            )
    
    st.markdown("---")

    # Preparar dados para geração de documentos
    user = UserData(**user_data)
    internship = InternshipData(**internship_data)
    activity_storage_list = [
        ActivityStorage(encounter_date=date_str, description=desc)
        for date_str, desc in st.session_state.activity_descriptions.items()
    ]
    document_data = DocumentData(
        user=user,
        internship=internship,
        shifts=st.session_state.shifts,
        activity_descriptions=activity_storage_list
    )

    # Seção de Documentos Intermediários
    st.subheader("📝 Documentos Intermediários")
    if st.button("✅ Gerar Documentos Intermediários", type="secondary", use_container_width=True):
        try:
            mid_zip, missing_pdf = generate_mid_internship_documents(document_data, user_data['ra'])
            if missing_pdf:
                st.warning(
                    "⚠️ Nenhuma conversão para PDF detectada. "
                    "Instale o LibreOffice (soffice) para gerar arquivos PDF automaticamente."
                )
            st.success("✅ Documentos Intermediários gerados com sucesso!")
            with open(mid_zip, "rb") as fmid:
                st.download_button(
                    "⬇️ Baixar Documentos Intermediários",
                    data=fmid,
                    file_name=os.path.basename(mid_zip),
                    mime="application/zip",
                    use_container_width=True
                )
        except FileNotFoundError:
            st.error("⚠️ Arquivos intermediários não configurados. Peça ao supervisor para carregar os templates no sistema.")
        except Exception as e:
            st.error(f"❌ Erro ao gerar documentos intermediários: {str(e)}")

    # Botão de gerar documentos finais
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Somente habilita após junho para evitar confusão
        final_enabled = datetime.date.today().month >= 6
        btn_label = "🚀 Gerar Todos os Documentos"
        if not final_enabled:
            btn_label = "🚀 Gerar Todos os Documentos (disponível a partir de Junho)"
        if st.button(btn_label, type="primary", use_container_width=True, disabled=not final_enabled):
            if not final_enabled:
                st.warning("Documentos finais estarão disponíveis a partir de Junho.")
            else:
                # Validar dados
                is_valid, errors = validate_form_data(user_data, internship_data)
            
            if not is_valid:
                st.error("❌ Erro na validação dos dados:")
                for error in errors:
                    st.error(f"• {error}")
            else:
                with st.spinner("Gerando documentos..."):
                    try:
                        # Criar objetos de dados
                        user = UserData(**user_data)
                        internship = InternshipData(**internship_data)
                        
                        # Criar ActivityStorage objects
                        activity_storage_list = [
                            ActivityStorage(encounter_date=date_str, description=desc)
                            for date_str, desc in st.session_state.activity_descriptions.items()
                        ]
                        
                        # Criar DocumentData (calculará atividades complementares automaticamente)
                        document_data = DocumentData(
                            user=user,
                            internship=internship,
                            shifts=st.session_state.shifts,
                            activity_descriptions=activity_storage_list
                        )
                        
                        # Mostrar resumo de cálculo
                        with st.expander("📊 Resumo de Carga Horária", expanded=True):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Horas de Turnos", f"{document_data.get_total_shift_hours():.1f}h")
                            
                            with col2:
                                st.metric("Horas Complementares", f"{document_data.get_total_complementary_hours():.1f}h")
                            
                            with col3:
                                st.metric("Total", f"{document_data.get_total_hours():.1f}h / {internship.carga_horaria}h")
                            
                            if document_data.complementary_activities:
                                st.write("**Atividades Complementares Adicionadas:**")
                                for act in document_data.complementary_activities:
                                    st.write(f"• {act.titulo}: {act.horas:.1f}h")
                        
                        # Gerar documentos
                        doc_filler = DocFiller(document_data)
                        results = doc_filler.fill_all_documents()
                        
                        # Mesclar todos os PDFs em um único arquivo
                        merged_pdf_path = merge_pdfs_to_single_file(results, user_data['ra'])
                        
                        # Sucesso
                        st.success("✅ Documentos gerados com sucesso!")
                        try:
                            mid_zip, missing_pdf = generate_mid_internship_documents(document_data, user_data['ra'])
                        except FileNotFoundError:
                            st.warning("⚠️ Templates dos relatórios intermediários não estão disponíveis. Peça ao supervisor para configurar os templates.")
                        except Exception as e:
                            st.error(f"⚠️ Falha ao gerar os documentos intermediários automaticamente: {str(e)}")
                        else:
                            st.success("✅ Documentos Intermediários gerados automaticamente!")
                            with open(mid_zip, "rb") as fmid:
                                st.download_button(
                                    "⬇️ Baixar Documentos Intermediários",
                                    data=fmid,
                                    file_name=os.path.basename(mid_zip),
                                    mime="application/zip",
                                    use_container_width=True
                                )
                            if missing_pdf:
                                st.warning(
                                    "⚠️ Nenhuma conversão para PDF detectada. "
                                    "Instale o LibreOffice (soffice) para gerar arquivos PDF automaticamente."
                                )
                        
                        # Exibir resumo
                        with st.expander("📄 Ver detalhes dos arquivos gerados"):
                            for category, files in results.items():
                                st.write(f"**{category}:** {len(files)} arquivo(s)")
                                for file in files:
                                    st.write(f"  • {os.path.basename(file)}")
                        
                        # Botão de download do PDF mesclado
                        with open(merged_pdf_path, "rb") as f:
                            st.download_button(
                                label="⬇️ Baixar todos os documentos (PDF único)",
                                data=f,
                                file_name=f"documentos_estagio_{user_data['ra']}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar documentos: {str(e)}")
                        st.exception(e)
                        st.exception(e)
    
    # Rodapé
    st.markdown("---")
    st.caption("💡 Preencha todos os campos obrigatórios (*) antes de gerar os documentos.")


if __name__ == "__main__":
    main()

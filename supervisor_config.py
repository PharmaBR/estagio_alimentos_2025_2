"""
Aplicação para supervisores configurarem o template de estágio.
"""
import streamlit as st
from datetime import date, time
import json
import os
from typing import Dict, List
from date_utils import generate_date_range, is_brazilian_holiday


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


def save_template_config(config: dict):
    """Salva a configuração do template de estágio"""
    with open(TEMPLATE_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def main():
    """Função principal da aplicação do supervisor"""
    st.set_page_config(
        page_title="Configuração de Estágio - Supervisor",
        page_icon="👨‍🏫",
        layout="wide"
    )
    
    st.title("👨‍🏫 Configuração de Template de Estágio - Supervisor")
    st.markdown("---")
    
    st.info("👤 **Área do Supervisor:** Configure o template padrão de estágio que será aplicado para todos os estagiários.")
    
    # Carregar configuração existente
    current_config = load_template_config()
    
    # Seção 1: Configurações de Período e Horários
    st.header("📅 Período e Horários do Estágio")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Período")
        
        default_start = date.fromisoformat(current_config.get("start_date", date.today().isoformat()))
        default_end = date.fromisoformat(current_config.get("end_date", date.today().isoformat()))
        
        start_date_config = st.date_input(
            "Data de Início do Estágio",
            value=default_start,
            format="DD/MM/YYYY"
        )
        
        end_date_config = st.date_input(
            "Data de Término do Estágio",
            value=default_end,
            format="DD/MM/YYYY"
        )
        
        document_date = st.text_input(
            "Data do Documento",
            value=current_config.get("document_date", "Brasília, 28 de outubro de 2025"),
            placeholder="Ex: Brasília, 28 de outubro de 2025"
        )
    
    with col2:
        st.subheader("Horários")
        
        default_start_time = current_config.get("start_time", "08:00")
        default_end_time = current_config.get("end_time", "12:00")
        
        h_start, m_start = map(int, default_start_time.split(':'))
        h_end, m_end = map(int, default_end_time.split(':'))
        
        start_time_config = st.time_input(
            "Horário de Início",
            value=time(h_start, m_start)
        )
        
        end_time_config = st.time_input(
            "Horário de Término",
            value=time(h_end, m_end)
        )
    
    # Seção 2: Dias da Semana
    st.markdown("---")
    st.header("📆 Dias da Semana do Estágio")
    
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    
    default_weekdays = current_config.get("weekdays", [0, 1, 2, 3, 4])
    
    weekday_selection = {}
    with col1:
        weekday_selection[0] = st.checkbox("Segunda", value=0 in default_weekdays, key="wd_mon")
    with col2:
        weekday_selection[1] = st.checkbox("Terça", value=1 in default_weekdays, key="wd_tue")
    with col3:
        weekday_selection[2] = st.checkbox("Quarta", value=2 in default_weekdays, key="wd_wed")
    with col4:
        weekday_selection[3] = st.checkbox("Quinta", value=3 in default_weekdays, key="wd_thu")
    with col5:
        weekday_selection[4] = st.checkbox("Sexta", value=4 in default_weekdays, key="wd_fri")
    with col6:
        weekday_selection[5] = st.checkbox("Sábado", value=5 in default_weekdays, key="wd_sat")
    with col7:
        weekday_selection[6] = st.checkbox("Domingo", value=6 in default_weekdays, key="wd_sun")
    
    selected_weekdays = [day for day, selected in weekday_selection.items() if selected]
    
    if not selected_weekdays:
        st.warning("⚠️ Selecione pelo menos um dia da semana")
    
    # Seção 3: Descrições de Atividades por Data
    st.markdown("---")
    st.header("📝 Descrições de Atividades por Encontro")
    
    if selected_weekdays and start_date_config <= end_date_config:
        # Gerar datas baseado nos dias selecionados
        all_dates = generate_date_range(start_date_config, end_date_config)
        filtered_dates = [
            d for d in all_dates 
            if d.weekday() in selected_weekdays and not is_brazilian_holiday(d)
        ]
        
        st.info(f"📊 **{len(filtered_dates)} encontro(s)** serão criados baseado nas configurações acima (excluindo feriados).")
        
        # Carregar descrições existentes
        current_descriptions = current_config.get("activity_descriptions", {})
        
        # Campo para descrição padrão
        default_activity = st.text_area(
            "Descrição Padrão de Atividade",
            value=current_config.get("default_activity", ""),
            placeholder="Esta descrição será aplicada a todos os encontros. Você pode personalizá-las individualmente abaixo.",
            height=100
        )
        
        if st.button("📋 Aplicar Descrição Padrão a Todos os Encontros", type="secondary"):
            if default_activity.strip():
                for d in filtered_dates:
                    date_str = d.strftime("%d/%m/%Y")
                    current_descriptions[date_str] = default_activity.strip()
                st.success("✅ Descrição padrão aplicada a todos os encontros!")
                st.rerun()
        
        st.write("---")
        st.subheader("Descrições Individuais por Data")
        
        # Dividir em tabs para melhor organização
        dates_per_tab = 10
        num_tabs = (len(filtered_dates) + dates_per_tab - 1) // dates_per_tab
        
        if num_tabs > 1:
            tab_names = [f"Encontros {i*dates_per_tab+1}-{min((i+1)*dates_per_tab, len(filtered_dates))}" 
                        for i in range(num_tabs)]
            tabs = st.tabs(tab_names)
        else:
            tabs = [st.container()]
        
        # Armazenar descrições temporárias
        if 'temp_descriptions' not in st.session_state:
            st.session_state.temp_descriptions = current_descriptions.copy()
        
        for tab_idx, tab in enumerate(tabs):
            with tab:
                start_idx = tab_idx * dates_per_tab
                end_idx = min(start_idx + dates_per_tab, len(filtered_dates))
                
                for date_obj in filtered_dates[start_idx:end_idx]:
                    date_str = date_obj.strftime("%d/%m/%Y")
                    weekday_names = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
                    weekday = weekday_names[date_obj.weekday()]
                    
                    with st.expander(f"📅 {date_str} ({weekday})", expanded=False):
                        current_desc = st.session_state.temp_descriptions.get(date_str, "")
                        
                        description = st.text_area(
                            "Descrição das atividades:",
                            value=current_desc,
                            key=f"desc_{date_str}",
                            height=120,
                            placeholder="Descreva as atividades realizadas neste encontro..."
                        )
                        
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            if st.button("💾 Salvar", key=f"save_{date_str}", use_container_width=True):
                                if description and description.strip():
                                    st.session_state.temp_descriptions[date_str] = description.strip()
                                    st.success("✅ Salvo!")
                                    st.rerun()
                        
                        with col2:
                            if st.button("🗑️ Limpar", key=f"clear_{date_str}", use_container_width=True):
                                if date_str in st.session_state.temp_descriptions:
                                    del st.session_state.temp_descriptions[date_str]
                                    st.info("Descrição removida")
                                    st.rerun()
        
        # Estatísticas
        st.write("---")
        descriptions_count = len([d for d in st.session_state.temp_descriptions.values() if d.strip()])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Encontros", len(filtered_dates))
        with col2:
            st.metric("Com Descrição", descriptions_count)
        with col3:
            if descriptions_count == len(filtered_dates):
                st.metric("Status", "✅ Completo")
            else:
                st.metric("Faltando", len(filtered_dates) - descriptions_count)
    
    else:
        st.warning("⚠️ Configure o período e os dias da semana para visualizar os encontros.")
    
    # Botão de salvar configuração
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("💾 Salvar Configuração do Template", type="primary", use_container_width=True):
            if not selected_weekdays:
                st.error("❌ Selecione pelo menos um dia da semana!")
            elif start_date_config > end_date_config:
                st.error("❌ Data de início deve ser anterior à data de término!")
            elif not document_date.strip():
                st.error("❌ Informe a data do documento!")
            else:
                # Criar configuração
                config = {
                    "start_date": start_date_config.isoformat(),
                    "end_date": end_date_config.isoformat(),
                    "start_time": start_time_config.strftime("%H:%M"),
                    "end_time": end_time_config.strftime("%H:%M"),
                    "weekdays": selected_weekdays,
                    "document_date": document_date.strip(),
                    "default_activity": default_activity.strip() if default_activity else "",
                    "activity_descriptions": st.session_state.get('temp_descriptions', {})
                }
                
                save_template_config(config)
                st.success("✅ Configuração do template salva com sucesso!")
                st.success("🎓 Os estagiários agora podem usar este template ao gerar seus documentos.")
                
                # Mostrar resumo
                with st.expander("📊 Resumo da Configuração", expanded=True):
                    st.write(f"**Período:** {start_date_config.strftime('%d/%m/%Y')} a {end_date_config.strftime('%d/%m/%Y')}")
                    st.write(f"**Horário:** {start_time_config.strftime('%H:%M')} às {end_time_config.strftime('%H:%M')}")
                    st.write(f"**Dias da semana:** {len(selected_weekdays)} dia(s)")
                    
                    if filtered_dates:
                        st.write(f"**Total de encontros:** {len(filtered_dates)}")
                        descriptions_count = len([d for d in config['activity_descriptions'].values() if d.strip()])
                        st.write(f"**Encontros com descrição:** {descriptions_count}/{len(filtered_dates)}")
    
    # Botão de limpar configuração
    st.markdown("---")
    
    if current_config:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🗑️ Limpar Template Atual", type="secondary", use_container_width=True):
                if os.path.exists(TEMPLATE_CONFIG_FILE):
                    os.remove(TEMPLATE_CONFIG_FILE)
                if 'temp_descriptions' in st.session_state:
                    del st.session_state.temp_descriptions
                st.success("Template removido!")
                st.rerun()
    
    st.markdown("---")
    st.caption("💡 **Dica:** Esta configuração será usada como template pelos estagiários ao gerar seus documentos.")


if __name__ == "__main__":
    main()

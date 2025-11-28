"""
Aplicação para gerenciamento de feriados personalizados (para uso do responsável pelo estágio).
"""
import streamlit as st
from datetime import date
from date_utils import (
    add_custom_holiday, remove_custom_holiday, get_custom_holidays, 
    clear_custom_holidays, get_brazilian_holidays
)


def main():
    """Função principal da aplicação de gerenciamento"""
    st.set_page_config(
        page_title="Gerenciamento de Feriados",
        page_icon="🎉",
        layout="wide"
    )
    
    st.title("🎉 Gerenciamento de Feriados - Responsável pelo Estágio")
    st.markdown("---")
    
    st.info("👤 **Área Administrativa:** Configure feriados municipais, pontos facultativos e datas especiais que serão automaticamente aplicados para todos os estagiários.")
    
    # Seção de adicionar feriado
    st.header("➕ Adicionar Novo Feriado")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        custom_holiday_date = st.date_input(
            "Data do Feriado",
            value=date.today(),
            key="custom_holiday_date",
            format="DD/MM/YYYY"
        )
    
    with col2:
        custom_holiday_name = st.text_input(
            "Nome do Feriado",
            placeholder="Ex: Aniversário da Cidade, Ponto Facultativo",
            key="custom_holiday_name"
        )
    
    with col3:
        st.write("")  # Espaçamento
        st.write("")  # Espaçamento
        if st.button("➕ Adicionar", use_container_width=True, type="primary"):
            if custom_holiday_name.strip():
                add_custom_holiday(custom_holiday_date, custom_holiday_name.strip())
                st.success(f"✅ Feriado '{custom_holiday_name}' adicionado em {custom_holiday_date.strftime('%d/%m/%Y')}")
                st.rerun()
            else:
                st.error("❌ Por favor, informe o nome do feriado")
    
    st.markdown("---")
    
    # Mostrar feriados cadastrados
    st.header("📋 Feriados Cadastrados")
    
    # Tabs para separar oficiais e personalizados
    tab1, tab2 = st.tabs(["🎉 Feriados Personalizados", "🇧🇷 Feriados Oficiais (Referência)"])
    
    with tab1:
        custom_holidays = get_custom_holidays()
        
        if custom_holidays:
            st.write(f"**Total: {len(custom_holidays)} feriado(s) personalizado(s)**")
            st.write("")
            
            # Ordenar por data
            sorted_holidays = sorted(custom_holidays.items(), key=lambda x: x[0])
            
            # Agrupar por ano
            holidays_by_year = {}
            for holiday_date, holiday_name in sorted_holidays:
                year = holiday_date.year
                if year not in holidays_by_year:
                    holidays_by_year[year] = []
                holidays_by_year[year].append((holiday_date, holiday_name))
            
            # Mostrar por ano
            for year in sorted(holidays_by_year.keys()):
                with st.expander(f"📅 Ano {year} ({len(holidays_by_year[year])} feriado(s))", expanded=True):
                    for holiday_date, holiday_name in holidays_by_year[year]:
                        col1, col2, col3 = st.columns([2, 3, 1])
                        
                        with col1:
                            st.write(f"**{holiday_date.strftime('%d/%m/%Y')}**")
                        
                        with col2:
                            st.write(holiday_name)
                        
                        with col3:
                            if st.button("🗑️ Remover", key=f"remove_holiday_{holiday_date}", use_container_width=True):
                                remove_custom_holiday(holiday_date)
                                st.success("Feriado removido!")
                                st.rerun()
            
            st.markdown("---")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🗑️ Limpar Todos os Feriados", use_container_width=True, type="secondary"):
                    clear_custom_holidays()
                    st.success("✅ Todos os feriados personalizados foram removidos!")
                    st.rerun()
        else:
            st.info("ℹ️ Nenhum feriado personalizado cadastrado ainda.")
            st.write("Adicione feriados usando o formulário acima. Eles estarão disponíveis para todos os estagiários.")
    
    with tab2:
        st.info("ℹ️ Feriados nacionais brasileiros (automáticos - não precisam ser cadastrados)")
        
        # Mostrar feriados oficiais do ano atual e próximo
        current_year = date.today().year
        
        for year in [current_year, current_year + 1]:
            with st.expander(f"📅 Feriados Oficiais {year}", expanded=year == current_year):
                br_holidays = get_brazilian_holidays(year)
                
                if br_holidays:
                    sorted_official = sorted(br_holidays.items())
                    
                    for holiday_date, holiday_name in sorted_official:
                        col1, col2 = st.columns([2, 3])
                        with col1:
                            st.write(f"**{holiday_date.strftime('%d/%m/%Y')}**")
                        with col2:
                            st.write(holiday_name)
                else:
                    st.write("Nenhum feriado oficial encontrado para este ano.")
    
    st.markdown("---")
    st.caption("💡 **Dica:** Os feriados personalizados cadastrados aqui serão aplicados automaticamente ao gerar turnos por período na aplicação principal.")


if __name__ == "__main__":
    main()

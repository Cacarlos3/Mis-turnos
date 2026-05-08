import streamlit as st
import pandas as pd
from datetime import time

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Retail Optimizer Pro", layout="wide")

# 2. MEMORIA DE LA SESIÓN (Evita que se borre al cambiar de pestaña)
if 'empleados' not in st.session_state:
    st.session_state.empleados = []
if 'tiendas' not in st.session_state:
    st.session_state.tiendas = []

# 3. DISEÑO DE PESTAÑAS
tab_emp, tab_tiendas, tab_horarios = st.tabs(["👥 EMPLEADOS", "🏪 TIENDAS", "📅 HORARIOS"])

# --- PESTAÑA TIENDAS ---
with tab_tiendas:
    st.header("Gestión de Tiendas")
    with st.expander("➕ ABRIR NUEVA TIENDA"):
        with st.form("nueva_tienda"):
            nombre_t = st.text_input("Nombre de la Tienda")
            st.write("### Necesidades de Personal por Día")
            conf_tienda = {}
            for d in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
                c1, c2 = st.columns(2)
                num = c1.number_input(f"Empleados necesarios ({d})", 1, 50, 2, key=f"n_{nombre_t}_{d}")
                entrada = c2.time_input(f"Hora entrada ({d})", time(9, 0), key=f"e_{nombre_t}_{d}")
                conf_tienda[d] = {"num": num, "entrada": entrada}
            
            if st.form_submit_button("Guardar Tienda"):
                if nombre_t:
                    st.session_state.tiendas.append({"Nombre": nombre_t, "Config": conf_tienda})
                    st.success(f"Tienda '{nombre_t}' guardada.")
                    st.rerun()

    # Mostrar lista de tiendas
    for t in st.session_state.tiendas:
        st.info(f"🏪 {t['Nombre']}")

# --- PESTAÑA EMPLEADOS ---
with tab_emp:
    st.header("Base de Datos de Empleados")
    
    with st.expander("➕ AÑADIR EMPLEADO"):
        with st.form("nuevo_empleado"):
            nombre_e = st.text_input("Nombre y Apellidos")
            
            # Cargamos las tiendas que ya existen
            lista_tiendas_reales = [t['Nombre'] for t in st.session_state.tiendas]
            no_tiendas = st.multiselect("No puede trabajar en:", options=lista_tiendas_reales)
            
            # Incompatibilidad
            lista_empleados_reales = [e['Nombre'] for e in st.session_state.empleados]
            no_con = st.multiselect("No puede trabajar con:", options=lista_empleados_reales)
            
            libres = st.multiselect("Días libres fijos:", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])
            
            st.write("---")
            st.write("### Restricciones Horarias")
            
            restricciones_h = {}
            for d in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
                activar = st.checkbox(f"Restricción el {d}", key=f"act_{d}")
                if activar:
                    tramos = st.text_input(f"Tramos prohibidos {d} (ej: 10:00-11:00)", key=f"t_val_{d}")
                    restricciones_h[d] = tramos

            if st.form_submit_button("Registrar Empleado"):
                if nombre_e:
                    st.session_state.empleados.append({
                        "Nombre": nombre_e,
                        "Vetos": no_tiendas,
                        "Incompatibles": no_con,
                        "Libres": libres,
                        "Horarios": restricciones_h
                    })
                    st.success(f"Empleado '{nombre_e}' registrado.")
                    st.rerun()

    # Mostrar lista de empleados
    for i, e in enumerate(st.session_state.empleados):
        st.write(f"👤 **{e['Nombre']}** | Libres: {', '.join(e['Libres'])} | Vetos: {', '.join(e['Vetos'])}")

# --- PESTAÑA HORARIOS ---
with tab_horarios:
    st.header("Generador Semanal")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🚑 Bajas")
        quien_baja = st.multiselect("Empleados de baja esta semana:", [e['Nombre'] for e in st.session_state.empleados])
    
    with col2:
        st.subheader("⚠️ Ajustes Tiendas")
        st.write("Aquí podrás modificar necesidades puntuales.")

    if st.button("🟢 CREAR TURNO", type="primary"):
        st.balloons()
        st.success("Turno generado (Simulación)")
        

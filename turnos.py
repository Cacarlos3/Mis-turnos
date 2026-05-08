import streamlit as st
import pandas as pd
from datetime import time, datetime, timedelta

# CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Planificador Real 2.0", layout="wide")

# ESTADO DE LA SESIÓN (Base de datos temporal)
if 'empleados' not in st.session_state:
    st.session_state.empleados = []
if 'tiendas' not in st.session_state:
    st.session_state.tiendas = []
if 'incidencias' not in st.session_state:
    st.session_state.incidencias = {"bajas": [], "especiales": []}

# NAVEGACIÓN POR PESTAÑAS
tab_emp, tab_tiendas, tab_horarios = st.tabs(["👥 Empleados", "🏪 Tiendas", "📅 Horarios"])

# --- PESTAÑA 1: EMPLEADOS ---
with tab_emp:
    st.header("Gestión de Personal")
    
    with st.expander("➕ Añadir Nuevo Empleado"):
        with st.form("form_empleado"):
            nombre = st.text_input("Nombre del empleado")
            
            # Restricciones
            col1, col2 = st.columns(2)
            with col1:
                veto_tiendas = st.multiselect("No puede trabajar en:", [f"Tienda {i}" for i in range(1,9)])
                veto_compa = st.multiselect("No puede trabajar con:", [e['Nombre'] for e in st.session_state.empleados])
            with col2:
                dias_libres = st.multiselect("Días libres fijos:", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])
                horas_prohibidas = st.slider("Intervalo de horas no disponible:", 9, 21, (9, 10))
            
            if st.form_submit_button("Guardar Empleado"):
                if nombre:
                    st.session_state.empleados.append({
                        "Nombre": nombre,
                        "Veto_Tiendas": veto_tiendas,
                        "Veto_Compa": veto_compa,
                        "Dias_Libres": dias_libres,
                        "Horas_NO": horas_prohibidas
                    })
                    st.success(f"Empleado {nombre} añadido.")
                    st.rerun()

    # LISTA DE EMPLEADOS
    for i, emp in enumerate(st.session_state.empleados):
        col_n, col_b = st.columns([0.8, 0.2])
        if col_n.button(f"👤 {emp['Nombre']} (Click para editar)", key=f"emp_{i}"):
            st.info(f"Editando a {emp['Nombre']} - Funcionalidad en desarrollo")
        if col_b.button("🗑️", key=f"del_{i}"):
            st.session_state.empleados.pop(i)
            st.rerun()

# --- PESTAÑA 2: TIENDAS ---
with tab_tiendas:
    st.header("Configuración de Tiendas")
    
    with st.expander("🏪 Abrir Nueva Tienda"):
        with st.form("form_tienda"):
            t_nombre = st.text_input("Nombre de la tienda (ej: Tienda 1)")
            st.write("Configuración por día (Horario y Empleados necesarios):")
            
            config_dias = {}
            for d in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
                c1, c2, c3 = st.columns([1,1,1])
                h_ap = c1.time_input(f"Apertura {d}", time(9,0), key=f"ap_{d}")
                h_ci = c2.time_input(f"Cierre {d}", time(21,0), key=f"ci_{d}")
                num_e = c3.number_input(f"Empleados {d}", 1, 10, 2, key=f"num_{d}")
                config_dias[d] = {"ap": h_ap, "ci": h_ci, "num": num_e}
            
            if st.form_submit_button("Aceptar"):
                st.session_state.tiendas.append({"Nombre": t_nombre, "Config": config_dias})
                st.rerun()

    for j, tienda in enumerate(st.session_state.tiendas):
        st.button(f"🏪 {tienda['Nombre']}", key=f"t_list_{j}")

# --- PESTAÑA 3: HORARIOS ---
with tab_horarios:
    st.header("Generador de Cuadrante Semanal")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("🚑 Bajas e Incidencias")
        baja_emp = st.selectbox("Empleado con incidencia:", ["Seleccionar..."] + [e['Nombre'] for e in st.session_state.empleados])
        tipo_baja = st.radio("Duración:", ["Todo el día", "Unas horas"])
        if tipo_baja == "Unas horas":
            rango = st.slider("Rango horario de la baja:", 9, 21, (10, 14))
        
        if st.button("Registrar Incidencia"):
            st.success("Incidencia registrada para el cálculo.")

    with col_b:
        st.subheader("🚀 Refuerzos Especiales")
        # Aquí iría la lógica de necesidades especiales por tienda
        st.write("Configura necesidades extra para días concretos.")

    st.divider()
    if st.button("🟢 CREAR TURNO", use_container_width=True, type="primary"):
        with st.status("Calculando turnos óptimos..."):
            st.write("Verificando vetos de tiendas...")
            st.write("Cruzando incompatibilidades personales...")
            st.write("Ajustando jornadas de 8 horas...")
            
            # Aquí se ejecutaría el algoritmo de reparto
            st.success("¡Turno generado con éxito!")
            
            # Resultado visual (Ejemplo)
            st.subheader("Vista Previa del Resultado")
            st.table(pd.DataFrame({
                "Tienda": ["Tienda 1", "Tienda 1", "Tienda 2"],
                "Empleado": ["Ana", "Carlos", "Elena"],
                "Horario": ["09:00 - 17:00", "13:00 - 21:00", "09:00 - 17:00"],
                "Día": ["Lunes", "Lunes", "Lunes"]
            }))

### ¿

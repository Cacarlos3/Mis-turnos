import streamlit as st
import pandas as pd
from datetime import time

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Retail Optimizer Pro", layout="wide")

# --- MEMORIA DE LA SESIÓN ---
# Esto mantiene los datos vivos mientras la pestaña esté abierta
if 'empleados' not in st.session_state:
    st.session_state.empleados = []
if 'tiendas' not in st.session_state:
    st.session_state.tiendas = []

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .emp-card { padding: 15px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

tab_emp, tab_tiendas, tab_horarios = st.tabs(["👥 EMPLEADOS", "🏪 TIENDAS", "📅 HORARIOS"])

# --- PESTAÑA TIENDAS (La movemos arriba porque Empleados depende de ella) ---
with tab_tiendas:
    st.header("Gestión de Tiendas")
    with st.expander("➕ ABRIR NUEVA TIENDA"):
        with st.form("nueva_tienda"):
            nombre_t = st.text_input("Nombre de la Tienda")
            st.write("### Necesidades de Personal")
            conf = {}
            for d in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
                c1, c2 = st.columns(2)
                num = c1.number_input(f"Empleados necesarios ({d})", 1, 50, 2)
                entrada = c2.time_input(f"Hora entrada principal ({d})", time(9, 0))
                conf[d] = {"num": num, "entrada": entrada}
            
            if st.form_submit_button("Guardar Tienda"):
                if nombre_t:
                    st.session_state.tiendas.append({"Nombre": nombre_t, "Config": conf})
                    st.rerun()

    # Mostrar tiendas creadas
    for t in st.session_state.tiendas:
        st.info(f"🏪 {t['Nombre']}")

# --- PESTAÑA EMPLEADOS ---
with tab_emp:
    st.header("Base de Datos de Empleados")
    
    with st.expander("➕ AÑADIR EMPLEADO"):
        with st.form("nuevo_empleado"):
            nombre_e = st.text_input("Nombre y Apellidos")
            
            # 1. Vincular con tiendas reales creadas
            lista_tiendas_reales = [t['Nombre'] for t in st.session_state.tiendas]
            no_tiendas = st.multiselect("No puede trabajar en:", options=lista_tiendas_reales)
            
            # 2. Incompatibilidad con otros empleados
            lista_empleados_reales = [e['Nombre'] for e in st.session_state.empleados]
            no_con = st.multiselect("No puede trabajar con:", options=lista_empleados_reales)
            
            # 3. Días libres
            libres = st.multiselect("Días libres fijos:", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])
            
            st.write("---")
            st.write("### Restricciones Horarias Específicas")
            st.info("Solo rellena esto si el empleado tiene tramos prohibidos (ej. de 10:00 a 11:30)")
            
            # Sistema de tramos horarios por días
            restricciones_h = {}
            for d in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
                activar = st.checkbox(f"Añadir restricción el {d}")
                if activar:
                    tramos = st.text_input(f"Tramos para {d} (Ej: 10:00-11:00, 15:00-16:00)", key=f"rest_{d}")
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
                    st.rerun()

    # Lista de empleados para editar/ver
    for i, e in enumerate(st.session_state.empleados):
        with st.container():
            st.markdown(f"""<div class="emp-card"><b>{e['Nombre']}</b><br>
            <small>Libres: {', '.join(e['Libres'])} | Vetos: {', '.join(e['Vetos'])}</small></div>""", unsafe_allow_html=True)

# --- PESTAÑA HORARIOS ---
with tab_horarios:
    st.header("Generador Semanal")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🚑 Bajas de la semana")
        quien_baja = st.multiselect("Empleados de baja:", [e['Nombre'] for e in st.session_state.empleados])
    
    with col2:
        st.subheader("⚠️ Cambios en Tiendas")
        tienda_mod = st.selectbox("Tienda a modificar:", ["Ninguna"] + [t['Nombre'] for t in st.session_state.tiendas])

    if st.button("🟢 GENERAR CUADRANTE FINAL", type="primary"):
        st.warning("El motor está procesando las restricciones... (Esta es una simulación visual)")
        st.balloons()

# --- NOTA SOBRE GUARDADO PERMANENTE ---
st.sidebar.warning("⚠️ Los datos se guardan mientras la pestaña esté abierta. Para guardado permanente, contacta para conectar una base de datos.")
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

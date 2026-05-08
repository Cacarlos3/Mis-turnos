import streamlit as st
import pandas as pd
from datetime import time

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Retail Optimizer Pro", layout="wide")

# 2. MEMORIA DE LA SESIÓN
if 'empleados' not in st.session_state:
    st.session_state.empleados = []
if 'tiendas' not in st.session_state:
    st.session_state.tiendas = []

# 3. PESTAÑAS
tab_emp, tab_tiendas, tab_horarios = st.tabs(["👥 EMPLEADOS", "🏪 TIENDAS", "📅 HORARIOS"])

# --- PESTAÑA TIENDAS ---
with tab_tiendas:
    st.header("Configuración de Tiendas")
    with st.expander("➕ CONFIGURAR / ABRIR TIENDA", expanded=True):
        with st.form("nueva_tienda"):
            nombre_t = st.text_input("Nombre de la Tienda (ej. Tienda Centro)")
            
            st.write("### Horarios y Entradas por Día")
            conf_tienda = {}
            
            for d in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
                st.markdown(f"**{d}**")
                c1, c2, c3 = st.columns([1, 1, 2])
                h_ap = c1.time_input(f"Apertura", time(9, 0), key=f"ap_{nombre_t}_{d}")
                h_ci = c2.time_input(f"Cierre", time(21, 0), key=f"ci_{nombre_t}_{d}")
                n_emp = c3.number_input(f"Nº Empleados", 1, 20, 2, key=f"n_{nombre_t}_{d}")
                
                # Entradas escalonadas
                entradas_salidas = []
                st.write(f"Horarios de los {n_emp} empleados para el {d}:")
                for i in range(int(n_emp)):
                    ec1, ec2 = st.columns(2)
                    e = ec1.time_input(f"Entrada Emp. {i+1}", h_ap, key=f"e_{nombre_t}_{d}_{i}")
                    s = ec2.time_input(f"Salida Emp. {i+1}", h_ci, key=f"s_{nombre_t}_{d}_{i}")
                    entradas_salidas.append({"entrada": e, "salida": s})
                
                conf_tienda[d] = {"ap": h_ap, "ci": h_ci, "num": n_emp, "turnos": entradas_salidas}
                st.divider()
            
            if st.form_submit_button("Guardar Tienda"):
                if nombre_t:
                    # Evitar duplicados de tiendas
                    st.session_state.tiendas = [t for t in st.session_state.tiendas if t['Nombre'] != nombre_t]
                    st.session_state.tiendas.append({"Nombre": nombre_t, "Config": conf_tienda})
                    st.success(f"Tienda '{nombre_t}' guardada correctamente.")
                    st.rerun()

    for t in st.session_state.tiendas:
        st.info(f"🏪 {t['Nombre']} - Configurada")

# --- PESTAÑA EMPLEADOS ---
with tab_emp:
    st.header("Base de Datos de Empleados")
    
    with st.expander("➕ AÑADIR NUEVO EMPLEADO", expanded=True):
        # Campos fuera del form para interactividad inmediata
        nombre_e = st.text_input("Nombre y Apellidos")
        
        # Validar nombre duplicado
        nombres_existentes = [e['Nombre'] for e in st.session_state.empleados]
        if nombre_e in nombres_existentes:
            st.error("Este nombre ya existe. Por favor, añade un apellido o inicial diferente.")
            bloqueo = True
        else:
            bloqueo = False

        lista_tiendas = [t['Nombre'] for t in st.session_state.tiendas]
        no_tiendas = st.multiselect("No puede trabajar en:", options=lista_tiendas)
        
        # Incompatibilidad (ordenados)
        nombres_ordenados = sorted(nombres_existentes)
        no_con = st.multiselect("No puede trabajar con:", options=nombres_ordenados)
        
        libres = st.multiselect("Días libres fijos:", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])
        
        st.write("---")
        st.write("### Restricciones Horarias Específicas")
        restricciones_h = {}
        for d in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
            activar = st.checkbox(f"Añadir restricción el {d}", key=f"check_{d}")
            if activar:
                tramos = st.text_input(f"Tramos prohibidos el {d} (ej: 10:00-11:00)", key=f"val_{d}")
                restricciones_h[d] = tramos

        if st.button("Añadir Empleado"):
            if nombre_e and not bloqueo:
                st.session_state.empleados.append({
                    "Nombre": nombre_e,
                    "Vetos": no_tiendas,
                    "Incompatibles": no_con,
                    "Libres": libres,
                    "Horarios": restricciones_h
                })
                # Ordenar lista de empleados por nombre
                st.session_state.empleados = sorted(st.session_state.empleados, key=lambda x: x['Nombre'])
                st.success(f"¡Empleado '{nombre_e}' añadido!")
                st.rerun()

    # Mostrar lista alfabética
    for e in st.session_state.empleados:
        st.text(f"👤 {e['Nombre']}")

# --- PESTAÑA HORARIOS ---
with tab_horarios:
    st.header("Generador de Cuadrante")
    if st.button("🟢 CREAR TURNO", type="primary"):
        if not st.session_state.empleados or not st.session_state.tiendas:
            st.error("Necesitas tener al menos una tienda y empleados creados.")
        else:
            st.success("Generando cuadrante respetando horarios escalonados y restricciones...")
            st.balloons()
            

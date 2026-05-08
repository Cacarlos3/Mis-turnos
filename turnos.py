import streamlit as st
import pandas as pd
from datetime import time

# Configuración de la página
st.set_page_config(page_title="Gestor de Turnos Inteligente", layout="wide")

st.title("🗓️ Planificador de Turnos - Prototipo")
st.markdown("Configura los turnos y el sistema validará las restricciones automáticamente.")

# --- 1. BASE DE DATOS FICTICIA (Configurable en el futuro) ---
if 'empleados' not in st.session_state:
    st.session_state.empleados = [
        {"Nombre": "Ana", "Vetados": [8], "Incompatible": "Bruno"},
        {"Nombre": "Bruno", "Vetados": [2], "Incompatible": "Ana"},
        {"Nombre": "Carlos", "Vetados": [1, 3], "Incompatible": "Diana"},
        {"Nombre": "Diana", "Vetados": [], "Incompatible": "Carlos"},
        {"Nombre": "Elena", "Vetados": [5], "Incompatible": ""},
    ]

if 'cuadrante' not in st.session_state:
    st.session_state.cuadrante = pd.DataFrame(columns=["Empleado", "Día", "Tienda", "Entrada", "Salida"])

# --- 2. PANEL LATERAL: ENTRADA DE DATOS ---
with st.sidebar:
    st.header("Asignar Nuevo Turno")
    
    emp_nom = st.selectbox("Selecciona Empleado", [e["Nombre"] for e in st.session_state.empleados])
    dia = st.selectbox("Día de la semana", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])
    tienda_num = st.number_input("Número de Tienda (1-8)", min_value=1, max_value=8, value=1)
    tienda_label = f"Tienda {tienda_num}"
    
    t_entrada = st.time_input("Hora de Entrada", time(9, 0))
    t_salida = st.time_input("Hora de Salida", time(21, 0))
    
    boton_añadir = st.button("Añadir al Cuadrante")

# --- 3. LÓGICA DE VALIDACIÓN ---
if boton_añadir:
    # Obtener info del empleado
    info = next(item for item in st.session_state.empleados if item["Nombre"] == emp_nom)
    error = False
    
    # Validación 1: Tienda Vetada
    if tienda_num in info["Vetados"]:
        st.error(f"❌ {emp_nom} tiene prohibido trabajar en la Tienda {tienda_num}.")
        error = True
    
    # Validación 2: Incompatibilidad
    compañeros = st.session_state.cuadrante[
        (st.session_state.cuadrante["Día"] == dia) & 
        (st.session_state.cuadrante["Tienda"] == tienda_label)
    ]["Empleado"].tolist()
    
    if info["Incompatible"] in compañeros:
        st.error(f"❌ Conflicto: {emp_nom} no puede trabajar con {info['Incompatible']}.")
        error = True
        
    if not error:
        nuevo_turno = pd.DataFrame([{
            "Empleado": emp_nom,
            "Día": dia,
            "Tienda": tienda_label,
            "Entrada": t_entrada.strftime("%H:%M"),
            "Salida": t_salida.strftime("%H:%M")
        }])
        st.session_state.cuadrante = pd.concat([st.session_state.cuadrante, nuevo_turno], ignore_index=True)
        st.success(f"✅ Turno añadido para {emp_nom}")

# --- 4. VISUALIZACIÓN Y EXPORTACIÓN ---
st.subheader("Cuadrante Semanal Actual")
if not st.session_state.cuadrante.empty:
    # Ordenar por día para que se vea bien
    orden_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    st.session_state.cuadrante['Día'] = pd.Categorical(st.session_state.cuadrante['Día'], categories=orden_dias, ordered=True)
    df_visible = st.session_state.cuadrante.sort_values(["Día", "Tienda"])
    
    st.dataframe(df_visible, use_container_width=True)
    
    # Botón para descargar en CSV (Que puedes abrir en Excel)
    csv = df_visible.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar para Excel",
        data=csv,
        file_name="cuadrante_turnos.csv",
        mime="text/csv",
    )
    
    if st.button("Limpiar todo el cuadrante"):
        st.session_state.cuadrante = pd.DataFrame(columns=["Empleado", "Día", "Tienda", "Entrada", "Salida"])
        st.rerun()
else:
    st.info("Aún no hay turnos asignados. Usa el panel de la izquierda.")

st.divider()
st.info("💡 **Nota para el futuro:** Esta es una versión de prueba. En la versión final, el botón 'PDF' generará el archivo con tu diseño exacto de Excel de forma automática.")

import streamlit as st
import pandas as pd
from datetime import time, datetime
import time as time_lib

# --- CONFIGURACIÓN DE PÁGINA Y ESTILO ---
st.set_page_config(page_title="Turnos Maite", layout="wide", page_icon="📅")

# Inyección de CSS para: Fondo Rojo Pastel, Letras Blancas, Bordes Blancos Redondeados
st.markdown("""
    <style>
    /* Fondo General Rojo Pastel */
    .stApp {
        background-color: #FF7373;
    }
    
    /* Todo el texto principal en Blanco */
    h1, h2, h3, h4, p, span, label, .stMarkdown {
        color: white !important;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Título Principal */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        color: white;
        margin-bottom: 30px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }

    /* Contenedores (Cards) con Borde Blanco Redondeado */
    .card {
        background-color: rgba(255, 255, 255, 0.1); /* Transparencia sutil */
        padding: 20px;
        border-radius: 20px;
        border: 2px solid white;
        margin-bottom: 15px;
        color: white;
    }
    
    /* Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border: 2px solid white !important;
        border-radius: 15px 15px 0px 0px !important;
        color: white !important;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #FF7373 !important;
    }

    /* Botones Blancos con Letra Roja */
    .stButton>button {
        border-radius: 15px;
        background-color: white !important;
        color: #FF7373 !important;
        font-weight: bold;
        border: 2px solid white;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #FFDEDE !important;
        transform: scale(1.02);
    }

    /* Ajuste de inputs para que se vean sobre rojo */
    input, select, textarea {
        color: #FF7373 !important;
    }
    
    /* Expander con borde blanco */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid white !important;
        border-radius: 10px !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIO DE LÓGICA ---
if 'empleados' not in st.session_state:
    st.session_state.empleados = []
if 'tiendas' not in st.session_state:
    st.session_state.tiendas = []

st.markdown('<h1 class="main-title">Turnos Maite</h1>', unsafe_allow_html=True)

tab_emp, tab_tiendas, tab_horarios = st.tabs(["👥 EMPLEADOS", "🏪 TIENDAS", "📅 PLANIFICADOR"])

# --- PESTAÑA TIENDAS ---
with tab_tiendas:
    st.markdown('<div class="card"><h3>Configuración de Tiendas</h3></div>', unsafe_allow_html=True)
    with st.expander("➕ Añadir Nueva Tienda", expanded=False):
        with st.form("nueva_tienda"):
            nombre_t = st.text_input("Nombre de la Tienda")
            conf_tienda = {}
            for d in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
                st.write(f"**{d}**")
                c1, c2, c3 = st.columns([1, 1, 2])
                h_ap = c1.time_input(f"Apertura", time(9, 0), key=f"ap_{nombre_t}_{d}")
                h_ci = c2.time_input(f"Cierre", time(21, 0), key=f"ci_{nombre_t}_{d}")
                n_emp = c3.number_input(f"Nº Puestos", 1, 20, 2, key=f"n_{nombre_t}_{d}")
                
                turnos = []
                for i in range(int(n_emp)):
                    ec1, ec2 = st.columns(2)
                    e = ec1.time_input(f"Entrada P{i+1}", h_ap, key=f"e_{nombre_t}_{d}_{i}")
                    s = ec2.time_input(f"Salida P{i+1}", h_ci, key=f"s_{nombre_t}_{d}_{i}")
                    turnos.append({"entrada": e, "salida": s})
                conf_tienda[d] = {"ap": h_ap, "ci": h_ci, "num": n_emp, "turnos": turnos}
            
            if st.form_submit_button("Guardar Tienda"):
                if nombre_t:
                    st.session_state.tiendas = [t for t in st.session_state.tiendas if t['Nombre'] != nombre_t]
                    st.session_state.tiendas.append({"Nombre": nombre_t, "Config": conf_tienda})
                    st.session_state.tiendas = sorted(st.session_state.tiendas, key=lambda x: x['Nombre'])
                    msg = st.success("Tienda guardada")
                    time_lib.sleep(1.5)
                    msg.empty()
                    st.rerun()

    for t in st.session_state.tiendas:
        st.markdown(f'<div class="card">🏪 {t["Nombre"]}</div>', unsafe_allow_html=True)

# --- PESTAÑA EMPLEADOS ---
with tab_emp:
    st.markdown('<div class="card"><h3>Panel de Empleados</h3></div>', unsafe_allow_html=True)
    with st.expander("➕ Añadir Nuevo Empleado", expanded=False):
        nombre_e = st.text_input("Nombre Completo")
        nombres_existentes = [e['Nombre'] for e in st.session_state.empleados]
        
        c1, c2 = st.columns(2)
        with c1:
            no_tiendas = st.multiselect("Vetos de Tienda:", options=sorted([t['Nombre'] for t in st.session_state.tiendas]))
            no_con = st.multiselect("Incompatibilidad:", options=sorted(nombres_existentes))
        with c2:
            libres = st.multiselect("Días Libres:", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])

        restricciones_h = {}
        for d in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
            if st.checkbox(f"Indisponible el {d}", key=f"ch_{d}"):
                restricciones_h[d] = st.text_input(f"Horas prohibidas {d}", key=f"v_{d}")

        if st.button("Registrar Empleado"):
            if nombre_e and nombre_e not in nombres_existentes:
                st.session_state.empleados.append({
                    "Nombre": nombre_e, "Vetos": no_tiendas, "Incompatibles": no_con, 
                    "Libres": libres, "Horarios": restricciones_h
                })
                st.session_state.empleados = sorted(st.session_state.empleados, key=lambda x: x['Nombre'])
                msg = st.success("Empleado añadido")
                time_lib.sleep(1.5)
                msg.empty()
                st.rerun()

    for e in st.session_state.empleados:
        st.markdown(f"""<div class="card">
            <b>👤 {e['Nombre']}</b><br>
            <small>Libres: {', '.join(e['Libres']) if e['Libres'] else 'Ninguno'}</small>
        </div>""", unsafe_allow_html=True)

# --- PESTAÑA HORARIOS (CEREBRO) ---
with tab_horarios:
    st.markdown('<div class="card"><h3>Cálculo de Turnos Semanal</h3></div>', unsafe_allow_html=True)
    bajas = st.multiselect("Bajas de la Semana:", [e['Nombre'] for e in st.session_state.empleados])

    if st.button("🟢 GENERAR CUADRANTE INTELIGENTE"):
        if not st.session_state.empleados or not st.session_state.tiendas:
            st.error("Faltan datos")
        else:
            resultados = []
            empleados_disponibles = [e for e in st.session_state.empleados if e['Nombre'] not in bajas]
            
            for dia in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
                asignados_hoy = []
                for tienda in st.session_state.tiendas:
                    turnos_necesarios = tienda['Config'][dia]['turnos']
                    for idx, turno in enumerate(turnos_necesarios):
                        empleado_elegido = None
                        for emp in empleados_disponibles:
                            if dia in emp['Libres']: continue
                            if tienda['Nombre'] in emp['Vetos']: continue
                            if emp['Nombre'] in [a['Empleado'] for a in asignados_hoy]: continue
                            compas_tienda = [a['Empleado'] for a in asignados_hoy if a['Tienda'] == tienda['Nombre']]
                            if any(c in emp['Incompatibles'] for c in compas_tienda): continue
                            
                            if dia in emp['Horarios'] and emp['Horarios'][dia]:
                                try:
                                    p_inicio = datetime.strptime(emp['Horarios'][dia].split('-')[0], "%H:%M").time()
                                    if turno['entrada'] <= p_inicio <= turno['salida']: continue
                                except: pass
                            
                            empleado_elegido = emp['Nombre']
                            break
                        
                        registro = {
                            "Día": dia, "Tienda": tienda['Nombre'], 
                            "Empleado": empleado_elegido if empleado_elegido else "⚠️ SIN CUBRIR", 
                            "Entrada": turno['entrada'].strftime("%H:%M"), 
                            "Salida": turno['salida'].strftime("%H:%M")
                        }
                        asignados_hoy.append(registro)
                        resultados.append(registro)

            df_final = pd.DataFrame(resultados)
            st.balloons()
            
            for t_nombre in [t['Nombre'] for t in st.session_state.tiendas]:
                st.markdown(f'<div class="card">📋 {t_nombre}</div>', unsafe_allow_html=True)
                vista = df_final[df_final['Tienda'] == t_nombre].pivot(index='Entrada', columns='Día', values='Empleado').fillna("-")
                st.dataframe(vista)
          

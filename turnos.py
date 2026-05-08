                                            
import streamlit as st
import pandas as pd
from datetime import time, datetime
import time as time_lib

# --- CONFIGURACIÓN DE PÁGINA Y ESTILO ---
st.set_page_config(page_title="Retail Optimizer Pro", layout="wide", page_icon="📅")

# Inyección de CSS para la identidad visual: Rojo Claro y Blanco
st.markdown("""
    <style>
    /* Fondo general blanco humo */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* Títulos en Rojo Claro Corporativo */
    h1, h2, h3 {
        color: #FF5C5C;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700;
    }
    
    /* Estilo de las pestañas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: #FFF5F5;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        border: 1px solid #FFDEDE;
        color: #FF5C5C;
    }

    .stTabs [aria-selected="true"] {
        background-color: #FF5C5C !important;
        color: white !important;
        border: 1px solid #FF5C5C !important;
    }

    /* Tarjetas de empleados y tiendas */
    .card {
        background-color: #FFFFFF;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(255, 92, 92, 0.1);
        border: 1px solid #FFDEDE;
        margin-bottom: 12px;
    }
    
    /* Botones en Rojo Claro */
    .stButton>button {
        border-radius: 8px;
        background-color: #FF5C5C;
        color: white;
        font-weight: 600;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background-color: #FF7373;
        border: none;
        color: white;
    }

    /* Inputs y áreas de selección */
    .stTextInput>div>div>input, .stSelectbox>div>div {
        border-color: #FFDEDE !important;
    }

    /* Sidebar o menú lateral si se usara */
    [data-testid="stSidebar"] {
        background-color: #FFF5F5;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIO DE LÓGICA (Mantenemos el estado de la sesión) ---
if 'empleados' not in st.session_state:
    st.session_state.empleados = []
if 'tiendas' not in st.session_state:
    st.session_state.tiendas = []

st.title("🔴 Retail Optimizer Pro")

tab_emp, tab_tiendas, tab_horarios = st.tabs(["👥 GESTIÓN EMPLEADOS", "🏪 RED DE TIENDAS", "📅 PLANIFICADOR"])

# --- PESTAÑA TIENDAS ---
with tab_tiendas:
    st.subheader("Configuración de Puntos de Venta")
    with st.expander("➕ Configurar nueva tienda", expanded=False):
        with st.form("nueva_tienda"):
            nombre_t = st.text_input("Nombre de la Tienda")
            conf_tienda = {}
            for d in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
                st.markdown(f"#### {d}")
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
                st.divider()
            
            if st.form_submit_button("Guardar Tienda"):
                if nombre_t:
                    st.session_state.tiendas = [t for t in st.session_state.tiendas if t['Nombre'] != nombre_t]
                    st.session_state.tiendas.append({"Nombre": nombre_t, "Config": conf_tienda})
                    st.session_state.tiendas = sorted(st.session_state.tiendas, key=lambda x: x['Nombre'])
                    msg = st.success("🏪 Tienda guardada correctamente")
                    time_lib.sleep(1.5)
                    msg.empty()
                    st.rerun()

    cols = st.columns(3)
    for i, t in enumerate(st.session_state.tiendas):
        with cols[i % 3]:
            st.markdown(f"""<div class="card">
                <h3 style="margin-top:0;">🏪 {t['Nombre']}</h3>
                <p style="color: #666; font-size: 14px;">Horarios configurados para la semana completa.</p>
                </div>""", unsafe_allow_html=True)

# --- PESTAÑA EMPLEADOS ---
with tab_emp:
    st.subheader("Panel de Capital Humano")
    with st.expander("➕ Registrar nuevo empleado", expanded=False):
        nombre_e = st.text_input("Nombre Completo")
        nombres_existentes = [e['Nombre'] for e in st.session_state.empleados]
        
        c1, c2 = st.columns(2)
        with c1:
            no_tiendas = st.multiselect("Vetos de Tienda:", options=sorted([t['Nombre'] for t in st.session_state.tiendas]))
            no_con = st.multiselect("Incompatibilidad:", options=sorted(nombres_existentes))
        with c2:
            libres = st.multiselect("Días Libres:", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])

        restricciones_h = {}
        st.write("---")
        st.write("📌 **Restricciones Horarias Específicas**")
        for d in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
            if st.checkbox(f"Indisponible el {d}", key=f"ch_{d}"):
                restricciones_h[d] = st.text_input(f"Horas prohibidas {d} (ej: 10:00-12:00)", key=f"v_{d}")

        if st.button("Añadir a la plantilla"):
            if nombre_e and nombre_e not in nombres_existentes:
                st.session_state.empleados.append({
                    "Nombre": nombre_e, "Vetos": no_tiendas, "Incompatibles": no_con, 
                    "Libres": libres, "Horarios": restricciones_h
                })
                st.session_state.empleados = sorted(st.session_state.empleados, key=lambda x: x['Nombre'])
                msg = st.success("👤 Empleado registrado con éxito")
                time_lib.sleep(1.5)
                msg.empty()
                st.rerun()

    for e in st.session_state.empleados:
        st.markdown(f"""<div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <b style="color: #FF5C5C; font-size: 16px;">👤 {e['Nombre']}</b>
                <span style="background-color: #FFDEDE; color: #FF5C5C; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold;">PLANTILLA</span>
            </div>
            <p style="font-size: 13px; margin: 8px 0 0 0; color: #555;">
                <b>Libres:</b> {', '.join(e['Libres']) if e['Libres'] else 'Ninguno'} | 
                <b>Vetos:</b> {', '.join(e['Vetos']) if e['Vetos'] else 'Ninguno'}
            </p>
        </div>""", unsafe_allow_html=True)

# --- PESTAÑA HORARIOS (CEREBRO MATEMÁTICO) ---
with tab_horarios:
    st.subheader("Planificación de Turnos Semanal")
    bajas = st.multiselect("Marcar Bajas o Ausencias:", [e['Nombre'] for e in st.session_state.empleados])

    if st.button("🟢 GENERAR CUADRANTE INTELIGENTE", use_container_width=True):
        if not st.session_state.empleados or not st.session_state.tiendas:
            st.error("Error: Se requieren datos de tiendas y empleados para calcular.")
        else:
            resultados = []
            empleados_disponibles = [e for e in st.session_state.empleados if e['Nombre'] not in bajas]
            
            with st.spinner('Procesando restricciones corporativas...'):
                for dia in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
                    asignados_hoy = []
                    for tienda in st.session_state.tiendas:
                        turnos_necesarios = tienda['Config'][dia]['turnos']
                        for idx, turno in enumerate(turnos_necesarios):
                            empleado_elegido = None
                            for emp in empleados_disponibles:
                                # Reglas lógicas
                                if dia in emp['Libres']: continue
                                if tienda['Nombre'] in emp['Vetos']: continue
                                if emp['Nombre'] in [a['Empleado'] for a in asignados_hoy]: continue
                                compas_tienda = [a['Empleado'] for a in asignados_hoy if a['Tienda'] == tienda['Nombre']]
                                if any(c in emp['Incompatibles'] for c in compas_tienda): continue
                                
                                # Horas prohibidas
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
            
            # Tablas de resultados con estilo
            for t_nombre in [t['Nombre'] for t in st.session_state.tiendas]:
                st.markdown(f"### 📋 {t_nombre}")
                vista = df_final[df_final['Tienda'] == t_nombre].pivot(index='Entrada', columns='Día', values='Empleado').fillna("-")
                st.dataframe(vista, use_container_width=True)
            
            csv = df_final.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar cuadrante (.CSV)", csv, "horarios_empresa.csv", "text/csv")
        

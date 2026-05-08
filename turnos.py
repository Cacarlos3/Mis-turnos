import streamlit as st
import pandas as pd
from datetime import time, datetime, timedelta
import time as time_lib

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
    with st.expander("➕ CONFIGURAR / ABRIR TIENDA", expanded=False):
        with st.form("nueva_tienda"):
            nombre_t = st.text_input("Nombre de la Tienda")
            st.write("### Horarios y Entradas por Día")
            conf_tienda = {}
            for d in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
                st.markdown(f"**{d}**")
                c1, c2, c3 = st.columns([1, 1, 2])
                h_ap = c1.time_input(f"Apertura", time(9, 0), key=f"ap_{nombre_t}_{d}")
                h_ci = c2.time_input(f"Cierre", time(21, 0), key=f"ci_{nombre_t}_{d}")
                n_emp = c3.number_input(f"Nº Empleados", 1, 20, 2, key=f"n_{nombre_t}_{d}")
                
                entradas_salidas = []
                for i in range(int(n_emp)):
                    ec1, ec2 = st.columns(2)
                    e = ec1.time_input(f"Entrada Emp. {i+1}", h_ap, key=f"e_{nombre_t}_{d}_{i}")
                    s = ec2.time_input(f"Salida Emp. {i+1}", h_ci, key=f"s_{nombre_t}_{d}_{i}")
                    entradas_salidas.append({"entrada": e, "salida": s})
                conf_tienda[d] = {"ap": h_ap, "ci": h_ci, "num": n_emp, "turnos": entradas_salidas}
                st.divider()
            
            if st.form_submit_button("Guardar Tienda"):
                if nombre_t:
                    st.session_state.tiendas = [t for t in st.session_state.tiendas if t['Nombre'] != nombre_t]
                    st.session_state.tiendas.append({"Nombre": nombre_t, "Config": conf_tienda})
                    st.session_state.tiendas = sorted(st.session_state.tiendas, key=lambda x: x['Nombre'])
                    msg = st.success("🏪 Tienda añadida correctamente")
                    time_lib.sleep(2)
                    msg.empty()
                    st.rerun()

    for t in st.session_state.tiendas:
        st.info(f"🏪 {t['Nombre']}")

# --- PESTAÑA EMPLEADOS ---
with tab_emp:
    st.header("Base de Datos de Empleados")
    with st.expander("➕ AÑADIR NUEVO EMPLEADO", expanded=False):
        nombre_e = st.text_input("Nombre y Apellidos")
        nombres_existentes = [e['Nombre'] for e in st.session_state.empleados]
        bloqueo = nombre_e in nombres_existentes
        if bloqueo: st.error("El nombre ya existe")

        lista_tiendas = sorted([t['Nombre'] for t in st.session_state.tiendas])
        no_tiendas = st.multiselect("No puede trabajar en:", options=lista_tiendas)
        no_con = st.multiselect("No puede trabajar con:", options=sorted(nombres_existentes))
        libres = st.multiselect("Días libres fijos:", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])
        
        restricciones_h = {}
        for d in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
            if st.checkbox(f"Restricción el {d}", key=f"ch_{d}"):
                restricciones_h[d] = st.text_input(f"Tramos prohibidos {d}", key=f"v_{d}")

        if st.button("Añadir Empleado"):
            if nombre_e and not bloqueo:
                st.session_state.empleados.append({
                    "Nombre": nombre_e, "Vetos": no_tiendas, "Incompatibles": no_con, 
                    "Libres": libres, "Horarios": restricciones_h
                })
                st.session_state.empleados = sorted(st.session_state.empleados, key=lambda x: x['Nombre'])
                msg = st.success("👤 Empleado añadido")
                time_lib.sleep(2)
                msg.empty()
                st.rerun()

    for e in st.session_state.empleados:
        st.text(f"👤 {e['Nombre']}")

# --- PESTAÑA HORARIOS (EL CEREBRO MATEMÁTICO) ---
with tab_horarios:
    st.header("Generador Automático de Turnos")
    bajas = st.multiselect("Bajas esta semana:", [e['Nombre'] for e in st.session_state.empleados])

    if st.button("🟢 CREAR TURNO", type="primary"):
        if not st.session_state.empleados or not st.session_state.tiendas:
            st.error("Faltan datos de tiendas o empleados.")
        else:
            resultados = []
            empleados_disponibles = [e for e in st.session_state.empleados if e['Nombre'] not in bajas]
            
            with st.spinner('Ejecutando algoritmo de optimización...'):
                for dia in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
                    asignados_hoy = []
                    
                    for tienda in st.session_state.tiendas:
                        turnos_necesarios = tienda['Config'][dia]['turnos']
                        
                        for idx, turno in enumerate(turnos_necesarios):
                            empleado_elegido = None
                            
                            for emp in empleados_disponibles:
                                # REGLA 1: No trabajar en día libre
                                if dia in emp['Libres']: continue
                                # REGLA 2: No trabajar en tienda vetada
                                if tienda['Nombre'] in emp['Vetos']: continue
                                # REGLA 3: No estar ya asignado hoy
                                if emp['Nombre'] in [a['Empleado'] for a in asignados_hoy]: continue
                                # REGLA 4: Incompatibilidad de compañeros
                                compas_tienda = [a['Empleado'] for a in asignados_hoy if a['Tienda'] == tienda['Nombre']]
                                if any(c in emp['Incompatibles'] for c in compas_tienda): continue
                                
                                # REGLA 5: Tramos horarios prohibidos
                                if dia in emp['Horarios']:
                                    # Verificación simple de texto (ej: "10:00-11:00")
                                    prohibido = emp['Horarios'][dia]
                                    if prohibido:
                                        p_inicio = datetime.strptime(prohibido.split('-')[0], "%H:%M").time()
                                        if turno['entrada'] <= p_inicio <= turno['salida']: continue
                                
                                empleado_elegido = emp['Nombre']
                                break
                            
                            if empleado_elegido:
                                registro = {
                                    "Día": dia, "Tienda": tienda['Nombre'], 
                                    "Empleado": empleado_elegido, 
                                    "Entrada": turno['entrada'].strftime("%H:%M"), 
                                    "Salida": turno['salida'].strftime("%H:%M")
                                }
                                asignados_hoy.append(registro)
                                resultados.append(registro)
                            else:
                                resultados.append({"Día": dia, "Tienda": tienda['Nombre'], "Empleado": "⚠️ SIN CUBRIR", "Entrada": turno['entrada'], "Salida": turno['salida']})

            df_final = pd.DataFrame(resultados)
            st.success("¡Cuadrante generado con éxito!")
            
            # Visualización por Tienda
            for t_nombre in [t['Nombre'] for t in st.session_state.tiendas]:
                st.subheader(f"Cuadrante: {t_nombre}")
                vista = df_final[df_final['Tienda'] == t_nombre].pivot(index='Entrada', columns='Día', values='Empleado').fillna("-")
                st.table(vista)
                
            # Botón para descargar
            csv = df_final.to_csv(index=False).encode('utf-8')
            st.download_button("Descargar Cuadrante Completo (CSV)", csv, "horarios.csv", "text/csv")
            

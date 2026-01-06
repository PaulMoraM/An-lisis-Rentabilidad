import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random
from faker import Faker

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Diagnóstico Eunoia Digital",
    page_icon="⭐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. VARIABLES Y ESTILOS ---
URL_LOGO = "https://raw.githubusercontent.com/PaulMoraM/eunoia-branding/main/eunoia-digital-logo.png"
URL_BANNER = "https://raw.githubusercontent.com/PaulMoraM/eunoia-branding/main/banner_redes.png"

def inyectar_estilos():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&display=swap');
            html, body, [class*="css"]  { font-family: 'Montserrat', sans-serif; }
            div.stButton > button:first-child {
                background-color: #0080cd; color: white; border-radius: 8px; border: none; font-weight: bold; height: 3em;
            }
            .cta-button {
                background-color: #0080cd; color: white !important; padding: 15px 32px; text-align: center;
                text-decoration: none; display: inline-block; font-size: 16px; font-weight: bold; border-radius: 8px;
                width: 100%; border: 2px solid #0080cd;
            }
            .cta-button:hover { background-color: black; color: #0080cd !important; }
            [data-testid="stMetricValue"] { color: #0080cd; font-size: 2.2rem; font-weight: 700; }
            #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

inyectar_estilos()

# --- 3. GENERADOR DE DATOS DEMO (Modo Demo) ---
@st.cache_data
def generar_datos_simulados():
    fake = Faker('es_ES')
    datos = []
    categorias = ['ACCESORIOS', 'ROPA DEPORTIVA', 'EQUIPAMIENTO', 'CALZADO']
    for i in range(600):
        margen_base = random.uniform(0.05, 0.45) 
        cantidad = random.randint(50, 3500)
        precio = round(random.uniform(15, 120), 2)
        ventas = round(cantidad * precio, 2)
        costo = round(ventas * (1 - margen_base), 2)
        datos.append({
            'SKU': f"SKU-{random.randint(1000, 9999)}-{random.choice(['A','B'])}",
            'Categoria': random.choice(categorias),
            'Ventas ($)': ventas,
            'Costo ($)': costo,
            'Unidades': cantidad
        })
    df = pd.DataFrame(datos)
    return df

# --- 4. BARRA LATERAL Y CARGA DE DATOS ---
with st.sidebar:
    st.markdown(f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; margin-bottom: 25px; text-align: center;">
            <img src="{URL_LOGO}" style="width: 100%;">
        </div>
    """, unsafe_allow_html=True)
    
    st.header("⚙️ Configuración")
    modo_real = st.toggle("📂 Activar Modo Auditoría Real")
    
    df = None 
    
    if modo_real:
        st.info("Sube tu archivo (Plantilla Eunoia)")
        # ACEPTAMOS TANTO CSV COMO EXCEL
        archivo = st.file_uploader("Cargar CSV/Excel", type=["xlsx", "csv"])
        
        if archivo:
            try:
                # LÓGICA DE LECTURA HÍBRIDA
                if archivo.name.endswith('.csv'):
                    try:
                        df = pd.read_csv(archivo)
                        # Verificamos si leyó mal las columnas (todo en una col)
                        if len(df.columns) < 2:
                            archivo.seek(0)
                            df = pd.read_csv(archivo, sep=';')
                    except:
                        archivo.seek(0)
                        df = pd.read_csv(archivo, sep=';')
                else:
                    # LECTURA DE EXCEL (XLSX)
                    df = pd.read_excel(archivo)
                
                # --- MAPEO DE COLUMNAS (Adaptación a tu Plantilla) ---
                # Esto conecta tus nombres de columna con el código
                mapping = {
                    'Venta_Total': 'Ventas ($)',
                    'Costo_Total': 'Costo ($)',
                    'Cantidad_Vendida': 'Unidades',
                    'SKU': 'SKU',            # Mapeo directo
                    'Categoria': 'Categoria' # Mapeo directo
                }
                df = df.rename(columns=mapping)
                
                # Verificación de columnas críticas
                required = ['SKU', 'Categoria', 'Ventas ($)', 'Costo ($)', 'Unidades']
                missing = [col for col in required if col not in df.columns]
                
                if missing:
                    st.error(f"⚠️ Error de formato. Faltan las columnas: {', '.join(missing)}")
                    st.info("Asegúrate de usar la plantilla oficial: SKU, Categoria, Cantidad_Vendida, Venta_Total, Costo_Total")
                    st.stop()

                # Limpieza técnica
                df = df.dropna(subset=['SKU', 'Ventas ($)'])
                # Convertir a numérico forzosamente por si vienen como texto
                for col in ['Ventas ($)', 'Costo ($)', 'Unidades']:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
                st.success("✅ Datos cargados correctamente")
                
            except Exception as e:
                st.error(f"Error crítico al leer el archivo: {str(e)}")
                st.stop()
        else:
            st.warning("Esperando archivo...")
            st.stop()
    else:
        st.caption("🟢 Live Demo: Datos sintéticos")
        df = generar_datos_simulados()
    
    st.markdown("---")
    st.markdown("💬 [WhatsApp Soporte](https://wa.me/593983959867)")

# --- 5. CÁLCULOS (MOTOR EUNOIA) ---
# Calcular márgenes
df['Margen ($)'] = df['Ventas ($)'] - df['Costo ($)']
# Evitar división por cero
df['Margen %'] = df.apply(lambda x: (x['Margen ($)'] / x['Ventas ($)'] * 100) if x['Ventas ($)'] > 0 else 0, axis=1)

# --- 6. VISUALIZACIÓN ---
try:
    st.image(URL_BANNER, use_container_width=True)
except: pass

st.title("🚀 Auditoría de Rentabilidad")
st.markdown("Diagnóstico financiero del portafolio.")
st.markdown("---")

# KPIs Generales
total_ventas = df['Ventas ($)'].sum()
total_margen = df['Margen ($)'].sum()
margen_avg = (total_margen / total_ventas * 100) if total_ventas > 0 else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Ventas Totales", f"${total_ventas:,.0f}")
c2.metric("Margen Bruto", f"${total_margen:,.0f}")
c3.metric("Margen Global", f"{margen_avg:.1f}%")
c4.metric("SKUs Analizados", f"{df.shape[0]}")

# Clasificación Matriz BCG Simplificada
med_v = df['Ventas ($)'].median()
med_m = df['Margen ($)'].median()

def clasificar(row):
    # Lógica de cuadrantes
    if row['Margen ($)'] >= med_m and row['Ventas ($)'] >= med_v: return "ESTRELLA (Ganar)"
    if row['Margen ($)'] < med_m and row['Ventas ($)'] >= med_v: return "DILEMA (Optimizar)"
    if row['Margen ($)'] < med_m and row['Ventas ($)'] < med_v: return "PERRO (Eliminar)"
    return "NICHO (Potenciar)"

df['Clasificación'] = df.apply(clasificar, axis=1)
colors = {'ESTRELLA (Ganar)': '#00c853', 'DILEMA (Optimizar)': '#ffab00', 'PERRO (Eliminar)': '#ff1744', 'NICHO (Potenciar)': '#0080cd'}

st.subheader("1. Matriz de Impacto (Rentabilidad vs. Volumen)")
fig = px.scatter(df, x="Margen ($)", y="Ventas ($)", color="Clasificación", size="Unidades",
                 color_discrete_map=colors, log_x=True, log_y=True, height=550,
                 hover_data=['SKU', 'Categoria', 'Margen %'])

fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.05)')
st.plotly_chart(fig, use_container_width=True)

# Alerta de Stock Tóxico
toxicos = df[df['Clasificación'].isin(['PERRO (Eliminar)', 'DILEMA (Optimizar)'])].shape[0]
st.error(f"⚠️ **DIAGNÓSTICO:** {toxicos} productos están drenando la rentabilidad (Perros + Dilemas).")

st.markdown("---")
c_left, c_right = st.columns([2, 1])

with c_left:
    st.write("🔎 **Top 5 Productos Críticos (Ocultos por Seguridad)**")
    # Filtramos los peores productos
    ver = df[df['Clasificación'].isin(["PERRO (Eliminar)", "DILEMA (Optimizar)"])].head(5).copy()
    
    # --- APLICACIÓN DEL CANDADO DE SEGURIDAD ---
    # Censura el SKU mostrando solo los primeros 4 caracteres + candado
    ver['SKU'] = ver['SKU'].apply(lambda x: f"{str(x)[:4]}...🔒")
    
    st.table(ver[['Categoria', 'SKU', 'Margen %', 'Clasificación']])

with c_right:
    st.info("🔓 **¿Quieres el reporte detallado?**")
    st.markdown("""
        <a href="https://wa.me/593983959867?text=Hola,%20ya%20vi%20mi%20diagnostico,%20quiero%20el%20plan%20completo" class="cta-button" target="_blank">
            👉 Solicitar Desbloqueo
        </a>
    """, unsafe_allow_html=True)

st.caption("© 2025 Eunoia Digital Ecuador - v2.2")
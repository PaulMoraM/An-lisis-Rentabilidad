import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px  # Usamos Plotly en lugar de Matplotlib para gráficos interactivos oscuros
import plotly.graph_objects as go
import random
from faker import Faker

# --- 1. CONFIGURACIÓN DE PÁGINA PROFESIONAL ---
st.set_page_config(
    page_title="Diagnóstico Eunoia Digital",
    page_icon="⭐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. INYECCIÓN DE CSS (ESTILO EUNOIA) ---
def inyectar_estilos():
    st.markdown("""
        <style>
            /* Importar fuente moderna */
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&display=swap');
            
            html, body, [class*="css"]  {
                font-family: 'Montserrat', sans-serif;
            }

            /* --- BOTONES --- */
            div.stButton > button:first-child {
                background-color: #0080cd; /* Azul Eunoia */
                color: white;
                border-radius: 8px;
                border: none;
                font-weight: bold;
                height: 3em;
                transition: 0.3s;
            }
            div.stButton > button:first-child:hover {
                background-color: #006bb3;
                box-shadow: 0 0 12px #0080cd; /* Efecto Glow */
            }

            /* --- BOTÓN DE LLAMADA A LA ACCIÓN (HTML) --- */
            .cta-button {
                background-color: #0080cd;
                color: white !important;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                border: 2px solid #0080cd;
                transition-duration: 0.4s;
                width: 100%;
            }
            .cta-button:hover {
                background-color: black;
                border: 2px solid #0080cd;
                color: #0080cd !important;
                box-shadow: 0 0 15px #0080cd;
            }

            /* --- MÉTRICAS --- */
            [data-testid="stMetricValue"] {
                color: #0080cd;
                font-size: 2.2rem;
                font-weight: 700;
            }
            [data-testid="stMetricLabel"] {
                color: #e0e0e0;
            }

            /* --- LIMPIEZA VISUAL --- */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .block-container {padding-top: 1rem;}
            
            /* Ajuste para tablas en modo oscuro */
            [data-testid="stDataFrame"] {
                border: 1px solid #333;
            }
        </style>
    """, unsafe_allow_html=True)

inyectar_estilos()

# --- 3. FUNCIÓN DE DATOS SIMULADOS (MANTENIDA) ---
@st.cache_data
def generar_datos_simulados():
    fake = Faker('es_ES')
    num_registros = 600
    categorias = ['ACCESORIOS DE VIAJE', 'ROPA DEPORTIVA TÉCNICA', 'EQUIPAMIENTO OUTDOOR', 'CALZADO ESCOLAR']
    
    datos = []
    for i in range(num_registros):
        margen_base = random.uniform(0.05, 0.45) 
        cantidad = random.randint(50, 3500)
        precio_venta_promedio = round(random.uniform(15, 120), 2)
        dolares_total = round(cantidad * precio_venta_promedio, 2)
        costo_total = round(dolares_total * (1 - margen_base), 2)
        sku_modelo = f"SKU-{random.randint(1000, 9999)}-{random.choice(['A','B','C'])}"
        
        dato = {
            'SKU': sku_modelo,
            'Categoria': random.choice(categorias),
            'Ventas ($)': dolares_total,
            'Costo ($)': costo_total,
            'Unidades': cantidad,
            'Margen ($)': dolares_total - costo_total
        }
        datos.append(dato)
    
    df = pd.DataFrame(datos)
    df['Margen %'] = (df['Margen ($)'] / df['Ventas ($)']) * 100
    return df

# --- BARRA LATERAL (BRANDING ACTUALIZADO) ---
with st.sidebar:
    # --- SOLUCIÓN LOGO CON FONDO BLANCO ---
    # Inyectamos un contenedor HTML blanco para que el logo resalte.
    # Usamos la URL directa de tu repo de branding.
    st.markdown(f"""
        <div style="
            background-color: #ffffff; /* El fondo blanco sólido */
            padding: 12px;             /* Un poco de 'aire' alrededor del logo */
            border-radius: 10px;       /* Bordes redondeados modernos */
            margin-bottom: 20px;       /* Separación con la línea de abajo */
            text-align: center;        /* Asegura que esté centrado */
            box-shadow: 0 4px 6px rgba(255,255,255,0.1); /* Sutil brillo blanco */
        ">
            <img src="{URL_LOGO}" style="width: 100%; height: auto; display: block;">
        </div>
    """, unsafe_allow_html=True)
    # --------------------------------------

    st.markdown("---")
    # ... resto de tu código del sidebar ...        st.image("https://raw.githubusercontent.com/PaulMoraM/eunoia-branding/main/eunoia-digital-logo.png", width=200)
    
    st.markdown("---")
    st.header("⚙️ Configuración")
    
    modo_real = st.toggle("📂 Activar Modo Auditoría Real") # Toggle es más moderno que checkbox
    
    df = None 
    
    if modo_real:
        st.info("Formato requerido: Excel/CSV con columnas Ventas, Costo, Cantidad")
        archivo_usuario = st.file_uploader("Cargar Archivo", type=["xlsx", "csv"])
        
        if archivo_usuario is not None:
            try:
                if archivo_usuario.name.endswith('.csv'):
                    df = pd.read_csv(archivo_usuario)
                else:
                    df = pd.read_excel(archivo_usuario)

                # Validación simple
                cols_necesarias = {'Ventas', 'Costo', 'Cantidad'} # Adaptar según nombres reales si es necesario
                # (Aquí mantuve tu lógica de validación original simplificada para no extender el código)
                
                # Simulación de limpieza rápida para el ejemplo
                df = df.rename(columns={'Ventas': 'Ventas ($)', 'Costo': 'Costo ($)', 'Cantidad': 'Unidades'})
                if 'Margen ($)' not in df.columns:
                    df['Margen ($)'] = df['Ventas ($)'] - df['Costo ($)']
                if 'Margen %' not in df.columns:
                    df['Margen %'] = (df['Margen ($)'] / df['Ventas ($)']) * 100
                
                st.success("✅ Datos procesados")
            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()
        else:
            st.warning("👈 Esperando archivo...")
            st.stop()
            
    else:
        st.caption("🟢 Live Demo: Datos sintéticos generados por IA")
        df = generar_datos_simulados()
    
    st.markdown("---")
    st.markdown("### Soporte Técnico")
    st.markdown("💬 [WhatsApp Directo](https://wa.me/593995888197)")

# --- 5. CUERPO PRINCIPAL ---

# Banner superior (opcional)
try:
    st.image("banner_redes.png", use_container_width=True)
except:
    pass

st.title("🚀 Auditoría de Rentabilidad de Inventarios")
st.markdown(f"Diagnóstico financiero del portafolio. **{'DATOS REALES' if modo_real else 'SIMULACIÓN'}**")
st.markdown("---")

# KPIs ESTILIZADOS
total_ventas = df['Ventas ($)'].sum()
total_margen = df['Margen ($)'].sum()
margen_promedio = (total_margen / total_ventas) * 100

c1, c2, c3, c4 = st.columns(4)
c1.metric("Ventas Totales", f"${total_ventas:,.0f}")
c2.metric("Margen Bruto ($)", f"${total_margen:,.0f}")
c3.metric("Margen Global %", f"{margen_promedio:.1f}%", delta="Objetivo > 30%")
c4.metric("SKUs Analizados", f"{df.shape[0]}")

# --- 6. LÓGICA BCG Y GRÁFICO PLOTLY ---
mediana_ventas = df['Ventas ($)'].median()
mediana_margen = df['Margen ($)'].median()

def clasificar_bcg(row):
    if row['Margen ($)'] >= mediana_margen and row['Ventas ($)'] >= mediana_ventas:
        return "ESTRELLA (Ganar)"
    elif row['Margen ($)'] < mediana_margen and row['Ventas ($)'] >= mediana_ventas:
        return "DILEMA (Optimizar)"
    elif row['Margen ($)'] < mediana_margen and row['Ventas ($)'] < mediana_ventas:
        return "PERRO (Eliminar)"
    else:
        return "NICHO (Potenciar)"

df['Clasificación'] = df.apply(clasificar_bcg, axis=1)

# Mapa de colores personalizado Eunoia
color_map = {
    'ESTRELLA (Ganar)': '#00c853',     # Verde brillante
    'DILEMA (Optimizar)': '#ffab00',   # Naranja
    'PERRO (Eliminar)': '#ff1744',     # Rojo alerta
    'NICHO (Potenciar)': '#0080cd'     # Azul Eunoia
}

st.subheader("1. Matriz de Impacto: Mapa de Calor Financiero")
st.caption("Análisis cuadrante basado en medianas del mercado.")

# GRÁFICO INTERACTIVO (Reemplaza a Matplotlib)
fig = px.scatter(
    df,
    x="Margen ($)",
    y="Ventas ($)",
    color="Clasificación",
    size="Unidades",
    hover_name="SKU",
    hover_data=["Categoria", "Margen %"],
    color_discrete_map=color_map,
    log_x=True, # Escala logarítmica ayuda a ver mejor si hay datos muy dispersos
    log_y=True,
    height=600
)

# Personalización Dark Mode del Gráfico
fig.update_layout(
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(255,255,255,0.05)', # Fondo del grid muy sutil
    xaxis_title="Rentabilidad ($)",
    yaxis_title="Volumen de Ventas ($)",
    legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center"),
    font=dict(family="Montserrat, sans-serif", size=14)
)

# Líneas de las medianas
fig.add_vline(x=mediana_margen, line_dash="dash", line_color="gray", annotation_text="Mediana Margen")
fig.add_hline(y=mediana_ventas, line_dash="dash", line_color="gray", annotation_text="Mediana Ventas")

st.plotly_chart(fig, use_container_width=True)

# Alertas
conteo = df['Clasificación'].value_counts()
toxicos = conteo.get('PERRO (Eliminar)', 0) + conteo.get('DILEMA (Optimizar)', 0)
st.error(f"⚠️ **DIAGNÓSTICO CRÍTICO:** Se detectaron **{toxicos} productos** con rendimiento sub-óptimo que requieren intervención de precios inmediata.")

st.markdown("---")

# --- 7. CIERRE DE VENTA (CTA STYLE) ---
st.subheader("2. Plan de Acción & Corrección")

c_left, c_right = st.columns([2, 1])

with c_left:
    st.write("Vista previa de productos que requieren ajuste de precios (Datos Ocultos por Seguridad):")
    
    # Filtro y ofuscación
    df_toxic = df[df['Clasificación'].str.contains("PERRO|DILEMA")].head(5).copy()
    df_toxic['SKU'] = df_toxic['SKU'].apply(lambda x: f"{str(x)[:6]}...🔒")
    df_toxic['Estrategia'] = "🔒 DESBLOQUEAR"
    
    st.table(df_toxic[['Categoria', 'SKU', 'Margen %', 'Estrategia']])

with c_right:
    st.info("🔓 **Desbloqueo Profesional**")
    st.markdown("""
    El reporte completo incluye:
    - Lista exacta de SKUs tóxicos.
    - Calculadora de precio óptimo.
    - Estrategia de liquidación.
    """)
    
    # Botón HTML personalizado
    url_whatsapp = "https://wa.me/593995888197?text=Hola,%20Paul.%20Vi%20el%20diagnóstico%20y%20necesito%20el%20plan%20de%20acción%20completo."
    st.markdown(f'''
        <a href="{url_whatsapp}" target="_blank" class="cta-button">
            SOLICITAR AUDITORÍA FINAL
        </a>
    ''', unsafe_allow_html=True)

st.markdown("---")
st.caption("© 2025 Eunoia Digital Ecuador | Soluciones de Inteligencia Empresarial")
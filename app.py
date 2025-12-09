import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import random
from faker import Faker

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Diagnóstico Eunoia Digital",
    page_icon="📊",
    layout="wide"
)

# Estilos CSS para ocultar elementos innecesarios y dar estilo a los botones
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6
    }
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/270/270023.png", width=100) # Icono genérico de gráfico
    st.title("Eunoia Digital")
    st.markdown("---")
    st.write("**Simulador de Rentabilidad**")
    st.info("""
    Esta herramienta demuestra cómo nuestro algoritmo clasifica miles de productos en segundos.
    
    Los datos mostrados aquí son **simulados** para fines demostrativos.
    """)
    st.markdown("---")
    st.write("¿Quieres este análisis con tus datos reales?")
    st.markdown("[**Contactar por WhatsApp**](https://wa.me/593995888197?text=Hola%20Paul,%20vi%20la%20demo%20y%20quiero%20analizar%20mi%20negocio)")

# --- 3. GENERACIÓN DE DATOS (Faker) ---
@st.cache_data
def generar_datos_simulados():
    fake = Faker('es_ES')
    UMBRAL_CANTIDAD = 100
    num_registros = 600 # Aumentamos un poco para volumen
    categorias = ['ACCESORIOS DE VIAJE', 'ROPA DEPORTIVA TÉCNICA', 'EQUIPAMIENTO OUTDOOR', 'CALZADO ESCOLAR']
    
    datos = []
    for i in range(num_registros):
        margen_base = random.uniform(0.05, 0.45) # Variabilidad de margen
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
    # Calcular Margen %
    df['Margen %'] = (df['Margen ($)'] / df['Ventas ($)']) * 100
    return df

# Cargar la data
df = generar_datos_simulados()

# --- 4. CUERPO PRINCIPAL DEL INFORME ---

st.title("🚀 Auditoría de Rentabilidad de Inventarios")
st.markdown("### Diagnóstico de Salud Financiera del Portafolio")
st.write("A continuación visualizamos cómo se distribuye el capital de una empresa típica del sector Retail.")

# Métricas Globales (KPIs)
col1, col2, col3 = st.columns(3)
col1.metric("Ventas Totales Analizadas", f"${df['Ventas ($)'].sum():,.0f}")
col2.metric("Margen Total Capturado", f"${df['Margen ($)'].sum():,.0f}")
col3.metric("SKUs (Productos) Evaluados", f"{df.shape[0]}")

st.markdown("---")

# --- 5. LÓGICA DE NEGOCIO (Clasificación BCG) ---
mediana_ventas = df['Ventas ($)'].median()
mediana_margen = df['Margen ($)'].median()

# Clasificación
def clasificar_bcg(row):
    if row['Margen ($)'] >= mediana_margen and row['Ventas ($)'] >= mediana_ventas:
        return "ESTRELLA (Ganancia y Volumen)"
    elif row['Margen ($)'] < mediana_margen and row['Ventas ($)'] >= mediana_ventas:
        return "DILEMA (Alto Volumen / Bajo Margen)"
    elif row['Margen ($)'] < mediana_margen and row['Ventas ($)'] < mediana_ventas:
        return "PERRO (Bajo Volumen / Bajo Margen)"
    else:
        return "NICHO (Alto Margen / Bajo Volumen)"

df['Clasificación'] = df.apply(clasificar_bcg, axis=1)

# Contar cuántos hay de cada uno
resumen_clasificacion = df['Clasificación'].value_counts()

# --- 6. VISUALIZACIÓN DE IMPACTO (El Gancho) ---
st.subheader("1. Matriz de Impacto: ¿Dónde está atrapado su dinero?")
st.markdown("Cada punto representa un producto. Los colores indican su salud financiera.")

fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(
    data=df, 
    x='Margen ($)', 
    y='Ventas ($)', 
    hue='Clasificación',
    size='Unidades',
    sizes=(20, 200),
    palette={'ESTRELLA (Ganancia y Volumen)': 'green', 
             'DILEMA (Alto Volumen / Bajo Margen)': 'orange',
             'PERRO (Bajo Volumen / Bajo Margen)': 'red',
             'NICHO (Alto Margen / Bajo Volumen)': 'blue'},
    alpha=0.6,
    ax=ax
)
# Líneas de corte
ax.axvline(mediana_margen, color='grey', linestyle='--')
ax.axhline(mediana_ventas, color='grey', linestyle='--')
ax.set_title("Mapa de Calor de Rentabilidad (BCG Proxy)", fontsize=12)
st.pyplot(fig)

st.success(f"✅ El algoritmo ha detectado **{resumen_clasificacion.get('ESTRELLA (Ganancia y Volumen)', 0)} productos Estrella** que sostienen el negocio.")
st.error(f"⚠️ **ALERTA CRÍTICA:** Se han detectado **{resumen_clasificacion.get('PERRO (Bajo Volumen / Bajo Margen)', 0) + resumen_clasificacion.get('DILEMA (Alto Volumen / Bajo Margen)', 0)} Productos Tóxicos** (Categorías Perro y Dilema) que están consumiendo flujo de caja.")

st.markdown("---")

# --- 7. EL "PAYWALL" ESTRATÉGICO (Cierre de Venta) ---
st.subheader("2. Detalle de Acciones Sugeridas")

col_left, col_right = st.columns([2, 1])

with col_left:
    st.write("En una Auditoría completa, usted recibiría el listado exacto de estos productos con acciones recomendadas:")
    
    # Tabla "Falsa" o borrosa (Solo mostramos estructura, no datos reales valiosos)
    st.markdown("**Vista previa del formato de entrega (Datos Ocultos por Seguridad):**")
    
    # Creamos un dataframe de ejemplo con datos censurados
    df_preview = df[df['Clasificación'].str.contains("DILEMA")].head(5).copy()
    df_preview['SKU'] = "🔒 BLOQUEADO"
    df_preview['Acción Recomendada'] = "🔒 REQUIE CONSULTORÍA"
    df_preview = df_preview[['Categoria', 'SKU', 'Ventas ($)', 'Margen %', 'Acción Recomendada']]
    
    st.table(df_preview)

with col_right:
    st.warning("🔓 **Desbloqueo de Información**")
    st.write("¿Quiere saber exactamente cuáles son sus productos tóxicos y cómo corregir el precio?")
    
    st.markdown("### Su diagnóstico incluye:")
    st.markdown("""
    - 📋 Lista detallada de SKUs a liquidar.
    - 💲 Estrategia de precios nuevos.
    - 📉 Proyección de recuperación de caja.
    """)
    
    # BOTÓN DE LLAMADA A LA ACCIÓN (CTA)
    url_whatsapp = "https://wa.me/593995888197?text=Hola%20Paul,%20quiero%20agendar%20mi%20Diagnóstico%20Express%20de%2048%20horas."
    st.markdown(f'<a href="{url_whatsapp}" target="_blank"><button>SOLICITAR AUDITORÍA AHORA</button></a>', unsafe_allow_html=True)

st.markdown("---")
st.caption("© 2025 Eunoia Digital Ecuador - Soluciones de Inteligencia de Negocios")
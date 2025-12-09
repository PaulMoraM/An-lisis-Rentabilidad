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

# Estilos CSS
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
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. FUNCIÓN DE DATOS SIMULADOS (MODO DEMO) ---
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

# --- 3. BARRA LATERAL (LÓGICA HÍBRIDA) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/270/270023.png", width=80)
    st.title("Eunoia Digital")
    st.markdown("---")
    
    # INTERRUPTOR: MODO REAL VS DEMO
    modo_real = st.checkbox("📂 Activar Modo Auditoría (Cargar Datos Reales)")
    
    df = None # Inicializamos variable
    
    if modo_real:
        st.warning("⚠️ Modo Real Activado")
        st.info("El archivo debe tener las columnas: SKU, Categoria, Ventas, Costo, Cantidad")
        archivo_usuario = st.file_uploader("Sube el Excel de Ventas", type=["xlsx", "csv"])
        
        if archivo_usuario is not None:
            try:
                if archivo_usuario.name.endswith('.csv'):
                    df = pd.read_csv(archivo_usuario)
                else:
                    df = pd.read_excel(archivo_usuario)

                # Validación simple de columnas
                cols_necesarias = {'Ventas', 'Costo', 'Cantidad'}
                if set(df.columns).issuperset(cols_necesarias):
                    # Renombrar para estandarizar
                    df = df.rename(columns={
                        'Ventas': 'Ventas ($)',
                        'Costo': 'Costo ($)',
                        'Cantidad': 'Unidades'
                    })
                    # Cálculos
                    df['Margen ($)'] = df['Ventas ($)'] - df['Costo ($)']
                    df['Margen %'] = (df['Margen ($)'] / df['Ventas ($)']) * 100
                    st.success("✅ Datos cargados con éxito")
                else:
                    st.error("❌ Faltan columnas requeridas (Ventas, Costo, Cantidad)")
                    st.stop()
            except Exception as e:
                st.error(f"Error al leer archivo: {e}")
                st.stop()
        else:
            st.info("👈 Sube un archivo para comenzar.")
            st.stop()
            
    else:
        # MODO DEMO
        st.write("**Modo Simulación Activo**")
        st.caption("Mostrando datos generados por IA para demostración.")
        df = generar_datos_simulados()
        
    st.markdown("---")
    st.markdown("### ¿Necesitas ayuda?")
    st.markdown("[**Contactar Soporte**](https://wa.me/593995888197)")


# --- 4. CUERPO PRINCIPAL DEL INFORME ---

st.title("🚀 Auditoría de Rentabilidad de Inventarios")

if modo_real:
    st.markdown("### 🔍 Análisis de Datos Reales")
else:
    st.markdown("### 🎓 Simulador de Diagnóstico (Datos Ficticios)")

st.write("Visualización de la salud financiera del portafolio de productos.")

# Métricas Globales (KPIs)
col1, col2, col3 = st.columns(3)
col1.metric("Ventas Totales", f"${df['Ventas ($)'].sum():,.0f}")
col2.metric("Margen Total", f"${df['Margen ($)'].sum():,.0f}")
col3.metric("SKUs Evaluados", f"{df.shape[0]}")

st.markdown("---")

# --- 5. LÓGICA BCG ---
mediana_ventas = df['Ventas ($)'].median()
mediana_margen = df['Margen ($)'].median()

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
resumen = df['Clasificación'].value_counts()

# --- 6. GRÁFICO DE IMPACTO ---
st.subheader("1. Matriz de Impacto: ¿Dónde está atrapado su dinero?")
st.markdown("Cada punto es un producto. Los colores indican su salud financiera.")

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
ax.axvline(mediana_margen, color='grey', linestyle='--')
ax.axhline(mediana_ventas, color='grey', linestyle='--')
ax.set_title("Mapa de Calor de Rentabilidad", fontsize=12)
st.pyplot(fig)

# Alertas
toxicos = resumen.get('PERRO (Bajo Volumen / Bajo Margen)', 0) + resumen.get('DILEMA (Alto Volumen / Bajo Margen)', 0)
st.error(f"⚠️ **ALERTA CRÍTICA:** Se han detectado **{toxicos} Productos Tóxicos** que consumen recursos sin aportar ganancia real.")

st.markdown("---")

# --- 7. CIERRE DE VENTA (PAYWALL) ---
st.subheader("2. Plan de Acción Recomendado")

col_left, col_right = st.columns([2, 1])

with col_left:
    st.write("Muestra de productos que requieren intervención inmediata:")
    
    # Tabla censurada intencionalmente
    df_preview = df[df['Clasificación'].str.contains("DILEMA|PERRO", regex=True)].head(5).copy()
    
    # Si es modo real, también ocultamos para forzar la consultoría
    df_preview['SKU'] = df_preview['SKU'].apply(lambda x: f"{str(x)[:4]}...🔒")
    df_preview['Acción'] = "🔒 REQUIERE AUDITORÍA"
    
    st.table(df_preview[['Categoria', 'SKU', 'Ventas ($)', 'Margen %', 'Acción']])

with col_right:
    st.warning("🔓 **Desbloquear Informe Completo**")
    st.markdown("""
    Para obtener el listado exacto de los SKUs tóxicos y la **estrategia de precios** corregida:
    
    1. Agende su Auditoría Express.
    2. Reciba el plan de liquidación.
    3. Recupere flujo de caja en 30 días.
    """)
    
    url_whatsapp = "https://wa.me/593995888197?text=Hola%20Paul,%20ya%20vi%20el%20diagnóstico%20y%20quiero%20el%20plan%20de%20acción%20para%20mis%20productos."
    st.markdown(f'<a href="{url_whatsapp}" target="_blank"><button>SOLICITAR SOLUCIÓN AHORA</button></a>', unsafe_allow_html=True)

st.markdown("---")
st.caption("© 2025 Eunoia Digital Ecuador")
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
    st.markdown("### 🔍 Análisis de Datos Re
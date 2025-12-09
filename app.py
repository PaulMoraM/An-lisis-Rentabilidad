# -*- coding: utf-8 -*-
"""
Created on Tue Dec  9 09:44:28 2025

@author: indu_analistanegocio
"""

import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import random
from faker import Faker

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Diagnóstico Eunoia Digital", layout="wide")

st.title("🚀 Informe de Optimización de Rentabilidad")
st.markdown("""
**Introducción: ¿Dónde está el dinero?**
Este análisis se enfoca en la rentabilidad de los productos de mayor impacto financiero para identificar oportunidades de maximización de ganancias.
""")

# --- GENERACIÓN DE DATOS (Con caché para que no cambie al interactuar) ---
@st.cache_data
def generar_datos():
    fake = Faker('es_ES')
    UMBRAL_CANTIDAD = 100
    num_registros = 500
    categorias = ['ACCESORIOS DE VIAJE', 'ROPA DEPORTIVA TÉCNICA', 'EQUIPAMIENTO OUTDOOR']
    
    datos = []
    for i in range(num_registros):
        margen_base = random.uniform(0.1, 0.4)
        cantidad = random.randint(UMBRAL_CANTIDAD, 3000)
        precio_venta_promedio = round(random.uniform(20, 150), 2)
        dolares_total = round(cantidad * precio_venta_promedio * random.uniform(0.95, 1.05), 2)
        costo_total = round(dolares_total * (1 - margen_base), 2)
        sku_modelo = f"{random.randint(100, 999)}{random.choice('ABCD')}"
        
        dato = {
            'Cantidad': cantidad,
            'Dolares': dolares_total,
            'Costo': costo_total,
            'Categoria': random.choice(categorias),
            'SKU': sku_modelo,
            'Precio_Venta': round(dolares_total / cantidad, 2)
        }
        datos.append(dato)
    
    df = pd.DataFrame(datos)
    
    # Cálculos
    df['Margen'] = df['Dolares'] - df['Costo']
    df['MargenPorcentual'] = (df['Margen'] / df['Dolares'].replace(0, np.nan)) * 100
    
    return df

# Cargar datos
df_alto_volumen = generar_datos()

# --- MOSTRAR DATASET INICIAL ---
st.subheader("Dataset Generado (Muestra)")
st.dataframe(df_alto_volumen.head())

# --- RESUMEN POR CATEGORÍA ---
st.subheader("1. Resumen de Rentabilidad por Categoría")
resumen_categoria = df_alto_volumen.groupby('Categoria').agg(
    Ventas_Totales=('Dolares', 'sum'),
    Margen_Total=('Margen', 'sum'),
    Margen_Promedio=('MargenPorcentual', 'mean')
).sort_values('Margen_Promedio', ascending=True)

st.dataframe(resumen_categoria)

# --- MATRIZ BCG (GRÁFICO) ---
st.subheader("2. Matriz de Impacto: Margen vs. Ventas")

# Cálculos para el gráfico
mediana_dolares = df_alto_volumen['Dolares'].median()
mediana_margen_abs = df_alto_volumen['Margen'].median()
UMBRAL_MARGEN = 15.0
toxicos_criticos = df_alto_volumen[df_alto_volumen['MargenPorcentual'] < UMBRAL_MARGEN]
top_5_toxicos = toxicos_criticos.sort_values('MargenPorcentual', ascending=True).head(5)

# Crear figura explícita para Streamlit
fig, ax = plt.subplots(figsize=(12, 8))

sns.scatterplot(
    data=df_alto_volumen,
    x='Margen',
    y='Dolares',
    size='Cantidad',
    hue='Categoria',
    sizes=(50, 500), # Ajusté un poco el tamaño para web
    alpha=0.7,
    palette='viridis',
    ax=ax
)

# Líneas y Textos
ax.axvline(mediana_margen_abs, color='k', linestyle='--', linewidth=2)
ax.axhline(mediana_dolares, color='k', linestyle='--', linewidth=2)

# Etiquetas cuadrantes (Simplificadas para visualización limpia)
ax.text(mediana_margen_abs * 1.1, mediana_dolares * 1.1, 'ESTRELLA (Ganancia)', color='green', weight='bold')
ax.text(mediana_margen_abs * 0.9, mediana_dolares * 1.1, 'DILEMA (Volumen sin Margen)', color='orange', weight='bold', ha='right')
ax.text(mediana_margen_abs * 0.9, mediana_dolares * 0.9, 'PERRO (Revisar)', color='red', weight='bold', ha='right')
ax.text(mediana_margen_abs * 1.1, mediana_dolares * 0.9, 'NICHO (Potencial)', color='blue', weight='bold')

# Anotaciones de tóxicos
for index, row in top_5_toxicos.iterrows():
    ax.annotate(row['SKU'], (row['Margen'], row['Dolares']), color='red', weight='bold', fontsize=8)

st.pyplot(fig) # Comando CLAVE para mostrar el gráfico en web

# --- SEGMENTACIÓN Y DESCARGAS ---
st.subheader("3. Detalle de Oportunidades (Nichos)")
st.write("SKUs con Alto Margen pero Baja Venta:")

nichos = df_alto_volumen[
    (df_alto_volumen['Margen'] >= mediana_margen_abs) & 
    (df_alto_volumen['Dolares'] < mediana_dolares)
].sort_values('Margen', ascending=False)

st.dataframe(nichos.head(10))
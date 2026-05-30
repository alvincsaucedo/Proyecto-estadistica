# ============================================
# APLICACIÓN STREAMLIT - ANÁLISIS DE ENCUESTA
# VERSIÓN MEJORADA CON SELECCIÓN DE VARIABLES
# ============================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go

# Configurar la página
st.set_page_config(
    page_title="Análisis Estadístico - Encuesta Estudiantil",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar estilo
plt.style.use('ggplot')
sns.set_style("whitegrid")

# ============================================
# FUNCIONES AUXILIARES
# ============================================

def limpiar_edad(valor):
    """Limpia y convierte valores de edad"""
    if pd.isna(valor) or valor == "" or valor == " ":
        return np.nan
    try:
        if isinstance(valor, (int, float)):
            if 10 <= float(valor) <= 100:
                return float(valor)
            else:
                return np.nan
        if isinstance(valor, str):
            valor = valor.strip()
            numeros = re.findall(r'\d+', valor)
            if numeros:
                edad = float(numeros[0])
                if 10 <= edad <= 100:
                    return edad
                else:
                    return np.nan
        return np.nan
    except:
        return np.nan

def encontrar_columna(patron, df):
    """Encuentra columnas por patrón"""
    for col in df.columns:
        if patron.lower() in col.lower():
            return col
    return None

def generar_descarga_grafico(fig):
    """Convierte gráfico matplotlib a bytes para descarga"""
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
    buf.seek(0)
    return buf

def clasificar_variable(col_name, df):
    """Clasifica una variable como cualitativa o cuantitativa"""
    # Intentar convertir a numérico
    try:
        pd.to_numeric(df[col_name], errors='raise')
        return "cuantitativa"
    except:
        return "cualitativa"

# ============================================
# TÍTULO
# ============================================

st.title("📊 Laboratorio de Estadística Descriptiva")
st.markdown("### Medidas de Tendencia Central y Análisis de Datos")
st.markdown("---")

# ============================================
# SIDEBAR - CONFIGURACIÓN
# ============================================

with st.sidebar:
    st.markdown("## 📋 Configuración")
    
    # Carga de archivo
    archivo = st.file_uploader(
        "📂 Cargar archivo de datos (.csv):",
        type=['csv'],
        help="Sube tu archivo CSV con los datos de la encuesta"
    )
    
    st.markdown("---")
    st.markdown("### 🎯 Selecciona la fase de análisis:")
    
    fase_analisis = st.radio(
        "",
        ["📊 Panel de Datos Base", "📈 Variables Cualitativas", "🔢 Variables Cuantitativas"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 👨‍🏫 Información")
    st.markdown("**Docente:** Lic. Eduardo Zubieta")
    st.markdown("**UAP - Estadística**")
    
    st.markdown("---")
    st.markdown("### 📝 Instrucciones")
    st.markdown("""
    1. Carga un archivo CSV
    2. Selecciona la fase de análisis
    3. Elige una variable del menú
    4. Visualiza tablas y gráficos
    """)

# ============================================
# CARGA DE DATOS
# ============================================

if archivo is not None:
    try:
        # Leer el archivo CSV
        df = pd.read_csv(archivo)
        
        st.success(f"✅ Archivo cargado correctamente - {len(df)} registros encontrados")
        
        # Limpiar nombres de columnas (remover espacios y caracteres especiales)
        df.columns = df.columns.str.strip()
        
        # Crear una copia limpia para análisis
        df_clean = df.copy()
        
        # Identificar y limpiar columna de edad si existe
        col_edad = encontrar_columna('edad', df_clean)
        if col_edad:
            df_clean['Edad_limpia'] = df_clean[col_edad].apply(limpiar_edad)
        
        # ============================================
        # PANEL DE DATOS BASE
        # ============================================
        
        if fase_analisis == "📊 Panel de Datos Base":
            st.header("📊 Panel de Datos Base")
            
            # Mostrar información del dataset
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total de registros", len(df_clean))
            with col2:
                st.metric("Total de columnas", len(df_clean.columns))
            with col3:
                st.metric("Datos duplicados", df_clean.duplicated().sum())
            with col4:
                st.metric("Variables numéricas", sum(df_clean.dtypes.apply(lambda x: x in ['int64', 'float64'])))
            
            # Mostrar primeras filas
            with st.expander("📋 Ver primeros registros", expanded=True):
                st.dataframe(df_clean.head(10), use_container_width=True)
            
            # Mostrar información de columnas
            with st.expander("ℹ️ Información de columnas", expanded=False):
                info_df = pd.DataFrame({
                    'Variable': df_clean.columns,
                    'Tipo': df_clean.dtypes.values,
                    'Valores nulos': df_clean.isnull().sum().values,
                    'Valores únicos': df_clean.nunique().values
                })
                st.dataframe(info_df, use_container_width=True)
            
            # Mostrar estadísticas básicas de variables numéricas
            numeric_cols = df_clean.select_dtypes(include=['int64', 'float64']).columns
            if len(numeric_cols) > 0:
                with st.expander("📊 Estadísticas de variables numéricas", expanded=False):
                    st.dataframe(df_clean[numeric_cols].describe(), use_container_width=True)
        
        # ============================================
        # VARIABLES CUALITATIVAS
        # ============================================
        
        elif fase_analisis == "📈 Variables Cualitativas":
            st.header("📈 Análisis de Variables Cualitativas")
            
            # Identificar variables cualitativas
            variables_cualitativas = []
            for col in df_clean.columns:
                if clasificar_variable(col, df_clean) == "cualitativa":
                    # Excluir columnas de timestamp y marcas temporales
                    if 'marca' not in col.lower() and 'tiempo' not in col.lower() and 'fecha' not in col.lower():
                        variables_cualitativas.append(col)
            
            if len(variables_cualitativas) > 0:
                # Selector de variable en sidebar
                with st.sidebar:
                    st.markdown("---")
                    st.markdown("### 📌 Selecciona una variable:")
                    var_seleccionada = st.selectbox(
                        "Variables cualitativas disponibles:",
                        variables_cualitativas
                    )
                
                if var_seleccionada:
                    st.markdown(f"### 📊 Análisis de: **{var_seleccionada}**")
                    st.markdown("---")
                    
                    # Limpiar datos
                    datos_var = df_clean[var_seleccionada].copy()
                    datos_var = datos_var.fillna("No especificado")
                    datos_var = datos_var.replace("", "No especificado")
                    
                    # Calcular frecuencias
                    frecuencias = datos_var.value_counts().reset_index()
                    frecuencias.columns = [var_seleccionada, "Frecuencia (fi)"]
                    frecuencias["Porcentaje (%)"] = ((frecuencias["Frecuencia (fi)"] / len(df_clean)) * 100).round(2)
                    frecuencias["Frec. Acumulada (Fi)"] = frecuencias["Frecuencia (fi)"].cumsum()
                    frecuencias["Porcentaje Acum. (%)"] = (frecuencias["Frec. Acumulada (Fi)"] / len(df_clean) * 100).round(2)
                    
                    # Mostrar tabla de frecuencias
                    st.subheader("📋 Tabla de Frecuencias")
                    st.dataframe(frecuencias, use_container_width=True)
                    
                    # Calcular moda
                    moda_valor = frecuencias.iloc[0][var_seleccionada]
                    moda_frecuencia = frecuencias.iloc[0]["Frecuencia (fi)"]
                    moda_porcentaje = frecuencias.iloc[0]["Porcentaje (%)"]
                    
                    st.info(f"⭐ **Moda (valor más frecuente):** {moda_valor} - {moda_frecuencia} respuestas ({moda_porcentaje}%)")
                    
                    # Selección de tipo de gráfico
                    st.subheader("📊 Visualización")
                    tipo_grafico = st.radio(
                        "Selecciona tipo de gráfico:",
                        ["Gráfico de Barras", "Gráfico de Torta"],
                        horizontal=True
                    )
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        if tipo_grafico == "Gráfico de Barras":
                            # Gráfico de barras con Plotly
                            fig = px.bar(
                                frecuencias, 
                                x=var_seleccionada, 
                                y="Frecuencia (fi)",
                                title=f"Distribución de {var_seleccionada}",
                                color="Frecuencia (fi)",
                                color_continuous_scale="Blues",
                                text="Frecuencia (fi)"
                            )
                            fig.update_traces(textposition='outside')
                            fig.update_layout(showlegend=False)
                            st.plotly_chart(fig, use_container_width=True)
                        
                        elif tipo_grafico == "Gráfico de Torta":
                            # Gráfico de torta con Plotly
                            fig = px.pie(
                                frecuencias, 
                                values="Frecuencia (fi)", 
                                names=var_seleccionada,
                                title=f"Distribución Porcentual de {var_seleccionada}",
                                hole=0.3
                            )
                            fig.update_traces(textposition='inside', textinfo='percent+label')
                            st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Mostrar resumen de la moda
                        st.markdown("### 📌 Resumen")
                        st.markdown(f"""
                        **Variable:** {var_seleccionada}
                        
                        **Tipo:** Cualitativa
                        
                        **Categorías:** {len(frecuencias)}
                        
                        **Moda:** {moda_valor}
                        
                        **Frecuencia de la moda:** {moda_frecuencia} ({moda_porcentaje}%)
                        """)
                    
                    # Mostrar todas las categorías
                    with st.expander("📋 Ver todas las categorías", expanded=False):
                        for idx, row in frecuencias.iterrows():
                            st.markdown(f"• **{row[var_seleccionada]}**: {row['Frecuencia (fi)']} ({row['Porcentaje (%)']}%)")
            else:
                st.warning("⚠️ No se detectaron variables cualitativas en el archivo")
        
        # ============================================
        # VARIABLES CUANTITATIVAS
        # ============================================
        
        elif fase_analisis == "🔢 Variables Cuantitativas":
            st.header("🔢 Análisis de Variables Cuantitativas")
            
            # Identificar variables cuantitativas
            variables_cuantitativas = []
            for col in df_clean.columns:
                if clasificar_variable(col, df_clean) == "cuantitativa":
                    # Excluir IDs y columnas de edad limpia si ya existe la original
                    if 'id' not in col.lower() and col != 'Edad_limpia':
                        variables_cuantitativas.append(col)
            
            # Añadir edad limpia si existe
            if 'Edad_limpia' in df_clean.columns and df_clean['Edad_limpia'].notna().sum() > 0:
                if 'Edad_limpia' not in variables_cuantitativas:
                    variables_cuantitativas.append('Edad_limpia')
            
            if len(variables_cuantitativas) > 0:
                # Selector de variable en sidebar
                with st.sidebar:
                    st.markdown("---")
                    st.markdown("### 📌 Selecciona una variable:")
                    var_seleccionada = st.selectbox(
                        "Variables cuantitativas disponibles:",
                        variables_cuantitativas
                    )
                
                if var_seleccionada:
                    st.markdown(f"### 📊 Análisis de: **{var_seleccionada}**")
                    st.markdown("---")
                    
                    # Limpiar datos
                    datos_var = df_clean[var_seleccionada].dropna()
                    
                    if len(datos_var) > 0:
                        # Calcular medidas de tendencia central
                        media = datos_var.mean()
                        mediana = datos_var.median()
                        moda = datos_var.mode()
                        moda_valor = moda.iloc[0] if len(moda) > 0 else "N/A"
                        desviacion = datos_var.std()
                        varianza = datos_var.var()
                        minimo = datos_var.min()
                        maximo = datos_var.max()
                        rango = maximo - minimo
                        
                        # Mostrar tarjetas de medidas
                        st.subheader("📈 Medidas de Tendencia Central")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("📊 Media", f"{media:.2f}")
                        with col2:
                            st.metric("📈 Mediana", f"{mediana:.2f}")
                        with col3:
                            if isinstance(moda_valor, (int, float)):
                                st.metric("⭐ Moda", f"{moda_valor:.2f}")
                            else:
                                st.metric("⭐ Moda", moda_valor)
                        with col4:
                            st.metric("📉 Desviación Estándar", f"{desviacion:.2f}")
                        
                        # Tabla de estadísticos
                        st.subheader("📋 Resumen de Estadísticos")
                        estadisticos_df = pd.DataFrame({
                            'Medida': ['Media', 'Mediana', 'Moda', 'Mínimo', 'Máximo', 'Rango', 
                                      'Desviación Estándar', 'Varianza', 'Número de Datos'],
                            'Valor': [
                                f"{media:.2f}",
                                f"{mediana:.2f}",
                                f"{moda_valor:.2f}" if isinstance(moda_valor, (int, float)) else moda_valor,
                                f"{minimo:.2f}",
                                f"{maximo:.2f}",
                                f"{rango:.2f}",
                                f"{desviacion:.2f}",
                                f"{varianza:.2f}",
                                len(datos_var)
                            ]
                        })
                        st.dataframe(estadisticos_df, use_container_width=True)
                        
                        # Datos agrupados con regla de Sturges
                        st.subheader("📊 Datos Agrupados (Regla de Sturges)")
                        
                        n = len(datos_var)
                        k = int(np.ceil(1 + 3.322 * np.log10(n)))
                        rango_datos = datos_var.max() - datos_var.min()
                        amplitud = np.ceil(rango_datos / k) if k > 0 else 1
                        
                        st.info(f"**Parámetros:** n={n}, k={k}, Rango={rango_datos:.2f}, Amplitud={amplitud:.2f}")
                        
                        limite_inferior = datos_var.min()
                        limites = [limite_inferior + i * amplitud for i in range(k + 1)]
                        
                        intervalos = pd.cut(datos_var, bins=limites, right=False, include_lowest=True)
                        
                        frec_agrupada = pd.DataFrame()
                        frec_agrupada["Intervalo"] = intervalos.value_counts().sort_index().index.astype(str)
                        frec_agrupada["Frecuencia (fi)"] = intervalos.value_counts().sort_index().values
                        frec_agrupada["Porcentaje (%)"] = ((frec_agrupada["Frecuencia (fi)"] / n) * 100).round(2)
                        frec_agrupada["Frec. Acumulada (Fi)"] = frec_agrupada["Frecuencia (fi)"].cumsum()
                        
                        st.dataframe(frec_agrupada, use_container_width=True)
                        
                        # Selección de gráfico
                        st.subheader("📊 Visualización")
                        tipo_grafico = st.radio(
                            "Selecciona tipo de gráfico:",
                            ["Histograma", "Boxplot", "Histograma + Polígono"],
                            horizontal=True
                        )
                        
                        fig, ax = plt.subplots(figsize=(12, 6))
                        
                        if tipo_grafico == "Histograma":
                            ax.hist(datos_var, bins=k, edgecolor='black', 
                                   color='steelblue', alpha=0.7)
                            ax.axvline(media, color='red', linestyle='--', 
                                      linewidth=2, label=f"Media: {media:.2f}")
                            ax.axvline(mediana, color='green', linestyle='--', 
                                      linewidth=2, label=f"Mediana: {mediana:.2f}")
                            ax.legend()
                            
                        elif tipo_grafico == "Boxplot":
                            ax.boxplot(datos_var, vert=True, patch_artist=True,
                                      boxprops=dict(facecolor='lightblue', color='black'),
                                      medianprops=dict(color='red', linewidth=2))
                            ax.set_xticklabels([var_seleccionada])
                            
                        elif tipo_grafico == "Histograma + Polígono":
                            # Histograma
                            ax.hist(datos_var, bins=limites, edgecolor='black', 
                                   color='lightblue', alpha=0.7, label='Histograma')
                            
                            # Polígono de frecuencias
                            marcas_clase = [(limites[i] + limites[i+1]) / 2 for i in range(k)]
                            frecuencias_val = intervalos.value_counts().sort_index().values
                            ax.plot(marcas_clase, frecuencias_val, 'ro-', linewidth=2, 
                                   markersize=8, label='Polígono')
                            ax.legend()
                        
                        ax.set_title(f'Distribución de {var_seleccionada}', fontsize=14, fontweight='bold')
                        ax.set_xlabel(var_seleccionada, fontsize=12)
                        ax.set_ylabel('Frecuencia', fontsize=12)
                        ax.grid(True, alpha=0.3)
                        
                        st.pyplot(fig)
                        
                        # Botón de descarga
                        buf = generar_descarga_grafico(fig)
                        st.download_button("📥 Descargar gráfico", buf, f"grafico_{var_seleccionada}.png", "image/png")
                        plt.close()
                    else:
                        st.warning(f"No hay datos válidos para la variable {var_seleccionada}")
            else:
                st.warning("⚠️ No se detectaron variables cuantitativas en el archivo")
    
    except Exception as e:
        st.error(f"Error al procesar el archivo: {str(e)}")
        st.info("Asegúrate de que el archivo CSV tenga el formato correcto")

else:
    # Mensaje cuando no hay archivo
    st.info("👈 Por favor, carga un archivo CSV en el panel lateral para comenzar el análisis")
    
    # Mostrar ejemplo
    with st.expander("📋 Ver formato de ejemplo", expanded=True):
        st.markdown("""
        ### Formato esperado del CSV:
        
        Tu archivo debe contener columnas como:
        - **Edad** (ej: 18, 19 años, 20, etc.)
        - **Sexo** (Masculino, Femenino, etc.)
        - **Semestre** (1° Semestre, 3° Semestre, etc.)
        
        ### Ejemplo:
        | Edad | Sexo | Semestre |
        |------|------|----------|
        | 18   | Masculino | 1° Semestre |
        | 19   | Femenino | 3° Semestre |
        | 20   | Masculino | 5° Semestre |
        """)

st.markdown("---")
st.markdown("### 📌 **Docente: Lic. Eduardo Zubieta | UAP**")
st.markdown("✅ **Aplicación lista para usar - Carga tu archivo CSV y comienza el análisis**")
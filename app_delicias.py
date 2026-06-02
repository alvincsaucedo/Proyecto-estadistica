# ============================================
# APLICACIÓN STREAMLIT - DELÍCIAS DEL CIELO
# VERSIÓN COMPLETA CON MEDIDAS Y DESVIACIÓN ESTÁNDAR
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
    page_title="Análisis Estadístico - Delícias Del Cielo",
    page_icon="🍰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar estilo
plt.style.use('ggplot')
sns.set_style("whitegrid")

# ============================================
# FUNCIÓN ESPECIAL PARA LEER CSV CON COMILLAS DOBLES
# ============================================

def leer_csv_comillas_dobles(archivo):
    """Lee específicamente el formato de Delicias_Del_Cielo.csv"""
    try:
        contenido = archivo.getvalue().decode('latin-1')
        lineas = contenido.strip().split('\n')
        
        # Procesar encabezados
        primera_linea = lineas[0]
        encabezados = []
        
        patron = r'""([^""]+)""'
        encabezados_raw = re.findall(patron, primera_linea)
        
        if not encabezados_raw:
            encabezados_raw = re.findall(r'"([^"]+)"', primera_linea)
        
        for h in encabezados_raw:
            h_limpio = h.strip().replace('"', '')
            if 'Marca temporal' not in h_limpio and 'marca' not in h_limpio.lower():
                encabezados.append(h_limpio)
        
        # Procesar datos
        datos = []
        for linea in lineas[1:]:
            if not linea.strip():
                continue
            
            valores = re.findall(r'""([^""]*)""', linea)
            if not valores:
                valores = re.findall(r'"([^"]*)"', linea)
            
            valores_limpios = []
            for v in valores:
                v_limpio = v.strip()
                if v_limpio:
                    valores_limpios.append(v_limpio)
            
            if len(valores_limpios) > 10:
                valores_limpios = valores_limpios[1:11]
            
            if len(valores_limpios) >= 10:
                datos.append(valores_limpios[:10])
        
        if datos and encabezados:
            df = pd.DataFrame(datos, columns=encabezados[:10])
            return df
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def limpiar_texto(valor):
    """Limpia valores de texto"""
    if pd.isna(valor) or valor == "" or valor == " ":
        return "No especificado"
    return str(valor).strip()

def generar_descarga_grafico(fig):
    """Convierte gráfico matplotlib a bytes para descarga"""
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
    buf.seek(0)
    return buf

def clasificar_variable_cualitativa(col_name, df):
    """Clasifica una variable cualitativa como nominal u ordinal"""
    valores_unicos = df[col_name].unique()
    
    palabras_orden = ['excelente', 'bueno', 'regular', 'malo', 'poco', 'muy', 'atractiva', 'adecuado']
    
    tiene_orden = False
    for valor in valores_unicos:
        if isinstance(valor, str):
            valor_lower = valor.lower()
            for palabra in palabras_orden:
                if palabra in valor_lower:
                    tiene_orden = True
                    break
    
    return "Ordinal" if tiene_orden else "Nominal"

def clasificar_variable_cuantitativa(col_name, df):
    """Clasifica una variable cuantitativa como discreta o continua"""
    datos = pd.to_numeric(df[col_name], errors='coerce').dropna()
    
    if len(datos) == 0:
        return "No se puede determinar"
    
    es_entero = all(x.is_integer() for x in datos)
    
    return "Discreta" if es_entero else "Continua"

# ============================================
# TÍTULO
# ============================================

st.title("🍰 Laboratorio de Estadística Descriptiva")
st.markdown("### Análisis de Encuesta - Repostería **Delícias Del Cielo**")
st.markdown("---")

# ============================================
# SIDEBAR - CONFIGURACIÓN
# ============================================

with st.sidebar:
    st.markdown("## 🍰 Delícias Del Cielo")
    st.markdown("### 📋 Configuración")
    
    archivo = st.file_uploader(
        "📂 Cargar archivo de datos (.csv):",
        type=['csv'],
        help="Sube tu archivo CSV con los datos de la encuesta"
    )
    
    st.markdown("---")
    st.markdown("### 🎯 Selecciona la fase de análisis:")
    
    fase_analisis = st.radio(
        "",
        ["📊 Panel de Datos Base", "📈 Variables Cualitativas", "🔢 Variables Cuantitativas", "📊 Dashboard General"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 👨‍🏫 Información")
    st.markdown("**Docente:** Lic. Eduardo Zubieta")
    st.markdown("**UAP - Estadística**")
    st.markdown("**Negocio:** Delícias Del Cielo")
    
    st.markdown("---")
    st.markdown("### 📝 Instrucciones")
    st.markdown("""
    1. Carga el archivo CSV
    2. Selecciona la fase de análisis
    3. Las variables se clasifican automáticamente
    4. Explora las tablas y gráficos
    """)

# ============================================
# CARGA DE DATOS
# ============================================

if archivo is not None:
    try:
        with st.spinner("📂 Procesando archivo..."):
            df = leer_csv_comillas_dobles(archivo)
            
            if df is None:
                st.error("❌ No se pudo leer el archivo.")
                st.stop()
            
            for col in df.columns:
                df[col] = df[col].apply(limpiar_texto)
        
        st.success(f"✅ Archivo cargado correctamente - {len(df)} encuestados")
        
        with st.expander("📋 Ver información del dataset", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de encuestados", len(df))
            with col2:
                st.metric("Total de preguntas", len(df.columns))
            with col3:
                st.metric("Datos completos", df.notna().all(axis=1).sum())
            
            st.markdown("**Primeros registros:**")
            st.dataframe(df.head(), use_container_width=True)
        
        # ============================================
        # PANEL DE DATOS BASE
        # ============================================
        
        if fase_analisis == "📊 Panel de Datos Base":
            st.header("📊 Panel de Datos Base")
            
            st.subheader("📋 Lista de preguntas de la encuesta")
            
            tipo_variable = []
            subtipo = []
            
            for col in df.columns:
                try:
                    pd.to_numeric(df[col], errors='raise')
                    tipo_variable.append("Cuantitativa")
                    subtipo.append(clasificar_variable_cuantitativa(col, df))
                except:
                    tipo_variable.append("Cualitativa")
                    subtipo.append(clasificar_variable_cualitativa(col, df))
            
            preguntas_df = pd.DataFrame({
                'N°': range(1, len(df.columns) + 1),
                'Pregunta': df.columns,
                'Tipo de Variable': tipo_variable,
                'Subtipo': subtipo,
                'Valores únicos': df.nunique().values
            })
            st.dataframe(preguntas_df, use_container_width=True)
            
            st.subheader("📊 Resumen rápido de respuestas")
            for col in df.columns:
                with st.expander(f"📌 {col}"):
                    valores = df[col].value_counts()
                    st.dataframe(valores, use_container_width=True)
        
        # ============================================
        # VARIABLES CUALITATIVAS
        # ============================================
        
        elif fase_analisis == "📈 Variables Cualitativas":
            st.header("📈 Análisis de Variables Cualitativas")
            
            variables_cualitativas = []
            subtipos_cualitativas = []
            
            for col in df.columns:
                try:
                    pd.to_numeric(df[col], errors='raise')
                except:
                    variables_cualitativas.append(col)
                    subtipos_cualitativas.append(clasificar_variable_cualitativa(col, df))
            
            if len(variables_cualitativas) > 0:
                pregunta_seleccionada = st.selectbox(
                    "Selecciona una pregunta para analizar:",
                    variables_cualitativas,
                    format_func=lambda x: f"{variables_cualitativas.index(x)+1}. {x}"
                )
                
                if pregunta_seleccionada:
                    idx = variables_cualitativas.index(pregunta_seleccionada)
                    subtipo = subtipos_cualitativas[idx]
                    
                    st.markdown(f"### 📊 {pregunta_seleccionada}")
                    st.markdown(f"**Tipo de variable:** Cualitativa - **{subtipo}**")
                    st.markdown("---")
                    
                    if subtipo == "Nominal":
                        st.info("📌 **Variable Nominal:** Las categorías no tienen un orden específico")
                    else:
                        st.info("📊 **Variable Ordinal:** Las categorías tienen un orden jerárquico")
                    
                    datos = df[pregunta_seleccionada].copy()
                    datos = datos[datos != "No especificado"]
                    
                    if len(datos) > 0:
                        frecuencias = datos.value_counts()
                        
                        # ============================================
                        # MEDIDAS DE TENDENCIA CENTRAL
                        # ============================================
                        st.subheader("📈 Medidas de Tendencia Central")
                        
                        moda_valor = frecuencias.index[0]
                        moda_frecuencia = frecuencias.values[0]
                        moda_porcentaje = (moda_frecuencia / len(df)) * 100
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("📊 Media", "No aplica")
                        with col2:
                            st.metric("📈 Mediana", "No aplica")
                        with col3:
                            st.metric("⭐ Moda", moda_valor)
                        with col4:
                            st.metric("📉 Desviación Estándar", "No aplica")
                        
                        st.caption(f"📌 La moda aparece {moda_frecuencia} veces ({moda_porcentaje:.1f}% del total)")
                        st.markdown("---")
                        
                        # ============================================
                        # GRÁFICO DE DESVIACIÓN (Para cualitativas: gráfico de barras con línea de moda)
                        # ============================================
                        st.subheader("📊 Gráfico de Distribución")
                        
                        fig, ax = plt.subplots(figsize=(12, 6))
                        colores_barras = plt.cm.Set3(np.linspace(0, 1, len(frecuencias)))
                        barras = ax.bar(range(len(frecuencias)), frecuencias.values, 
                                      color=colores_barras, edgecolor='black', alpha=0.8)
                        
                        # Resaltar la barra de la moda
                        for i, (respuesta, valor) in enumerate(frecuencias.items()):
                            if respuesta == moda_valor:
                                barras[i].set_color('#FF9800')
                                barras[i].set_edgecolor('red')
                                barras[i].set_linewidth(2)
                        
                        ax.set_xticks(range(len(frecuencias)))
                        ax.set_xticklabels(frecuencias.index, rotation=45, ha='right', fontsize=10)
                        ax.set_title(f'Distribución de {pregunta_seleccionada[:50]}\n(La barra naranja representa la MODA)', 
                                    fontsize=14, fontweight='bold')
                        ax.set_ylabel('Frecuencia', fontsize=12)
                        ax.set_xlabel('Respuestas', fontsize=12)
                        
                        # Añadir línea horizontal de referencia (frecuencia promedio)
                        freq_promedio = frecuencias.values.mean()
                        ax.axhline(y=freq_promedio, color='red', linestyle='--', 
                                  linewidth=2, label=f'Frecuencia Promedio: {freq_promedio:.1f}')
                        ax.legend()
                        
                        # Añadir valores en las barras
                        for barra, valor in zip(barras, frecuencias.values):
                            ax.text(barra.get_x() + barra.get_width()/2, barra.get_height() + 0.2,
                                   str(valor), ha='center', va='bottom', fontsize=10, fontweight='bold')
                        
                        plt.tight_layout()
                        st.pyplot(fig)
                        plt.close()
                        
                        # Tabla de frecuencias
                        st.subheader("📋 Tabla de Frecuencias")
                        frec_df = pd.DataFrame({
                            'Respuesta': frecuencias.index,
                            'Frecuencia (fi)': frecuencias.values,
                            'Porcentaje (%)': (frecuencias.values / len(df) * 100).round(2)
                        })
                        frec_df['Frec. Acumulada (Fi)'] = frec_df['Frecuencia (fi)'].cumsum()
                        frec_df['Porc. Acum. (%)'] = (frec_df['Frec. Acumulada (Fi)'] / len(df) * 100).round(2)
                        st.dataframe(frec_df, use_container_width=True)
                        
                        # Gráficos adicionales
                        col1, col2 = st.columns(2)
                        with col1:
                            fig_bar = px.bar(
                                x=frecuencias.index.tolist(),
                                y=frecuencias.values.tolist(),
                                title=f"Gráfico de Barras Interactivo",
                                labels={'x': 'Respuesta', 'y': 'Frecuencia'},
                                color=frecuencias.values.tolist(),
                                color_continuous_scale='Viridis',
                                text=frecuencias.values.tolist()
                            )
                            fig_bar.update_traces(textposition='outside')
                            fig_bar.update_layout(xaxis_tickangle=-45)
                            st.plotly_chart(fig_bar, use_container_width=True)
                        
                        with col2:
                            fig_pie = px.pie(
                                values=frecuencias.values.tolist(),
                                names=frecuencias.index.tolist(),
                                title=f"Distribución porcentual",
                                hole=0.3,
                                color_discrete_sequence=px.colors.qualitative.Set3
                            )
                            st.plotly_chart(fig_pie, use_container_width=True)
                    else:
                        st.warning("No hay datos válidos para esta pregunta")
            else:
                st.warning("⚠️ No se detectaron variables cualitativas en el archivo")
        
        # ============================================
        # VARIABLES CUANTITATIVAS
        # ============================================
        
        elif fase_analisis == "🔢 Variables Cuantitativas":
            st.header("🔢 Análisis de Variables Cuantitativas")
            
            variables_cuantitativas = []
            subtipos_cuantitativas = []
            
            for col in df.columns:
                try:
                    pd.to_numeric(df[col], errors='raise')
                    variables_cuantitativas.append(col)
                    subtipos_cuantitativas.append(clasificar_variable_cuantitativa(col, df))
                except:
                    pass
            
            if len(variables_cuantitativas) > 0:
                var_seleccionada = st.selectbox(
                    "Selecciona una variable numérica:",
                    variables_cuantitativas,
                    format_func=lambda x: f"{variables_cuantitativas.index(x)+1}. {x}"
                )
                
                if var_seleccionada:
                    idx = variables_cuantitativas.index(var_seleccionada)
                    subtipo = subtipos_cuantitativas[idx]
                    
                    st.markdown(f"### 📊 {var_seleccionada}")
                    st.markdown(f"**Tipo de variable:** Cuantitativa - **{subtipo}**")
                    st.markdown("---")
                    
                    if subtipo == "Discreta":
                        st.info("🔢 **Variable Discreta:** Solo toma valores enteros")
                    else:
                        st.info("📈 **Variable Continua:** Puede tomar cualquier valor decimal")
                    
                    datos_var = pd.to_numeric(df[var_seleccionada], errors='coerce').dropna()
                    
                    if len(datos_var) > 0:
                        # ============================================
                        # MEDIDAS DE TENDENCIA CENTRAL
                        # ============================================
                        media = datos_var.mean()
                        mediana = datos_var.median()
                        moda = datos_var.mode()
                        moda_valor = moda.iloc[0] if len(moda) > 0 else "N/A"
                        desviacion = datos_var.std()
                        
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
                        
                        st.caption(f"📌 La desviación estándar indica la dispersión de los datos respecto a la media")
                        st.markdown("---")
                        
                        # ============================================
                        # GRÁFICO DE DESVIACIÓN ESTÁNDAR
                        # ============================================
                        st.subheader("📊 Gráfico de Desviación Estándar")
                        
                        fig, ax = plt.subplots(figsize=(14, 7))
                        
                        # Histograma
                        n_bins = int(np.ceil(1 + 3.322 * np.log10(len(datos_var))))
                        counts, bins, patches = ax.hist(datos_var, bins=n_bins, edgecolor='black', 
                                                        color='steelblue', alpha=0.7, label='Datos')
                        
                        # Línea de la media
                        ax.axvline(media, color='red', linestyle='--', linewidth=2.5, 
                                  label=f'Media = {media:.2f}')
                        
                        # Líneas de desviación estándar
                        ax.axvline(media - desviacion, color='orange', linestyle=':', linewidth=2, 
                                  label=f'-1σ = {media - desviacion:.2f}')
                        ax.axvline(media + desviacion, color='orange', linestyle=':', linewidth=2, 
                                  label=f'+1σ = {media + desviacion:.2f}')
                        
                        # Sombreado del área de desviación
                        ax.axvspan(media - desviacion, media + desviacion, alpha=0.2, color='green', 
                                  label=f'Área de ±1σ ({desviacion*2:.2f})')
                        
                        # Línea de la mediana
                        ax.axvline(mediana, color='green', linestyle='--', linewidth=2, 
                                  label=f'Mediana = {mediana:.2f}')
                        
                        ax.set_title(f'Distribución de {var_seleccionada}\nDesviación Estándar = {desviacion:.2f}', 
                                    fontsize=14, fontweight='bold')
                        ax.set_xlabel(var_seleccionada, fontsize=12)
                        ax.set_ylabel('Frecuencia', fontsize=12)
                        ax.legend(loc='upper right')
                        ax.grid(True, alpha=0.3)
                        
                        plt.tight_layout()
                        st.pyplot(fig)
                        plt.close()
                        
                        # ============================================
                        # INTERPRETACIÓN DE LA DESVIACIÓN ESTÁNDAR
                        # ============================================
                        with st.expander("📖 Interpretación de la Desviación Estándar", expanded=True):
                            if desviacion < (datos_var.max() - datos_var.min()) / 4:
                                st.success(f"✅ **Desviación Estándar Baja ({desviacion:.2f})**: Los datos están concentrados cerca de la media.")
                            elif desviacion < (datos_var.max() - datos_var.min()) / 2:
                                st.warning(f"⚠️ **Desviación Estándar Moderada ({desviacion:.2f})**: Los datos tienen dispersión media.")
                            else:
                                st.error(f"❌ **Desviación Estándar Alta ({desviacion:.2f})**: Los datos están muy dispersos alrededor de la media.")
                            
                            st.markdown(f"""
                            - **Media ± 1σ**: {media - desviacion:.2f} a {media + desviacion:.2f}
                            - **Rango de datos**: {datos_var.min():.2f} a {datos_var.max():.2f}
                            - **Coeficiente de variación**: {(desviacion/media*100):.1f}%
                            """)
                        
                        # Tabla de estadísticos
                        st.subheader("📋 Resumen de Estadísticos")
                        estadisticos_df = pd.DataFrame({
                            'Medida': ['Media', 'Mediana', 'Moda', 'Desviación Estándar', 'Mínimo', 'Máximo', 'Rango', 'Varianza', 'N° Datos'],
                            'Valor': [
                                f"{media:.2f}",
                                f"{mediana:.2f}",
                                f"{moda_valor:.2f}" if isinstance(moda_valor, (int, float)) else moda_valor,
                                f"{desviacion:.2f}",
                                f"{datos_var.min():.2f}",
                                f"{datos_var.max():.2f}",
                                f"{datos_var.max() - datos_var.min():.2f}",
                                f"{datos_var.var():.2f}",
                                len(datos_var)
                            ]
                        })
                        st.dataframe(estadisticos_df, use_container_width=True)
                        
                        # Gráficos adicionales
                        st.subheader("📊 Visualización Adicional")
                        tipo_grafico = st.radio(
                            "Selecciona tipo de gráfico adicional:",
                            ["Boxplot", "Histograma + Polígono", "Gráfico de Dispersión"],
                            horizontal=True
                        )
                        
                        fig2, ax2 = plt.subplots(figsize=(12, 6))
                        
                        if tipo_grafico == "Boxplot":
                            bp = ax2.boxplot(datos_var, vert=True, patch_artist=True,
                                            boxprops=dict(facecolor='lightblue', color='black'),
                                            medianprops=dict(color='red', linewidth=2),
                                            whiskerprops=dict(color='black'),
                                            capprops=dict(color='black'))
                            ax2.set_xticklabels([var_seleccionada[:30]])
                            ax2.set_title(f'Boxplot de {var_seleccionada}', fontsize=14, fontweight='bold')
                            ax2.set_ylabel('Valores', fontsize=12)
                            ax2.grid(True, alpha=0.3)
                            
                        elif tipo_grafico == "Histograma + Polígono":
                            n = len(datos_var)
                            k = int(np.ceil(1 + 3.322 * np.log10(n)))
                            rango_datos = datos_var.max() - datos_var.min()
                            amplitud = np.ceil(rango_datos / k) if k > 0 else 1
                            limites = [datos_var.min() + i * amplitud for i in range(k + 1)]
                            
                            ax2.hist(datos_var, bins=limites, edgecolor='black', color='lightblue', alpha=0.7, label='Histograma')
                            
                            marcas_clase = [(limites[i] + limites[i+1]) / 2 for i in range(k)]
                            intervalos = pd.cut(datos_var, bins=limites, right=False, include_lowest=True)
                            frecuencias_val = intervalos.value_counts().sort_index().values
                            ax2.plot(marcas_clase, frecuencias_val, 'ro-', linewidth=2, markersize=8, label='Polígono')
                            ax2.legend()
                            ax2.set_title(f'Histograma y Polígono de {var_seleccionada}', fontsize=14, fontweight='bold')
                            ax2.set_xlabel(var_seleccionada, fontsize=12)
                            ax2.set_ylabel('Frecuencia', fontsize=12)
                            ax2.grid(True, alpha=0.3)
                            
                        elif tipo_grafico == "Gráfico de Dispersión":
                            ax2.scatter(range(len(datos_var)), datos_var.values, alpha=0.6, color='steelblue')
                            ax2.axhline(media, color='red', linestyle='--', linewidth=2, label=f'Media: {media:.2f}')
                            ax2.axhline(media + desviacion, color='orange', linestyle=':', linewidth=2, label=f'+1σ: {media + desviacion:.2f}')
                            ax2.axhline(media - desviacion, color='orange', linestyle=':', linewidth=2, label=f'-1σ: {media - desviacion:.2f}')
                            ax2.set_title(f'Gráfico de Dispersión de {var_seleccionada}', fontsize=14, fontweight='bold')
                            ax2.set_xlabel('Índice de la observación', fontsize=12)
                            ax2.set_ylabel('Valor', fontsize=12)
                            ax2.legend()
                            ax2.grid(True, alpha=0.3)
                        
                        plt.tight_layout()
                        st.pyplot(fig2)
                        plt.close()
                    else:
                        st.warning("No hay datos numéricos válidos")
            else:
                st.info("ℹ️ No se detectaron variables cuantitativas en este archivo. Todas las preguntas son cualitativas.")
        
        # ============================================
        # DASHBOARD GENERAL
        # ============================================
        
        elif fase_analisis == "📊 Dashboard General":
            st.header("📊 Dashboard General - Todas las preguntas")
            
            for i, col in enumerate(df.columns):
                with st.container():
                    try:
                        pd.to_numeric(df[col], errors='raise')
                        tipo = "Cuantitativa"
                        subtipo = clasificar_variable_cuantitativa(col, df)
                    except:
                        tipo = "Cualitativa"
                        subtipo = clasificar_variable_cualitativa(col, df)
                    
                    st.markdown(f"### {i+1}. {col}")
                    st.caption(f"📌 Tipo: {tipo} - {subtipo}")
                    
                    datos = df[col].copy()
                    datos = datos[datos != "No especificado"]
                    
                    if len(datos) > 0:
                        frecuencias = datos.value_counts()
                        moda_valor = frecuencias.index[0]
                        
                        # Mostrar medidas en columnas
                        col_medidas = st.columns(4)
                        with col_medidas[0]:
                            if tipo == "Cuantitativa":
                                try:
                                    datos_num = pd.to_numeric(datos, errors='coerce').dropna()
                                    if len(datos_num) > 0:
                                        media_val = datos_num.mean()
                                        st.metric("Media", f"{media_val:.2f}")
                                    else:
                                        st.metric("Media", "N/A")
                                except:
                                    st.metric("Media", "N/A")
                            else:
                                st.metric("Media", "N/A")
                        
                        with col_medidas[1]:
                            if tipo == "Cuantitativa":
                                try:
                                    datos_num = pd.to_numeric(datos, errors='coerce').dropna()
                                    if len(datos_num) > 0:
                                        mediana_val = datos_num.median()
                                        st.metric("Mediana", f"{mediana_val:.2f}")
                                    else:
                                        st.metric("Mediana", "N/A")
                                except:
                                    st.metric("Mediana", "N/A")
                            else:
                                st.metric("Mediana", "N/A")
                        
                        with col_medidas[2]:
                            st.metric("Moda", moda_valor)
                        
                        with col_medidas[3]:
                            if tipo == "Cuantitativa":
                                try:
                                    datos_num = pd.to_numeric(datos, errors='coerce').dropna()
                                    if len(datos_num) > 0:
                                        desv_val = datos_num.std()
                                        st.metric("Desv. Estándar", f"{desv_val:.2f}")
                                    else:
                                        st.metric("Desv. Estándar", "N/A")
                                except:
                                    st.metric("Desv. Estándar", "N/A")
                            else:
                                st.metric("Desv. Estándar", "N/A")
                        
                        # Gráfico
                        fig, ax = plt.subplots(figsize=(10, 5))
                        colores = plt.cm.Set3(np.linspace(0, 1, len(frecuencias)))
                        barras = ax.bar(range(len(frecuencias)), frecuencias.values, 
                                      color=colores, edgecolor='black', alpha=0.8)
                        
                        # Resaltar moda
                        for j, (respuesta, valor) in enumerate(frecuencias.items()):
                            if respuesta == moda_valor:
                                barras[j].set_color('#FF9800')
                                barras[j].set_edgecolor('red')
                                barras[j].set_linewidth(2)
                        
                        ax.set_xticks(range(len(frecuencias)))
                        ax.set_xticklabels(frecuencias.index, rotation=45, ha='right', fontsize=10)
                        ax.set_title(f'Distribución', fontsize=12, fontweight='bold')
                        ax.set_ylabel('Frecuencia', fontsize=10)
                        
                        for barra, valor in zip(barras, frecuencias.values):
                            ax.text(barra.get_x() + barra.get_width()/2, barra.get_height() + 0.2,
                                   str(valor), ha='center', va='bottom', fontsize=9)
                        
                        plt.tight_layout()
                        st.pyplot(fig)
                        plt.close()
                        
                        st.markdown("---")
        
        # ============================================
        # EXPORTAR RESULTADOS
        # ============================================
        
        st.markdown("---")
        st.header("📥 Exportar Resultados")
        
        if st.button("📊 Generar Reporte Completo"):
            resultados = []
            for col in df.columns:
                try:
                    pd.to_numeric(df[col], errors='raise')
                    tipo = "Cuantitativa"
                    subtipo = clasificar_variable_cuantitativa(col, df)
                    datos = pd.to_numeric(df[col], errors='coerce').dropna()
                    if len(datos) > 0:
                        moda = datos.mode()
                        moda_valor = moda.iloc[0] if len(moda) > 0 else "N/A"
                        resultados.append({
                            'Variable': col,
                            'Tipo': tipo,
                            'Subtipo': subtipo,
                            'Media': f"{datos.mean():.2f}",
                            'Mediana': f"{datos.median():.2f}",
                            'Moda': moda_valor if isinstance(moda_valor, str) else f"{moda_valor:.2f}",
                            'Desviación Estándar': f"{datos.std():.2f}",
                            'N_Datos': len(datos)
                        })
                except:
                    tipo = "Cualitativa"
                    subtipo = clasificar_variable_cualitativa(col, df)
                    datos = df[col].copy()
                    datos = datos[datos != "No especificado"]
                    if len(datos) > 0:
                        frecuencias = datos.value_counts()
                        resultados.append({
                            'Variable': col,
                            'Tipo': tipo,
                            'Subtipo': subtipo,
                            'Media': 'No aplica',
                            'Mediana': 'No aplica',
                            'Moda': frecuencias.index[0],
                            'Desviación Estándar': 'No aplica',
                            'N_Datos': len(datos)
                        })
            
            if resultados:
                resultados_df = pd.DataFrame(resultados)
                st.dataframe(resultados_df, use_container_width=True)
                
                csv = resultados_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar reporte completo (CSV)",
                    data=csv,
                    file_name="reporte_completo_delicias.csv",
                    mime="text/csv"
                )
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

else:
    st.info("👈 Por favor, carga un archivo CSV en el panel lateral para comenzar el análisis")
    
    with st.expander("📋 Ver formato esperado del CSV", expanded=True):
        st.markdown("""
        ### Formato esperado del CSV - Encuesta Delícias Del Cielo:
        
        El archivo debe contener las siguientes columnas:
        1. **¿Que productos compro con mayor frecuencia?** (Nominal)
        2. **¿Como califica el sabor de los productos?** (Ordinal)
        3. **¿Como califica la presentación de los productos?** (Ordinal)
        4. **¿Como califica la atencion al cliente?** (Ordinal)
        5. **¿Como considera el precio en relación a la calidad?** (Ordinal)
        6. **¿Volveria a comprar a esta repostera?** (Nominal)
        7. **¿Recomendaria este servicio a otras personas?** (Nominal)
        8. **¿Como percibe la higiene del producto?** (Ordinal)
        9. **¿el empaque del producto es adecuado?** (Nominal)
        10. **¿La variedad de productos le parece suficiente?** (Ordinal)
        """)

st.markdown("---")
st.markdown("### 🍰 **Delícias Del Cielo - Análisis de Satisfacción del Cliente**")
st.markdown("### 📌 **Docente: Lic. Eduardo Zubieta | UAP**")
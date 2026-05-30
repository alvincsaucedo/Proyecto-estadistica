# ============================================
# MEDIDAS DE TENDENCIA CENTRAL
# CON TABLAS EN TERMINAL + GRÁFICOS
# ============================================

print("=" * 70)
print("LABORATORIO DE ESTADÍSTICA DESCRIPTIVA")
print("MEDIDAS DE TENDENCIA CENTRAL - ENCUESTA")
print("=" * 70)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
from matplotlib.patches import Patch

# Configurar estilo de gráficos
plt.style.use('ggplot')
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

print("\n✅ Librerías importadas correctamente")

# ============================================
# 1. CARGAR DATOS
# ============================================

print("\n📂 Cargando archivo CSV...")

# Cargar el archivo CSV
df = pd.read_csv("Datos encuesta.csv")

print(f"\n📊 Total de estudiantes: {len(df)}")
print(f"📊 Columnas disponibles: {list(df.columns)}")

print("\n=== PRIMEROS 5 REGISTROS ===")
print(df.head())

print("\n=== INFORMACIÓN DEL DATAFRAME ===")
print(df.info())

# Función para encontrar columnas por patrón
def encontrar_columna(patron, df):
    for col in df.columns:
        if patron.lower() in col.lower():
            return col
    return None

# Función para limpiar edad
def limpiar_edad(valor):
    if pd.isna(valor) or valor == "" or valor == " ":
        return np.nan
    try:
        if isinstance(valor, (int, float)):
            return float(valor) if 10 <= float(valor) <= 100 else np.nan
        if isinstance(valor, str):
            numeros = re.findall(r'\d+', valor)
            if numeros:
                edad = float(numeros[0])
                return edad if 10 <= edad <= 100 else np.nan
        return np.nan
    except:
        return np.nan

# Identificar columnas
col_edad = encontrar_columna('edad', df)
col_sexo = encontrar_columna('sexo', df)
col_semestre = encontrar_columna('semestre', df)

if col_edad:
    df['Edad_limpia'] = df[col_edad].apply(limpiar_edad)

# Crear carpeta para gráficos
if not os.path.exists("graficos_encuesta"):
    os.makedirs("graficos_encuesta")
    print("\n📁 Carpeta 'graficos_encuesta' creada")

# ============================================
# 2. TABLAS DE FRECUENCIAS (COMO EL ORIGINAL)
# ============================================

print("\n" + "=" * 70)
print("FASE 2: TABLA DE FRECUENCIAS - SEMESTRE")
print("=" * 70)

if col_semestre:
    # Limpiar datos de semestre
    df[col_semestre] = df[col_semestre].fillna("No especificado")
    df[col_semestre] = df[col_semestre].replace("", "No especificado")
    
    frec_semestre = df[col_semestre].value_counts().reset_index()
    frec_semestre.columns = ["semestre", "fi"]
    frec_semestre["hi"] = frec_semestre["fi"] / len(df)
    frec_semestre["hip"] = frec_semestre["hi"] * 100
    frec_semestre["Fi"] = frec_semestre["fi"].cumsum()
    frec_semestre["Hi"] = frec_semestre["hi"].cumsum()
    
    print("\n📊 TABLA DE FRECUENCIAS: SEMESTRE")
    print("-" * 70)
    print(frec_semestre.to_string(index=False))
    print("-" * 70)

print("\n" + "=" * 70)
print("FASE 2b: TABLA DE FRECUENCIAS - GÉNERO")
print("=" * 70)

if col_sexo:
    df[col_sexo] = df[col_sexo].fillna("No especificado")
    df[col_sexo] = df[col_sexo].replace("", "No especificado")
    
    frec_genero = df[col_sexo].value_counts().reset_index()
    frec_genero.columns = ["genero", "fi"]
    frec_genero["hi"] = frec_genero["fi"] / len(df)
    frec_genero["hip"] = frec_genero["hi"] * 100
    frec_genero["Fi"] = frec_genero["fi"].cumsum()
    frec_genero["Hi"] = frec_genero["hi"].cumsum()
    
    print("\n📊 TABLA DE FRECUENCIAS: GÉNERO")
    print("-" * 70)
    print(frec_genero.to_string(index=False))
    print("-" * 70)

# ============================================
# 3. DATOS AGRUPADOS PARA EDAD (REGLAS DE STURGES)
# ============================================

if col_edad and df['Edad_limpia'].notna().sum() > 0:
    print("\n" + "=" * 70)
    print("FASE 3: DATOS AGRUPADOS - EDAD (REGLAS DE STURGES)")
    print("=" * 70)
    
    datos_edad = df['Edad_limpia'].dropna()
    
    # Paso A: Cálculo de parámetros críticos
    n = len(datos_edad)
    k = int(np.ceil(1 + 3.322 * np.log10(n)))
    rango = datos_edad.max() - datos_edad.min()
    amplitud = np.ceil(rango / k)
    
    print(f"\n📐 PARÁMETROS CRÍTICOS:")
    print(f"   • Número de datos (n): {n}")
    print(f"   • Número de intervalos (k) según Sturges: {k}")
    print(f"   • Valor mínimo: {datos_edad.min()}")
    print(f"   • Valor máximo: {datos_edad.max()}")
    print(f"   • Rango: {rango}")
    print(f"   • Amplitud del intervalo: {amplitud}")
    
    # Paso B: Segmentación y Marca de Clase
    limite_inferior = datos_edad.min()
    limites = [limite_inferior + i * amplitud for i in range(k + 1)]
    
    # Crear los intervalos
    intervalos = pd.cut(datos_edad, bins=limites, right=False, include_lowest=True)
    
    # Crear tabla de frecuencias agrupadas
    frec_edad_agrupada = pd.DataFrame()
    frec_edad_agrupada["intervalo"] = intervalos.value_counts().sort_index().index
    frec_edad_agrupada["fi"] = intervalos.value_counts().sort_index().values
    frec_edad_agrupada["marca_clase"] = [(intervalo.left + intervalo.right) / 2 for intervalo in frec_edad_agrupada["intervalo"]]
    frec_edad_agrupada["hi"] = frec_edad_agrupada["fi"] / n
    frec_edad_agrupada["hip"] = frec_edad_agrupada["hi"] * 100
    frec_edad_agrupada["Fi"] = frec_edad_agrupada["fi"].cumsum()
    frec_edad_agrupada["Hi"] = frec_edad_agrupada["hi"].cumsum()
    
    print("\n📊 TABLA DE FRECUENCIAS: EDAD (DATOS AGRUPADOS)")
    print("-" * 70)
    print(frec_edad_agrupada.to_string(index=False))
    print("-" * 70)

# ============================================
# 4. MEDIDAS DE TENDENCIA CENTRAL
# ============================================

print("\n" + "=" * 70)
print("FASE 4: MEDIDAS DE TENDENCIA CENTRAL")
print("=" * 70)

def calcular_medidas(datos, nombre):
    datos_limpios = datos.dropna()
    if len(datos_limpios) == 0:
        return None
    
    media = datos_limpios.mean()
    mediana = datos_limpios.median()
    
    moda = datos_limpios.mode()
    if len(moda) > 1:
        moda_str = f"Múltiple: {list(moda)}"
    elif len(moda) == 1:
        moda_str = moda.iloc[0]
    else:
        moda_str = "No hay moda"
    
    return {'media': round(media, 2), 'mediana': mediana, 'moda': moda_str, 'n': len(datos_limpios)}

if col_edad and df['Edad_limpia'].notna().sum() > 0:
    medidas_edad = calcular_medidas(df['Edad_limpia'], 'Edad')
    if medidas_edad:
        print(f"\n📊 VARIABLE: EDAD")
        print("-" * 50)
        print(f"   • Media (promedio): {medidas_edad['media']} años")
        print(f"   • Mediana (valor central): {medidas_edad['mediana']} años")
        print(f"   • Moda (valor más frecuente): {medidas_edad['moda']} años")
        print(f"   • Total datos válidos: {medidas_edad['n']}")
        print("-" * 50)

# Moda para variables cualitativas
if col_semestre:
    moda_semestre = df[col_semestre].mode()
    moda_semestre_str = moda_semestre.iloc[0] if len(moda_semestre) > 0 else "N/A"
    print(f"\n📊 VARIABLE: SEMESTRE")
    print("-" * 50)
    print(f"   • Moda: {moda_semestre_str}")
    print("-" * 50)

if col_sexo:
    moda_sexo = df[col_sexo].mode()
    moda_sexo_str = moda_sexo.iloc[0] if len(moda_sexo) > 0 else "N/A"
    print(f"\n📊 VARIABLE: GÉNERO")
    print("-" * 50)
    print(f"   • Moda: {moda_sexo_str}")
    print("-" * 50)

# ============================================
# 5. GRÁFICOS
# ============================================

print("\n" + "=" * 70)
print("FASE 5: GENERANDO GRÁFICOS")
print("=" * 70)

# GRÁFICO 1: Histograma de Edades
if col_edad and df['Edad_limpia'].notna().sum() > 0:
    print("\n   📊 Generando Gráfico 1: Histograma de Edades")
    fig, ax = plt.subplots()
    
    ax.hist(df['Edad_limpia'].dropna(), bins=k, edgecolor='black', 
            color='steelblue', alpha=0.7, label='Frecuencia')
    
    if medidas_edad:
        ax.axvline(medidas_edad['media'], color='red', linestyle='--', 
                   linewidth=2, label=f"Media: {medidas_edad['media']}")
        ax.axvline(medidas_edad['mediana'], color='green', linestyle='--', 
                   linewidth=2, label=f"Mediana: {medidas_edad['mediana']}")
    
    ax.set_title('Distribución de Edades de los Estudiantes', fontsize=14, fontweight='bold')
    ax.set_xlabel('Edad (años)', fontsize=12)
    ax.set_ylabel('Frecuencia Absoluta (fi)', fontsize=12)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('graficos_encuesta/01_histograma_edades.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("      ✅ Guardado: graficos_encuesta/01_histograma_edades.png")

# GRÁFICO 2: Diagrama de Barras - Semestre
if col_semestre and len(frec_semestre) > 0:
    print("   📊 Generando Gráfico 2: Diagrama de Barras - Semestre")
    fig, ax = plt.subplots()
    
    colores_barras = plt.cm.Set3(np.linspace(0, 1, len(frec_semestre)))
    barras = ax.bar(range(len(frec_semestre)), frec_semestre["fi"], 
                    color=colores_barras, edgecolor='black', alpha=0.8)
    
    ax.set_xticks(range(len(frec_semestre)))
    ax.set_xticklabels(frec_semestre["semestre"], rotation=45, ha='right')
    ax.set_title('Distribución de Estudiantes por Semestre', fontsize=14, fontweight='bold')
    ax.set_xlabel('Semestre', fontsize=12)
    ax.set_ylabel('Frecuencia Absoluta (fi)', fontsize=12)
    
    for barra, valor in zip(barras, frec_semestre["fi"]):
        ax.text(barra.get_x() + barra.get_width()/2, barra.get_height() + 0.2,
                str(valor), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('graficos_encuesta/02_barras_semestre.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("      ✅ Guardado: graficos_encuesta/02_barras_semestre.png")

# GRÁFICO 3: Diagrama de Barras - Género
if col_sexo and len(frec_genero) > 0:
    print("   📊 Generando Gráfico 3: Diagrama de Barras - Género")
    fig, ax = plt.subplots()
    
    colores_sexo = ['lightblue', 'lightcoral', 'lightgray']
    barras = ax.bar(range(len(frec_genero)), frec_genero["fi"], 
                    color=colores_sexo[:len(frec_genero)], edgecolor='black', alpha=0.8)
    
    ax.set_xticks(range(len(frec_genero)))
    ax.set_xticklabels(frec_genero["genero"], rotation=0)
    ax.set_title('Distribución de Estudiantes por Género', fontsize=14, fontweight='bold')
    ax.set_xlabel('Género', fontsize=12)
    ax.set_ylabel('Frecuencia Absoluta (fi)', fontsize=12)
    
    for barra, valor in zip(barras, frec_genero["fi"]):
        ax.text(barra.get_x() + barra.get_width()/2, barra.get_height() + 0.2,
                str(valor), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('graficos_encuesta/03_barras_genero.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("      ✅ Guardado: graficos_encuesta/03_barras_genero.png")

# GRÁFICO 4: Diagrama de Torta - Semestre
if col_semestre and len(frec_semestre) > 0:
    print("   📊 Generando Gráfico 4: Diagrama de Torta - Semestre")
    fig, ax = plt.subplots()
    
    colores_torta = plt.cm.Pastel1(np.linspace(0, 1, len(frec_semestre)))
    explode = [0.02] * len(frec_semestre)
    
    ax.pie(frec_semestre["fi"], labels=frec_semestre["semestre"], autopct='%1.1f%%',
           colors=colores_torta, explode=explode, shadow=True, startangle=90)
    ax.set_title('Distribución Porcentual por Semestre', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('graficos_encuesta/04_torta_semestre.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("      ✅ Guardado: graficos_encuesta/04_torta_semestre.png")

# GRÁFICO 5: Diagrama de Torta - Género
if col_sexo and len(frec_genero) > 0:
    print("   📊 Generando Gráfico 5: Diagrama de Torta - Género")
    fig, ax = plt.subplots()
    
    ax.pie(frec_genero["fi"], labels=frec_genero["genero"], autopct='%1.1f%%',
           colors=colores_sexo, shadow=True, startangle=90)
    ax.set_title('Distribución Porcentual por Género', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('graficos_encuesta/05_torta_genero.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("      ✅ Guardado: graficos_encuesta/05_torta_genero.png")

# GRÁFICO 6: Histograma + Polígono (Edad)
if col_edad and df['Edad_limpia'].notna().sum() > 0:
    print("   📊 Generando Gráfico 6: Histograma + Polígono (Edad)")
    fig, ax = plt.subplots()
    
    # Histograma
    ax.hist(datos_edad, bins=limites, edgecolor='black', color='lightblue', 
            alpha=0.7, label='Histograma')
    
    # Polígono de frecuencias
    marcas_clase = frec_edad_agrupada["marca_clase"]
    frecuencias = frec_edad_agrupada["fi"]
    ax.plot(marcas_clase, frecuencias, 'ro-', linewidth=2, markersize=8, 
            label='Polígono de frecuencias')
    
    ax.set_title('Distribución de Edades - Histograma y Polígono', fontsize=14, fontweight='bold')
    ax.set_xlabel('Edad (años)', fontsize=12)
    ax.set_ylabel('Frecuencia Absoluta (fi)', fontsize=12)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('graficos_encuesta/06_histograma_poligono_edad.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("      ✅ Guardado: graficos_encuesta/06_histograma_poligono_edad.png")

# GRÁFICO 7: Ojiva (Frecuencia Acumulada - Edad)
if col_edad and df['Edad_limpia'].notna().sum() > 0:
    print("   📊 Generando Gráfico 7: Ojiva (Edad)")
    fig, ax = plt.subplots()
    
    limites_superiores = limites[1:]
    frec_acumulada = frec_edad_agrupada["Fi"].values
    
    x_ojiva = [limites[0]] + limites_superiores
    y_ojiva = [0] + list(frec_acumulada)
    
    ax.plot(x_ojiva, y_ojiva, 'go-', linewidth=2, markersize=8, label='Ojiva')
    ax.fill_between(x_ojiva, y_ojiva, alpha=0.2, color='green')
    
    ax.set_title('Ojiva - Frecuencia Acumulada de Edades', fontsize=14, fontweight='bold')
    ax.set_xlabel('Edad (años)', fontsize=12)
    ax.set_ylabel('Frecuencia Acumulada (Fi)', fontsize=12)
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('graficos_encuesta/07_ojiva_edad.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("      ✅ Guardado: graficos_encuesta/07_ojiva_edad.png")

# GRÁFICO 8: Boxplot de Edades
if col_edad and df['Edad_limpia'].notna().sum() > 0:
    print("   📊 Generando Gráfico 8: Boxplot de Edades")
    fig, ax = plt.subplots(figsize=(10, 6))
    
    box = ax.boxplot(df['Edad_limpia'].dropna(), vert=True, patch_artist=True,
                      boxprops=dict(facecolor='lightblue', color='black'),
                      whiskerprops=dict(color='black'),
                      capprops=dict(color='black'),
                      medianprops=dict(color='red', linewidth=2))
    
    ax.set_title('Diagrama de Caja - Distribución de Edades', fontsize=14, fontweight='bold')
    ax.set_ylabel('Edad (años)', fontsize=12)
    ax.set_xticklabels(['Edades'])
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('graficos_encuesta/08_boxplot_edades.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("      ✅ Guardado: graficos_encuesta/08_boxplot_edades.png")

# ============================================
# 6. RESUMEN FINAL
# ============================================

print("\n" + "=" * 70)
print("RESUMEN FINAL DEL LABORATORIO")
print("=" * 70)

print("\n📊 TABLAS GENERADAS EN TERMINAL:")
print("   ✅ Tabla de frecuencias - Semestre")
print("   ✅ Tabla de frecuencias - Género")
print("   ✅ Tabla de frecuencias agrupadas - Edad (Sturges)")
print("   ✅ Medidas de tendencia central (Media, Mediana, Moda)")

print("\n📈 GRÁFICOS GENERADOS (carpeta 'graficos_encuesta/'):")
print("   ✅ 01_histograma_edades.png")
print("   ✅ 02_barras_semestre.png")
print("   ✅ 03_barras_genero.png")
print("   ✅ 04_torta_semestre.png")
print("   ✅ 05_torta_genero.png")
print("   ✅ 06_histograma_poligono_edad.png")
print("   ✅ 07_ojiva_edad.png")
print("   ✅ 08_boxplot_edades.png")

print("\n📊 MEDIDAS DE TENDENCIA CENTRAL CALCULADAS:")
if col_edad and medidas_edad:
    print(f"   • EDAD: Media={medidas_edad['media']}, Mediana={medidas_edad['mediana']}, Moda={medidas_edad['moda']}")
if col_semestre:
    print(f"   • SEMESTRE: Moda={moda_semestre_str}")
if col_sexo:
    print(f"   • GÉNERO: Moda={moda_sexo_str}")

print("\n" + "=" * 70)
print("✅ LABORATORIO COMPLETADO EXITOSAMENTE")
print("✅ Todos los gráficos guardados en la carpeta 'graficos_encuesta'")
print("=" * 70)
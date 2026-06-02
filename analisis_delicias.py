# ============================================
# MEDIDAS DE TENDENCIA CENTRAL
# ENCUESTA - DELÍCIAS DEL CIELO
# ============================================

print("=" * 70)
print("LABORATORIO DE ESTADÍSTICA DESCRIPTIVA")
print("MEDIDAS DE TENDENCIA CENTRAL - DELÍCIAS DEL CIELO")
print("ANÁLISIS COMPLETO DE 10 PREGUNTAS")
print("=" * 70)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
from collections import Counter

# Configurar estilo de gráficos
plt.style.use('ggplot')
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

print("\n✅ Librerías importadas correctamente")

# ============================================
# 1. CARGAR DATOS (MANEJO ESPECIAL PARA CSV CON COMILLAS)
# ============================================

print("\n📂 Cargando archivo CSV...")

nombre_archivo = "Delicias_Del_Cielo.csv"

# Función para leer CSV con formato problemático
def leer_csv_problematico(archivo):
    """Lee un CSV que tiene todas las columnas en una sola por comillas anidadas"""
    try:
        # Leer línea por línea
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Dividir por líneas
        lineas = contenido.strip().split('\n')
        
        # Procesar primera línea (encabezados)
        primera_linea = lineas[0]
        # Extraer encabezados usando expresión regular
        encabezados = re.findall(r'"([^"]*)"', primera_linea)
        # Limpiar encabezados
        encabezados = [h.strip() for h in encabezados if h.strip()]
        
        print(f"   Encabezados encontrados: {len(encabezados)}")
        
        # Procesar datos
        datos = []
        for linea in lineas[1:]:
            # Extraer valores entre comillas
            valores = re.findall(r'"([^"]*)"', linea)
            # Limpiar valores
            valores = [v.strip() if v else '' for v in valores]
            if len(valores) >= len(encabezados):
                datos.append(valores[:len(encabezados)])
            elif valores:
                # Completar con vacíos si faltan
                valores.extend([''] * (len(encabezados) - len(valores)))
                datos.append(valores)
        
        # Crear DataFrame
        df = pd.DataFrame(datos, columns=encabezados)
        return df
        
    except Exception as e:
        print(f"   Error en lectura manual: {e}")
        return None

# Intentar cargar el archivo
df = None

# Método 1: Lectura manual
print("   Intentando lectura manual...")
df = leer_csv_problematico(nombre_archivo)

if df is None:
    # Método 2: pandas normal
    try:
        print("   Intentando pandas normal...")
        df = pd.read_csv(nombre_archivo, encoding='utf-8')
    except:
        pass

if df is None:
    print("\n❌ Error: No se pudo cargar el archivo")
    exit()

# Limpiar nombres de columnas
df.columns = [col.replace('ï»¿', '').replace('\ufeff', '').strip() for col in df.columns]

# Eliminar columna de timestamp/marca temporal si existe
if 'Marca temporal' in df.columns:
    df = df.drop(columns=['Marca temporal'])
    print("   ✅ Columna 'Marca temporal' eliminada")

print(f"\n📊 Total de encuestados: {len(df)}")
print(f"📊 Columnas disponibles: {len(df.columns)}")

# Mostrar nombres de columnas encontradas
print("\n=== COLUMNAS ENCONTRADAS ===")
for i, col in enumerate(df.columns):
    print(f"   {i+1}. {col}")

print("\n=== PRIMEROS 3 REGISTROS ===")
print(df.head(3))

# ============================================
# FUNCIONES AUXILIARES
# ============================================

def limpiar_texto(valor):
    """Limpia valores de texto"""
    if pd.isna(valor) or valor == "" or valor == " ":
        return "No especificado"
    return str(valor).strip()

def crear_grafico_barras(datos, titulo, nombre_archivo, xlabel):
    """Crea y guarda un gráfico de barras"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colores = plt.cm.Set3(np.linspace(0, 1, len(datos)))
    barras = ax.bar(range(len(datos)), datos.values, color=colores, edgecolor='black', alpha=0.8)
    ax.set_xticks(range(len(datos)))
    ax.set_xticklabels(datos.index, rotation=45, ha='right', fontsize=10)
    ax.set_title(titulo, fontsize=14, fontweight='bold')
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel('Frecuencia', fontsize=12)
    
    for barra, valor in zip(barras, datos.values):
        ax.text(barra.get_x() + barra.get_width()/2, barra.get_height() + 0.2,
                str(valor), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'graficos_delicias/{nombre_archivo}', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"      ✅ Guardado: {nombre_archivo}")

def crear_grafico_torta(datos, titulo, nombre_archivo):
    """Crea y guarda un gráfico de torta"""
    if len(datos) == 0:
        return
    fig, ax = plt.subplots(figsize=(10, 8))
    
    colores = plt.cm.Pastel1(np.linspace(0, 1, len(datos)))
    explode = [0.02] * len(datos)
    
    wedges, texts, autotexts = ax.pie(datos.values, labels=datos.index, autopct='%1.1f%%',
                                        colors=colores, explode=explode, shadow=True, startangle=90)
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')
    
    ax.set_title(titulo, fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'graficos_delicias/{nombre_archivo}', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"      ✅ Guardado: {nombre_archivo}")

# Crear carpeta para gráficos
if not os.path.exists("graficos_delicias"):
    os.makedirs("graficos_delicias")
    print("\n📁 Carpeta 'graficos_delicias' creada")

# ============================================
# DEFINICIÓN DE LAS 10 PREGUNTAS (nombres exactos)
# ============================================

# Usar los nombres exactos de las columnas del archivo
preguntas = [
    {'col': '1) �Que productos compro con mayor frecuencia?', 'nombre': '1. Producto más comprado', 'tipo': 'barras'},
    {'col': '2) �Como califica el sabor de los productos?', 'nombre': '2. Calificación del Sabor', 'tipo': 'ambos'},
    {'col': '3) �Como califica la presentaci�n de los productos?', 'nombre': '3. Calificación de la Presentación', 'tipo': 'ambos'},
    {'col': '4) �Como califica la atencion al cliente?', 'nombre': '4. Calificación de la Atención', 'tipo': 'ambos'},
    {'col': '5) �Como considera el precio en relaci�n a la calidad?', 'nombre': '5. Precio vs Calidad', 'tipo': 'ambos'},
    {'col': '6) �Volveria a comprar a esta repostera?', 'nombre': '6. Intención de Recompra', 'tipo': 'torta'},
    {'col': '7) �Recomendaria este servicio a otras personas?', 'nombre': '7. Recomendación', 'tipo': 'torta'},
    {'col': '8) �Como percibe la higiene del producto?', 'nombre': '8. Percepción de Higiene', 'tipo': 'ambos'},
    {'col': '9) �el empaque del producto es adecuado?', 'nombre': '9. Adecuación del Empaque', 'tipo': 'ambos'},
    {'col': '10) �La variedad de productos le parece suficiente?', 'nombre': '10. Suficiencia de Variedad', 'tipo': 'ambos'}
]

# ============================================
# PROCESAR CADA PREGUNTA
# ============================================

print("\n" + "=" * 70)
print("ANÁLISIS DE LAS 10 PREGUNTAS DE LA ENCUESTA")
print("=" * 70)

resultados = {}

for i, pregunta in enumerate(preguntas, 1):
    col_name = pregunta['col']
    titulo = pregunta['nombre']
    tipo_grafico = pregunta['tipo']
    
    print(f"\n{'='*70}")
    print(f"{titulo}")
    print(f"{'='*70}")
    
    if col_name in df.columns:
        # Limpiar datos
        datos = df[col_name].apply(limpiar_texto)
        datos = datos[datos != ""]
        
        if len(datos) > 0:
            # Calcular frecuencias
            frecuencias = datos.value_counts()
            
            # Crear tabla de frecuencias
            frec_df = pd.DataFrame({
                'Respuesta': frecuencias.index,
                'Frecuencia (fi)': frecuencias.values,
                'Porcentaje (%)': (frecuencias.values / len(df) * 100).round(2)
            })
            frec_df['Frec. Acumulada (Fi)'] = frec_df['Frecuencia (fi)'].cumsum()
            frec_df['Porc. Acum. (%)'] = (frec_df['Frec. Acumulada (Fi)'] / len(df) * 100).round(2)
            
            # Mostrar tabla
            print(f"\n📊 TABLA DE FRECUENCIAS")
            print("-" * 70)
            print(frec_df.to_string(index=False))
            print("-" * 70)
            
            # Calcular moda
            moda_valor = frecuencias.index[0]
            moda_frecuencia = frecuencias.values[0]
            moda_porcentaje = (moda_frecuencia / len(df)) * 100
            print(f"\n⭐ MODA: {moda_valor}")
            print(f"   • Frecuencia: {moda_frecuencia} respuestas")
            print(f"   • Porcentaje: {moda_porcentaje:.1f}%")
            
            # Guardar resultados
            resultados[titulo] = {
                'moda': moda_valor,
                'frecuencia': moda_frecuencia,
                'porcentaje': moda_porcentaje
            }
            
            # Generar gráficos
            print(f"\n   📊 Generando gráficos...")
            
            # Gráfico de barras
            crear_grafico_barras(
                frecuencias, 
                titulo, 
                f'{i:02d}_barras_{titulo[:20].replace(" ", "_").replace(".", "")}.png',
                'Respuesta'
            )
            
            # Gráfico de torta (si aplica)
            if tipo_grafico == 'ambos' or tipo_grafico == 'torta':
                crear_grafico_torta(
                    frecuencias, 
                    titulo, 
                    f'{i:02d}_torta_{titulo[:20].replace(" ", "_").replace(".", "")}.png'
                )
        else:
            print(f"\n⚠️ No hay datos válidos para esta pregunta")
    else:
        print(f"\n❌ Columna no encontrada: '{col_name}'")
        print(f"   Columnas disponibles: {list(df.columns)}")

# ============================================
# GRÁFICO RESUMEN DASHBOARD
# ============================================

print("\n" + "=" * 70)
print("GENERANDO DASHBOARD COMPLETO")
print("=" * 70)

# Dashboard con todas las preguntas (5x2)
fig, axes = plt.subplots(5, 2, figsize=(20, 24))
axes = axes.ravel()

for i, pregunta in enumerate(preguntas):
    col_name = pregunta['col']
    titulo = pregunta['nombre']
    
    if col_name in df.columns:
        datos = df[col_name].apply(limpiar_texto)
        datos = datos[datos != ""]
        if len(datos) > 0:
            frecuencias = datos.value_counts()
            
            # Crear gráfico de barras
            colores = plt.cm.Set3(np.linspace(0, 1, len(frecuencias)))
            barras = axes[i].bar(range(len(frecuencias)), frecuencias.values, 
                                  color=colores, edgecolor='black', alpha=0.8)
            axes[i].set_xticks(range(len(frecuencias)))
            axes[i].set_xticklabels(frecuencias.index, rotation=45, ha='right', fontsize=9)
            axes[i].set_title(titulo, fontsize=11, fontweight='bold')
            axes[i].set_ylabel('Frecuencia', fontsize=9)
            
            for barra, valor in zip(barras, frecuencias.values):
                axes[i].text(barra.get_x() + barra.get_width()/2, barra.get_height() + 0.2,
                            str(valor), ha='center', va='bottom', fontsize=8)

# Ocultar ejes vacíos
for i in range(len(preguntas), len(axes)):
    axes[i].axis('off')

fig.suptitle('DASHBOARD COMPLETO - ENCUESTA DELÍCIAS DEL CIELO\nAnálisis de las 10 preguntas', 
             fontsize=18, fontweight='bold')
plt.tight_layout()
plt.savefig('graficos_delicias/00_dashboard_completo.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ Guardado: graficos_delicias/00_dashboard_completo.png")

# ============================================
# GRÁFICO DE SATISFACCIÓN GENERAL
# ============================================

print("\n   📊 Generando Gráfico de Satisfacción General")

# Calcular satisfacción general
satisfaccion = {'Positiva': 0, 'Negativa': 0, 'Neutral': 0}
palabras_positivas = ['Excelente', 'Bueno', 'Atractiva', 'Adecuado', 'Si', 'Suficiente']
palabras_negativas = ['Malo', 'Poco atractiva', 'Poco Adecuado', 'No', 'Poco Suficiente']

for pregunta in preguntas:
    col_name = pregunta['col']
    if col_name in df.columns:
        datos = df[col_name].apply(limpiar_texto)
        for valor in datos:
            if valor in palabras_positivas:
                satisfaccion['Positiva'] += 1
            elif valor in palabras_negativas:
                satisfaccion['Negativa'] += 1
            else:
                satisfaccion['Neutral'] += 1

total = sum(satisfaccion.values())
if total > 0:
    fig, ax = plt.subplots(figsize=(10, 8))
    colores_satisfaccion = ['#4CAF50', '#FFC107', '#F44336']
    explode = (0.05, 0.03, 0.05)
    
    ax.pie(satisfaccion.values(), labels=satisfaccion.keys(), autopct='%1.1f%%',
           colors=colores_satisfaccion, explode=explode, shadow=True, startangle=90)
    ax.set_title('Satisfacción General - Delícias Del Cielo', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('graficos_delicias/satisfaccion_general.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("      ✅ Guardado: graficos_delicias/satisfaccion_general.png")

# ============================================
# RESUMEN DE MODAS
# ============================================

print("\n" + "=" * 70)
print("RESUMEN DE MODAS (TENDENCIA CENTRAL)")
print("=" * 70)

print("\n📊 MODA DE CADA PREGUNTA:")
print("-" * 70)

for titulo, info in resultados.items():
    print(f"   {titulo:<35} → {info['moda']:<20} ({info['frecuencia']} respuestas - {info['porcentaje']:.1f}%)")

# ============================================
# ESTADÍSTICAS CLAVE
# ============================================

print("\n" + "=" * 70)
print("ESTADÍSTICAS CLAVE DEL NEGOCIO")
print("=" * 70)

if '1. Producto más comprado' in resultados:
    print(f"\n🍰 PRODUCTO ESTRELLA:")
    print(f"   → {resultados['1. Producto más comprado']['moda']}")
    print(f"   → {resultados['1. Producto más comprado']['frecuencia']} de {len(df)} encuestados")
    print(f"   → {resultados['1. Producto más comprado']['porcentaje']:.1f}% de preferencia")

if '7. Recomendación' in resultados:
    print(f"\n⭐ TASA DE RECOMENDACIÓN:")
    print(f"   → {resultados['7. Recomendación']['moda']}")
    print(f"   → {resultados['7. Recomendación']['porcentaje']:.1f}% recomendaría el servicio")

if '6. Intención de Recompra' in resultados:
    print(f"\n🔄 INTENCIÓN DE RECOMPRA:")
    print(f"   → {resultados['6. Intención de Recompra']['moda']}")
    print(f"   → {resultados['6. Intención de Recompra']['porcentaje']:.1f}% volvería a comprar")

# ============================================
# RESUMEN FINAL
# ============================================

print("\n" + "=" * 70)
print("RESUMEN FINAL")
print("=" * 70)

print(f"\n📊 TOTAL DE GRÁFICOS GENERADOS:")
print(f"   • 10 gráficos de barras (uno por pregunta)")
print(f"   • 8 gráficos de torta (para preguntas de calificación)")
print(f"   • 1 Dashboard completo")
print(f"   • 1 Gráfico de satisfacción general")
print(f"   • TOTAL: 20 gráficos")

print(f"\n📁 Todos los gráficos guardados en: graficos_delicias/")

print("\n" + "=" * 70)
print("✅ LABORATORIO COMPLETADO EXITOSAMENTE")
print("✅ Análisis completo de las 10 preguntas")
print("=" * 70)
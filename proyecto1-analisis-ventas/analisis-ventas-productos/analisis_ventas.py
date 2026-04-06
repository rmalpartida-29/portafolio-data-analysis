import pandas as pd
import matplotlib.pyplot as plt

# ── 1. CARGAR DATOS ──────────────────────────────────────
df = pd.read_csv('data/ventas.csv')

print("=== PRIMERAS FILAS ===")
print(df.head())

print("\n=== INFORMACIÓN DEL DATASET ===")
print(df.info())

# ── 2. LIMPIEZA ──────────────────────────────────────────
df['fecha'] = pd.to_datetime(df['fecha'])
df['total_venta'] = df['cantidad'] * df['precio_unitario']

print("\n=== ESTADÍSTICAS BÁSICAS ===")
print(df.describe())

# ── 3. ANÁLISIS ──────────────────────────────────────────
print("\n=== VENTAS TOTALES POR CATEGORÍA ===")
ventas_categoria = df.groupby('categoria')['total_venta'].sum()
print(ventas_categoria)

print("\n=== PRODUCTO MÁS VENDIDO ===")
producto_top = df.groupby('producto')['cantidad'].sum().sort_values(ascending=False)
print(producto_top)

# ── 4. GRÁFICOS ──────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Gráfico 1 - Ventas por categoría
ventas_categoria.plot(kind='bar', ax=ax1, color=['#2196F3', '#4CAF50'])
ax1.set_title('Ventas Totales por Categoría')
ax1.set_xlabel('Categoría')
ax1.set_ylabel('Total (S/.)')
ax1.tick_params(axis='x', rotation=0)

# Gráfico 2 - Productos más vendidos
producto_top.plot(kind='barh', ax=ax2, color='#FF9800')
ax2.set_title('Cantidad Vendida por Producto')
ax2.set_xlabel('Cantidad')

plt.tight_layout()
plt.savefig('data/grafico_ventas.png')
plt.show()

print("\n✅ Análisis completado. Gráfico guardado en data/grafico_ventas.png")
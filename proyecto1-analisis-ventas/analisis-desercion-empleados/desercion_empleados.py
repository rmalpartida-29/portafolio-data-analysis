
# ============================================================
#  ANÁLISIS DE DESERCIÓN DE EMPLEADOS
#  Autor: Roy Yangaly Malpartida Sanchez
#  Stack: Python, Pandas, NumPy, Matplotlib, Seaborn
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

plt.rcParams.update({
    "font.family": "sans-serif",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 130,
})

PALETTE = ["#1B3A6B", "#E8593C"]

# ─────────────────────────────────────────────────────────────
# 1. GENERACIÓN DEL DATASET
# ─────────────────────────────────────────────────────────────
np.random.seed(42)
N = 1_500

departamentos = ["Ventas", "TI", "RRHH", "Operaciones", "Finanzas", "Marketing"]
cargos        = ["Analista", "Supervisor", "Coordinador", "Asistente", "Gerente"]

df = pd.DataFrame({
    "empleado_id":    [f"EMP-{str(i).zfill(4)}" for i in range(1, N+1)],
    "edad":           np.random.randint(22, 58, N),
    "departamento":   np.random.choice(departamentos, N),
    "cargo":          np.random.choice(cargos, N),
    "antiguedad":     np.random.randint(0, 20, N),
    "salario":        np.round(np.random.lognormal(7.8, 0.4, N), 0).clip(1500, 15000),
    "horas_extra":    np.random.choice([0, 1], N, p=[0.6, 0.4]),
    "satisfaccion":   np.random.randint(1, 5, N),
    "evaluacion":     np.round(np.random.uniform(2.0, 5.0, N), 1),
    "distancia_km":   np.random.randint(1, 60, N),
})

# Deserción con lógica realista
prob_desercion = (
    0.05
    + (df["satisfaccion"] < 3).astype(float) * 0.20
    + (df["salario"] < 3000).astype(float) * 0.15
    + (df["horas_extra"] == 1).astype(float) * 0.10
    + (df["antiguedad"] < 2).astype(float) * 0.12
    + (df["distancia_km"] > 40).astype(float) * 0.08
)
df["desercion"] = (np.random.rand(N) < prob_desercion).astype(int)
df["desercion_label"] = df["desercion"].map({1: "Renunció", 0: "Se quedó"})

print("=" * 55)
print("  ANÁLISIS DE DESERCIÓN DE EMPLEADOS")
print("=" * 55)
print(f"\n  Total empleados   : {len(df):,}")
print(f"  Desertaron        : {df['desercion'].sum():,} ({df['desercion'].mean()*100:.1f}%)")
print(f"  Se quedaron       : {(df['desercion']==0).sum():,}")

# ─────────────────────────────────────────────────────────────
# 2. ANÁLISIS POR DEPARTAMENTO
# ─────────────────────────────────────────────────────────────
desercion_dept = df.groupby("departamento")["desercion"].mean().sort_values(ascending=False) * 100
print("\n── Tasa de deserción por departamento ───────────────────")
for dept, tasa in desercion_dept.items():
    print(f"  {dept:<15} {tasa:.1f}%")

# ─────────────────────────────────────────────────────────────
# 3. VISUALIZACIONES
# ─────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle("Análisis de Deserción de Empleados", fontsize=15, fontweight="bold", color="#1B3A6B")

# 3.1 Tasa por departamento
ax1 = axes[0, 0]
colors = ["#E8593C" if v == desercion_dept.max() else "#2E5FA3" for v in desercion_dept.values]
bars = ax1.bar(desercion_dept.index, desercion_dept.values, color=colors, edgecolor="none")
for bar, val in zip(bars, desercion_dept.values):
    ax1.text(bar.get_x() + bar.get_width()/2, val + 0.3, f"{val:.1f}%", ha="center", fontsize=9)
ax1.set_title("Tasa de deserción por departamento", fontweight="bold", color="#1B3A6B")
ax1.set_ylabel("% de deserción")
ax1.tick_params(axis="x", rotation=15)

# 3.2 Salario vs Deserción
ax2 = axes[0, 1]
sns.boxplot(data=df, x="desercion_label", y="salario", palette=["#2E5FA3", "#E8593C"], ax=ax2)
ax2.set_title("Salario vs Deserción", fontweight="bold", color="#1B3A6B")
ax2.set_xlabel("")
ax2.set_ylabel("Salario (S/)")

# 3.3 Satisfacción vs Deserción
ax3 = axes[0, 2]
satisf = df.groupby(["satisfaccion", "desercion_label"]).size().unstack()
satisf.plot(kind="bar", ax=ax3, color=["#2E5FA3", "#E8593C"], edgecolor="none")
ax3.set_title("Satisfacción vs Deserción", fontweight="bold", color="#1B3A6B")
ax3.set_xlabel("Nivel de satisfacción (1=bajo, 4=alto)")
ax3.set_ylabel("N° empleados")
ax3.tick_params(axis="x", rotation=0)
ax3.legend(fontsize=8)

# 3.4 Horas extra vs Deserción
ax4 = axes[1, 0]
horas = df.groupby("horas_extra")["desercion"].mean() * 100
ax4.bar(["Sin horas extra", "Con horas extra"], horas.values,
        color=["#2E5FA3", "#E8593C"], edgecolor="none")
for i, val in enumerate(horas.values):
    ax4.text(i, val + 0.3, f"{val:.1f}%", ha="center", fontsize=10)
ax4.set_title("Horas extra vs Deserción", fontweight="bold", color="#1B3A6B")
ax4.set_ylabel("% de deserción")

# 3.5 Antigüedad vs Deserción
ax5 = axes[1, 1]
df["rango_antiguedad"] = pd.cut(df["antiguedad"], bins=[0,2,5,10,20],
                                 labels=["0-2 años","3-5 años","6-10 años","11+ años"])
ant = df.groupby("rango_antiguedad")["desercion"].mean() * 100
ax5.bar(ant.index, ant.values, color=PALETTE[0], edgecolor="none")
for i, val in enumerate(ant.values):
    ax5.text(i, val + 0.3, f"{val:.1f}%", ha="center", fontsize=9)
ax5.set_title("Antigüedad vs Deserción", fontweight="bold", color="#1B3A6B")
ax5.set_ylabel("% de deserción")

# 3.6 Distribución por cargo
ax6 = axes[1, 2]
cargo_des = df.groupby("cargo")["desercion"].mean().sort_values(ascending=True) * 100
ax6.barh(cargo_des.index, cargo_des.values, color="#5B8DD9", edgecolor="none")
for i, val in enumerate(cargo_des.values):
    ax6.text(val + 0.2, i, f"{val:.1f}%", va="center", fontsize=9)
ax6.set_title("Deserción por cargo", fontweight="bold", color="#1B3A6B")
ax6.set_xlabel("% de deserción")

plt.tight_layout()
plt.savefig("desercion_dashboard.png", bbox_inches="tight", dpi=150)
print("\n  Gráfico guardado → desercion_dashboard.png")

# ─────────────────────────────────────────────────────────────
# 4. CONCLUSIONES
# ─────────────────────────────────────────────────────────────
dept_max = desercion_dept.idxmax()
tasa_max = desercion_dept.max()
salario_renuncia = df[df["desercion"]==1]["salario"].mean()
salario_queda    = df[df["desercion"]==0]["salario"].mean()
tasa_horas_extra = df[df["horas_extra"]==1]["desercion"].mean() * 100

print("\n── Conclusiones principales ─────────────────────────────")
print(f"  1. {dept_max} tiene la mayor tasa de deserción: {tasa_max:.1f}%")
print(f"  2. Salario promedio de quienes renuncian : S/ {salario_renuncia:,.0f}")
print(f"  3. Salario promedio de quienes se quedan : S/ {salario_queda:,.0f}")
print(f"  4. Empleados con horas extra desertan {tasa_horas_extra:.1f}% de las veces")
print(f"  5. Empleados con 0-2 años son los más propensos a renunciar")
print("=" * 55)

# ─────────────────────────────────────────────────────────────
# 5. EXPORTAR
# ─────────────────────────────────────────────────────────────
df.to_csv("desercion_empleados.csv", index=False, encoding="utf-8-sig")
df[df["desercion"]==1].to_csv("empleados_en_riesgo.csv", index=False, encoding="utf-8-sig")
print("\n  Archivos exportados:")
print("    → desercion_empleados.csv")
print("    → empleados_en_riesgo.csv")
print("    → desercion_dashboard.png")
print("=" * 55)

plt.show()
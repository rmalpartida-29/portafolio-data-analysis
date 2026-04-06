# ============================================================
#  SEGMENTACIÓN RFM DE CLIENTES — CALL CENTER
#  Autor: Roy Yangaly Malpartida Sanchez
#  Stack: Python, Pandas, NumPy, Matplotlib, Seaborn
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

plt.rcParams.update({
    "font.family": "sans-serif",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 130,
})
PALETTE = ["#1B3A6B", "#2E5FA3", "#5B8DD9", "#A8C4F0", "#D6E4F7"]

np.random.seed(42)
N_CLIENTES   = 1_200
N_COMPRAS    = 8_000
FECHA_HOY    = datetime(2024, 12, 31)
FECHA_INICIO = datetime(2023, 1, 1)

clientes_ids = [f"CLI-{str(i).zfill(4)}" for i in range(1, N_CLIENTES + 1)]
dias_totales = (FECHA_HOY - FECHA_INICIO).days
fechas = [FECHA_INICIO + timedelta(days=int(d))
          for d in np.random.randint(0, dias_totales, N_COMPRAS)]

transacciones = pd.DataFrame({
    "cliente_id": np.random.choice(clientes_ids, N_COMPRAS),
    "fecha":      fechas,
    "monto_soles": np.round(
        np.random.lognormal(mean=5.0, sigma=0.8, size=N_COMPRAS), 2
    ).clip(20, 3000),
})

print("=" * 55)
print("  PROYECTO: SEGMENTACIÓN RFM — CALL CENTER")
print("=" * 55)
print(f"\n  Dataset generado: {len(transacciones):,} transacciones")
print(f"  Clientes únicos : {transacciones['cliente_id'].nunique():,}")
print(f"  Período         : {FECHA_INICIO.date()} → {FECHA_HOY.date()}")
print(f"  Monto promedio  : S/ {transacciones['monto_soles'].mean():.2f}")

rfm = transacciones.groupby("cliente_id").agg(
    ultima_compra = ("fecha",       "max"),
    frecuencia    = ("fecha",       "count"),
    monto_total   = ("monto_soles", "sum"),
).reset_index()

rfm["recencia"] = (FECHA_HOY - rfm["ultima_compra"]).dt.days

rfm["R_score"] = pd.qcut(rfm["recencia"],    q=5, labels=[5,4,3,2,1]).astype(int)
rfm["F_score"] = pd.qcut(rfm["frecuencia"].rank(method="first"), q=5, labels=[1,2,3,4,5]).astype(int)
rfm["M_score"] = pd.qcut(rfm["monto_total"], q=5, labels=[1,2,3,4,5]).astype(int)
rfm["RFM_score"] = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]

def segmentar(row):
    r, f, m = row["R_score"], row["F_score"], row["M_score"]
    score = row["RFM_score"]
    if score >= 13:
        return "Campeones"
    elif r >= 4 and f >= 3:
        return "Leales"
    elif r >= 4 and f <= 2:
        return "Potencial"
    elif r <= 2 and f >= 4:
        return "En riesgo"
    elif r == 1 and f == 1:
        return "Perdidos"
    else:
        return "Regulares"

rfm["segmento"] = rfm.apply(segmentar, axis=1)

top_20 = rfm.nlargest(int(len(rfm) * 0.20), "monto_total").copy()
top_20["prioridad_discador"] = range(1, len(top_20) + 1)

print(f"\n  Top 20% rentable: {len(top_20)} clientes listos para el discador")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Análisis de Segmentación RFM — Call Center", fontsize=15, fontweight="bold", color="#1B3A6B")

ax1 = axes[0, 0]
seg_plot = rfm["segmento"].value_counts()
bars = ax1.barh(seg_plot.index, seg_plot.values, color=PALETTE[:len(seg_plot)], edgecolor="none")
for bar, val in zip(bars, seg_plot.values):
    ax1.text(val + 2, bar.get_y() + bar.get_height()/2, f"{val:,}", va="center", fontsize=10)
ax1.set_title("Clientes por segmento", fontweight="bold", color="#1B3A6B")
ax1.set_xlabel("N° de clientes")

ax2 = axes[0, 1]
monto_seg = rfm.groupby("segmento")["monto_total"].sum().sort_values(ascending=True)
bars2 = ax2.barh(monto_seg.index, monto_seg.values / 1000, color="#2E5FA3", edgecolor="none")
for bar, val in zip(bars2, monto_seg.values):
    ax2.text(val/1000 + 1, bar.get_y() + bar.get_height()/2, f"S/{val/1000:.0f}K", va="center", fontsize=9)
ax2.set_title("Monto total por segmento", fontweight="bold", color="#1B3A6B")
ax2.set_xlabel("Miles de soles (S/)")

ax3 = axes[1, 0]
for seg in rfm["segmento"].unique():
    sub = rfm[rfm["segmento"] == seg]
    ax3.scatter(sub["recencia"], sub["monto_total"], label=seg, alpha=0.5, s=18)
ax3.set_title("Recencia vs Monto total", fontweight="bold", color="#1B3A6B")
ax3.set_xlabel("Días desde última compra")
ax3.set_ylabel("Monto total (S/)")
ax3.legend(fontsize=7)

ax4 = axes[1, 1]
ax4.hist(rfm["RFM_score"], bins=12, color="#1B3A6B", edgecolor="white")
ax4.axvline(rfm["RFM_score"].quantile(0.80), color="#E8593C", linestyle="--",
            linewidth=1.5, label="Top 20%")
ax4.set_title("Distribución del RFM Score", fontweight="bold", color="#1B3A6B")
ax4.set_xlabel("RFM Score (3–15)")
ax4.set_ylabel("N° de clientes")
ax4.legend()

plt.tight_layout()
plt.savefig("rfm_dashboard.png", bbox_inches="tight", dpi=150)

rfm.to_csv("rfm_resultados.csv", index=False, encoding="utf-8-sig")
top_20.to_csv("top20_discador.csv", index=False, encoding="utf-8-sig")

print("\n  Archivos generados:")
print("    rfm_dashboard.png")
print("    rfm_resultados.csv")
print("    top20_discador.csv")
print("=" * 55)

plt.show()
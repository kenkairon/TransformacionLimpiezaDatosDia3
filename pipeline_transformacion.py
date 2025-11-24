import pandas as pd
import numpy as np

# ========== 1. CREAR DATASET ==========
np.random.seed(42)
n = 1000

df = pd.DataFrame({
    'id_cliente': range(1, n+1),
    'edad': np.random.normal(35, 15, n).clip(18, 80).astype(int),
    'ingresos': np.random.lognormal(10, 0.8, n),
    'gastos_mensuales': np.random.normal(2000, 500, n).clip(500, 10000),
    'categoria_cliente': np.random.choice(['A', 'B', 'C', 'D'], n),
    'fecha_registro': pd.date_range('2020-01-01', periods=n, freq='D')[:n],
    'email': [f'cliente{i}@ejemplo.com' for i in range(1, n+1)],
    'telefono': [f'({np.random.randint(100, 999)}){np.random.randint(100, 999)}-{np.random.randint(1000, 9999)}' for _ in range(n)]
})

# Introducir errores
error_idx = np.random.choice(n, 50, replace=False)
df.loc[error_idx[:20], 'edad'] = np.random.choice([-5, 150, np.nan], 20)
df.loc[error_idx[20:35], 'ingresos'] = -1000
df.loc[error_idx[35:], 'gastos_mensuales'] = df.loc[error_idx[35:], 'ingresos'] * 2

print("=" * 60)
print("DATOS ORIGINALES (primeras 5 filas)")
print("=" * 60)
print(df.head())
print(f"\nTotal registros: {len(df)}")

# ========== 2. VALIDACIONES Y CORRECCIONES ==========
print("\n" + "=" * 60)
print("VALIDACIONES Y CORRECCIONES")
print("=" * 60)

# Validar edades
df['edad_valida'] = df['edad'].between(18, 80, inclusive='both')
edades_inv = (~df['edad_valida']).sum()
df.loc[~df['edad_valida'], 'edad'] = np.nan
print(f"Edades inválidas corregidas: {edades_inv}")

# Validar ingresos
ingresos_neg = (df['ingresos'] < 0).sum()
df.loc[df['ingresos'] < 0, 'ingresos'] = np.nan
print(f"Ingresos negativos corregidos: {ingresos_neg}")

# Validar gastos vs ingresos
df['ratio_gasto_ingreso'] = df['gastos_mensuales'] / df['ingresos']
gastos_exc = (df['ratio_gasto_ingreso'] > 1).sum()
df.loc[df['ratio_gasto_ingreso'] > 1, 'gastos_mensuales'] = df.loc[df['ratio_gasto_ingreso'] > 1, 'ingresos'] * 0.8
print(f"Gastos excesivos ajustados: {gastos_exc}")

# ========== 3. TRANSFORMACIONES ==========
print("\n" + "=" * 60)
print("TRANSFORMACIONES Y ENRIQUECIMIENTOS")
print("=" * 60)

# Categorizar edad
df['grupo_edad'] = pd.cut(df['edad'], 
                          bins=[18, 25, 35, 50, 80], 
                          labels=['Joven', 'Adulto_Joven', 'Adulto', 'Senior'])

# Capacidad financiera
df['capacidad_ahorro'] = df['ingresos'] - df['gastos_mensuales']
df['ratio_ahorro'] = df['capacidad_ahorro'] / df['ingresos']

# Clasificación financiera
df['clasificacion_financiera'] = np.where(
    df['ratio_ahorro'] > 0.3, 'Ahorra_Mucho',
    np.where(df['ratio_ahorro'] > 0.1, 'Ahorra_Poco',
             np.where(df['ratio_ahorro'] > 0, 'Equilibra', 'Deficit')))

# Código de área
df['codigo_area'] = df['telefono'].str.extract(r'\((\d{3})\)')

# Antigüedad
df['antiguedad_dias'] = (pd.Timestamp.now() - df['fecha_registro']).dt.days
df['antiguedad_meses'] = df['antiguedad_dias'] // 30

print("Nuevas columnas creadas:")
print("- grupo_edad, capacidad_ahorro, ratio_ahorro")
print("- clasificacion_financiera, codigo_area")
print("- antiguedad_dias, antiguedad_meses")

# ========== 4. MÉTRICAS AGREGADAS ==========
print("\n" + "=" * 60)
print("MÉTRICAS POR GRUPO DE EDAD")
print("=" * 60)

metricas_edad = df.groupby('grupo_edad').agg({
    'ingresos': ['mean', 'median', 'std'],
    'capacidad_ahorro': 'mean',
    'ratio_ahorro': 'mean'
}).round(2)

print(metricas_edad)

# Resumen de clasificación financiera
print("\n" + "=" * 60)
print("DISTRIBUCIÓN DE CLASIFICACIÓN FINANCIERA")
print("=" * 60)
print(df['clasificacion_financiera'].value_counts())

# ========== 5. RESUMEN FINAL ==========
print("\n" + "=" * 60)
print("RESUMEN DE VALIDACIÓN")
print("=" * 60)

resumen = {
    'Total registros': len(df),
    'Edades inválidas': edades_inv,
    'Ingresos negativos': ingresos_neg,
    'Gastos ajustados': gastos_exc,
    'Registros procesados': len(df[df['edad'].notna() & df['ingresos'].notna()])
}

for k, v in resumen.items():
    print(f"{k}: {v}")

# Mostrar muestra final
print("\n" + "=" * 60)
print("DATOS TRANSFORMADOS (muestra)")
print("=" * 60)
cols_importantes = ['id_cliente', 'edad', 'grupo_edad', 'ingresos', 
                    'capacidad_ahorro', 'clasificacion_financiera']
print(df[cols_importantes].head(10))
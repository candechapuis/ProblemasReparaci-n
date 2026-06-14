import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from math import inf
from random import expovariate

# =============================================================================
# SIMULACIÓN DEL MODELO CON UN TÉCNICO DE REPARACIÓN
# =============================================================================

def sim_reparacion_un_tecnico(N, S, TF, TR, generar_falla, generar_reparacion):
    """
    Simula el tiempo hasta el colapso de un sistema con N máquinas
    operativas y S máquinas de repuesto.

    Parámetros:
        N (int):
            Número de máquinas en funcionamiento.
        S (int):
            Número de máquinas de repuesto disponibles.
        TF (float):
            Tiempo medio de funcionamiento de una máquina antes de fallar.
        TR (float):
            Tiempo medio de reparación de una máquina averiada.
        generar_falla (callable):
            Función que recibe TF y genera un tiempo aleatorio de
            funcionamiento antes de la siguiente falla.
        generar_reparacion (callable):
            Función que recibe TR y genera un tiempo aleatorio de
            reparación.

    Dato de salida:
        T (float):
            Tiempo de colapso del sistema, medido en la misma unidad que
            TF y TR.
    """
    # t
    # Tiempo de simulación transcurrido
    t = 0
    # Máquinas averiadas
    r = 0
    # Tiempos de falla
    tiempos_falla = []
    for i in range(N):
        fi = generar_falla(TF)
        tiempos_falla.append(fi)
    tiempos_falla.sort()
    # Tiempo de finalización de reparación actual
    tiempo_fin_rep = inf
    # Mientras las máquinas averiadas no superes las de repuesto
    while r <= S:
        # Registro si viene primero una falla o un final de reparación.
        # tiempos_falla se mantiene siempre ordenado, el primer tiempo
        # es el más pequeño (el más temprano).
        prox_evento = min(tiempos_falla[0], tiempo_fin_rep)
        # Si viene primero una falla...
        if prox_evento == tiempos_falla[0]:
            t = prox_evento
            r += 1
            if r > S:
                break
            # Si es la única máquina averiada, la reparo.
            if r == 1:
                rep = generar_reparacion(TR)
                tiempo_fin_rep = t + rep
            # La máquina es reemplazada por un repuesto con su tiempo de falla.
            nueva_falla = generar_falla(TF)
            tiempos_falla[0] = t + nueva_falla
            tiempos_falla.sort()
        # Si viene primero un tiempo de finalización de reparación...
        else:
            t = tiempo_fin_rep 
            r -= 1
            # Si hay otras máquinas averiadas, genero tiempo de reparación
            # para la siguiente.
            if r > 0:
                rep = generar_reparacion(TR)
                tiempo_fin_rep = t + rep
            # Sino, no
            else:
                tiempo_fin_rep = inf
    # Registro el tiempo de colapso
    T = t
    return T

# =============================================================================
# ESTIMACIÓN DE PARÁMETROS
# =============================================================================
# Parámetros del sistema que se van a simular
N_maquinas = 7
S_repuestos = 3
TF_medio = 1.0     # 1 mes
TR_medio = 1/8.0   # 0.125 meses
M = 10000          # Número total de réplicas de simulación

# Genero las M realizaciones del tiempo de colapso del sistema
print(f"Ejecutando {M} simulaciones del sistema...")
tiempos_reales = np.array([sim_reparacion_un_tecnico(N_maquinas, S_repuestos, TF_medio, TR_medio,expovariate, expovariate) for _ in range(M)])

# Estimadores puntuales a partir de la muestra simulada
media_muestral = np.mean(tiempos_reales)
desvio_muestral = np.std(tiempos_reales, ddof=1) # ddof=1 para estimador S (muestral)

# Muestro los resultados principales de la simulación
print("-" * 40)
print(f"RESULTADOS ESTIMACIONES:")
print(f"MTTF (Tiempo Medio al Fallo): {media_muestral:.4f} meses")
print(f"Desviación Estándar (S): {desvio_muestral:.4f} meses")
print("-" * 40)

# =============================================================================
# TESTS DE BONDAD DE AJUSTE GAMMA CON RE-ESTIMACIÓN
# =============================================================================

def calcular_T_Pearson_Gamma(datos, bins, params):
    """
    Calcula el estadístico de Pearson para evaluar la bondad de ajuste
    de una distribución Gamma a un conjunto de datos simulados.

    Parámetros:
        datos (array-like):
            Muestra de datos simulados. En este caso, contiene los tiempos
            de colapso del sistema obtenidos mediante simulación.

        bins (array-like):
            Extremos de los intervalos utilizados para agrupar los datos.
            Estos intervalos permiten comparar las frecuencias observadas
            con las frecuencias esperadas bajo la distribución ajustada.

        params (tuple):
            Parámetros de la distribución Gamma ajustada a los datos.
            Son los parámetros devueltos por stats.gamma.fit.

    Dato de salida:
        T (float):
            Valor del estadístico de Pearson, calculado como la suma de
            las diferencias cuadráticas entre frecuencias observadas y
            esperadas, normalizadas por la frecuencia esperada.
    """
    # Cuenta cuántos datos caen en cada intervalo del histograma
    obs, _ = np.histogram(datos, bins=bins)
    n_total = len(datos)
    esp = []
    # Calcula cuántos datos esperaría la Gamma ajustada en cada intervalo
    for i in range(len(bins)-1):
        p = stats.gamma.cdf(bins[i+1], *params) - stats.gamma.cdf(bins[i], *params)
        esp.append(p * n_total)
    
    esp = np.array(esp)
    # Evita divisiones por valores demasiado chicos
    esp = np.where(esp < 0.1, 0.1, esp) 
    # Estadístico de Pearson
    return np.sum((obs - esp)**2 / esp)

# Ajuste de la distribución Gamma a los datos simulados
params_reales_g = stats.gamma.fit(tiempos_reales)

# Defino los intervalos usados para el test de bondad de ajuste para ambas distribuciones
k_bins = 20
_, bins_test = np.histogram(tiempos_reales, bins=k_bins)

# Estadístico observado para la Gamma sobre los datos reales
t_obs = calcular_T_Pearson_Gamma(tiempos_reales, bins_test, params_reales_g)

# Simulación del p-valor para evaluar la bondad de ajuste Gamma
M_pvalor = 1000 # Número de muestras para el test
excesos_g = 0

for _ in range(M_pvalor):
    muestra_ficticia = stats.gamma.rvs(*params_reales_g, size=M)
    
    params_ficticios = stats.gamma.fit(muestra_ficticia)
    
    # Calculamos T sim contra su propia estimación
    t_sim = calcular_T_Pearson_Gamma(muestra_ficticia, bins_test, params_ficticios)
    
    if t_sim >= t_obs:
        excesos_g += 1

p_valor_g = excesos_g / M_pvalor

print(f"\nRESULTADOS PRUEBAS Bondad de Ajuste Gamma:")
print(f"Estadístico T observado: {t_obs:.4f}")
print(f"p-valor: {p_valor_g:.4f}")

if p_valor_g < 0.05:
    print("CONCLUSIÓN: Se rechaza H0 (La Gamma no ajusta bien).")
else:
    print("CONCLUSIÓN: No se rechaza H0 (La Gamma es un buen modelo).")


# =============================================================================
# BONDAD DE AJUSTE WEIBULL CON RE-ESTIMACIÓN
# =============================================================================

def calcular_T_Pearson_Weibull(datos, bins, params):
    """
    Calcula el estadístico de Pearson para evaluar la bondad de ajuste
    de una distribución Weibull a un conjunto de datos simulados.

    Parámetros:
        datos (array-like):
            Muestra de datos simulados. En este caso, contiene los tiempos
            de colapso del sistema obtenidos mediante simulación.

        bins (array-like):
            Extremos de los intervalos utilizados para agrupar los datos.
            Estos intervalos permiten comparar las frecuencias observadas
            con las frecuencias esperadas bajo la distribución ajustada.

        params (tuple):
            Parámetros de la distribución Weibull ajustada a los datos.
            Son los parámetros devueltos por stats.weibull_min.fit.

    Dato de salida:
        T (float):
            Valor del estadístico de Pearson, calculado como la suma de
            las diferencias cuadráticas entre frecuencias observadas y
            esperadas, normalizadas por la frecuencia esperada.
    """
    # Cuenta cuántos datos caen en cada intervalo del histograma
    obs, _ = np.histogram(datos, bins=bins)
    n_total = len(datos)
    # Calcula cuántos datos esperaría la Weibull ajustada en cada intervalo
    esp = []
    for i in range(len(bins) - 1):
        p = (
            stats.weibull_min.cdf(bins[i+1], *params)
            - stats.weibull_min.cdf(bins[i], *params)
        )
        esp.append(p * n_total)
    # Evita divisiones por valores demasiado chicos
    esp = np.array(esp)
    esp = np.where(esp < 0.1, 0.1, esp)

    # Estadístico de Pearson
    return np.sum((obs - esp)**2 / esp)

# Ajuste de la distribución Weibull a los datos simulados
params_reales_w = stats.weibull_min.fit(tiempos_reales)
t_obs_w = calcular_T_Pearson_Weibull(tiempos_reales, bins_test, params_reales_w)

# Simulación del p-valor para evaluar la bondad de ajuste Weibull
print("Simulando p-valor Weibull...")
excesos_w = 0
for _ in range(M_pvalor):
    muestra_f = stats.weibull_min.rvs(*params_reales_w, size=M)
    params_f = stats.weibull_min.fit(muestra_f) 
    t_sim_w = calcular_T_Pearson_Weibull(muestra_f, bins_test, params_f)
    if t_sim_w >= t_obs_w:
        excesos_w += 1

p_valor_w = excesos_w / M_pvalor

print(f"\nRESULTADOS PRUEBA Bondad de Ajuste Weibull:")
print(f"Estadístico T observado: {t_obs_w:.4f}")
print(f"p-valor: {p_valor_w:.4f}")

if p_valor_w < 0.05:
    print("CONCLUSIÓN: Se rechaza H0 (La Weibull no ajusta bien).")
else:
    print("CONCLUSIÓN: No se rechaza H0 (La Weibull es un modelo plausible).")

# =============================================================================
# GRÁFICOS
# =============================================================================
# Genero el gráfico comparativo entre los ajustes Gamma y Weibull
plt.figure(figsize=(10, 5))
plt.hist(tiempos_reales, bins=50, density=True, alpha=0.5, color='gray', label='Datos Simulados')

x = np.linspace(0, max(tiempos_reales), 200)
# Curva Gamma
plt.plot(x, stats.gamma.pdf(x, *params_reales_g), 'r-', lw=2, label=f'Ajuste Gamma (p={p_valor_g:.3f})')
# Curva Weibull
plt.plot(x, stats.weibull_min.pdf(x, *params_reales_w), 'b--', lw=2, label=f'Ajuste Weibull (p={p_valor_w:.3f})')

plt.title('Comparación de Ajustes: Gamma vs Weibull')
plt.xlabel('Tiempo (meses)')
plt.ylabel('Densidad')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('grafico_comparativo.png')
print("--- GRÁFICO GENERADO: 'grafico_comparativo.png' ---")

# =============================================================================
# SIMULACIÓN DEL MODELO CON DOS TÉCNICOS DE REPARACIÓN
# =============================================================================

def sim_reparacion_dos_tecnicos(N, S, TF, TR, generar_falla, generar_reparacion):
    """
    Simula el tiempo hasta el colapso de un sistema con N máquinas
    operativas, S máquinas de repuesto y dos técnicos de reparación.

    Parámetros:
        N (int):
            Número de máquinas en funcionamiento.
        S (int):
            Número de máquinas de repuesto disponibles.
        TF (float):
            Tiempo medio de funcionamiento de una máquina antes de fallar.
        TR (float):
            Tiempo medio de reparación de una máquina averiada.
        generar_falla (callable):
            Función que recibe TF y genera un tiempo aleatorio de
            funcionamiento antes de la siguiente falla.
        generar_reparacion (callable):
            Función que recibe TR y genera un tiempo aleatorio de
            reparación.

    Dato de salida:
        T (float):
            Tiempo de colapso del sistema, medido en la misma unidad que
            TF y TR.
    """
    # Tiempo de simulación transcurrido
    t = 0
    # Máquinas averiadas
    r = 0
    # Máquinas esperando reparación (máquinas averiadas que no pueden ser reparadas aún por falta de técnicos)
    esperando_rep = 0
    # Tiempos de falla
    tiempos_falla = []
    for i in range(N):
        fi = generar_falla(TF)
        tiempos_falla.append(fi)
    tiempos_falla.sort()
    # Dos técnicos: cada uno puede tener un tiempo de finalización de reparación.
    tecnicos_disponibles = 2
    tiempos_fin_rep = [inf, inf]
    # Mientras las máquinas averiadas no superes las de repuesto
    while r <= S:
        prox_falla = tiempos_falla[0]
        prox_rep = min(tiempos_fin_rep)
        prox_evento = min(prox_falla, prox_rep)
        # Si viene primero una falla...
        if prox_evento == prox_falla:
            t = prox_evento
            r += 1 
            if r > S:
                break
            # Si hay técnico libre, inicio una reparación.
            if tecnicos_disponibles > 0:
                tecnicos_disponibles -= 1
                rep = generar_reparacion(TR)
                for i in range(2):
                    if tiempos_fin_rep[i] == inf:
                        tiempos_fin_rep[i] = t + rep
                        break
                tiempos_fin_rep.sort()
            # La máquina es reemplazada por un repuesto con su tiempo de falla.
            nueva_falla = generar_falla(TF)
            tiempos_falla[0] = t + nueva_falla
            tiempos_falla.sort()
        # Si viene primero una finalización de reparación...
        else:
            t = prox_rep
            # Busco qué técnico terminó su reparación y lo libero.
            indice = tiempos_fin_rep.index(t)
            tiempos_fin_rep[indice] = inf
            tecnicos_disponibles += 1
            r -= 1
            # Cantidad de técnicos que siguen ocupados después de liberar al que terminó.
            tecnicos_ocupados = 2 - tecnicos_disponibles
            # Máquinas averiadas que NO están siendo reparadas por ningún técnico.
            maquinas_esperando = r - tecnicos_ocupados
            # Si hay máquinas esperando y un técnico libre, empieza una nueva reparación.
            if maquinas_esperando > 0 and tecnicos_disponibles > 0:
                tecnicos_disponibles -= 1
                rep = generar_reparacion(TR)
                tiempos_fin_rep[indice] = t + rep
            tiempos_fin_rep.sort()
    # Registro el tiempo de colapso
    T = t
    return T

print("\n=== SIMULACIÓN CON DOS TÉCNICOS DE REPARACIÓN ===")

# =============================================================================
# ESTIMACIÓN DE PARÁMETROS PARA EL PROBLEMA CON DOS TÉCNICOS
# =============================================================================
# Parámetros del sistema que se van a simular, mismos que antes.

# Genero las M realizaciones del tiempo de colapso del sistema, esta vez con dos técnicos de reparación.
print(f"Ejecutando {M} simulaciones del sistema...")
tiempos_reales = np.array([sim_reparacion_dos_tecnicos(N_maquinas, S_repuestos, TF_medio, TR_medio,expovariate, expovariate) for _ in range(M)])

# Estimadores puntuales a partir de la muestra simulada
media_muestral = np.mean(tiempos_reales)
desvio_muestral = np.std(tiempos_reales, ddof=1) # ddof=1 para estimador S (muestral)

# Muestro los resultados principales de la simulación
print("-" * 40)
print(f"RESULTADOS ESTIMACIONES:")
print(f"MTTF (Tiempo Medio al Fallo): {media_muestral:.4f} meses")
print(f"Desviación Estándar (S): {desvio_muestral:.4f} meses")
print("-" * 40)
# =============================================================================
# FUNCIONES AUXILIARES PARA EJERCICIOS 3 Y 4
# =============================================================================

def calcular_estadisticas_descriptivas(tiempos):
    """Calcula estadísticas descriptivas completas."""
    return {
        'media': np.mean(tiempos),
        'desv_est': np.std(tiempos, ddof=1),
        'varianza': np.var(tiempos, ddof=1),
        'minimo': np.min(tiempos),
        'maximo': np.max(tiempos),
        'mediana': np.median(tiempos),
        'q1': np.percentile(tiempos, 25),
        'q3': np.percentile(tiempos, 75),
        'iqr': np.percentile(tiempos, 75) - np.percentile(tiempos, 25),
        'asimetria': stats.skew(tiempos),
        'curtosis': stats.kurtosis(tiempos),
    }

def test_bondad_ajuste_completo(datos, distribucion='gamma', n_iteraciones=250):
    """
    Test de bondad de ajuste OPTIMIZADO (rápido para 10000 simulaciones).
    Reducido a 250 iteraciones MC para mantener tiempo razonable.
    """
    print(f"  → Calculando parámetros de {distribucion}...")
    
    if distribucion == 'gamma':
        try:
            params = stats.gamma.fit(datos, floc=0)
            calc_T = calcular_T_Pearson_Gamma
            rvs_func = stats.gamma.rvs
            nombre_dist = 'Gamma'
        except:
            params = stats.gamma.fit(datos)
            calc_T = calcular_T_Pearson_Gamma
            rvs_func = stats.gamma.rvs
            nombre_dist = 'Gamma'
    else:  # weibull
        try:
            params = stats.weibull_min.fit(datos, floc=0)
            calc_T = calcular_T_Pearson_Weibull
            rvs_func = stats.weibull_min.rvs
            nombre_dist = 'Weibull'
        except:
            params = stats.weibull_min.fit(datos)
            calc_T = calcular_T_Pearson_Weibull
            rvs_func = stats.weibull_min.rvs
            nombre_dist = 'Weibull'
    
    _, bins = np.histogram(datos, bins=20)
    t_obs = calc_T(datos, bins, params)
    
    print(f"  → Simulando p-valor con {n_iteraciones} iteraciones...")
    
    excesos = 0
    for iteracion in range(n_iteraciones):
        if (iteracion + 1) % 50 == 0:
            print(f"    Iteración {iteracion + 1}/{n_iteraciones}...", end='\r')
        
        try:
            muestra_fic = rvs_func(*params, size=len(datos))
            
            if distribucion == 'gamma':
                try:
                    params_fic = stats.gamma.fit(muestra_fic, floc=0)
                except:
                    params_fic = params
            else:
                try:
                    params_fic = stats.weibull_min.fit(muestra_fic, floc=0)
                except:
                    params_fic = params
            
            t_sim = calc_T(muestra_fic, bins, params_fic)
            
            if t_sim >= t_obs:
                excesos += 1
        except:
            continue
    
    print(f"    Iteración {n_iteraciones}/{n_iteraciones}... ✓")
    
    p_valor = excesos / n_iteraciones
    rechazar = p_valor < 0.05
    conclusion = "No se rechaza H0" if not rechazar else "Se rechaza H0"
    
    return {
        'distribucion': nombre_dist,
        'params': params,
        't_observado': t_obs,
        'p_valor': p_valor,
        'rechazar': rechazar,
        'conclusion': conclusion,
        'bins': bins
    }

# =============================================================================
# GRÁFICOS
# =============================================================================

def grafico_histograma_original(tiempos, stats_desc, test_gamma):
    """Genera histograma con curva Gamma ajustada."""
    fig, ax = plt.subplots(figsize=(12, 7))
    
    n, bins, patches = ax.hist(tiempos, bins=50, density=True, 
                               alpha=0.65, color='#419D78',
                               edgecolor='black', linewidth=1.2,
                               label=f'Datos Simulados (n={len(tiempos)})')
    
    x = np.linspace(0, np.max(tiempos), 300)
    y_gamma = stats.gamma.pdf(x, *test_gamma['params'])
    ax.plot(x, y_gamma, 'r-', lw=3, label='Ajuste Gamma', zorder=5)
    
    media = stats_desc['media']
    ax.axvline(media, color='darkgreen', linestyle='--', linewidth=2.5, 
              label=f'Media = {media:.4f} meses', zorder=4)
    
    desv = stats_desc['desv_est']
    ax.axvline(media - desv, color='orange', linestyle=':', linewidth=2, alpha=0.7)
    ax.axvline(media + desv, color='orange', linestyle=':', linewidth=2, alpha=0.7,
              label=f'±1σ = ±{desv:.4f} meses')
    
    ax.set_xlabel('Tiempo de Colapso (meses)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Densidad de Probabilidad', fontsize=12, fontweight='bold')
    ax.set_title('EJERCICIO 3: Histograma de Tiempos de Colapso\nSistema Original (N=7, S=3, 1 Técnico, M=10000)',
                fontsize=13, fontweight='bold', pad=20)
    
    textstr = f'MTTF: {media:.4f} meses\nDesv. Est.: {desv:.4f} meses\n'
    textstr += f'Min: {stats_desc["minimo"]:.4f} | Max: {stats_desc["maximo"]:.4f}\n'
    textstr += f'Asimetría: {stats_desc["asimetria"]:.4f}\np-valor Gamma: {test_gamma["p_valor"]:.4f}'
    
    ax.text(0.98, 0.97, textstr, transform=ax.transAxes,
           fontsize=10, verticalalignment='top', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
           family='monospace')
    
    ax.legend(fontsize=11, loc='upper left', framealpha=0.95)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_ylim(bottom=0)
    
    plt.tight_layout()
    plt.savefig('03_histograma_original.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfico guardado: 03_histograma_original.png")
    plt.close()

def analizar_caracteristicas_histograma(tiempos, stats_desc):
    """Análisis detallado del histograma."""
    print("\n" + "="*80)
    print("ANÁLISIS DETALLADO - EJERCICIO 3")
    print("="*80)
    
    print("\n1. MEDIDAS DE TENDENCIA CENTRAL:")
    print(f"   • Media (MTTF): {stats_desc['media']:.4f} meses")
    print(f"   • Mediana: {stats_desc['mediana']:.4f} meses")
    print(f"   • Diferencia Media-Mediana: {(stats_desc['media'] - stats_desc['mediana']):.4f} meses")
    
    print("\n2. MEDIDAS DE DISPERSIÓN:")
    print(f"   • Desviación Estándar: {stats_desc['desv_est']:.4f} meses")
    print(f"   • Varianza: {stats_desc['varianza']:.6f}")
    print(f"   • Rango Intercuartílico (IQR): {stats_desc['iqr']:.4f} meses")
    
    print("\n3. RANGO:")
    print(f"   • Mínimo: {stats_desc['minimo']:.4f} meses")
    print(f"   • Máximo: {stats_desc['maximo']:.4f} meses")
    print(f"   • Rango Total: {(stats_desc['maximo'] - stats_desc['minimo']):.4f} meses")
    
    print("\n4. FORMA:")
    print(f"   • Asimetría (Skewness): {stats_desc['asimetria']:.4f}")
    asimetria_tipo = "POSITIVA (cola derecha)" if stats_desc['asimetria'] > 0 else "NEGATIVA"
    print(f"   • Tipo: {asimetria_tipo}")
    print(f"   • Curtosis: {stats_desc['curtosis']:.4f}")
    
    print("\n" + "="*80 + "\n")

def grafico_comparativo_tres_sistemas(t_orig, t_dos_tec, t_mas_rep,
                                      test_g_orig, test_g_dos, test_g_mas):
    """Gráfico comparativo de los tres sistemas."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    sistemas = [
        (t_orig, 'Sistema Original\n(1 técnico, S=3)', '#2E86AB', test_g_orig),
        (t_dos_tec, 'Mejora V1: 2 Técnicos\n(2 técnicos, S=3)', '#A23B72', test_g_dos),
        (t_mas_rep, 'Mejora V2: +1 Repuesto\n(1 técnico, S=4)', '#F18F01', test_g_mas)
    ]
    
    for idx, (tiempos, titulo, color, test_gamma) in enumerate(sistemas):
        ax = axes[idx]
        
        ax.hist(tiempos, bins=50, density=True, alpha=0.6, 
               color=color, label='Datos Simulados', edgecolor='black', linewidth=0.8)
        
        x = np.linspace(0, np.max(tiempos), 200)
        y = stats.gamma.pdf(x, *test_gamma['params'])
        ax.plot(x, y, 'r-', lw=2.5, label='Ajuste Gamma', zorder=5)
        
        media = np.mean(tiempos)
        ax.axvline(media, color='darkgreen', linestyle='--', linewidth=2, 
                  label=f'μ={media:.4f}', zorder=4)
        
        ax.set_title(titulo, fontsize=11, fontweight='bold', pad=10)
        ax.set_xlabel('Tiempo (meses)', fontsize=10)
        ax.set_ylabel('Densidad', fontsize=10)
        ax.legend(fontsize=9, loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(bottom=0)
        
        p_val_text = f"p={test_gamma['p_valor']:.4f}"
        ax.text(0.02, 0.98, p_val_text, transform=ax.transAxes,
               fontsize=9, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
    
    plt.suptitle('EJERCICIO 4: Comparativa de Tres Configuraciones (M=10000)',
                fontsize=13, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.savefig('04_comparativo_tres_sistemas.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfico guardado: 04_comparativo_tres_sistemas.png")
    plt.close()

def tabla_resumen_estadisticas(s_orig, s_dos, s_mas):
    """Tabla con resumen de estadísticas."""
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.axis('tight')
    ax.axis('off')
    
    tabla_data = [
        ['Métrica', 'Original\n(1 técnico)', '2 Técnicos', '+1 Repuesto\n(S=4)'],
        ['MTTF (meses)', f"{s_orig['media']:.4f}", f"{s_dos['media']:.4f}", f"{s_mas['media']:.4f}"],
        ['Desv. Est. (meses)', f"{s_orig['desv_est']:.4f}", f"{s_dos['desv_est']:.4f}", f"{s_mas['desv_est']:.4f}"],
        ['Mínimo (meses)', f"{s_orig['minimo']:.4f}", f"{s_dos['minimo']:.4f}", f"{s_mas['minimo']:.4f}"],
        ['Mediana (meses)', f"{s_orig['mediana']:.4f}", f"{s_dos['mediana']:.4f}", f"{s_mas['mediana']:.4f}"],
        ['Máximo (meses)', f"{s_orig['maximo']:.4f}", f"{s_dos['maximo']:.4f}", f"{s_mas['maximo']:.4f}"],
    ]
    
    table = ax.table(cellText=tabla_data, cellLoc='center', loc='center',
                    colWidths=[0.25, 0.25, 0.25, 0.25])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.5)
    
    for i in range(4):
        table[(0, i)].set_facecolor('#40466e')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    for i in range(1, len(tabla_data)):
        table[(i, 1)].set_facecolor('#2E86AB33')
        table[(i, 2)].set_facecolor('#A23B7233')
        table[(i, 3)].set_facecolor('#F1810133')
    
    plt.title('Tabla 1: Resumen de Estadísticas Descriptivas (M=10000)',
             fontsize=12, fontweight='bold', pad=20)
    plt.savefig('06_tabla_resumen.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfico guardado: 06_tabla_resumen.png")
    plt.close()

def tabla_bondad_ajuste(test_g_orig, test_w_orig, test_g_dos, test_w_dos,
                       test_g_mas, test_w_mas):
    """Tabla de tests de bondad."""
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.axis('tight')
    ax.axis('off')
    
    tabla_test = [
        ['Sistema', 'Distribución', 'T Pearson', 'p-valor', 'Conclusión'],
        ['Original', 'Gamma', f"{test_g_orig['t_observado']:.4f}", f"{test_g_orig['p_valor']:.4f}", test_g_orig['conclusion']],
        ['Original', 'Weibull', f"{test_w_orig['t_observado']:.4f}", f"{test_w_orig['p_valor']:.4f}", test_w_orig['conclusion']],
        ['2 Técnicos', 'Gamma', f"{test_g_dos['t_observado']:.4f}", f"{test_g_dos['p_valor']:.4f}", test_g_dos['conclusion']],
        ['2 Técnicos', 'Weibull', f"{test_w_dos['t_observado']:.4f}", f"{test_w_dos['p_valor']:.4f}", test_w_dos['conclusion']],
        ['+1 Repuesto', 'Gamma', f"{test_g_mas['t_observado']:.4f}", f"{test_g_mas['p_valor']:.4f}", test_g_mas['conclusion']],
        ['+1 Repuesto', 'Weibull', f"{test_w_mas['t_observado']:.4f}", f"{test_w_mas['p_valor']:.4f}", test_w_mas['conclusion']],
    ]
    
    table = ax.table(cellText=tabla_test, cellLoc='center', loc='center',
                    colWidths=[0.2, 0.15, 0.2, 0.15, 0.3])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.2)
    
    for i in range(5):
        table[(0, i)].set_facecolor('#40466e')
        table[(0, i)].set_text_props(weight='bold', color='white', size=9)
    
    for i in range(1, 3):
        for j in range(5):
            table[(i, j)].set_facecolor('#2E86AB22')
    
    for i in range(3, 5):
        for j in range(5):
            table[(i, j)].set_facecolor('#A23B7222')
    
    for i in range(5, 7):
        for j in range(5):
            table[(i, j)].set_facecolor('#F1810122')
    
    plt.title('Tabla 2: Resultados de Tests de Bondad de Ajuste',
             fontsize=12, fontweight='bold', pad=20)
    plt.savefig('07_tabla_tests_bondad.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfico guardado: 07_tabla_tests_bondad.png")
    plt.close()

def tabla_comparativa_mejoras(s_orig, s_dos, s_mas):
    """Tabla comparativa de mejoras."""
    mejora_dos = ((s_dos['media'] - s_orig['media']) / s_orig['media'] * 100)
    mejora_mas = ((s_mas['media'] - s_orig['media']) / s_orig['media'] * 100)
    mejor_opcion = "2 Técnicos" if mejora_dos > mejora_mas else "+1 Repuesto"
    
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.axis('tight')
    ax.axis('off')
    
    tabla_mejoras = [
        ['Métrica', '2 Técnicos', '+1 Repuesto', 'Mejor'],
        ['Mejora MTTF (%)', f"{mejora_dos:+.2f}%", f"{mejora_mas:+.2f}%", mejor_opcion],
        ['MTTF (meses)', f"{s_dos['media']:.4f}", f"{s_mas['media']:.4f}", 
         f"{'2 Técnicos' if s_dos['media'] > s_mas['media'] else '+1 Repuesto'}"],
    ]
    
    table = ax.table(cellText=tabla_mejoras, cellLoc='center', loc='center',
                    colWidths=[0.3, 0.23, 0.23, 0.24])
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.3)
    
    for i in range(4):
        table[(0, i)].set_facecolor('#40466e')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    for i in range(1, len(tabla_mejoras)):
        table[(i, 1)].set_facecolor('#A23B7233')
        table[(i, 2)].set_facecolor('#F1810133')
    
    plt.title('Tabla 3: Análisis Comparativo de Mejoras',
             fontsize=12, fontweight='bold', pad=20)
    plt.savefig('08_tabla_comparativa_mejoras.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfico guardado: 08_tabla_comparativa_mejoras.png")
    plt.close()
    
    return {
        'mejora_dos_pct': mejora_dos,
        'mejora_mas_pct': mejora_mas,
        'mejor_opcion': mejor_opcion
    }

def ejecutar_ejercicios_3_y_4():
    """Ejecuta ejercicios 3 y 4 completos."""
    
    # Calcular estadísticas del sistema original
    stats_original = calcular_estadisticas_descriptivas(tiempos_reales)
    
    print(f"\n▶ EJERCICIO 3: Realizando test de bondad de ajuste (sistema original)...")
    test_gamma_orig = test_bondad_ajuste_completo(tiempos_reales, 'gamma', n_iteraciones=250)
    test_weibull_orig = test_bondad_ajuste_completo(tiempos_reales, 'weibull', n_iteraciones=250)
    
    print(f"\n▶ Generando gráfico del Ejercicio 3...")
    grafico_histograma_original(tiempos_reales, stats_original, test_gamma_orig)
    analizar_caracteristicas_histograma(tiempos_reales, stats_original)
    
    # EJERCICIO 4
    print("\n" + "="*80)
    print("EJERCICIO 4: COMPARATIVA DE MEJORAS (M=10000)")
    print("="*80)
    
    print(f"\n▶ MEJORA V1: Simulando con 2 TÉCNICOS...")
    tiempos_dos = np.array([
        sim_reparacion_dos_tecnicos(N_maquinas, S_repuestos, TF_medio, TR_medio, expovariate, expovariate)
        for _ in range(M)
    ])
    stats_dos = calcular_estadisticas_descriptivas(tiempos_dos)
    print(f"✓ MTTF 2 Técnicos: {stats_dos['media']:.4f} meses")
    
    print(f"\n▶ MEJORA V2: Simulando con +1 REPUESTO...")
    tiempos_mas = np.array([
        sim_reparacion_un_tecnico(N_maquinas, S_repuestos + 1, TF_medio, TR_medio, expovariate, expovariate)
        for _ in range(M)
    ])
    stats_mas = calcular_estadisticas_descriptivas(tiempos_mas)
    print(f"✓ MTTF +1 Repuesto: {stats_mas['media']:.4f} meses")
    
    print(f"\n▶ Realizando tests de bondad de ajuste...")
    test_gamma_dos = test_bondad_ajuste_completo(tiempos_dos, 'gamma', n_iteraciones=250)
    test_weibull_dos = test_bondad_ajuste_completo(tiempos_dos, 'weibull', n_iteraciones=250)
    
    test_gamma_mas = test_bondad_ajuste_completo(tiempos_mas, 'gamma', n_iteraciones=250)
    test_weibull_mas = test_bondad_ajuste_completo(tiempos_mas, 'weibull', n_iteraciones=250)
    
    print(f"\n▶ Generando gráficos y tablas...")
    grafico_comparativo_tres_sistemas(tiempos_reales, tiempos_dos, tiempos_mas,
                                     test_gamma_orig, test_gamma_dos, test_gamma_mas)
    
    tabla_resumen_estadisticas(stats_original, stats_dos, stats_mas)
    tabla_bondad_ajuste(test_gamma_orig, test_weibull_orig,
                       test_gamma_dos, test_weibull_dos,
                       test_gamma_mas, test_weibull_mas)
    
    resultados = tabla_comparativa_mejoras(stats_original, stats_dos, stats_mas)
    
    print("\n" + "="*80)
    print("RESUMEN FINAL")
    print("="*80)
    print(f"Mejora 2 Técnicos: {resultados['mejora_dos_pct']:+.2f}%")
    print(f"Mejora +1 Repuesto: {resultados['mejora_mas_pct']:+.2f}%")
    print(f"MEJOR OPCIÓN: {resultados['mejor_opcion']}")
    print("="*80 + "\n")

if __name__ == "__main__":
    ejecutar_ejercicios_3_y_4()
    print("\n>>> PROCESO FINALIZADO")
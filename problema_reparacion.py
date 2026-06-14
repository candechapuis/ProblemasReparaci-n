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


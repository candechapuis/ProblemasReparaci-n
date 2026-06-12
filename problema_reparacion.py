
from math import inf
from random import expovariate

def sim_reparacion(N, S, TF, TR, generar_falla, generar_reparacion):
    """
    Simulación de un sistema con N máquinas en funcionamiento
    y S máquinas de repuesto.

    Parámetros:
        N (int) : 
            número de máquinas en funcionamiento.
        S (int) : 
            número de máquinas de repuesto.
        TF (float) : 
            tiempo medio de funcionamiento de una máquina antes de fallar.
        TR (float) : 
            tiempo medio de reparación de una máquina averiada.
        generar_falla (callable[float]) : 
            función que  recibe TF y genera un tiempo aleatorio de 
            funcionamiento de una máquina antes de fallar.
        generar_reparación (callable[float]) : 
            función que recibe TR y genera un tiempo aleatorio de
            reparación de una máquina averiada.
    
    Dato de salida:
        T (float):
            tiempo de colapso del sistema.
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

# Prueba
def gen_exp(lamda):
    return expovariate(lamda)

colapso = sim_reparacion(3, 1, 1, 1,expovariate, expovariate)
print(colapso)


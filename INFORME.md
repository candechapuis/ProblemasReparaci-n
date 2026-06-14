# Generación de eventos discretos - Problemas de reparación 

### Modelos y Simulación - FaMAF - 2026

-----------------------------------------------------------------------

## Descripción del problema

Se presenta el sistema de un pequeño supermercado que cuenta con *N* cajas registradoras en servicio y con *S* máquinas de repuesto, todas ellas de idéntica marca, modelo y antigüedad. Dicho suprmercado tiene, además, un técnico que repara las máquinas *en serie*, encargándose de una sola por vez. 

Cuando una caja en uso falla, es reemplazada inmediatamente por un repuesto y enviada a reparación con el técnico.

El sistema *falla* o *colapsa* cuando la cantidad de máquinas defectuosas esperando a ser reparadas supera a la cantidad de repuestos disponibles.

Todos los tiempos de funcionamiento de las cajas hasta descomponerse son variables independientes exponenciales con un tiempo medio hasta fallar de *TF*, y el tiempo de reparación de una caja que ingresa a taller es una variable exponencial con tiempo medio igual a *TR*, independiente de todos los anteriores.

Este problema es conocido como: **Modelo de reparación**

El objetivo de este proyecto es, primero, estimar el tiempo medio de fallo del sistema y su correspondiente desviación estándar de dicho sistema, para un *N*, *S*, *TF* y *TR* dados. Luego se quiere poder crear una hipótesis sobre la distribución a la que se podría ajustar el tiempo medio y la desviación.

Como segundo objetivo, se desea analizar, dadas dos posibles mejoras para el sistema, cuál es mejor. Las dos opciones son: contratar dos operarios, o bien comprar otra caja extra como repuesto. Para ello también estimaremos el tiempo medio de fallo del sistema. Luego, al igual que para el sistema original, querremos crear una hipótesis sobre la distribución que podría tener dicho tiempo medio.

## Resolución

Primero escribimos un programa que simule este modelo para *N* cajas registradoras, *S* cajas de respuesto, *TF* tiempo medio hasta fallar de las máquinas y *TR* tiempo medio que tarda el técnico en repararlas.

Usamos las siguientes variables:

* **Tiempo *t***: tiempo de simulación transcurrido
* **Estado *r***: número de cajas que están averiadas (en reparación o en espera de ser reparadas) al tiempo *t*.
* **Generadora de tiempos de falla *generar_falla***: generará los tiempos de funcionamiento de las máquinas desde que entran en uso hasta que fallan.
* **Generadora de tiempo de reparación *generar_reparacion***: generará los tiempos que tarda el técnico en reparar cada máquina.
* **Tiempo *tiempo_fin_rep*** : tiempo de finalización de reparación actual (t + tiempo generado por G).
* **Tiempo de colapso *T***: tiempo en el que el sistema colapsó.

El algoritmo implementado puede desglosarse en pasos:

1. Se inicializan las variables y otras estructuras auxiliares para el correcto funcionamiento del programa: 
   * *t*, *r* = 0
   * Se crea un arreglo *tiempos_falla* con los *N* tiempos de falla para cada una de las cajas en funcionamiento, ya sean originales o repuestos. Son generados por *generar_falla*. El arreglo debe quedar con los tiempos ordenados de menor a mayor.
   * *tiempo_fin_rep* = infinito (todavía no hay ninguna caja en reparación).

Mientras la cantidad de cajas averiadas *r* no supere a la cantidad de cajas de repuesto *S*:

2. Encuentro el próximo evento a ocurrir, ya sea el fallo de una caja o la finalización de alguna reparación:

   * **Si es un fallo**: 

     i. Actualizo el tiempo transcurrido *t*, aumento las cajas averiadas *r*.

     ii. Chequeo si las cajas averiadas *r* superan a los repuestos *S*, si lo hacen, finalizo la simulación.

     iii.. Si hay una sola caja averiada, entonces genero un tiempo de demora de reparación con *G* y actualizo *tiempo_fin_rep*.

     iv. Genero un nuevo tiempo de funcionamiento con *generar_falla* para el repuesto que reemplaza a la caja averiada y se lo asigno en el arreglo *tiempos_falla*. Luego reordeno mi arreglo *tiempos_falla*. 

   * **Si es la finalización de la reparación:**

     i. Actualizo el tiempo transcurrido *t*, disminuyo las cajas averiadas *r*.

     ii. Si tengo cajas averiadas aún, genero un nuevo tiempo de demora de reparación con *generar_reparacion* . Sino, no genero nada. 

     iii. Actualizo *tiempo_fin_rep* dependiendo del caso (con un nuevo tiempo o con infinito).

Cuando la cantidad de cajas averiadas *r* supere a los repuestos *S*:

3. Asigno a *T* el tiempo transcurrido *t* y lo doy como dato de salida.

*Aclaración:* Para este problema particular, en donde las cajas son idénticas y los tiempos son exponenciales independientes, no es necesario llevar registro de **qué** caja particular falló. Lo importante aquí es **cuántas** cajas están averiadas en simultáneo y si superan o no a la cantidad de repuestos disponibles.

# Resultados y Análisis Estadístico (Ejercicio 1)

Para validar el comportamiento del sistema bajo las condiciones iniciales, se realizaron **M = 10.000** simulaciones utilizando los parámetros:

* **N = 7** cajas en funcionamiento.
* **S = 3** cajas de repuesto.
* **TF = 1.0** mes (tiempo medio hasta la falla).
* **TR = 0.125** meses (tiempo medio de reparación).

---

## 1. Estimación de Parámetros (Punto B)

A partir de las muestras obtenidas se calcularon los estimadores puntuales para el tiempo medio de fallo del sistema (MTTF) y su dispersión, utilizando los estimadores muestrales insesgados presentados en las Secciones 7.3.4 y 7.3.5 de las notas.

| Métrica                      | Símbolo   | Valor Simulado |
| ---------------------------- | --------- | -------------- |
| Tiempo Medio al Fallo (MTTF) | $\bar{X}$ | 0.5774 meses   |
| Desviación Estándar Muestral | $S$       | 0.2941 meses   |

### Interpretación de los resultados

El MTTF obtenido (~0.58 meses) es notablemente inferior al tiempo medio de falla individual de una caja registradora ($TF = 1$ mes). Este comportamiento evidencia que el principal factor limitante del sistema es la tasa de falla combinada de las siete cajas operando simultáneamente.

Dado que cada caja falla con tasa $\lambda = 1$, la tasa total de fallas del sistema es aproximadamente:

$$
\lambda_{total} = 7
$$

Por otra parte, el técnico posee una tasa media de reparación:

$$
\mu = \frac{1}{TR} = \frac{1}{0.125} = 8
$$

La cercanía entre ambas tasas implica que el sistema opera en un régimen de alta utilización. En estas condiciones, pequeñas acumulaciones de fallas pueden superar rápidamente la capacidad de reparación disponible, provocando el colapso del sistema en tiempos relativamente cortos.

---

## 2. Análisis de Distribución y Bondad de Ajuste (Punto C)

Con el objetivo de caracterizar estadísticamente el tiempo hasta el colapso, se analizó el histograma de frecuencias obtenido a partir de las simulaciones y se evaluaron dos modelos probabilísticos alternativos:

* Distribución Gamma.
* Distribución Normal.

![Comparación de ajustes](grafico_comparativo.png)

### Análisis Morfológico y Físico

El histograma presenta una marcada **asimetría positiva** y una densidad prácticamente nula en el origen ($t = 0$).

Esta característica tiene una interpretación física importante: dado que el sistema dispone de **3 máquinas de repuesto**, resulta imposible que colapse instantáneamente. Para alcanzar el estado de fallo global es necesario acumular al menos **4 fallas simultáneas**.

La Distribución Gamma modela naturalmente este fenómeno mediante su parámetro de forma ($\alpha$), mientras que la Distribución Normal presenta limitaciones evidentes, ya que asigna probabilidad a valores cercanos a cero e incluso a tiempos negativos, los cuales carecen de significado físico en este contexto.

---

### Validación mediante Test $\chi^2$ con Re-estimación

Para evitar el sesgo asociado a la estimación de parámetros sobre la misma muestra utilizada para evaluar el ajuste, se siguió el procedimiento recomendado en las páginas 147 y 155 de las notas de la materia.

Se empleó el estadístico de Pearson:

$$
T = \sum_{i=1}^{k}\frac{(N_i -n*P_i)^2}{n*P_i}
$$

donde:

* $O_i$ representa la frecuencia observada en el intervalo $i$.
* $E_i$ representa la frecuencia esperada bajo la distribución ajustada.

El p-valor fue estimado mediante simulación Monte Carlo con **1.000 iteraciones**, re-estimando los parámetros de cada distribución en cada réplica.

Los resultados obtenidos fueron:

| Distribución Hipotética | Estadístico T (Pearson) | p-valor Simulado | Veredicto           |
| ----------------------- | ----------------------- | ---------------- | ------------------- |
| Gamma                   | 13.9419                 | 0.6610           | No se rechaza $H_0$ |
| Normal                  | 2711.5849               | 0.0000           | Se rechaza $H_0$    |

---

## Conclusión del Análisis

### Rechazo de la Distribución Normal

La hipótesis de normalidad es claramente incompatible con los datos observados. A pesar de la gran cantidad de eventos involucrados, el proceso de colapso no satisface las condiciones necesarias para que el Teorema Central del Límite produzca una aproximación normal adecuada.

La principal razón es que:

* Los tiempos son estrictamente positivos.
* El proceso presenta una fuerte asimetría.
* El fallo global depende de la acumulación de eventos discretos de falla.

Estas características generan una distribución sesgada hacia la derecha, incompatible con la simetría propia de la Normal.

### Aceptación de la Distribución Gamma

El ajuste Gamma obtuvo un p-valor de:

$$
p = 0.6610
$$

valor ampliamente superior al nivel de significancia habitual:

$$
\alpha = 0.05
$$

Por lo tanto, **no existe evidencia estadística suficiente para rechazar la hipótesis de que los datos provienen de una Distribución Gamma**.

Además de su respaldo estadístico, este modelo resulta físicamente consistente con la estructura del problema. El parámetro de forma estimado:

$$
\alpha \approx 3.64
$$

sugiere que el colapso ocurre tras la acumulación de aproximadamente cuatro eventos de falla, resultado coherente con el hecho de que el sistema dispone de tres máquinas de repuesto y falla al producirse la cuarta avería simultánea.

En consecuencia, la **Distribución Gamma constituye un modelo estadísticamente robusto y físicamente coherente para describir el tiempo de vida del sistema**.

# Generación de eventos discretos - Problemas de reparación 

### Modelos y Simulación - FaMAF - 2026

-----------------------------------------------------------------------

## Descripción del problema

Se presenta el sistema de un pequeño supermercado que cuenta con *N* cajas registradoras en servicio y con *S* máquinas de repuesto, todas ellas de idéntica marca, modelo y antigüedad. Dicho suprmercado tiene, además, un técnico que repara las máquinas *en serie*, encargándose de una sola por vez. 

Cuando una caja en uso falla, es reemplazada inmediatamente por un repuesto y enviada a reparación con el técnico.

El sistema *falla* o *colapsa* cuando la cantidad de máquinas defectuosas esperando a ser reparadas supera a la cantidad de repuestos disponibles.

Todos los tiempos de funcionamiento de las cajas hasta descomponerse son variables independientes exponenciales con un tiempo medio hasta fallar de *TF*, y el tiempo de reparación de una caja que ingresa a taller es una variable exponencial con tiempo medio igual a *TR*, independiente de todos los anteriores.

Este problema es conocido como: **Modelo de reparación**

El objetivo de este proyecto es, primero, estimar el tiempo medio de fallo del sistema y su correspondiente desviación estándar de dicho sistema, para un *N*, *S*, *TF* y *TR* dados. Luego se quiere poder crear una hipótesis sobre la distribución a la que se podría ajustar el tiempo medio.

Como segundo objetivo, se desea analizar, dadas dos posibles mejoras para el sistema, cuál es mejor. Las dos opciones son: contratar dos operarios, o bien comprar otra caja extra como repuesto. Para ello también estimaremos el tiempo medio de fallo del sistema. Luego, al igual que para el sistema original, querremos crear una hipótesis sobre la distribución que podría tener dicho tiempo medio.

## Primer objetivo: sistema con un técnico.

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

## Resultados y Análisis Estadístico

Para validar el comportamiento del sistema bajo las condiciones iniciales, se realizaron **M = 10.000** simulaciones utilizando los parámetros:

* **N = 7** cajas en funcionamiento.
* **S = 3** cajas de repuesto.
* **TF = 1.0** mes (tiempo medio hasta la falla).
* **TR = 0.125** meses (tiempo medio de reparación).

-------------------------------

### Estimación de Parámetros

A partir de las muestras obtenidas se calcularon los estimadores puntuales para el tiempo medio de fallo del sistema (MTTF) y su dispersión, utilizando los estimadores muestrales insesgados media muestral y varianza muestral.

| Métrica                      | Valor Simulado |
| ---------------------------- | -------------- |
| Tiempo Medio al Fallo (MTTF) | 0.5774 meses   |
| Desviación Estándar Muestral | 0.2941 meses   |

### Interpretación de los resultados

El MTTF obtenido (~0.58 meses) es notablemente inferior al tiempo medio de falla individual de una caja registradora (TF = 1 mes). Este comportamiento evidencia que el principal factor limitante del sistema es la tasa de falla combinada de las siete cajas operando simultáneamente.

Dado que cada caja falla con tasa $/lambda = 1$, la tasa total de fallas del sistema es aproximadamente:

$$
\lambda_{total} = 7
$$

Por otra parte, el técnico posee una tasa media de reparación:

$$
\mu = \frac{1}{TR} = \frac{1}{0.125} = 8
$$

La cercanía entre ambas tasas implica que el sistema opera en un régimen de alta utilización. En estas condiciones, pequeñas acumulaciones de fallas pueden superar rápidamente la capacidad de reparación disponible, provocando el colapso del sistema en tiempos relativamente cortos.

-------------------------------

### Análisis de Distribución y Bondad de Ajuste

Con el objetivo de caracterizar estadísticamente el tiempo hasta el colapso, se analizó el histograma de frecuencias obtenido a partir de las simulaciones y se evaluaron dos modelos probabilísticos alternativos: 

* Distribución Gamma 
* Distribución Weibull. 

![Comparación de ajustes](grafico_comparativo.png)

### Análisis Morfológico y Físico

El histograma presenta una marcada **asimetría positiva** y una densidad prácticamente nula en el origen ($t = 0$).

Esta característica tiene una interpretación física importante: dado que el sistema dispone de **3 máquinas de repuesto**, resulta imposible que colapse instantáneamente. Para alcanzar el estado de fallo global es necesario acumular al menos **4 fallas simultáneas**.

Tanto la Distribución Gamma como la Distribución Weibull resultan razonables para este análisis, ya que ambas están definidas para valores positivos y pueden representar distribuciones asimétricas. La Gamma es una candidata natural cuando se estudian tiempos acumulados hasta que ocurren varios eventos, mientras que la Weibull es frecuentemente utilizada para modelar tiempos de vida o tiempos hasta la falla. Por ello, ambas distribuciones son compatibles, al menos desde el punto de vista cualitativo, con la forma observada en el histograma.

---

### Validación mediante Test $\chi^2$ con Re-estimación

Para evaluar si los tiempos de colapso simulados pueden ser modelados mediante una determinada distribución teórica, se realizó una prueba de bondad de ajuste. Para cada distribución candidata se planteó la hipótesis nula:
$$
\
H_0: \text{los tiempos de colapso provienen de la distribución ajustada}
$$
frente a la hipótesis alternativa:
$$
H_1: \text{los tiempos de colapso no provienen de dicha distribución.}
$$
Como los tiempos de colapso son variables continuas, para aplicar el estadístico de Pearson se agruparon previamente los datos en $k$ intervalos o clases. En cada intervalo se comparó la frecuencia observada con la frecuencia esperada bajo la distribución ajustada.

Se empleó el estadístico de Pearson:

$$
T = \sum_{i=1}^{k}\frac{(N_i -n*P_i)^2}{n*P_i}
$$

donde:

* donde:
  - $N_i$ representa la frecuencia observada en el intervalo $i$.
  - $n$ es la cantidad total de simulaciones.
  - $P_i$ es la probabilidad que la distribución ajustada asigna al intervalo $i$.
  - $nP_i$ representa la frecuencia esperada bajo la distribución ajustada.

Si el intervalo $i$ tiene extremos $b_i$ y $b_{i+1}$, entonces:
$$
P_i = F(b_{i+1}) - F(b_i)
$$
donde $F$ es la función de distribución acumulada del modelo ajustado.

Se optó por esta prueba porque el análisis partió del histograma de los tiempos simulados, por lo que resulta natural comparar frecuencias observadas y esperadas en intervalos. El test de Kolmogorov-Smirnov también es una alternativa válida para datos continuos, ya que compara la función de distribución empírica con la función de distribución teórica sin agrupar los datos. Sin embargo, en este trabajo se utilizó el test de Pearson sobre datos agrupados.

Dado que los parámetros de cada distribución fueron estimados a partir de la misma muestra utilizada para evaluar el ajuste, el p-valor no se obtuvo directamente de una tabla $\chi^2$. En su lugar, se estimó mediante simulación Monte Carlo con 1.000 iteraciones. En cada iteración se generó una muestra ficticia desde la distribución ajustada, se reestimaron sus parámetros y se recalculó el estadístico de Pearson. Finalmente, el p-valor se estimó como la proporción de réplicas en las que el estadístico simulado resultó mayor o igual al estadístico observado.

Los resultados obtenidos fueron:

| Distribución Hipotética | Estadístico T (Pearson) | p-valor Simulado | Veredicto           |
| ----------------------- | ----------------------- | ---------------- | ------------------- |
| Gamma                   | 13.9419                 | 0.6610           | No se rechaza $H_0$ |
| Weibull                 | 301.2051                | < 0.001          | Se rechaza $H_0$    |

---

## Conclusión del Análisis

### Rechazo de la Distribución Weibull

La hipótesis de que los tiempos de colapso provienen de una Distribución Weibull fue rechazada por la prueba de bondad de ajuste. El estadístico de Pearson observado resultó elevado en comparación con los valores obtenidos en las réplicas simuladas bajo dicha distribución, y el p-valor simulado fue menor que el nivel de significancia habitual:
$$
\alpha = 0.05
$$
En particular, dado que se realizaron 1.000 réplicas Monte Carlo para estimar el p-valor, obtener un valor reportado como (0.0000) debe interpretarse como:
$$
p < 0.001
$$
y no como un p-valor exactamente nulo. Esto indica que, bajo el modelo Weibull ajustado, sería muy poco probable obtener una discrepancia entre frecuencias observadas y esperadas tan grande como la observada en los datos simulados. Por lo tanto, se rechaza la hipótesis nula para la Distribución Weibull.Aceptación de la Distribución Gamma

### No rechazo de la Distribucón Gamma

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

Este resultado indica que, de las distribuciones consideradas, la Gamma proporciona el ajuste más adecuado según la prueba de bondad de ajuste realizada. Además, esta conclusión es coherente con la interpretación cualitativa del histograma, ya que los tiempos de colapso son positivos y presentan asimetría hacia la derecha.

En consecuencia, aunque tanto Gamma como Weibull eran candidatas razonables desde el punto de vista morfológico, la prueba estadística favorece claramente a la Distribución Gamma como modelo para describir los tiempos de colapso del sistema simulado.

---------------------

## Segundo objetivo: comparación de mejoras.

### Sistema con dos técnicos

## Simulación del modelo con dos técnicos

## Simulación del modelo con dos técnicos

Para analizar la alternativa de contratar un segundo técnico, escribimos un nuevo programa que simula el modelo de reparación para *N* cajas registradoras, *S* cajas de repuesto, *TF* tiempo medio hasta fallar de las máquinas y *TR* tiempo medio que tarda cada técnico en reparar una máquina.

La estructura general es similar al caso con un solo técnico: cuando una caja en funcionamiento falla, es reemplazada inmediatamente por un repuesto y enviada a reparación. La diferencia principal es que ahora hay dos técnicos trabajando en paralelo, por lo que pueden repararse hasta dos cajas averiadas simultáneamente. Si ambos técnicos están ocupados, las nuevas cajas averiadas quedan esperando hasta que alguno termine su reparación.

Usamos las siguientes variables:

- **Tiempo \*t\***: tiempo de simulación transcurrido.
- **Estado \*r\***: número total de cajas averiadas al tiempo *t*, incluyendo tanto las que están siendo reparadas como las que están esperando reparación.
- **Generadora de tiempos de falla \*generar_falla\***: generará los tiempos de funcionamiento de las máquinas desde que entran en uso hasta que fallan.
- **Generadora de tiempos de reparación \*generar_reparacion\***: generará los tiempos que tarda cada técnico en reparar una caja averiada.
- **Tiempos de falla \*tiempos_falla\***: arreglo que contiene los tiempos de falla de las *N* cajas que se encuentran en funcionamiento, ya sean originales o repuestos.
- **Técnicos disponibles \*tecnicos_disponibles\***: cantidad de técnicos libres en cada instante de la simulación.
- **Tiempos de finalización de reparación \*tiempos_fin_rep\***: arreglo que contiene los tiempos de finalización de reparación de cada técnico. Si un técnico está libre, su tiempo asociado es infinito.
- **Tiempo de colapso \*T\***: tiempo en el que el sistema colapsó.

El algoritmo implementado puede desglosarse en pasos:

1. Se inicializan las variables y estructuras auxiliares para el correcto funcionamiento del programa:
   - *t*, *r* = 0.
   - Se crea un arreglo *tiempos_falla* con los *N* tiempos de falla para cada una de las cajas en funcionamiento, ya sean originales o repuestos. Son generados por *generar_falla*. El arreglo debe quedar con los tiempos ordenados de menor a mayor.
   - Se inicializa *tecnicos_disponibles* = 2, ya que al comienzo ambos técnicos están libres.
   - Se crea un arreglo *tiempos_fin_rep* con dos valores infinitos, uno por cada técnico, ya que inicialmente no hay ninguna caja en reparación.

Mientras la cantidad de cajas averiadas *r* no supere a la cantidad de cajas de repuesto *S*:

1. Encuentro el próximo evento a ocurrir. Este puede ser el fallo de una caja o la finalización de una reparación por parte de alguno de los técnicos.

   - La próxima falla está dada por el menor valor del arreglo *tiempos_falla*.
   - La próxima finalización de reparación está dada por el menor valor del arreglo *tiempos_fin_rep*.

   El próximo evento será el mínimo entre ambos tiempos.

2. **Si es un fallo**:

   i. Actualizo el tiempo transcurrido *t* al instante en que ocurre la falla.

   ii. Aumento en una unidad la cantidad de cajas averiadas *r*.

   iii. Chequeo si las cajas averiadas *r* superan a los repuestos *S*. Si lo hacen, finalizo la simulación porque el sistema colapsó.

   iv. Si el sistema no colapsa, la caja fallada es reemplazada inmediatamente por un repuesto. Entonces genero un nuevo tiempo de funcionamiento con *generar_falla* para ese repuesto y actualizo el arreglo *tiempos_falla*. Luego reordeno dicho arreglo.

   v. Si hay al menos un técnico disponible, la caja averiada comienza a ser reparada inmediatamente. Para ello genero un tiempo de reparación con *generar_reparacion*, actualizo el tiempo de finalización de reparación correspondiente a ese técnico y disminuyo en uno la cantidad de técnicos disponibles.

   vi. Si no hay técnicos disponibles, la caja averiada queda esperando. En este caso no se genera todavía un nuevo tiempo de reparación, ya que la reparación comenzará recién cuando alguno de los técnicos quede libre.

3. **Si es la finalización de una reparación**:

   i. Actualizo el tiempo transcurrido *t* al instante en que termina la reparación.

   ii. Identifico cuál de los técnicos terminó su reparación y lo marco como disponible.

   iii. Disminuyo en una unidad la cantidad de cajas averiadas *r*, ya que una caja fue reparada.

   iv. Calculo cuántos técnicos siguen ocupados y, a partir de eso, cuántas cajas averiadas permanecen esperando reparación. Esto es necesario porque no toda caja averiada está necesariamente esperando: algunas pueden estar siendo reparadas por el otro técnico.

   v. Si hay cajas averiadas esperando y hay un técnico libre, asigno inmediatamente una nueva reparación a ese técnico. Para ello genero un nuevo tiempo de reparación con *generar_reparacion* y actualizo el tiempo de finalización correspondiente.

   vi. Finalmente, reordeno el arreglo *tiempos_fin_rep* para poder identificar correctamente cuál será la próxima reparación en finalizar.

Cuando la cantidad de cajas averiadas *r* supere a los repuestos *S*:

4. Asigno a *T* el tiempo transcurrido *t* y lo doy como dato de salida.




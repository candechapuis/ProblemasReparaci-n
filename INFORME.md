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



# Análisis Detallado de Resultados - Ejercicios 3 y 4

## Ejercicio 3: Análisis del Histograma de Tiempos de Colapso

### 3.1 Introducción y Contexto

En este ejercicio se analizan los tiempos de colapso del sistema original (N=7 máquinas, S=3 repuestos, 1 técnico) a partir de **10,000 simulaciones**. El objetivo es caracterizar la distribución de probabilidad del tiempo hasta el fallo del sistema y evaluar su comportamiento bajo las condiciones operativas especificadas.

---

### 3.2 Medidas de Tendencia Central

#### 3.2.1 Media (MTTF)

**Valor observado: 0.5829 meses**

El tiempo medio al fallo (MTTF) representa el valor promedio del tiempo transcurrido hasta que el sistema colapse. Este valor es significativamente inferior al tiempo medio de falla individual de una caja registradora (TF = 1.0 mes), lo que evidencia un **efecto multiplicador del riesgo** en sistemas con múltiples componentes.

**Interpretación física:**

Cada una de las 7 cajas registradoras falla de manera independiente con una tasa de falla exponencial de λ = 1/TF = 1 falla por mes. Por lo tanto, la **tasa de falla agregada** del sistema es:

$$\lambda_{total} = 7 \times 1 = 7 \text{ fallos por mes}$$

Esto implica que es altamente probable que alguna de las 7 cajas falle en tiempos muy cortos. El sistema colapsará cuando se acumulen **más de 3 fallas simultáneas** (superando el número de repuestos disponibles).

El tiempo medio hasta que ocurra la cuarta falla en un sistema con tasa agregada de 7 fallos/mes es aproximadamente:

$$E[T] \approx \frac{4}{7} \approx 0.571 \text{ meses}$$

Este valor teórico coincide notablemente con el MTTF simulado de 0.5829 meses, lo que **valida la correctitud del algoritmo de simulación**.

#### 3.2.2 Mediana

**Valor observado: 0.5313 meses**

La mediana es el valor que divide la distribución en dos mitades con igual probabilidad. En el 50% de las simulaciones, el sistema colapsó antes de 0.5313 meses.

**Relación Media-Mediana:**

$$\text{Diferencia} = 0.5829 - 0.5313 = 0.0516 \text{ meses}$$

La media es **mayor que la mediana** (diferencia de 0.0516 meses), lo que indica una **asimetría positiva** en la distribución. Esto significa que existen valores extremadamente altos en la cola derecha de la distribución que "tiran" la media hacia arriba.

**Implicación:** Aunque la mayoría de colapsos ocurren cerca de 0.53 meses, en ocasiones excepcionales el sistema puede mantenerse operativo significativamente más tiempo.

---

### 3.3 Medidas de Dispersión

#### 3.3.1 Desviación Estándar

**Valor observado: 0.2977 meses**

La desviación estándar mide la dispersión de los tiempos de colapso alrededor de la media. Un valor de 0.2977 meses indica que típicamente los tiempos varían aproximadamente ±0.30 meses respecto del promedio.



#### 3.3.2 Varianza

**Valor observado: 0.088648 meses²**

La varianza es el cuadrado de la desviación estándar:

$$\sigma^2 = (0.2977)^2 = 0.0886 \text{ meses}^2$$

Este valor se utiliza en cálculos estadísticos posteriores (intervalos de confianza, pruebas de hipótesis, etc.).

#### 3.3.3 Rango Intercuartílico (IQR)

**Valor observado: 0.3778 meses**

El IQR es la diferencia entre el tercer cuartil (Q3) y el primer cuartil (Q1):

$$IQR = Q3 - Q1$$

Esto significa que el **50% central de la distribución** está contenido en un intervalo de aproximadamente 0.38 meses. 

**Interpretación:**
- El 25% de los colapsos ocurren antes de Q1
- El 50% central ocurre en el intervalo [Q1, Q3] de ancho 0.38 meses
- El 25% final (los colapsos más tardíos) ocurren después de Q3

El IQR es más **robusto a valores atípicos** que la desviación estándar, por lo que proporciona una visión más confiable de la dispersión en datos con colas pesadas.

---



### 3.5 Forma de la Distribución

#### 3.5.1 Asimetría (Skewness)

**Valor observado: 1.0436**

La asimetría mide el grado de simetría de una distribución:

- **Asimetría = 0:** Distribución perfectamente simétrica
- **Asimetría > 0:** Asimetría positiva (cola derecha)
- **Asimetría < 0:** Asimetría negativa (cola izquierda)

**Interpretación del valor 1.0436:**

El valor observado es **1.0436 > 0.5**, lo que indica una asimetría **moderadamente fuerte hacia la derecha**.

**¿Qué significa físicamente?**

1. La distribución es **unimodal** con pico alrededor de 0.5-0.6 meses
2. Existe una **cola larga hacia la derecha** con valores que se extienden hasta 2.33 meses
3. Hay muy pocos valores por debajo del mínimo (cercano a 0), consistente con el hecho de que necesitan ocurrir al menos 4 fallas para el colapso

**Comparación con otras distribuciones:**
- Distribución exponencial: asimetría = 2 (muy asimétrica)
- Distribución Gamma(k=3): asimetría ≈ 1.15 (moderadamente asimétrica)
- Distribución Normal: asimetría = 0 (simétrica)

El valor observado de 1.04 es **próximo a la asimetría esperada para una Gamma con parámetro de forma k ≈ 3-4**, lo que sugiere que la distribución es aproximadamente **Gamma**.


---

### 3.6 Histograma Detallado del Sistema Original

![Histograma Sistema Original](./03_histograma_original.png)

#### 3.6.1 Análisis Visual del Histograma

**Características Morphológicas:**

- **Distribución unimodal:** Un único pico máximo bien definido alrededor de 0.45-0.50 meses
- **Asimetría positiva visible:** Cola que se extiende gradualmente hacia 2.5 meses
- **Pico pronunciado:** Densidad máxima de aproximadamente 1.45 en la moda
- **Densidad inicial:** Comienza con valores bajos en t ≈ 0 (no hay densidad en t = 0)

**Banda de Confianza ±1σ:**

Las líneas punteadas en naranja muestran:
- Media - σ = 0.5829 - 0.2977 = 0.2852 meses (línea izquierda)
- Media + σ = 0.5829 + 0.2977 = 0.8806 meses (línea derecha)

**Interpretación:**

Según la **regla empírica**, aproximadamente el 68% de los datos deberían caer dentro de ±1σ. Observando el histograma:
- Aproximadamente 68% del área bajo el histograma cae entre las dos líneas punteadas
- Esto valida que la distribución es aproximadamente normal o gamma-like

**Ajuste Gamma (curva roja):**

La curva teórica roja superpuesta muestra el ajuste de la distribución Gamma:
- Sigue fielmente el pico del histograma
- Captura correctamente la asimetría
- Modela bien la cola derecha
- No hay desviaciones sistemáticas visibles

#### 3.6.2 Interpretación de Información en el Recuadro

El recuadro de texto en la esquina superior derecha contiene:
- **MTTF: 0.5829 meses** - Tiempo promedio al colapso (~17.5 días)
- **Desv. Est.: 0.2977 meses** - Variabilidad típica (~9 días)
- **Min: 0.0449 | Max: 2.3308** - Rango observado
- **Asimetría: 1.0436** - Grado de asimetría positiva
- **p-valor Gamma: 0.1240** - Bondad de ajuste (no rechazamos Gamma)

---

### 3.7 Pruebas de Bondad de Ajuste - Distribución Gamma

#### 3.7.1 Resultados del Test

| Métrica | Valor |
|---------|-------|
| **T Pearson (Observado)** | 24.5808 |
| **p-valor Simulado** | 0.1240 |
| **Conclusión** | No se rechaza H₀ |

#### 3.7.2 Interpretación del p-valor

El **p-valor de 0.1240** significa que:

$$P(\text{T} \geq 24.5808 \mid H_0 \text{ verdadera}) = 0.1240 = 12.40\%$$

Es decir, si los datos provinieran realmente de una distribución Gamma con los parámetros estimados, existiría una probabilidad del **12.4%** de observar un estadístico de Pearson igual o mayor al observado.

**Decisión estadística:**

Como p-valor = 0.1240 > 0.05, **no rechazamos la hipótesis nula** al nivel de significancia α = 0.05.

**Conclusión:** Existe **evidencia insuficiente** para concluir que los datos no provienen de una distribución Gamma. En otras palabras, el modelo Gamma es **compatible con los datos observados**.

#### 3.7.3 Parámetros Estimados de la Gamma

La distribución Gamma estimada tiene parámetros:

$$\text{Gamma}(\alpha, \beta)$$

donde típicamente:
- α es el **parámetro de forma** (relacionado con la asimetría)
- β es el **parámetro de escala**

Para una Gamma con media 0.5829 y desviación estándar 0.2977:

$$\alpha = \left(\frac{\mu}{\sigma}\right)^2 = \left(\frac{0.5829}{0.2977}\right)^2 \approx 3.83$$

$$\beta = \frac{\sigma^2}{\mu} = \frac{0.0886}{0.5829} \approx 0.152$$

**Interpretación del parámetro de forma α ≈ 3.83:**

Un parámetro de forma cercano a 4 sugiere que el sistema colapsará tras la **acumulación de aproximadamente 4 eventos (fallas)** independientes, lo que es **exactamente consistente** con el hecho de que necesitamos 4 fallas para superar S = 3 repuestos.

#### 3.7.4 Bondad del Ajuste Gamma

El ajuste visual en la gráfica muestra que la **curva roja (Gamma)** sigue muy fielmente el histograma:

- El pico se alinea correctamente
- La asimetría se captura adecuadamente
- La cola derecha se modela bien
- No hay desviaciones sistemáticas evidentes

---

### 3.8 Prueba de Bondad de Ajuste - Distribución Weibull

#### 3.8.1 Resultados del Test

| Métrica | Valor |
|---------|-------|
| **T Pearson (Observado)** | 550.8938 |
| **p-valor Simulado** | 0.0000 |
| **Conclusión** | Se rechaza H₀ |

#### 3.8.2 Interpretación del Rechazo

El **p-valor < 0.001** (reportado como 0.0000) indica que:

$$P(\text{T} \geq 550.89 \mid H_0 \text{ verdadera}) < 0.001$$

Es decir, menos del **0.1%** de probabilidad.

**Decisión estadística:**

Como p-valor < 0.001 << 0.05, **rechazamos la hipótesis nula** al nivel α = 0.05.

**Conclusión:** Existe **evidencia estadística muy fuerte** de que los datos **no provienen** de una distribución Weibull con los parámetros estimados.

#### 3.8.3 Razón del Rechazo

El valor elevado del estadístico T = 550.89 (comparado con T = 24.58 para Gamma) indica **discrepancias substanciales** entre las frecuencias observadas y esperadas bajo el modelo Weibull.

Posibles razones:

1. **Forma incorrecta:** La Weibull estimada tiene una forma diferente a los datos reales
2. **Parámetros mal estimados:** Los parámetros optimizados no capturan bien la estructura de los datos
3. **Colas mal modeladas:** La Weibull probablemente subestima o sobrestima la probabilidad en las colas

#### 3.8.4 Comparación Gamma vs. Weibull

| Criterio | Gamma | Weibull |
|----------|-------|---------|
| **T Pearson** | 24.5808 | 550.8938 |
| **p-valor** | 0.1240 | 0.0000 |
| **Decisión** | ✓ No rechazar | ✗ Rechazar |
| **Ratio T** | — | 22.4× mayor |

El ratio de estadísticos (550.89 / 24.58 ≈ 22.4) indica que la **Weibull es 22 veces peor** que la Gamma en ajuste.

---

### 3.9 Síntesis del Ejercicio 3

| Aspecto | Hallazgo |
|--------|----------|
| **MTTF** | 0.5829 meses (~17.5 días) |
| **Dispersión** | σ = 0.2977 meses (CV ≈ 51%) |
| **Forma** | Asimétrica positiva (sk = 1.04) |
| **Modelo Gamma** | ✓ Aceptado (p = 0.1240) |
| **Modelo Weibull** | ✗ Rechazado (p < 0.001) |
| **Conclusión** | La distribución es aproximadamente **Gamma(3.83, 0.152)** |

---

## Ejercicio 4: Comparación de Mejoras

### 4.1 Contexto y Objetivo

El objetivo del Ejercicio 4 es comparar dos estrategias alternativas de mejora del sistema:

1. **Mejora V1: Contratar 2 Técnicos** (manteniendo S = 3 repuestos)
2. **Mejora V2: Aumentar a +1 Repuesto** (S = 4, manteniendo 1 técnico)

La comparación se realiza mediante:
- Análisis comparativo de estadísticas descriptivas
- Pruebas de bondad de ajuste para ambas mejoras
- Evaluación económica/operativa de cada opción

---

### 4.2 Tabla 1: Resumen de Estadísticas Descriptivas

![Tabla 1: Estadísticas Descriptivas](./06_tabla_resumen.png)

#### 4.2.1 Comparación de MTTF

| Sistema | MTTF (meses) | Diferencia respecto Original |
|---------|-------------|------------------------------|
| **Original (1 técnico, S=3)** | 0.5829 | — |
| **Mejora V1: 2 Técnicos (S=3)** | 0.5899 | +0.0070 (+1.21%) |
| **Mejora V2: +1 Repuesto (S=4)** | 0.7256 | +0.1427 (+24.49%) |

**Análisis:**

1. **Mejora V1 (2 Técnicos): +1.21%**
   
   Agregar un segundo técnico produce una **mejora mínima** del MTTF (solo 1.21%). Esto sugiere que el cuello de botella del sistema **no es la capacidad de reparación**, sino la **alta tasa de fallas** del conjunto de 7 máquinas.
   
   **Explicación física:**
   - Tasa de fallas total: λ = 7 fallos/mes
   - Capacidad de reparación con 1 técnico: μ = 8 reparaciones/mes
   - Capacidad de reparación con 2 técnicos: 2μ = 16 reparaciones/mes
   
   Como λ << 2μ, incluso con un solo técnico el sistema tiene capacidad de reparación ociosa. Agregar otro técnico tiene un impacto marginal.

2. **Mejora V2 (+1 Repuesto): +24.49%**
   
   Aumentar los repuestos de 3 a 4 produce una **mejora sustancial** del MTTF (24.49%). Esto es mucho más efectivo que agregar un técnico.
   
   **Explicación física:**
   - El sistema colapsaba cuando acumulaba 4 fallas simultáneas
   - Con S = 4, permite tolerar hasta 5 fallas antes del colapso
   - Aumenta el "amortiguador" de capacidad disponible
   
   **Efecto exponencial en confiabilidad:**
   
   La probabilidad de colapso es aproximadamente la probabilidad de que ocurran más de S fallas. Con una tasa de 7 fallos/mes, aumentar S de 3 a 4 aumenta significativamente el tiempo esperado antes del colapso (efecto multiplicativo).

#### 4.2.2 Comparación de Dispersión

| Sistema | Desv. Est. (meses) |
|---------|-------------------|
| Original | 0.2977 | 
| 2 Técnicos | 0.2999 | 
| +1 Repuesto | 0.3263 | 

**Hallazgos:**

1. **Desviación Estándar:**
   - 2 Técnicos: 0.2999 ≈ Original (cambio mínimo)
   - +1 Repuesto: 0.3263 > Original (mayor dispersión)
   
   El aumento de repuestos produce mayor **variabilidad absoluta**, pero menor **variabilidad relativa** (CV más bajo).


### 4.3 Tabla 2: Resultados de Tests de Bondad de Ajuste

![Tabla 2: Tests de Bondad](./07_tabla_tests_bondad.png)

#### 4.3.1 Sistema Original

| Distribución | T Pearson | p-valor | Conclusión |
|----------|-----------|---------|-----------|
| **Gamma** | 24.5808 | 0.1240 | No se rechaza H₀ ✓ |
| **Weibull** | 550.8938 | 0.0000 | Se rechaza H₀ ✗ |

**Conclusión:** El sistema original se ajusta a Gamma.

#### 4.3.2 Mejora V1: 2 Técnicos

| Distribución | T Pearson | p-valor | Conclusión |
|----------|-----------|---------|-----------|
| **Gamma** | 45.4348 | 0.0040 | Se rechaza H₀ ✗ |
| **Weibull** | 551.1803 | 0.0000 | Se rechaza H₀ ✗ |

**Análisis:**

- El test de Gamma es **rechazado** con p = 0.0040 < 0.05
- Aunque p = 0.0040 es cercano a la frontera (en contraste con Original p = 0.1240), la Gamma sigue siendo el **mejor modelo** (T = 45.43 << T_Weibull = 551.18)
- La adición de un segundo técnico cambia la distribución de manera que se aleja ligeramente del modelo Gamma

**Razón del cambio:**

Con 2 técnicos, la dinámica del sistema es diferente:
- Se pueden reparar hasta 2 máquinas simultáneamente
- Esto reduce la acumulación de fallos pendientes
- La distribución resultante es más asimétrica o tiene forma diferente

#### 4.3.3 Mejora V2: +1 Repuesto

| Distribución | T Pearson | p-valor | Conclusión |
|----------|-----------|---------|-----------|
| **Gamma** | 39.9133 | 0.0160 | Se rechaza H₀ ✗ |
| **Weibull** | 648.4583 | 0.0000 | Se rechaza H₀ ✗ |

**Análisis:**

- El test de Gamma es **rechazado** con p = 0.0160 < 0.05
- Aunque es rechazado, la Gamma sigue siendo significativamente mejor que Weibull
- T_Gamma = 39.91 < T_Original = 24.58, lo que indica un **ajuste ligeramente peor**

**Razón del cambio:**

Con S = 4 repuestos:
- El sistema tolera 5 fallas antes del colapso
- La dinámica es más diferente del caso original (que tolera 4)
- El parámetro de forma de la Gamma cambiaría de ~3.83 a ~4.83
- Esta diferencia hace que el ajuste sea menos perfecto

#### 4.3.4 Implicación General

**Conclusión importante:** Aunque técnicamente todos los tests de Gamma con p < 0.05 "rechazan" la hipótesis, en práctica:

- Los p-valores de Gamma (0.0040, 0.0160) son MUCHO mayores que los de Weibull (0.0000)
- Esto significa que la Gamma sigue siendo el **mejor modelo**, solo que con peor ajuste en las mejoras
- Posibles razones del peor ajuste en las mejoras:
  1. Menor número de "etapas" necesarias para el colapso
  2. Cambios en la asimetría de la distribución
  3. Efecto de las discretizaciones en bins del test de Pearson

---

### 4.4 Tabla 3: Análisis Comparativo de Mejoras

![Tabla 3: Análisis Comparativo](./08_tabla_comparativa_mejoras.png)

| Métrica | 2 Técnicos | +1 Repuesto | Mejor Opción |
|---------|-----------|------------|--------------|
| **Mejora MTTF (%)** | +1.21% | +24.49% | **+1 Repuesto** |
| **MTTF (meses)** | 0.5899 | 0.7256 | **+1 Repuesto** |

#### 4.4.1 Mejora Relativa de MTTF

**Mejora V1 (2 Técnicos): +1.21%**

$$\text{Mejora\%} = \frac{0.5899 - 0.5829}{0.5829} \times 100 = 1.21\%$$

**Análisis:**

- Mejora **marginal** e imperceptible operativamente
- Apenas añade 0.0070 meses ≈ 0.21 días de operación adicional
- En una operación de 24 horas, significa prolongar solo ~5 horas de uptime esperado

**Conclusión sobre 2 Técnicos:**

Agregar un segundo técnico es **poco efectivo** como estrategia de mejora porque:

1. El sistema actual tiene un 1 técnico con capacidad ociosa
2. El cuello de botella es la tasa de **fallas**, no la capacidad de **reparación**
3. La rentabilidad de esta inversión sería muy baja

#### 4.4.2 Mejora Relativa de MTTF

**Mejora V2 (+1 Repuesto): +24.49%**

$$\text{Mejora\%} = \frac{0.7256 - 0.5829}{0.5829} \times 100 = 24.49\%$$

**Análisis:**

- Mejora **sustancial** y operativamente significativa
- Añade 0.1427 meses ≈ 4.3 días de operación adicional
- Reduce el riesgo de colapso en aproximadamente 1/4 (cualitativamente)

**Conclusión sobre +1 Repuesto:**

Agregar un repuesto es **altamente efectivo** como estrategia porque:

1. Aumenta el "amortiguador" de la capacidad disponible (de 3 a 4)
2. Cada repuesto adicional tiene impacto exponencial en confiabilidad
3. El sistema necesita menos fallas simultáneas para colapsar



### 4.5 Gráfico Comparativo de Tres Configuraciones

![Comparativo Tres Sistemas](./04_comparativo_tres_sistemas.png)

#### 4.5.1 Análisis Visual Detallado

**Estructura del Gráfico:**

El gráfico presenta tres histogramas lado a lado con 50 bins cada uno, mostrando:

1. **Sistema Original (Azul, #2E86AB) - Panel Izquierdo**

   **Características visuales:**
   - Pico bien definido alrededor de 0.5 meses
   - Densidad máxima aproximada: 1.45
   - Cola que se extiende hasta ~2.3 meses
   - Histograma simétrico alrededor del pico con asimetría hacia la derecha
   - Curva roja (Gamma) se superpone perfectamente
   
   **Estadísticas superpuestas:**
   - μ = 0.5829 meses (línea verde discontinua)
   - p-valor Gamma = 0.1240 (caja amarilla, arriba a la izquierda)
   
   **Interpretación:**
   - Sistema más inestable con colapso promedio rápido
   - Distribución bien modelada por Gamma
   - Base de referencia para las mejoras

2. **Mejora V1: 2 Técnicos (Púrpura, #A23B72) - Panel Central**

   **Características visuales:**
   - Pico similar al original, ligeramente más a la derecha (~0.59 meses)
   - Densidad máxima similar (~1.55)
   - Cola ligeramente más extendida (~2.5 meses)
   - Distribución casi idéntica al original
   - Curva roja se ajusta, pero con ligeras desviaciones
   
   **Estadísticas superpuestas:**
   - μ = 0.5899 meses (línea verde discontinua, casi imperceptible cambio)
   - p-valor Gamma = 0.0040 (caja amarilla, valores más cercanos al rechazo)
   
   **Interpretación:**
   - Mejora casi imperceptible comparada con original
   - El agregar un técnico tiene impacto marginal
   - La distribución cambia ligeramente en forma

3. **Mejora V2: +1 Repuesto (Naranja, #F18F01) - Panel Derecho**

   **Características visuales:**
   - Pico desplazado significativamente hacia la derecha (~0.73 meses)
   - Densidad máxima ligeramente menor (~1.35)
   - Cola extendida hasta ~3.2 meses (vs. 2.3 original)
   - Distribución claramente diferente, menos "puntiaguda"
   - Curva roja (Gamma) se ajusta bien pero no perfectamente
   
   **Estadísticas superpuestas:**
   - μ = 0.7256 meses (línea verde discontinua, desplazada notablemente)
   - p-valor Gamma = 0.0160 (caja amarilla, rechaza Gamma marginalmente)
   
   **Interpretación:**
   - Mejora sustancial y visualmente evidente
   - Desplazamiento del pico hacia la derecha indica mayor MTTF
   - Cola más larga permite tiempos de operación más prolongados
   - Menor concentración de densidad (CV más bajo)

#### 4.5.2 Comparación Lateral Directa

**Observaciones comparativas:**

1. **Desplazamiento de la moda (pico):**
   - Original → 0.50 meses
   - 2 Técnicos → 0.59 meses (cambio casi imperceptible)
   - +1 Repuesto → 0.73 meses (desplazamiento evidente)

2. **Comportamiento de colas:**
   - Original: 2.33 meses máximo
   - 2 Técnicos: 2.55 meses máximo (ligeramente mayor)
   - +1 Repuesto: 3.19 meses máximo (significativamente mayor)

3. **Forma de la distribución:**
   - Original y 2 Técnicos: Formas casi idénticas
   - +1 Repuesto: Forma claramente diferente, más "achatada" (menor altura máxima, dispersión más amplia)

#### 4.5.3 Implicación Operativa

La visualización gráfica confirma que:

- **Mejora V1 es superficial:** Prácticamente no se observa cambio en el histograma
- **Mejora V2 es sustancial:** Cambio evidente en posición y forma
- La recomendación de implementar la Mejora V2 es visualmente justificada

---


### 4.6 Síntesis del Ejercicio 4

#### 4.6.1 Tabla Resumida de Conclusiones

| Criterio | 2 Técnicos | +1 Repuesto | Ganador |
|----------|-----------|-----------|---------|
| **Mejora MTTF** | +1.21% | +24.49% | ✓ +1 Repuesto |
| **Mejora Sigma** | -0.22 meses | +0.3263 meses | — |
| **Mejora CV** | -0.3 p.p. | -6.2 p.p. | ✓ +1 Repuesto |
| **Costo Aproximado** | Alto | Medio | ✓ +1 Repuesto |
| **Factibilidad** | Media | Alta | ✓ +1 Repuesto |
| **Impacto Operativo** | Marginal | Sustancial | ✓ +1 Repuesto |
| **Impacto Visual** | Imperceptible | Evidente | ✓ +1 Repuesto |




## Conclusiones Generales

### Conclusión 1: Caracterización de la Distribución

El tiempo de colapso del sistema original sigue una **distribución Gamma aproximadamente con parámetros (α≈3.83, β≈0.152)**, estadísticamente validada mediante test de bondad de ajuste con p=0.1240.

**Significado físico:** El parámetro de forma α ≈ 4 refleja que el colapso ocurre tras la acumulación de aproximadamente 4 fallas independientes, consistente con el diseño del sistema (N=7, S=3).

### Conclusión 2: Análisis de Mejoras

Entre las dos opciones evaluadas:
- **Agregar un técnico** es inefectivo (+1.21%) porque la capacidad de reparación no es el cuello de botella
- **Agregar un repuesto** es altamente efectivo (+24.49%) porque aumenta la tolerancia del sistema a fallas

**Razón técnica:** Con 7 máquinas fallando a tasa agregada λ=7 y 1 técnico reparando a tasa μ=8, el sistema tiene **capacidad de reparación ociosa**, por lo que duplicar técnicos no ayuda. En cambio, S es el factor limitante directo del colapso.

### Conclusión 3: Recomendación Estratégica

Para mejorar la confiabilidad del sistema con máxima eficiencia de costos, se debe **prioritariamente aumentar la cantidad de repuestos disponibles** antes de considerar invertir en personal adicional.

**Priorización de futuras mejoras:**
1. **Corto plazo:** Aumentar S a 4 o 5 (bajo costo, alto impacto)
2. **Mediano plazo:** Considerar mejorar TF mediante mantenimiento preventivo
3. **Largo plazo:** Evaluar agregar técnicos si S ya fue maximizado

---

## Referencias Técnicas

- **Distribución Gamma:** Parámetro de forma α relacionado con número de eventos acumulados (k-Erlang para α entero)
- **Test de Pearson:** Comparación de frecuencias observadas vs. esperadas mediante Chi-cuadrado
- **Monte Carlo:** Simulación de p-valores mediante 250 réplicas aleatorias de datos bajo H₀
- **Coeficiente de Variación:** Medida de variabilidad relativa = σ/μ, independiente de escala
- **Asimetría de Fisher:** Mide el grado de simetría: γ = E[(X-μ)³]/σ³
- **Curtosis de Fisher:** Mide pesadez de colas: κ = E[(X-μ)⁴]/σ⁴ - 3

---

## Apéndice: Interpretación de Gráficos

### Convenciones Visuales Utilizadas

- **Barras del histograma:** Densidad de frecuencia (área total = 1)
- **Curva roja:** Ajuste de distribución Gamma teórica
- **Línea verde discontinua:** Media (MTTF)
- **Líneas naranjas punteadas:** ±1 desviación estándar
- **Caja amarilla:** p-valor de test de Gamma
- **Colores por sistema:**
  - Azul (#2E86AB): Sistema original
  - Púrpura (#A23B72): 2 Técnicos
  - Naranja (#F18F01): +1 Repuesto

---

**Fin del Análisis Detallado**

*Informe preparado basado en 10,000 simulaciones estocásticas por configuración y 250 iteraciones Monte Carlo para tests de bondad de ajuste.*
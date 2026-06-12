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
* **Distribución de falla *F***: generará los tiempos hasta la próxima falla de cada máquina en uso.
* **Distribución de reparación *G***: generará los tiempos que tarda el técnico en reparar cada máquina.
* **Tiempo *t****: tiempo de finalización de reparación actual (t + tiempo generado por G).
* **Tiempo de colapso *T***: tiempo en el que el sistema colapsó.

El algoritmo implementado puede desglosarse en pasos:

1. Se inicializan las variables y otras estructuras auxiliares para el correcto funcionamiento del programa: 
   * *t*, *r* = 0
   * Se crea un arreglo con los *N* tiempos de falla para cada una de las cajas, generados por *F* (*Tf*), con los tiempos ordenados de menor a mayor.
   * *t* * = infinito (todavía no hay ninguna caja en reparación).

Mientras la cantidad de cajas averiadas *r* no supere a la cantidad de cajas de repuesto *S*:

2. Encuentro el próximo evento a ocurrir, ya sea el fallo de una caja o la finalización de alguna reparación:

   * **Si es un fallo**: 

     i. Actualizo el tiempo transcurrido *t*, aumento las cajas averiadas *r*.

     ii. Chequeo si las cajas averiadas *r* superan a los repuestos *S*, si lo hacen, finalizo la simulación.

     iii.. Si hay una sola caja averiada, entonces genero un tiempo de demora de reparación con *G* y actualizo *t* *.

     iv. Actualizo el tiempo de falla de la caja en mi arreglo *Tf* a infinito, hasta que termine de repararse.

     v. Reordeno mi arreglo *Tf*.

   * **Si es la finalización de la reparación:**

     i. Actualizo el tiempo transcurrido *t*, disminuyo las cajas averiadas *r*.

     ii. Genero un nuevo tiempo de falla para la caja, con F, y actualizo *Tf*.

     iii. Si tengo cajas averiadas aún, genero un nuevo tiempo de demora de reparación con *G* . Sino, no genero nada. Actualizo *t* * dependiendo del caso (con un nuevo tiempo o con infinito).

     iv. Reordeno mi arreglo *Tf*.

Cuando la cantidad de cajas averiadas *r* supere a los repuestos *S*:

3. Asigno a *T* el tiempo transcurrido *t* y lo doy como dato de salida.

*Aclaración:* Para este problema particular, en donde las cajas son idénticas y los tiempos son exponenciales independientes, no es necesario llevar registro de **qué** caja particular falló. Lo importante aquí es **cuántas** cajas están averiadas en simultáneo y si superan o no a la cantidad de repuestos disponibles.


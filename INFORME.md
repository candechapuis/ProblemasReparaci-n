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




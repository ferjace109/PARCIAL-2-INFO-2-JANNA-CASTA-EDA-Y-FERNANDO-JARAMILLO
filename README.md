# PARCIAL-2-INFO-2-JANNA-CASTAÑEDA-Y-FERNANDO-JARAMILLO

Es un sistema que permite explorar dos tipos de archivos:
- Archivos CSV del SIATA: datos de calidad del aire (PM2.5, NO₂, ozono, etc.)
- Archivos MAT de EEG: señales cerebrales de pacientes con y sin Parkinson

El proyecto tiene dos archivos ".py":
- clases.py: aquí viven todas las clases y funciones
- main.py: aquí está el menú y la lógica de navegación
- graficos: acá se guardan automáticamente todos los gráficos generados


¿Que contiene clases.py?
Tiene cuatro bloques principales:

  1. Funciones de validación
Tres funciones ("validar_entero", "validar_float", "validar_opcion") que se usan en todo el programa para pedirle datos al usuario sin que el programa explote si escribe algo raro.

  2. Clase SiataCSV
Maneja los archivos CSV del SIATA. Al cargarla convierte automáticamente la columna "fecha_hora" en índice para poder hacer remuestreo. Tiene estos métodos:
- "mostrar_info()": imprime "info()" y "describe()" del DataFrame
- "graficar_columna()": muestra plot, boxplot e histograma de una columna en 3 subplots
- "operaciones()": submenú con apply (z-score), map (categorías) y suma/resta de columnas. Cada resultado se puede previsualizar con head, tail, sample o rango
- "graficar_remuestreo()": grafica los datos agrupados por día, mes y trimestre

  3. Clase "ArchivoEEG"
Maneja los archivos ".mat" de electroencefalografía. Detecta automáticamente si el archivo es de un paciente Control o Parkinson según el nombre. Tiene:
- "mostrar_llaves()": usa "whosmat" para mostrar las variables del archivo
- "sumar_canales()": el usuario elige 3 canales y un rango de muestras, grafica los canales individuales y su suma en 2 subplots con ejes
- "estadisticas_3d()": calcula promedio y desviación estándar sobre la matriz 3D a lo largo de un eje elegido y los muestra con gráficos stem

4. Clase "Repositorio"
Un almacén de objetos que guarda todo lo que se va cargando durante la sesión. Permite buscar por nombre, por tipo (csv / eeg / control / parkinson), listar todo lo que hay y eliminar entradas.



¿Que contiene main.py?

Tiene el menú principal y los submenús. No tiene lógica propia, solo llama los métodos de las clases. Está dividido así:

- "menu_principal()": punto de entrada, opciones para cargar CSV, MAT o ir al repositorio
- "submenu_csv()": navega las opciones de un objeto "SiataCSV"
- "submenu_eeg()": navega las opciones de un objeto "ArchivoEEG"
- "submenu_repositorio()": gestiona el repositorio: listar, buscar, abrir o eliminar objetos

Cada archivo que se carga queda guardado automáticamente en el repositorio, así se pueden cargar varios y volver a cualquiera sin tener que cargarlo de nuevo.


Forma de uso:

  1. Corre main.py
  2. Elige cargar un CSV o un MAT
  3. Ingresa la ruta del archivo (puede arrastrar el archivo a la terminal)
  4. El objeto se carga y se abre su submenú directamente
  5. Explora lo que necesite: gráficos, estadísticas, operaciones
  6. Vuelve al menú principal y carga otro archivo si quiere
  7. En cualquier momento puede ir al Repositorio y abrir algo que ya cargó


Sobre los gráficos

Todos los gráficos se guardan automáticamente en la carpeta "graficos" que se crea sola al lado del script. El nombre del archivo incluye el nombre del CSV o MAT y la operación que se hizo, para que sea fácil identificarlos después.

#Sistema de Exploración Neuroambiental
#Universidad de Antioquia – Bioingeniería – Informática II 2026-1

import clases.py #este es la carpeta resultantes de clases_siata.py y clases_eeg.py
import os
import sys

# Asegura que Python encuentre clases.py en el mismo directorio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from clases import (
    SiataCSV,
    ArchivoEEG,
    Repositorio,
    validar_entero,
    validar_opcion,
)

#crear carpeta graficos
CARPETA_GRAFICOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graficos")
os.makedirs(CARPETA_GRAFICOS, exist_ok=True)


#Funciones de utilidad para el menú
def encabezado(titulo: str): #Imprime un encabezado visual.
    linea = "═" * 62
    print(f"\n{linea}")
    print(f"  {titulo}")
    print(linea)


def pausa(): #Pausa hasta que el usuario presione Enter.
    input("\n  [Presione Enter para continuar...]")


def limpiar(): #Limpia la pantalla 
    os.system("cls" if os.name == "nt" else "clear")


def pedir_ruta(extensiones: list) -> str:    
    ext_str = "/".join(extensiones)
    while True:
        ruta = input(f"  Ingrese la ruta del archivo ({ext_str}): ").strip().strip('"').strip("'")
        if not ruta:
            print("  ⚠  La ruta no puede estar vacía.")
            continue
        if not os.path.isfile(ruta):
            print(f"  ⚠  No se encontró el archivo: '{ruta}'")
            continue
        if not any(ruta.lower().endswith(e) for e in extensiones):
            print(f"  ⚠  El archivo debe ser de tipo: {ext_str}")
            continue
        return ruta
    

repositorio = Repositorio()

#SUBMENUS
#___ MENU SIATA CSV ___
def submenu_csv(obj: SiataCSV):
    while True:
        encabezado(f"SIATA CSV  ›  {obj.nombre}")
        print("  1. Mostrar información básica (info + describe)")
        print("  2. Graficar columna (plot / boxplot / histograma)")
        print("  3. Operaciones (apply, map, suma/resta de columnas)")
        print("  4. Gráfico de remuestreo (días / meses / trimestres)")
        print("  0. Volver al menú principal")

        opcion = validar_entero("\n  Opción: ", 0, 4)

        if opcion == 1:
            obj.mostrar_info()
            pausa()
        elif opcion == 2:
            obj.graficar_columna()
            pausa()
        elif opcion == 3:
            obj.operaciones()
            pausa()
        elif opcion == 4:
            obj.graficar_remuestreo()
            pausa()
        elif opcion == 0:
            break
#___ MENU EEG ___
def submenu_eeg(obj: ArchivoEEG):
    while True:
        encabezado(f"EEG MAT  ›  {obj.nombre}  ({obj.tipo})")
        print("  1. Mostrar llaves del archivo (.whosmat)")
        print("  2. Sumar 3 canales en un rango → graficar (señal 2D)")
        print("  3. Promedio y desviación estándar por eje (señal 3D, stem)")
        print("  0. Volver al menú principal")

        opcion = validar_entero("\n  Opción: ", 0, 3)

        if opcion == 1:
            obj.mostrar_llaves()
            pausa()
        elif opcion == 2:
            obj.sumar_canales()
            pausa()
        elif opcion == 3:
            obj.estadisticas_3d()
            pausa()
        elif opcion == 0:
            break

#__MENU REPOSITORIO___

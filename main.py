#Sistema de Exploración Neuroambiental
#Universidad de Antioquia – Bioingeniería – Informática II 2026-1

import clases #este es la carpeta resultantes de clases_siata.py y clases_eeg.py
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
def submenu_repositorio(): #Submenú de gestión del repositorio de objetos
    while True:
        encabezado("REPOSITORIO DE OBJETOS")
        print(f"  Objetos almacenados: {len(repositorio)}")
        print()
        print("  1. Listar todos los objetos")
        print("  2. Buscar objeto por nombre")
        print("  3. Buscar objetos por tipo (csv / eeg / control / parkinson)")
        print("  4. Abrir objeto almacenado")
        print("  5. Eliminar objeto del repositorio")
        print("  0. Volver al menú principal")

        opcion = validar_entero("\n  Opción: ", 0, 5)

        if opcion == 1:
            repositorio.listar()
            pausa()

        elif opcion == 2:
            nombre = input("  Nombre a buscar: ").strip()
            resultado = repositorio.buscar(nombre)
            if resultado and not isinstance(resultado, dict):
                abrir = input("  ¿Desea abrir este objeto? [s/n]: ").strip().lower()
                if abrir == "s":
                    if isinstance(resultado, SiataCSV):
                        submenu_csv(resultado)
                    elif isinstance(resultado, ArchivoEEG):
                        submenu_eeg(resultado)
            pausa()

        elif opcion == 3:
            tipo = input("  Tipo a buscar (csv / eeg / control / parkinson): ").strip()
            repositorio.buscar_por_tipo(tipo)
            pausa()

        elif opcion == 4:
            repositorio.listar()
            nombre = input("  Nombre del objeto a abrir: ").strip()
            obj = repositorio.buscar(nombre)
            if obj and not isinstance(obj, dict):
                if isinstance(obj, SiataCSV):
                    submenu_csv(obj)
                elif isinstance(obj, ArchivoEEG):
                    submenu_eeg(obj)

        elif opcion == 5:
            repositorio.listar()
            nombre = input("  Nombre del objeto a eliminar: ").strip()
            repositorio.eliminar(nombre)
            pausa()

        elif opcion == 0:
            break

#_______MENU PRINCIPAL_____
def menu_principal():
    while True:
        limpiar()
        encabezado("SISTEMA DE EXPLORACIÓN NEUROAMBIENTAL")
        print("  Universidad de Antioquia – Bioingeniería – Informática II 2026-1")
        print()
        print("  ── Archivos CSV (SIATA – Calidad del Aire) ──────────────")
        print("  1. Cargar archivo CSV y explorar")
        print()
        print("  ── Archivos MAT (EEG – Electroencefalografía) ───────────")
        print("  2. Cargar archivo MAT (Control o Parkinson) y explorar")
        print()
        print("  ── Repositorio de objetos ───────────────────────────────")
        print("  3. Gestionar repositorio (listar / buscar / abrir)")
        print()
        print("  0. Salir")

        opcion = validar_entero("\n  Seleccione una opción: ", 0, 3)

        if opcion == 1:
            encabezado("CARGAR ARCHIVO CSV – SIATA")
            ruta = pedir_ruta([".csv"])
            try:
                obj_csv = SiataCSV(ruta, carpeta_graficos=CARPETA_GRAFICOS)
                repositorio.agregar(obj_csv)
                pausa()
                submenu_csv(obj_csv)
            except Exception as e:
                print(f"\n  ❌  Error al cargar el archivo: {e}")
                pausa()

        elif opcion == 2:
            encabezado("CARGAR ARCHIVO MAT – EEG")
            ruta = pedir_ruta([".mat"])
            try:
                obj_eeg = ArchivoEEG(ruta, carpeta_graficos=CARPETA_GRAFICOS)
                repositorio.agregar(obj_eeg)
                pausa()
                submenu_eeg(obj_eeg)
            except Exception as e:
                print(f"\n  ❌  Error al cargar el archivo: {e}")
                pausa()

        elif opcion == 3:
            submenu_repositorio()

        # ── Salir ────────────────────────────────────────────────────────────
        elif opcion == 0:
            print("\n  Hasta luego. ¡Buena suerte!\n")
            sys.exit(0)


if __name__ == "__main__":
    menu_principal()
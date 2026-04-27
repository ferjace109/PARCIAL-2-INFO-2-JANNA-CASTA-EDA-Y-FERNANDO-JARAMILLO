

#Sistema de Exploración Neuroambiental
#Universidad de Antioquia – Bioingeniería – Informática II 2026-1

#Contiene:
# Funciones de validación numérica
# Clase SiataCSV   -> manejo de archivos CSV de calidad del aire (SIATA)
# Clase ArchivoEEG -> manejo de archivos MAT de electroencefalografía
# Clase Repositorio -> almacén de objetos con búsqueda (puntos extra)


import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.io as sio

#  FUNCIONES DE VALIDACIÓN NUMÉRICA
def validar_entero(mensaje: str, minimo: int = None, maximo: int = None) -> int:
    #Pide un entero al usuario con validación de rango opcional.
    while True:
        try:
            valor = int(input(mensaje))
            if minimo is not None and valor < minimo:
                print(f"  ⚠  El valor debe ser ≥ {minimo}.")
                continue
            if maximo is not None and valor > maximo:
                print(f"  ⚠  El valor debe ser ≤ {maximo}.")
                continue
            return valor
        except ValueError:
            print("  ⚠  Ingrese un número entero válido.")


def validar_float(mensaje: str, minimo: float = None, maximo: float = None) -> float:
    #Pide un flotante al usuario con validación de rango opcional.
    while True:
        try:
            valor = float(input(mensaje))
            if minimo is not None and valor < minimo:
                print(f"  ⚠  El valor debe ser ≥ {minimo}.")
                continue
            if maximo is not None and valor > maximo:
                print(f"  ⚠  El valor debe ser ≤ {maximo}.")
                continue
            return valor
        except ValueError:
            print("  ⚠  Ingrese un número decimal válido.")


def validar_opcion(mensaje: str, opciones: list) -> str:
    #Valida que la entrada pertenezca a una lista de opciones válidas.
    while True:
        valor = input(mensaje).strip()
        if valor in opciones:
            return valor
        print(f"  ⚠  Opción inválida. Elija entre: {opciones}")


#  _________________CLASE SiataCSV_________________


class SiataCSV:
  

#Atributos
#ruta:tipo str  – ruta completa del archivo
#nombre:tipo str  – nombre del archivo sin extensión
#df: tipo DataFrame – datos cargados con fecha_hora como índice
# carpeta_g:tipo str  – carpeta donde se guardan los gráficos
   

    COLUMNAS_CALIDAD = {
        "pm25": "PM2.5 (µg/m³)",
        "pm10": "PM10 (µg/m³)",
        "no":   "NO (ppb)",
        "no2":  "NO₂ (ppb)",
        "nox":  "NOx (ppb)",
        "ozono":"Ozono (ppb)",
        "co":   "CO (ppm)",
    }

    def __init__(self, ruta: str, carpeta_graficos: str = "graficos"):
        if not os.path.isfile(ruta):
            raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
        if not ruta.lower().endswith(".csv"):
            raise ValueError("El archivo debe ser .csv")

        self.ruta = ruta
        self.nombre = os.path.splitext(os.path.basename(ruta))[0]
        self.carpeta_g = carpeta_graficos
        os.makedirs(self.carpeta_g, exist_ok=True)
        #indice hora
        self.df = pd.read_csv(ruta, parse_dates=["fecha_hora"])
        self.df.set_index("fecha_hora", inplace=True)
        print(f"  ✔  Archivo '{self.nombre}' cargado correctamente. "
              f"({len(self.df)} registros, {len(self.df.columns)} columnas)")
        
 #  Información básica 

    def mostrar_info(self):
        # Muestra info() y describe() del DataFrame
        print("\n" + "="*60)
        print(f"  INFO – {self.nombre}")
        print("="*60)
        self.df.info()
        print("\n" + "-"*60)
        print("  ESTADÍSTICAS DESCRIPTIVAS:")
        print("-"*60)
        print(self.df.describe().to_string())
        print("="*60 + "\n")

    def listar_columnas(self):
        print("\n  Columnas disponibles:")
        for i, col in enumerate(self.df.columns, 1):
            unidad = self.COLUMNAS_CALIDAD.get(col, "")
            print(f"    {i}. {col}  {unidad}")

    def _elegir_columna(self, mensaje: str = "  Nombre de la columna: ") -> str: #Solicita al usuario elegir una columna válida.
        self.listar_columnas()
        cols = list(self.df.columns)
        while True:
            col = input(mensaje).strip()
            if col in cols:
                return col
            try:
                idx = int(col) - 1
                if 0 <= idx < len(cols):
                    return cols[idx]
            except ValueError:
                pass
            print("  ⚠  Columna inválida, intente de nuevo.")

 #  Gráfios

    def graficar_columna(self):#Muestra plot, boxplot e histograma de una columna elegida por el usuario.
                                                
        columna = self._elegir_columna("  Columna para graficar: ")
        serie = self.df[columna].dropna()
        unidad = self.COLUMNAS_CALIDAD.get(columna, columna)

        fig, axes = plt.subplots(1, 3, figsize=(16, 4))
        fig.suptitle(f"Análisis de '{columna}' – {self.nombre}", fontsize=14, fontweight="bold")

        # Plot temporal
        axes[0].plot(serie.index, serie.values, color="steelblue", linewidth=0.8)
        axes[0].set_title("Serie temporal")
        axes[0].set_xlabel("Fecha / Hora")
        axes[0].set_ylabel(unidad)
        axes[0].tick_params(axis="x", rotation=30)

        # Boxplot
        axes[1].boxplot(serie.values, patch_artist=True,
                        boxprops=dict(facecolor="lightcyan", color="steelblue"),
                        medianprops=dict(color="red", linewidth=2))
        axes[1].set_title("Boxplot")
        axes[1].set_ylabel(unidad)
        axes[1].set_xticks([1])
        axes[1].set_xticklabels([columna])

        # Histograma
        axes[2].hist(serie.values, bins=30, color="steelblue", edgecolor="white", alpha=0.85)
        axes[2].set_title("Histograma")
        axes[2].set_xlabel(unidad)
        axes[2].set_ylabel("Frecuencia")

        plt.tight_layout()
        plt.show()
        self._guardar_figura(fig, f"{self.nombre}_{columna}_3graficos")

# Previsualización de Series/DataFrames 

    def _previsualizar(self, datos: pd.Series, titulo: str):
        
        #Muestra una porción del resultado de una operación.
        #El usuario elige el modo:
          #1. head(n)    –> primeras n filas
          #2. tail(n)    –> últimas n filas
          #3. sample(n)  –> n filas aleatorias
          #4. rango      –> desde la fila i hasta la fila j
        
        total = len(datos)
        print(f"\n  {'─'*56}")
        print(f"  Resultado: {titulo}  ({total} filas en total)")
        print(f"  {'─'*56}")
        print("  ¿Cómo desea ver los datos?")
        print("    1. head   – primeras N filas")
        print("    2. tail   – últimas N filas")
        print("    3. sample – N filas aleatorias")
        print("    4. rango  – desde la fila i hasta la fila j")

        modo = validar_entero("  Modo (1-4): ", 1, 4)

        if modo in (1, 2, 3):
            n = validar_entero(f"  ¿Cuántas filas desea ver? (1-{min(total, 100)}): ",
                               1, min(total, 100))
            if modo == 1:
                fragmento = datos.head(n)
            elif modo == 2:
                fragmento = datos.tail(n)
            else:
                fragmento = datos.sample(n)
        else:  # rango
            print(f"  El índice numérico va de 0 a {total - 1}.")
            desde = validar_entero(f"  Desde la fila (0-{total - 2}): ", 0, total - 2)
            hasta = validar_entero(f"  Hasta la fila ({desde + 1}-{total - 1}): ",
                                   desde + 1, total - 1)
            fragmento = datos.iloc[desde:hasta + 1]

        print(f"\n{fragmento.to_string()}")
        print(f"  {'─'*56}\n")

# Operaciones 

    def _op_apply(self): #apply: z-score de una columna elegida por el usuario.
        print("\n  ℹ  apply ejecuta una función fila por fila sobre una Serie.")
        print("     Aquí calculamos el Z-score: cuántas desviaciones estándar")
        print("     se aleja cada valor de la media de su columna.\n")
        col = self._elegir_columna("  Columna para apply (z-score): ")
        serie = self.df[col].dropna()
        zscore = serie.apply(lambda x: (x - serie.mean()) / serie.std())
        self._previsualizar(zscore, f"Z-score de '{col}'")

    def _op_map(self): #map: categorización de niveles en una columna.
        print("\n  ℹ  map sustituye cada valor de una Serie aplicando una")
        print("     función o un diccionario de reemplazo elemento a elemento.")
        print("     Aquí etiquetamos cada valor como 'Bajo', 'Medio' o 'Alto'")
        print("     según los terciles de la columna.\n")
        col = self._elegir_columna("  Columna para map (categorizar niveles): ")
        vals = self.df[col].dropna()
        q33, q66 = vals.quantile(0.33), vals.quantile(0.66)
        categorias = vals.map(
            lambda x: "Alto" if x > q66 else ("Medio" if x > q33 else "Bajo")
        )
        self._previsualizar(categorias, f"Categorías de '{col}'")
        print(f"  Distribución de categorías:\n{categorias.value_counts().to_string()}\n")

    def _op_aritmetica(self): #suma o resta de dos columnas elegidas por el usuario.
        print("\n  Seleccione la primera columna:")
        col1 = self._elegir_columna("  Primera columna: ")
        print("  Seleccione la segunda columna:")
        col2 = self._elegir_columna("  Segunda columna: ")
        op = validar_opcion("  Operación [suma / resta]: ", ["suma", "resta"])

        if op == "suma":
            resultado = self.df[col1].add(self.df[col2])
            etiqueta = f"{col1} + {col2}"
        else:
            resultado = self.df[col1].sub(self.df[col2])
            etiqueta = f"{col1} - {col2}"

        self._previsualizar(resultado.dropna(), f"Resultado de '{etiqueta}'")

    def operaciones(self):
        #
        #Submenú que permite elegir cuál de las tres operaciones ejecutar:
        #  1. apply  -> z-score de una columna
        #  2. map    -> categorización por terciles
        #  3. suma/resta de dos columnas
        #En cada caso el usuario elige cómo previsualizar el resultado.
        
        while True:
            print("\n─── Operaciones sobre el CSV ─────────────────────────────")
            print("  1. apply      – z-score de una columna")
            print("  2. map        – categorizar valores en Bajo / Medio / Alto")
            print("  3. suma/resta – resultado de operar dos columnas")
            print("  0. Volver")

            opcion = validar_entero("\n  Operación: ", 0, 3)

            if opcion == 1:
                self._op_apply()
            elif opcion == 2:
                self._op_map()
            elif opcion == 3:
                self._op_aritmetica()
            elif opcion == 0:
                break

            print("─"*60)

    #  Remuestreo 
    def graficar_remuestreo(self): #muestra los datos a días, meses y trimestres y grafica en 3 subplots
       
        col = self._elegir_columna("  Columna para remuestrear y graficar: ")
        unidad = self.COLUMNAS_CALIDAD.get(col, col)
        serie = self.df[col].dropna()

        diario     = serie.resample("D").mean()
        mensual    = serie.resample("ME").mean()
        trimestral = serie.resample("QE").mean()

        fig, axes = plt.subplots(3, 1, figsize=(14, 10))
        fig.suptitle(f"Remuestreo de '{col}' – {self.nombre}",
                     fontsize=14, fontweight="bold")

        for ax, datos, titulo, color in zip(
            axes,
            [diario, mensual, trimestral],
            ["Promedio Diario", "Promedio Mensual", "Promedio Trimestral"],
            ["steelblue", "darkorange", "seagreen"]
        ):
            ax.plot(datos.index, datos.values, marker="o", markersize=3,
                    color=color, linewidth=1.2)
            ax.set_title(titulo, fontsize=11)
            ax.set_xlabel("Fecha")
            ax.set_ylabel(unidad)
            ax.grid(True, alpha=0.35)
            ax.tick_params(axis="x", rotation=30)

        plt.tight_layout()
        plt.show()
        self._guardar_figura(fig, f"{self.nombre}_{col}_remuestreo")
#  Guardar figura
    def _guardar_figura(self, fig: plt.Figure, nombre_base: str): #Guarda la figura como PNG en la carpeta de gráficos.
        ruta_salida = os.path.join(self.carpeta_g, f"{nombre_base}.png")
        fig.savefig(ruta_salida, dpi=150, bbox_inches="tight")
        print(f"  💾  Gráfico guardado → {ruta_salida}")

    def __str__(self):
        return (f"SiataCSV | archivo: {self.nombre} | "
                f"registros: {len(self.df)} | columnas: {list(self.df.columns)}")

    def __repr__(self):
        return f"SiataCSV('{self.ruta}')"

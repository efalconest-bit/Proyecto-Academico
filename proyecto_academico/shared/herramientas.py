import os

# Diccionario: relaciona cada color con su código de consola.
COLORES = {
    "ROJO": "\033[91m",
    "VERDE": "\033[92m",
    "AZUL": "\033[94m",
    "AMARILLO": "\033[93m",
    "CYAN": "\033[96m",
    "RESET": "\033[0m",
}

# Tupla: respuestas afirmativas fijas.
RESPUESTAS_SI = ("si", "sí", "s", "yes", "y")


def limpiar_pantalla():
    """Limpia la consola, según el sistema operativo."""
    os.system("cls" if os.name == "nt" else "clear")


def imprimir_color(texto, color="CYAN"):
    """Imprime texto con color; si el color no existe, usa CYAN."""
    codigo = COLORES.get(color, COLORES["CYAN"])
    print(f"{codigo}{texto}{COLORES['RESET']}")


def imprimir_titulo(texto):
    """Muestra un título sin borrar los datos del programa."""
    imprimir_color("=" * 60, "AZUL")
    print(texto.center(60))
    imprimir_color("=" * 60, "AZUL")


def imprimir_exito(mensaje):
    imprimir_color(f"✓ {mensaje}", "VERDE")


def imprimir_error(mensaje):
    imprimir_color(f"✗ {mensaje}", "ROJO")


def imprimir_info(mensaje):
    imprimir_color(f"ℹ {mensaje}", "CYAN")


def confirmar(pregunta):
    """Devuelve True si la respuesta pertenece a la tupla afirmativa."""
    return input(f"{pregunta} (si/no): ").strip().lower() in RESPUESTAS_SI


def es_email_valido(texto):
    """Validación básica de correo electrónico para esta práctica."""
    texto = texto.strip()
    if texto.count("@") != 1:
        return False
    usuario, dominio = texto.split("@")
    return bool(usuario) and "." in dominio and not dominio.endswith(".")

from colorama import Fore as fo

colores = {
    "Black": fo.BLACK,
    "Yellow": fo.YELLOW,
    "Red": fo.RED,
    "Green": fo.GREEN,
    "Cyan": fo.CYAN, 
    "Magenta": fo.MAGENTA, 
    "Gray": fo.LIGHTBLACK_EX,
    "Blue": fo.BLUE, 
    "Black": fo.BLACK, 
    "yellow": fo.LIGHTYELLOW_EX,
    "red": fo.LIGHTRED_EX,
    "green": fo.LIGHTGREEN_EX,
    "cyan": fo.LIGHTCYAN_EX, 
    "magenta": fo.LIGHTMAGENTA_EX, 
    "blue": fo.LIGHTBLUE_EX, 
}

class Ppp(): 
    """
    Clase para imprimir mensajes en consola con colores.
    Uso: Ppp.p("Mensaje a imprimir", color="Red")

    """
    @staticmethod 
    def p(texto_imprimir, color: str):
        """
        Imprime un mensaje en consola con el color especificado.
        
        Args:
            texto_imprimir (str): El texto a imprimir.
            color (str): El color del texto. Debe ser una clave del diccionario colores.
        
        Raises:
            ValueError: Si el color no es válido.
        """
        if color not in colores:
            raise ValueError(f"Color '{color}' no es válido. Debe ser una de las siguientes claves: {list(colores.keys())}")
        print(colores[color] + f"{texto_imprimir}" + fo.RESET)

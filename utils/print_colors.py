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
    @staticmethod 
    def p(texto_imprimir, color: str):
        print(colores[color] + f"{texto_imprimir}" + fo.RESET)

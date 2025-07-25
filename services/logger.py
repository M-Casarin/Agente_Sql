"""
El modulo denota una clase que modela un logger, donde podremos registrar los 
eventos relevantes. 
"""
import logging 
import os 
import glob 
import colorama 


class Logger: 

    os.makedirs("log", exist_ok=True)

    logging.basicConfig(
        # filename="log/app.log",
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("log/app.log"), 
            logging.StreamHandler()  # Muestra en consola 
        ],
        encoding="utf-8"
    )

    logger = logging.getLogger()
    print(colorama.Fore.RESET, "")

    @staticmethod 
    def info(message):
        """
        Guarda un log del tipo INFO en el archivo de logs.
        """
        print(colorama.Fore.LIGHTCYAN_EX, "")
        Logger.logger.info(message)
        print(colorama.Fore.RESET)

    @staticmethod
    def error(message: str):
        """
        Guarda un log del tipo error en el log file
        """
        print(colorama.Fore.RED, "")
        Logger.logger.error(message)    
        print(colorama.Fore.RESET)

    @staticmethod
    def warning(message: str):
        """
        Guarda un log del tipo error en el log file
        """
        print(colorama.Fore.LIGHTYELLOW_EX, "")
        Logger.logger.warning(message)    
        print(colorama.Fore.RESET)



if __name__ == '__main__': 

    Logger.error("Ejemplo de error")
    Logger.info("Ejemplo de info ")
    Logger.warning("Ejemplo de warning")
    Logger.warning("No se leer ni escribir, solo se deletrear")
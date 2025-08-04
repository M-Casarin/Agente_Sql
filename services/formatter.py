import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pandas as pd
from utils.print_colors import Ppp
from typing import Literal, Tuple
import pandas as pd


def format_result(
    result: dict,
    formato: Literal["html", "text"] = "html"
) -> Tuple[str, str]:
    """
    Dado un dict con:
      - 'columns' & 'rows'  => formatea como tabla
      - 'image', 'iframe', 'svg' => regresa tipo 'grafico' con el HTML
    """
    # 1) Gráficos
    if "image" in result:
        html = f'<img src="{result["image"]}" alt="Gráfico" style="width:100%;max-width:500px;">'
        return "grafico", html
    if "iframe" in result:
        html = f'<iframe src="{result["iframe"]}" width="100%" height="400" frameborder="0" allowfullscreen></iframe>'
        return "grafico", html
    if "svg" in result:
        return "grafico", result["svg"]

    # 2) Tablas SQL -> Al ejecutar la sentencia en el consultador la respuesta necesariamente contiene 'columns' y 'rows' 
    if "columns" in result and "rows" in result:
        cols = result["columns"]
        rows = result["rows"] or []
        # caso una celda
        if len(cols) == 1 and len(rows) == 1:
            return "texto", f"<b>{cols[0]}</b>: {rows[0][0]}"
        # DataFrame para HTML
        df = pd.DataFrame(rows, columns=cols)
        print(f"Formato: {formato}")

        # Formato HTML para pintar en el lado derecho de la pantalla 
        if formato == "html":
            resumen = f"<p><strong>Resumen:</strong> {len(df)} filas, {len(cols)} columnas.</p>"
            tabla = df.to_html(index=False, classes="dataframe", border=0)
            return "tabla", resumen + tabla
        else:
            # texto plano
            lines = ["\t".join(cols)] + [
                "\t".join(str(cell) for cell in row) for row in rows
            ]
            return "tabla", "```\n" + "\n".join(lines) + "\n```"

    # 3) Texto genérico
    return "texto", str(result)

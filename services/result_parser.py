import pandas as pd
from typing import List, Tuple, Any, Dict


class ResultParser:
    """
    Convierte los resultados de una consulta SQL en formatos útiles para frontend:
    - JSON
    - Tabla HTML
    - KPIs (valores únicos)
    - Datos para gráficos
    """

    def __init__(self) -> None:
        pass

    def to_json(self, columns: List[str], rows: List[List[Any]]) -> List[Dict[str, Any]]:
        """
        Convierte columnas y filas en una lista de diccionarios JSON.
        """
        return [dict(zip(columns, row)) for row in rows]

    def to_dataframe(self, columns: List[str], rows: List[List[Any]]) -> pd.DataFrame:
        """
        Convierte los datos a un DataFrame de pandas.
        """
        return pd.DataFrame(rows, columns=columns)

    def to_html_table(self, columns: List[str], rows: List[List[Any]]) -> str:
        """
        Convierte los datos a una tabla HTML con clases de estilo.
        """
        df = self.to_dataframe(columns, rows)
        return df.to_html(classes="table table-striped table-sm", index=False, border=0)

    def detect_kpi(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Si el DataFrame contiene un solo valor, lo devuelve como KPI.
        """
        if df.shape == (1, 1):
            return {"label": df.columns[0], "value": df.iloc[0, 0]}
        return {}

    def detect_chart_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detecta si los datos son graficables automáticamente.
        Si hay 2 columnas (categórica + numérica), retorna datos para gráfico de barras.
        """
        if df.shape[1] == 2 and pd.api.types.is_numeric_dtype(df[df.columns[1]]):
            return {
                "type": "bar",
                "x": df[df.columns[0]].astype(str).tolist(),
                "y": df[df.columns[1]].tolist(),
                "label_x": df.columns[0],
                "label_y": df.columns[1],
            }
        return {}

    def parse_result(self, columns: List[str], rows: List[List[Any]]) -> Dict[str, Any]:
        """
        Método principal: devuelve una estructura con múltiples formatos del resultado.
        """
        df = self.to_dataframe(columns, rows)
        return {
            "json": self.to_json(columns, rows),
            "html": self.to_html_table(columns, rows),
            "kpi": self.detect_kpi(df),
            "chart": self.detect_chart_data(df),
            "rows_count": len(rows),
            "columns_count": len(columns),
        }




import pandas as pd


def analyze_excel(file):
    # Read Excel file
    df = pd.read_excel(file)

    # Basic information
    rows = len(df)
    columns = len(df.columns)

    # Missing values
    missing_values = df.isnull().sum()

    # Numeric columns
    numeric_columns = df.select_dtypes(include="number").columns

    statistics = {}

    for column in numeric_columns:
        statistics[column] = {
            "total": df[column].sum(),
            "average": df[column].mean(),
            "minimum": df[column].min(),
            "maximum": df[column].max()
        }

    return {
        "data": df,
        "rows": rows,
        "columns": columns,
        "missing": missing_values,
        "statistics": statistics
    }
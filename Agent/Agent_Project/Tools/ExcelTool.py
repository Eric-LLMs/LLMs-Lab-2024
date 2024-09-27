import pandas as pd


def get_sheet_names(
        filename: str
) -> str:
    """Get the names of the worksheets in an Excel file."""
    excel_file = pd.ExcelFile(filename)
    sheet_names = excel_file.sheet_names
    return f"Here are the worksheet names in the '{filename}' file:\n\n{sheet_names}"


def get_column_names(
        filename: str
) -> str:
    """Get the column names of an Excel file."""

    # Read the first worksheet of the Excel file
    df = pd.read_excel(filename, sheet_name=0)  # sheet_name=0 means the first worksheet

    column_names = '\n'.join(
        df.columns.to_list()
    )

    result = f"Here are the column names of the first worksheet in the '{filename}' file:\n\n{column_names}"
    return result


def get_first_n_rows(
        filename: str,
        n: int = 3
) -> str:
    """Get the first n rows of an Excel file."""

    result = get_sheet_names(filename) + "\n\n"

    result += get_column_names(filename) + "\n\n"

    # Read the first worksheet of the Excel file
    df = pd.read_excel(filename, sheet_name=0)  # sheet_name=0 means the first worksheet

    n_lines = '\n'.join(
        df.head(n).to_string(index=False, header=True).split('\n')
    )

    result += f"Here are the first {n} rows of the first worksheet in the '{filename}' file:\n\n{n_lines}"
    return result

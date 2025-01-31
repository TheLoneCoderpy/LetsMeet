
def get_excel_data():
    import polars as pl

    df = pl.read_excel("Lets Meet DB Dump.xlsx")
    df = df.with_columns(pl.col("Geburtsdatum").str.strptime(pl.Date, "%d.%m.%Y"))
    print(df)
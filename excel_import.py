
def get_excel_data() -> dict:
    import polars as pl

    def safe(l, idx):
        try:
            return l[idx].rstrip(" ").lstrip(" ")
        except:
            return ""

    df = pl.read_excel("Lets Meet DB Dump.xlsx")
    df = df.with_columns(pl.col("Geburtsdatum").str.strptime(pl.Date, "%d.%m.%Y"))

    df = df.with_columns(pl.col("Nachname, Vorname").map_elements(lambda x: x.split(", ")[0]).alias("Nachname"))
    df = df.with_columns(pl.col("Nachname, Vorname").map_elements(lambda x: x.split(", ")[1]).alias("Vorname"))

    df = df.rename({"Straße Nr, PLZ Ort": "place", "Hobby1 %Prio1%; Hobby2 %Prio2%; Hobby3 %Prio3%; Hobby4 %Prio4%; Hobby5 %Prio5%;": "hob"})

    df = df.with_columns(pl.col("place").map_elements(lambda x: x.split(",")))
    df = df.with_columns(pl.col("place").map_elements(lambda x: x[0]).alias("Straße"))
    df = df.with_columns(pl.col("place").map_elements(lambda x: x[1].rstrip(" ").lstrip(" ")).alias("PLZ"))
    df = df.with_columns(pl.col("place").map_elements(lambda x: x[2].rstrip(" ").lstrip(" ")).alias("Ort"))
    df = df.with_columns(pl.col("Straße").map_elements(lambda x: x.split(" ")[-1]).alias("Hausnr."))
    df = df.with_columns(pl.col("Straße").map_elements(lambda x: "".join(x.split(" ")[:-1])).alias("Straße"))

    df = df.with_columns(pl.col("hob").map_elements(lambda x: x.replace(";", "").split("%")))
    df = df.with_columns([
        pl.col("hob").map_elements(lambda x: safe(x, 0)).alias("Hobby1"),
        pl.col("hob").map_elements(lambda x: safe(x, 1)).alias("Prio1"),
        pl.col("hob").map_elements(lambda x: safe(x, 2)).alias("Hobby2"),
        pl.col("hob").map_elements(lambda x: safe(x, 3)).alias("Prio2"),
        pl.col("hob").map_elements(lambda x: safe(x, 4)).alias("Hobby3"),
        pl.col("hob").map_elements(lambda x: safe(x, 5)).alias("Prio3"),
        pl.col("hob").map_elements(lambda x: safe(x, 6)).alias("Hobby4"),
        pl.col("hob").map_elements(lambda x: safe(x, 7)).alias("Prio4"),
        pl.col("hob").map_elements(lambda x: safe(x, 8)).alias("Hobby5"),
        pl.col("hob").map_elements(lambda x: safe(x, 9)).alias("Prio5")
    ])

    df = df.with_columns(pl.col("Telefon").map_elements(lambda x: x.replace("/ ", "").replace("(", "").replace(")", "")))

    df = df.drop(["Nachname, Vorname", "place", "hob"])

    df_out = df.to_dict(as_series=False)

    for c in ["Prio1", "Prio2", "Prio3", "Prio4", "Prio5"]:
        for i in range(len(df_out[c])):
            e = df_out[c][i]
            try:
                e = int(e)
            except:
                e = 0
            df_out[c][i] = e
            

    return df_out
import streamlit as st
st.set_page_config(layout="wide")
import pandas as pd
import models
import lang
trad = lang.get_translations(lang.lang_choice)


st.title(trad["Raw Materials Report"])

# Caricamento del file CSV

# Legge il file CSV in un DataFrame
raw_materials = models.query_collection(models.RawMaterial, models.raw_material_collection, as_dict=True, **{})
# get supplier's names

for raw_material in raw_materials:
    supplier = models.get_supplier_by_id(raw_material["supplier_id"])
    raw_material["supplier_name"] = supplier.name
    del raw_material["supplier_id"]


df = models.to_dataframes(raw_materials)
df.drop("_id", axis=1, inplace=True)

# st.subheader("Anteprima dei dati")
# st.write(df.head())


# for each row material name i want to get the sum of the quantity acquired form each supplier


# Selezione delle colonne per il filtro
st.sidebar.subheader("Filtri")
start_date = st.sidebar.date_input(trad["Start date"], value=None)
end_date = st.sidebar.date_input(trad["End date"], value=None)
if start_date and end_date:
    # datetime to datetime64[ns]
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

filter_columns = st.sidebar.multiselect("Seleziona le colonne per il filtro", df.columns)

filtered_df = df.copy()

for column in filter_columns:
    unique_values = filtered_df[column].unique()
    selected_values = st.sidebar.multiselect(f"Valori per {column}", unique_values, default=unique_values)
    filtered_df = filtered_df[filtered_df[column].isin(selected_values)]

# st.subheader("Dati filtrati")
# st.write(filtered_df)

# Selezione delle colonne per l'aggregazione
st.sidebar.subheader("Aggregazioni")
agg_column = st.sidebar.multiselect("Seleziona la colonna per l'aggregazione", df.columns, default=["quantity", "price"])
agg_func = st.sidebar.multiselect("Seleziona la funzione di aggregazione", ["sum", "mean", "count", "min", "max"], default=["sum", "mean"])

st.sidebar.subheader("Raggruppamento")
group_columns = st.sidebar.multiselect("Seleziona le colonne per il raggruppamento", df.columns, default=["quantity_unit", "supplier_name", "name"])

if st.sidebar.button("Applica aggregazione"):
    aggr_config = {ac: af for ac, af in zip(agg_column, agg_func)}
    if group_columns:
        # applica l'aggregazione su tutte le colonne numeriche
        aggregated_df = filtered_df.groupby(group_columns).agg(aggr_config)
    else:
        aggregated_df = filtered_df.agg(aggr_config)
else:
    aggregated_df = filtered_df
if "price" in agg_column:
    aggregated_df["total_price"] = aggregated_df["quantity"] * aggregated_df["price"]
aggregated_df = aggregated_df.dropna(how="all")
# riordina le colonne
# aggregated_df = aggregated_df[group_columns + agg_column]
st.subheader("Risultati dell'aggregazione")
st.dataframe(aggregated_df, use_container_width=True)

# download data
st.download_button(
    label="Download Data as CSV",
    data=aggregated_df.to_csv().encode("utf-8"),
    file_name="data.csv",
    mime="text/csv",
)
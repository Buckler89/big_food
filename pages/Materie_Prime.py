import streamlit as st
from bson.objectid import ObjectId
import models
import lang

from utils import dataframe_with_selections, manage_barcode
# Initialization
trad = lang.get_translations(lang.lang_choice)

st.sidebar.image("https://www.livafritta.it/wp-content/uploads/2020/02/logo-livafritta-01.png")

def main():
    st.title(trad["Raw Materials"])

    tab1, tab2 = st.tabs([
        trad["Data Entry"],
        trad["BarCode Generator"],
    ])

    # Raw Materials Tab
    with tab1:
        st.header(trad["Raw Materials"])
        error = False
        suppliers = models.query_collection(models.Supplier, models.supplier_collection, **{})
        suppliers_id_to_name = {supplier.id: supplier.name for supplier in suppliers}
        suppliers_name_to_id = {supplier.name: supplier.id for supplier in suppliers}
        raw_materials = models.query_collection(models.RawMaterial, models.raw_material_collection, **{})

        with st.form(trad["Add Raw Material"]):
            name = st.text_input(trad["Name"])
            supplier_name = st.selectbox(trad["Supplier name"], suppliers_id_to_name.values(), index=None)
            date = st.date_input(trad["acquiring date"], format=lang.datetime_format)
            expiration_date = st.date_input(trad["Expiration Date"], format=lang.datetime_format)
            batch_number = st.text_input(trad["Supplier batch number"])
            document_number = st.text_input(trad["Document Number"])
            quantity = st.number_input(trad["Quantity"])
            quantity_unit = st.selectbox(trad["Unit"], models.QuantityEnum.__members__.keys(), index=None)
            submit = st.form_submit_button(trad["Add Raw Material"])

            if submit:
                try:
                    supplier_id = models.supplier_collection.find_one({"name": supplier_name})['_id']
                    instance = models.RawMaterial(
                        name=name,
                        supplier_id=supplier_id,
                        date=date,
                        expiration_date=expiration_date,
                        batch_number=batch_number,
                        document_number=document_number,
                        quantity=quantity,
                        quantity_unit=quantity_unit
                    )
                    instance.insert()
                    st.success(trad["Raw Material added successfully"])
                    st.balloons()
                except Exception as e:
                    error = True
                    st.error(f"Error adding raw material {e}")

        df = models.to_dataframes(raw_materials)  # .drop('_id', axis=1)
        if len(df) > 0:
            df['supplier_name'] = df['supplier_id'].apply(lambda x: models.supplier_collection.find_one({"_id": ObjectId(x)})['name'])

            edited_df = dataframe_with_selections(
                df,
                config_columns={
                    "supplier_name": st.column_config.SelectboxColumn(
                        options=suppliers_name_to_id.keys(),
                        required=True),
                    "quantity_unit": st.column_config.SelectboxColumn(
                        options=models.QuantityEnum.__members__.keys(),
                        required=True),
                    "supplier_id": None,
                },
                disabled=["consumed_quantity", "is_finished"]
            )
            if st.button("Modify Data", key="raw_materials modify data"):
                edited_df = edited_df.dropna(how='all')
                try:
                    deleted_rows = edited_df[edited_df["delete"] == True]
                    edited_df = edited_df.drop(columns=["delete"])
                    if len(deleted_rows) > 0:
                        for index, row in deleted_rows.iterrows():
                            models.delete_raw_material_by_id(row['_id'])
                except Exception as e:
                    error = True
                    st.error(f"Error deleting raw material {e}")
                try:
                    # select new rows of edited_df wrt original df
                    new_rows = edited_df[~edited_df.index.isin(df.index)]
                    if len(new_rows) > 0:
                        new_rows['supplier_id'] = new_rows['supplier_name'].apply(lambda x: suppliers_name_to_id[x])
                        for index, row in new_rows.iterrows():
                            instance = models.RawMaterial(**row.dropna().to_dict())
                            instance.insert()
                except Exception as e:
                    error = True
                    st.error(f"Error adding raw material {e}")

                try:
                    # Find common indices to compare rows
                    common_indices = df.index.intersection(edited_df.index)

                    # Use the common indices to filter rows
                    common_rows_original = df.loc[common_indices]
                    common_rows_modified = edited_df.loc[common_indices]

                    # Creating a mask for changes
                    changes_mask = common_rows_modified != common_rows_original

                    # Applying the mask to display old values in unchanged columns
                    changes_mask_ = changes_mask.any(axis=1)
                    modifications = common_rows_modified[changes_mask_]
                    if len(modifications) > 0:
                        for index, row in modifications.iterrows():
                            instance = models.RawMaterial(**row.dropna().to_dict())
                            instance.insert(update=True)
                except Exception as e:
                    error = True
                    st.error(f"Error modifying raw material {e}")
                if not error:
                    st.success(trad["Data modified successfully"])
                    st.balloons()
                else:
                    st.error("Error modifying data")
    with tab2:
        manage_barcode(models.RawMaterial, models.raw_material_collection, trad["Select Raw Material"])

if __name__ == "__main__":
    main()

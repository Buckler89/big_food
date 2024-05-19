import streamlit as st
st.set_page_config(layout="wide")
from bson.objectid import ObjectId
import models
import lang
from uuid import uuid4
from streamlit_js_eval import streamlit_js_eval
from utils import dataframe_with_selections, manage_barcode
# Initialization
trad = lang.get_translations(lang.lang_choice)

st.sidebar.image("https://www.livafritta.it/wp-content/uploads/2020/02/logo-livafritta-01.png")

def main():
    st.title(trad["Raw Materials"])

    tab1, tab2 = st.tabs([
        trad["Data Entry"],
        trad["Data Search"],
    ])

    # Raw Materials Tab
    with tab1:
        st.header(trad["Raw Materials"])
        error = False
        suppliers = models.query_collection(models.Supplier, models.supplier_collection, **{})
        suppliers_id_to_name = {supplier.id: supplier.name for supplier in suppliers}
        suppliers_name_to_id = {supplier.name: supplier.id for supplier in suppliers}
        raw_materials = models.query_collection(models.RawMaterial, models.raw_material_collection, **{})

        name_options = list(set([instance.name.strip() for instance in raw_materials]))
        name_options.insert(0, trad["Insert new..."])


        # form = st.form(trad["Add Raw Material"], clear_on_submit=True)
        name_placeholder = st.empty()
        supplier_name_placeholder = st.empty()
        date_placeholder = st.empty()
        expiration_date_placeholder = st.empty()
        batch_number_placeholder = st.empty()
        document_number_placeholder = st.empty()
        quantity_placeholder = st.empty()
        quantity_unit_placeholder = st.empty()
        price_placeholder = st.empty()
        submit_placeholder = st.empty()

        if st.button(trad["Clear Form"]):
            streamlit_js_eval(js_expressions="parent.window.location.reload()")

        # if 'name' not in st.session_state:
        #     st.session_state.name = None
        # if 'supplier_name' not in st.session_state:
        #     st.session_state.supplier_name = None
        # if 'date' not in st.session_state:
        #     st.session_state.date = "default_value_today"
        # if 'expiration_date' not in st.session_state:
        #     st.session_state.expiration_date = "default_value_today"
        # if 'batch_number' not in st.session_state:
        #     st.session_state.batch_number = ""
        def define_form():
            name = name_placeholder.selectbox(trad["Name"], options=name_options, index=None)
            # Create text input for user entry
            if name == trad["Insert new..."]:
                name = name_placeholder.text_input(trad["Enter your other option..."])
            # name = name_placeholder.text_input(trad["Name"])
            supplier_name = supplier_name_placeholder.selectbox(trad["Supplier name"], suppliers_id_to_name.values(), index=None)
            date = date_placeholder.date_input(trad["acquiring date"], format=lang.datetime_format, )
            expiration_date = expiration_date_placeholder.date_input(trad["Expiration Date"], format=lang.datetime_format)
            batch_number = batch_number_placeholder.text_input(trad["Supplier batch number"])
            document_number = document_number_placeholder.text_input(trad["Document Number"])
            quantity = quantity_placeholder.number_input(trad["Quantity"], min_value=0.0001, max_value=2000.0, format="%.4f", step=1.00, value=None)
            quantity_unit = quantity_unit_placeholder.selectbox(trad["Unit"], models.QuantityEnum.__members__.keys(), index=None)
            price = price_placeholder.number_input(trad["Price"], min_value=0.01, step=1.00, format="%.2f", value=None)
            submit = submit_placeholder.button(trad["Add Raw Material"])
            return name, supplier_name, date, expiration_date, batch_number, document_number, quantity, quantity_unit, price, submit

        name, supplier_name, date, expiration_date, batch_number, document_number, quantity, quantity_unit, price, submit = define_form()

        if batch_number.strip().lower() in ["no"]:
            batch_number = f"N/A-{uuid4().hex[:4]}"
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
                    quantity_unit=quantity_unit,
                    price=price
                )
                instance.insert()
                st.success(trad["Raw Material added successfully"])
                st.balloons()
                st.warning(trad["Please reload the page to see the changes in the table and to clear the form"])
            except Exception as e:
                error = True
                st.error(f"Error adding raw material {e}")
                raise e

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
            if st.button(trad["Modify Data"], key="raw_materials modify data"):
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
        # manage_barcode(models.RawMaterial, models.raw_material_collection, trad["Select Raw Material"])

        col1, col2 = st.columns(2)
        with col1:
            o = manage_barcode(models.RawMaterial, models.raw_material_collection, trad["Select Raw Material"])
            selection = o[0]
            semi_finished_products_name_to_id = o[2]
        with col2:
            # load_selected = st.button(trad["Load Selected"])
            delete_selected_button_placeholder = st.empty()
            if selection:
                delete_selected = delete_selected_button_placeholder.button(trad["Delete this product"])

                element = models.get_raw_material_by_id(semi_finished_products_name_to_id[selection])
                qi = element.quantity_unit.value
                # get supplier name
                sn = models.get_supplier_by_id(element.supplier_id).name

                # create a vertical markdown table with all the semi-finished product data and ingredients
                # with st.sidebar:
                st.markdown(f"""
                    | {trad["Field"]} | {trad["Value"]} |
                    | --- | --- |
                    | {trad["Name"]} | {element.name} |
                    | {trad["Production Date"]} | {element.date} |
                    | {trad["Expiration Date"]} | {element.expiration_date} |
                    | {trad["batch number"]} | {element.batch_number} |
                    | {trad["Quantity"]} | {element.quantity} |
                    | {trad["Unit"]} | {qi} |
                    | {trad["Price"]} | {element.price} |
                    | {trad["Supplier name"]} | {sn} |
                    | {trad["Document Number"]} | {element.document_number} |
                    | {trad["Consumed Quantity"]} | {element.consumed_quantity} |
                    | {trad["Finished"]} | {element.is_finished} |
                    """)

                if delete_selected:
                    # before deleting the product, we need to check if it is used in any semi-finished product
                    # if it is, we cannot delete it
                    semi_finished_products = models.query_collection(models.SemiFinishedProduct, models.semi_finished_product_collection, **{})
                    used_in_semi_finished_products = []
                    for semi_finished_product in semi_finished_products:
                        if selection in semi_finished_product.ingredients:
                            used_in_semi_finished_products.append(semi_finished_product.name)
                    if len(used_in_semi_finished_products) > 0:
                        st.error(f"{trad['Cannot delete raw material']} {trad['used in']} {used_in_semi_finished_products}")
                    else:
                        models.delete_raw_material_by_id(semi_finished_products_name_to_id[selection])
                        st.success(f"{trad['Raw Material']} {selection} {trad['deleted successfully']}")
                        st.balloons()



if __name__ == "__main__":
    main()

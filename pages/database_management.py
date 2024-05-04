import numpy as np
import streamlit as st
import pymongo
from streamlit_extras.stylable_container import stylable_container
# from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_js_eval import streamlit_js_eval
from bson.objectid import ObjectId
from datetime import datetime
from pydantic import ValidationError
# Assuming your models and database initialization are in a file named models.py
import random
import models
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import pandas as pd
import lang
from typing import Union, List, Dict, Any, Optional, Tuple
# Initialization
trad = lang.get_translations(lang.lang_choice)
if 'trad' not in st.session_state:
    st.session_state['trad'] = trad
trad = st.session_state['trad']

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox(trad["Add filters"])

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect(trad["Filter dataframe on"], df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if isinstance(df[column].dtype, pd.CategoricalDtype) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]
    return df

def dataframe_with_selections(
        df, config_columns=None,
        disabled: Union[bool, List[str]] = False, delete_column: bool = True, select_column: bool | List = False,
        placeholder=None, key=None
) -> pd.DataFrame:
    df_with_selections = df.copy()
    column_config_base = {
        "_id": None,
    }
    if delete_column:
        df_with_selections.insert(len(df_with_selections.columns), "delete", False)
        column_config_base.update({"delete": st.column_config.CheckboxColumn(required=True, default=False)})
    if isinstance(select_column, list) or select_column == True:
        df_with_selections.insert(0, "Select", False)
        if isinstance(select_column, list) and not isinstance(select_column[0], bool):
                df_with_selections.loc[select_column, "Select"] = True
        column_config_base.update({"Select": st.column_config.CheckboxColumn(required=True, default=False)})

    column_config_base.update(config_columns or {})
    # Get dataframe row-selections from user with st.data_editor
    if placeholder is not None:
        _st = placeholder
    else:
        _st = st
    edited_df = _st.data_editor(
        df_with_selections,
        hide_index=True,
        column_config=column_config_base,
        disabled=disabled,
        num_rows="dynamic",
        key=key,
        # key=hash(df_with_selections.columns.values.tobytes()),

    )
    return edited_df

def main():
    st.title(trad["software name"])

    tab1, tab2, tab3 = st.tabs([
        trad["Semi-Finished Products"],
        trad["Raw Materials"],
        trad["Suppliers"],
    ])


    # Semi-Finished Products Tab
    with tab1:
        st.header(trad["Semi-Finished Products"])
        max_n_ingredients = 30
        error = False

        raw_materials = models.query_collection(models.RawMaterial, models.raw_material_collection, **{})
        raw_materials_id_to_name = {raw_material.id: raw_material.name for raw_material in raw_materials}
        raw_materials_name_to_id = {raw_material.name: raw_material.id for raw_material in raw_materials}

        name_placeholder = st.empty()
        date_placeholder = st.empty()
        expiration_date_placeholder = st.empty()
        batch_number_placeholder = st.empty()
        quantity_placeholder = st.empty()
        quantity_unit_placeholder = st.empty()
        # columns to lay out the inputs
        # if st.session_state.get("all_ingredients") is None:
        st.write(f'#### {trad["Raw Materials"]}')
        grid_raw_material_ingr = st.columns(2)
        st.write(f'#### {trad["Semi-Finished Products"]}')
        grid_semi_finished_prod_ingr = st.columns(2)
        with grid_raw_material_ingr[0]:
            raw_material_ingredients_placeholders = [st.empty() for _ in range(max_n_ingredients)]
            raw_materials_ingredient_quantity_placeholders = [st.empty() for _ in range(max_n_ingredients)]
        with grid_semi_finished_prod_ingr[0]:
            semi_finished_products_as_ingredients_placeholders = [st.empty() for _ in range(max_n_ingredients)]
            semi_finished_products_as_ingredients_quantity_placeholders = [st.empty() for _ in range(max_n_ingredients)]

        name = name_placeholder.text_input(trad["Name"], key="semi_finished_product_name", value=st.session_state.get("form_semi_finished_product", {}).get("name", None)) # todo deve prevedere la selezione dei nomi già inseriti in precedenza
        date = date_placeholder.date_input(trad["Production Date"], value=st.session_state.get("form_semi_finished_product", {}).get("date", None))  # this must be before the query since it is used to filter the expiration date

        if st.session_state.get("form_semi_finished_product") is None:
            semi_finished_products_as_ingredients = models.query_collection(models.SemiFinishedProduct,
                                                                            models.semi_finished_product_collection, **{
                    "is_finished": False,
                    "expiration_date": {"$gte": date}
                })
            semi_finished_products_as_ingredients_id_to_name = {semi_finished_product.id: f"{semi_finished_product.name} - {semi_finished_product.batch_number}" for
                                                 semi_finished_product in semi_finished_products_as_ingredients}
            semi_finished_products_as_ingredients_name_to_id = {f"{semi_finished_product.name} - {semi_finished_product.batch_number}": semi_finished_product.id for
                                                 semi_finished_product in semi_finished_products_as_ingredients}

            raw_materials = models.query_collection(models.RawMaterial, models.raw_material_collection, **{
                    "is_finished": False,
                    "expiration_date": {"$gte": date}
                })
            raw_materials_id_to_name = {raw_material.id: f"{raw_material.name} - {raw_material.batch_number}" for raw_material in raw_materials}
            raw_materials_name_to_id = {f"{raw_material.name} - {raw_material.batch_number}": raw_material.id for raw_material in raw_materials}

            max_quantity_value_raw_material = dict()
            for raw_material in raw_materials:
                v = raw_material.quantity - raw_material.consumed_quantity
                v = int(v) if raw_material.quantity_unit in [models.QuantityEnum.unit] else float(v)
                max_quantity_value_raw_material[f"{raw_material.name} - {raw_material.batch_number}"] = v

            max_quantity_value_semi_finished_products = dict()
            for semi_finished_product in semi_finished_products_as_ingredients:
                v = semi_finished_product.quantity - semi_finished_product.consumed_quantity
                v = int(v) if semi_finished_product.quantity_unit in [models.QuantityEnum.unit] else float(v)
                max_quantity_value_semi_finished_products[f"{semi_finished_product.name} - {semi_finished_product.batch_number}"] = v
        else:
            pass

        expiration_date = expiration_date_placeholder.date_input(trad["Expiration Date"], value=st.session_state.get("form_semi_finished_product", {}).get("expiration_date", None))
        batch_number = batch_number_placeholder.text_input(trad["batch number"], value=st.session_state.get("form_semi_finished_product", {}).get("batch_number", None))
        quantity = quantity_placeholder.number_input(trad["Quantity"], value=st.session_state.get("form_semi_finished_product", {}).get("quantity", None))
        try:
            index = list(models.QuantityEnum).index(st.session_state.get("form_semi_finished_product", {}).get("quantity_unit", None))
        except ValueError:
            index = None
        quantity_unit = quantity_unit_placeholder.selectbox(trad["Unit"], models.QuantityEnum.__members__.keys(), index=index)
        # --------------------------------------------------------------
        # ingredients_a = st.multiselect(trad["Ingredients A"], list(raw_materials_id_to_name.values()), default=None,
        #                                key="ingredients_a")
        # ingredients_quantity_a = st.multiselect(trad["Ingredients Quantity"], [0] * len(ingredients_a),
        #                                         key="ingredients_quantity_a")
        # ingredients_b = st.multiselect(trad["Ingredients B"], list(semi_finished_products_as_ingredients_id_to_name.values()), default=None,
        #                                key="ingredients_b")
        # ingredients_quantity_b = st.multiselect(trad["Ingredients Quantity"], [0] * len(ingredients_b),
        #                                         key="ingredients_quantity_b")
        # --------------------------------------------------------------
        st.write(f'## {trad["Ingredients"]}')
        # https://mathcatsand-examples.streamlit.app/add_data
        # n_raw_material_ingr = st.slider(trad['How many Raw Material?'], min_value=1, max_value=20)
        # n_semi_finished_prod_ingr = st.slider(trad['How many Semi-Finished Products?'], min_value=1, max_value=20)
        n_raw_material_ingr = st.number_input(trad['How many Raw Material?'], min_value=0, max_value=max_n_ingredients, step=1)
        n_semi_finished_prod_ingr = st.number_input(trad['How many Semi-Finished Products?'], min_value=0, max_value=max_n_ingredients, step=1)
        # a selection for the user to specify the number of rows
        # num_rows = st.slider('Number of rows', min_value=1, max_value=10)




        # Function to create a row of widgets (with row number input to assure unique keys)
        ingredient_user_input = {}

        def add_ingr(row, grid, options, key, placeholder, max_quantity_value=None):
            # i = st.selectbox(trad["Ingredient"], options, index=None, key=f'ingredient_{row}{id(grid)}')
            with grid[0]:
                st.session_state["all_ingredients"][f"ingredient_{row}{key}"] = placeholder[0].selectbox(
                    trad["Ingredient"],
                    options,
                    index=None,
                    key=f"ingredient_{row}{key}",
                )
            with grid[1]:
                max_value = max_quantity_value.get(st.session_state["all_ingredients"][f"ingredient_{row}{key}"])
                type_ = type(max_value) if max_value is not None else int
                st.session_state["all_ingredients"][f"ingredient_quantity_{row}{key}"] = \
                placeholder[1].number_input(trad["Quantity"], step=type_(1), min_value=type_(0), max_value=max_value, #max value non funziona
                                key=f"ingredient_quantity_{row}{key}")
            # return i, q

        # Loop to create rows of input widgets
        if st.session_state.get("all_ingredients") is None:
            st.session_state["all_ingredients"] = {}

        for r in range(n_raw_material_ingr):
            # if st.session_state["all_ingredients"].get(f'ingredient_{r}{id(grid_raw_material_ingr)}', 'None') == 'None':
            # if st.session_state.get(f'ingredient_{r}{id(grid_raw_material_ingr)}') is None:
            add_ingr(r, grid_raw_material_ingr, list(raw_materials_id_to_name.values()), key="grid_raw_material_ingr", max_quantity_value=max_quantity_value_raw_material, placeholder=raw_material_ingredients_placeholders[r])

        for r in range(n_semi_finished_prod_ingr):
            # if st.session_state["all_ingredients"].get(f'ingredient_{r}{id(grid_semi_finished_prod_ingr)}', 'None') == 'None':
            # if st.session_state.get(f'ingredient_{r}{id(grid_semi_finished_prod_ingr)}') is None:
            add_ingr(r, grid_semi_finished_prod_ingr, list(semi_finished_products_as_ingredients_id_to_name.values()), key="semi_finished_products_as_ingredients_id_to_name", max_quantity_value=max_quantity_value_semi_finished_products, placeholder=semi_finished_products_as_ingredients_placeholders[r])

        # --------------------------------------------------------------
        st.markdown("<hr>", unsafe_allow_html=True)

        add_vertical_space(1)

        # submit = st.button(trad["Add Semi-Finished Product"]) #todo rendere il pulsante più chiaro (verde o con scritta fatto)
        with stylable_container(
                "green",
                css_styles="""
            button {
                background-color: #00FF00;
                color: black;
            }""",
        ):
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                pass
            with col2:
                pass
            with col4:
                pass
            with col5:
                pass
            with col3:
                submit = st.button(trad["Done"], key="add_semi_finished_product")
            # submit = st.button(trad["Done"], key="add_semi_finished_product")
            if submit:
                raw_ingredients = {}
                semi_ingredients = {}
                try:
                    for r in range(n_raw_material_ingr):
                        i, q = (st.session_state["all_ingredients"][f'ingredient_{r}grid_raw_material_ingr'],
                                st.session_state["all_ingredients"][f'ingredient_quantity_{r}grid_raw_material_ingr'])
                        if i is not None:
                            raw_ingredients[i] = q
                    for r in range(n_semi_finished_prod_ingr):
                        i, q = (st.session_state["all_ingredients"][f'ingredient_{r}semi_finished_products_as_ingredients_id_to_name'],
                                st.session_state["all_ingredients"][f'ingredient_quantity_{r}semi_finished_products_as_ingredients_id_to_name'])
                        if i is not None:
                            semi_ingredients[i] = q
                    del st.session_state["all_ingredients"]
                    all_ingredients1 = {raw_materials_name_to_id[ingredient]: quantity for ingredient, quantity in raw_ingredients.items()}
                    all_ingredients2 = {semi_finished_products_as_ingredients_name_to_id[ingredient]: quantity for ingredient, quantity in semi_ingredients.items()}
                    all_ingredients = all_ingredients1 | all_ingredients2

                    instance = models.SemiFinishedProduct(
                        name=name,
                        date=date,
                        expiration_date=expiration_date,
                        batch_number=batch_number,
                        quantity=quantity,
                        quantity_unit=quantity_unit,
                        ingredients=all_ingredients
                    )
                    instance.insert()
                    # for ingredient_id, quantity in all_ingredients.items(): # todo update quantity of raw materials and semi-finished products
                    st.warning("The quantity of raw materials and semi-finished products has not been updated")

                    st.success(trad["Semi-Finished Product added successfully"])
                    st.balloons()
                except Exception as e:
                    error = True
                    st.error(f"Error adding semi-finished product {e}")

        search_word = st.text_input(trad["Search"])

        all_semi_finished_products = models.query_collection(models.SemiFinishedProduct,
                                                             models.semi_finished_product_collection, **{"name": search_word, "batch_number": search_word})
        semi_finished_products_id_to_name = {semi_finished_product.id: f"{semi_finished_product.name} - {semi_finished_product.batch_number}" for
                                             semi_finished_product in all_semi_finished_products}
        semi_finished_products_name_to_id = {f"{semi_finished_product.name} - {semi_finished_product.batch_number}": semi_finished_product.id for
                                             semi_finished_product in all_semi_finished_products}

        selection = st.selectbox(trad["Select Semi-Finished Product"], list(semi_finished_products_id_to_name.values()), index=None)
        load_selected = st.button(trad["Load Selected"])
        if load_selected and selection:
            semi_finished_product = models.get_semi_finished_product_by_id(semi_finished_products_name_to_id[selection])
            st.session_state["form_semi_finished_product"] = semi_finished_product.dict()
            st.session_state["form_semi_finished_product"]["all_ingredients_raw_material"] = {}
            st.session_state["form_semi_finished_product"]["all_ingredients_semi_finished_product"] = {}
            # get all ingredients
            for ingredient_id, quantity in semi_finished_product.ingredients.items():
                if ingredient_id in raw_materials_id_to_name:
                    st.session_state["form_semi_finished_product"]["all_ingredients_raw_material"][raw_materials_id_to_name[ingredient_id]] = quantity
                if ingredient_id in semi_finished_products_as_ingredients_id_to_name:
                    st.session_state["form_semi_finished_product"]["all_ingredients_semi_finished_product"][semi_finished_products_as_ingredients_id_to_name[ingredient_id]] = quantity
            name_placeholder.text_input(trad["Name"], value=semi_finished_product.name)
            date_placeholder.date_input(trad["Production Date"], value=semi_finished_product.date)
            expiration_date_placeholder.date_input(trad["Expiration Date"], value=semi_finished_product.expiration_date)
            batch_number_placeholder.text_input(trad["batch number"], value=semi_finished_product.batch_number)
            quantity_placeholder.number_input(trad["Quantity"], value=semi_finished_product.quantity)
            try:
                index = list(models.QuantityEnum).index(semi_finished_product.quantity_unit)
            except ValueError:
                index = None
            quantity_unit_placeholder.selectbox(trad["Unit"], models.QuantityEnum.__members__.keys(), index=index)

            # --------------------------------------------------------------


        # # Filter the dataframe using the temporary column, then drop the column
        # load_selected = st.button(trad["Load Selected"])
        # selected_rows = edited_df[edited_df.Select]
        # if len(selected_rows) > 0:
        #     selected_row = selected_rows.iloc[0]
        #     if load_selected:
        #         st.session_state["form_semi_finished_product"] = dict(
        #             name=selected_row["name"]
        #         )

        # todo aggingere tabella con i semilavorati presenti nel database e possibilità di selezionare un semilavorato e "caricarlo" nei campi del form

        # todo possibilità di leggere e generare barcode o qrcode per i semilavorati e i materiali grezzi
        # con una pistola/telefono si vuole leggere il qrcode ed aggiungerlo in automatico alla lista ingredienti
        add_vertical_space(200)

        """
        Un prodotto semilavorato è un prodotto che non è ancora finito, ma che ha subito una certa quantità di lavorazione.
        Quando si aggiunge un semilavorato al database, oltre ai campi fissi, è necessario specificare i materiali grezzi o i semilavorati che lo compongono e la quantità di ciascuno.
        Non possono essere usati semilavorati o materiali grezzi che non sono presenti nel database.
        1) Per prima cosa è necessario recuperare dal database i materiali grezzi e i semilavorati.
        2) Poi è necessario aggiungere un semilavorato o materiale grezzo alla lista degli ingredienti del semilavorat che si sta aggiungendo.
        3) Infine è necessario specificare la quantità di ciascun ingrediente.
        4) il sistema permette di "prelevare" dal magazino i materiali grezzi e semilavorati solo se la quantità presente è sufficiente.
        5) il sistema permette di "prelevare" dal magazino i materiali grezzi e semilavorati solo non sono scaduti.
        """

    # Raw Materials Tab
    with tab2:
        st.header(trad["Raw Materials"])
        error = False
        suppliers = models.query_collection(models.Supplier, models.supplier_collection, **{})
        suppliers_id_to_name = {supplier.id: supplier.name for supplier in suppliers}
        suppliers_name_to_id = {supplier.name: supplier.id for supplier in suppliers}
        raw_materials = models.query_collection(models.RawMaterial, models.raw_material_collection, **{})

        with st.form(trad["Add Raw Material"]):
            name = st.text_input(trad["Name"])
            supplier_name = st.selectbox(trad["Supplier name"], suppliers_id_to_name.values(), index=None)
            date = st.date_input(trad["Acquiring Date"])
            expiration_date = st.date_input(trad["Expiration Date"])
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
                    deleted_rows = edited_df[edited_df["delete"] is True]
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

    # Suppliers Tab
    with tab3:
        st.header(trad["Suppliers"])
        error = False
        suppliers = models.query_collection(models.Supplier, models.supplier_collection, **{})
        # generate_form(models.Supplier)
        with st.form(trad["Add Supplier"]):

            name = st.text_input(trad["Name"])
            address = st.text_input(trad["Address"])
            phone = st.text_input(trad["Phone number"])
            email = st.text_input(trad["Email"])
            submit = st.form_submit_button(trad["Add Supplier"])
            if name in [supplier.name for supplier in suppliers]:
                st.error(trad["Supplier already exists"])
            if submit:
                try:
                    instance = models.Supplier(name=name, address=address, phone=phone, email=email)
                    instance.insert()
                    st.success(trad["Supplier added successfully"])
                    st.balloons()
                except Exception as e:
                    error = True
                    st.error(f"Error adding supplier {e}")

        df = models.to_dataframes(suppliers)  # .drop('_id', axis=1)
        if len(df) > 0:

            edited_df = dataframe_with_selections(df)
            if st.button(trad["Modify Data"], key="supplier modify data"):
                edited_df = edited_df.dropna(how='all')
                try:
                    deleted_rows = edited_df[edited_df["delete"] == True]
                    edited_df = edited_df.drop(columns=["delete"])
                    if len(deleted_rows) > 0:
                        for index, row in deleted_rows.iterrows():
                            models.delete_supplier_by_id(row['_id'])
                except Exception as e:
                    error = True
                    st.error(f"Error deleting supplier {e} {edited_df.columns} {edited_df}")

                try:
                    # select new rows of edited_df wrt original df
                    new_rows = edited_df[~edited_df.index.isin(df.index)]
                    if len(new_rows) > 0:
                        for index, row in new_rows.iterrows():
                            instance = models.Supplier(**row.dropna().to_dict())
                            instance.insert()
                except Exception as e:
                    error = True
                    st.error(f"Error adding supplier {e} {edited_df.columns} {edited_df}")

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
                            supplier = models.Supplier(**row.to_dict())
                            supplier.insert(update=True)
                except Exception as e:
                    error = True
                    st.error(f"Error modifying supplier {e} {edited_df.columns} {edited_df}")
                if not error:
                    st.success(trad["Data modified successfully"])
                    st.balloons()
                else:
                    st.error(trad["Error modifying data"])


if __name__ == "__main__":
    main()

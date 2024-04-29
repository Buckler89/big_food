import streamlit as st
import pymongo
from bson.objectid import ObjectId
from datetime import datetime
from pydantic import ValidationError

# Assuming your models and database initialization are in a file named models.py
import models
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import pandas as pd


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters")

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
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
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

def dataframe_with_selections(df, config_columns=None, disabled=False):
    df_with_selections = df.copy()
    df_with_selections.insert(len(df_with_selections.columns), "delete", False)
    column_config_base = {
        "delete": st.column_config.CheckboxColumn(required=True, default=False),
        "_id": None,
    }
    column_config_base.update(config_columns or {})
    # Get dataframe row-selections from user with st.data_editor
    edited_df = st.data_editor(
        df_with_selections,
        hide_index=True,
        column_config=column_config_base,
        disabled=disabled,
        num_rows="dynamic",
        # key=hash(df_with_selections.columns.values.tobytes()),

    )

    return edited_df

def generate_form(model_class):
    with st.form(f"Add {model_class.__name__}"):
        for field_name, info in model_class.__fields__.items():
            if field_name == "_id":
                continue
            if info.annotation is datetime:
                value = st.date_input(field_name)
            elif info.annotation is int:
                value = st.number_input(field_name)
            elif info.annotation is list:
                value = st.text_input(field_name)
            else:
                value = st.text_input(field_name)
        submit = st.form_submit_button(f"Add {model_class.__name__}")
        if submit:
            instance = model_class(**{field.name: value})
            instance.insert()
        return value

def main():
    st.set_page_config(
        page_title="Ex-stream-ly Cool App",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://www.extremelycoolapp.com/help',
            'Report a bug': "https://www.extremelycoolapp.com/bug",
            'About': "# This is a header. This is an *extremely* cool app!"
        }
    )
    st.title('Food Traceability Database Management')

    tab1, tab2, tab3 = st.tabs(["Suppliers", "Raw Materials", "Semi-Finished Products"])

    # Suppliers Tab
    with tab1:
        st.header("Suppliers")
        error = False
        suppliers = models.query_collection(models.Supplier, models.supplier_collection, **{})
        # generate_form(models.Supplier)
        with st.form("Add Supplier"):

            name = st.text_input("Name")
            address = st.text_input("Address")
            phone = st.text_input("Phone")
            email = st.text_input("Email")
            submit = st.form_submit_button("Add Supplier")
            if name in [supplier.name for supplier in suppliers]:
                st.error("Supplier already exists")
            if submit:
                try:
                    instance = models.Supplier(name=name, address=address, phone=phone, email=email)
                    instance.insert()
                    st.success("Supplier added successfully")
                    st.balloons()
                except Exception as e:
                    error = True
                    st.error(f"Error adding supplier {e}")

        df = models.to_dataframes(suppliers)  # .drop('_id', axis=1)
        edited_df = dataframe_with_selections(df)
        if st.button("Modify Data", key="supplier modify data"):
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
                st.success("Data modified successfully")
                st.balloons()
            else:
                st.error("Error modifying data")

    # Raw Materials Tab
    with tab2:
        st.header("Raw Materials")
        error = False
        suppliers = models.query_collection(models.Supplier, models.supplier_collection, **{})
        suppliers_id_to_name = {supplier.id: supplier.name for supplier in suppliers}
        suppliers_name_to_id = {supplier.name: supplier.id for supplier in suppliers}
        raw_materials = models.query_collection(models.RawMaterial, models.raw_material_collection, **{})

        with st.form("Add Raw Material"):
            name = st.text_input("Name")
            supplier_name = st.selectbox("Supplier name", suppliers_id_to_name.values(), index=None)
            date = st.date_input("Acquiring Date")
            expiration_date = st.date_input("Expiration Date")
            batch_number = st.text_input("Supplier batch number")
            document_number = st.text_input("Document Number")
            quantity = st.number_input("Quantity")
            quantity_unit = st.selectbox("Quantity Unit", models.QuantityEnum.__members__.keys(), index=None)
            submit = st.form_submit_button("Add Raw Material")

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
                    st.success("Raw Material added successfully")
                    st.balloons()
                except Exception as e:
                    error = True
                    st.error(f"Error adding raw material {e}")

        df = models.to_dataframes(raw_materials)  # .drop('_id', axis=1)
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
                st.success("Data modified successfully")
                st.balloons()
            else:
                st.error("Error modifying data")

    # Semi-Finished Products Tab
    with tab3:
        pass


if __name__ == "__main__":
    main()

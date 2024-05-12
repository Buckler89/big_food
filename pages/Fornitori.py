import streamlit as st
import models
import lang
from utils import generate_barcode, dataframe_with_selections

# Initialization
trad = lang.get_translations(lang.lang_choice)

st.sidebar.image("https://www.livafritta.it/wp-content/uploads/2020/02/logo-livafritta-01.png")


def main():
    st.title(trad["software name"])

    tab1, = st.tabs([

        trad["Suppliers"],
    ])


    # Suppliers Tab
    with tab1:
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
                bar_code = generate_barcode(name)
                st.image(bar_code)

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
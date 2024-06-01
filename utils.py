from typing import Union, List
import streamlit as st
import lang
import pandas as pd
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import barcode
from barcode.writer import ImageWriter
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm
import io
from PIL import Image
import lang
import models

trad = lang.get_translations(lang.lang_choice)


def generate_barcode(text, img_format="byte"):
    assert img_format in ["byte", "PIL", "pdf"]
    # Generate barcode image
    barcode_class = barcode.get_barcode_class('code128')
    barcode_image = barcode_class(text, writer=ImageWriter())

    # Save to a BytesIO object
    image_io = io.BytesIO()
    barcode_image.write(image_io)
    image_io.seek(0)  # move cursor to the beginning of the file
    if img_format == "byte":
        return image_io.read()
    elif img_format == "PIL":
        return Image.open(image_io)
    elif img_format == "pdf":
        # Create a PDF with the barcode
        pdf_io = io.BytesIO()
        custom_page_size = (70 * mm, 30 * mm)  # Example: 70mm x 30mm
        c = canvas.Canvas(pdf_io, pagesize=custom_page_size)

        # c = canvas.Canvas(pdf_io, pagesize=letter)

        image = Image.open(image_io)
        image_reader = ImageReader(image)
        c.drawImage(image_reader, 3 * mm, 3 * mm, width=60 * mm, height=20 * mm)
        # c.drawImage(image_reader, 0, 0, width=200, height=100)
        c.showPage()
        c.save()
        pdf_io.seek(0)
        return pdf_io.read()


def search_elemnts(db_class, db_collection, search_word=None, query=None, filter: dict = {}):
    if query is None:
        filter.update({"name": search_word, "batch_number": search_word})
    elif filter != {}:
        filter = {}
        print(Warning("filter will be ignored if query is not None"))
    elements = models.query_collection(db_class, db_collection, mode='OR', query=query,
                                                         **filter)

    id_to_name = {element.id: f"{element.name}-{element.batch_number}" for element in elements}
    name_to_id = {f"{element.name}-{element.batch_number}": element.id for element in elements}
    name_to_batch = {f"{element.name}-{element.batch_number}": element.batch_number for element in elements}
    return id_to_name, name_to_id, name_to_batch


def manage_barcode(db_class, db_collection, radio_label):
    st.header(trad["Generate Barcode"])
    col1, col2 = st.columns(2)
    with col2:
        barcode_image_placeholder = st.empty()
        download_button_placeholder = st.empty()
    with col1:
        search_word = st.text_input(trad["Search"])
    id_to_name, name_to_id, name_to_batch = search_elemnts(db_class, db_collection, search_word)
    with col1:
        selection = st.radio(radio_label,
                             list(id_to_name.values())[:20], index=None,)
    if selection:
        img_format = "pdf"
        if img_format in ["byte", "PIL"]:
            extension = "png"
            mime = "image/png"
        elif img_format == "pdf":
            extension = "pdf"
            mime = "application/pdf"
        bar_code_img = generate_barcode(name_to_batch[selection])
        bar_code = generate_barcode(name_to_batch[selection], img_format=img_format)
        barcode_image_placeholder.image(bar_code_img)
        btn = download_button_placeholder.download_button(
                label="Download barcode",
                data=bar_code,
                file_name=f"{selection}.{extension}",
                mime=mime
              )
    return selection, id_to_name, name_to_id, name_to_batch


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
                    format=lang.datetime_format
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
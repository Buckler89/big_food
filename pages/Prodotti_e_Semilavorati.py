import streamlit as st
st.set_page_config(layout="wide")
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.add_vertical_space import add_vertical_space
from datetime import datetime
import models
import lang
from utils import manage_barcode
from uuid import uuid4
# Initialization
trad = lang.get_translations(lang.lang_choice)

st.sidebar.image("https://www.livafritta.it/wp-content/uploads/2020/02/logo-livafritta-01.png")
max_n_ingredients = 30


def manage_barcode_reader(n_semi_finished_prod_ingr_placeholder):
    barcode = st.session_state.scansioned_bar_code
    print(barcode)
    # Aggiorna il valore di un altro widget tramite session_state
    if barcode:
        try:

            # Imposta il valore di session_state per il numero
            st.session_state.n_raw_material_ingr += 1  # esempio di calcolo
            st.session_state.scansioned_bar_code = ""  # esempio di calcolo
            # the string is a list of barcodes separated by a newline
            # each barcode is a string representing a batch number of an ingredient
            # the batch number is used to identify the ingredient in the database
            # st.session_state[f"ingredient_{row}{key}"]
            st.session_state[f"ingredient_{st.session_state.n_raw_material_ingr - 1}grid_raw_material_ingr"] = 'carne di suino - 2939340'
            try:
                ingredient = models.get_raw_material_by_batch_number(barcode)
                if ingredient:

                    # add the ingredient to the list of ingredients
                    # if the ingredient is already in the list, increment the quantity
                    # if the ingredient is not in the list, add it to the list
                    st.session_state[
                        f"ingredient_{st.session_state.n_raw_material_ingr - 1}grid_raw_material_ingr"] =\
                        f"{ingredient.name} - {ingredient.batch_number}"
                else:
                    ingredient = models.get_semi_finished_product_by_batch_number(barcode)
                    if ingredient:
                        # add the ingredient to the list of ingredients
                        # if the ingredient is already in the list, increment the quantity
                        # if the ingredient is not in the list, add it to the list
                        st.session_state[
                            f"ingredient_{st.session_state.n_raw_material_ingr - 1}semi_finished_products_as_ingredients_id_to_name"] = \
                            f"{ingredient.name} - {ingredient.batch_number}"
                    else:
                        st.error(f"Ingredient with batch number {barcode} not found")
                        st.session_state.n_raw_material_ingr -= 1  # undo the increment
            except Exception as e:
                error = True
                st.error(f"Error adding ingredient {e}")
        except ValueError:
            st.error("Please enter a valid number for barcode.")


def main():
    # st.title(trad["software name"])
    st.title(trad["Semi-Finished Products"])

    tab1, tab2 = st.tabs([
        trad["Data Entry"],
        trad["Data Search"],
    ])


    # Semi-Finished Products Tab
    with tab1:
        st.header(trad["Semi-Finished Products"])
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

        st.write(f'## {trad["Ingredients"]}')
        st.write(f'#### {trad["Scan Barcode"]}')
        scan_barcode_placeholder = st.empty()
        st.write(f'#### {trad["Manual Input"]}')
        st.write(f'##### {trad["Raw Materials"]}')
        n_raw_material_ingr_placeholder = st.empty()
        grid_raw_material_ingr_placeholder = st.empty()
        st.write(f'##### {trad["Semi-Finished Products"]}')
        n_semi_finished_prod_ingr_placeholder = st.empty()
        grid_semi_finished_prod_ingr_placeholder = st.empty()

        # columns to lay out the inputs
        # if st.session_state.get("all_ingredients") is None:
        # https://mathcatsand-examples.streamlit.app/add_data
        # n_raw_material_ingr = st.slider(trad['How many Raw Material?'], min_value=1, max_value=20)
        # n_semi_finished_prod_ingr = st.slider(trad['How many Semi-Finished Products?'], min_value=1, max_value=20)

        scansioned_bar_code = scan_barcode_placeholder.text_input(trad["Scan Barcode"], on_change=manage_barcode_reader, args=(n_semi_finished_prod_ingr_placeholder,), key="scansioned_bar_code")

        n_raw_material_ingr = n_raw_material_ingr_placeholder.number_input(trad['How many Raw Material?'], min_value=0, max_value=max_n_ingredients, step=1, key="n_raw_material_ingr")
        grid_raw_material_ingr = grid_raw_material_ingr_placeholder.columns(2)

        n_semi_finished_prod_ingr = n_semi_finished_prod_ingr_placeholder.number_input(trad['How many Semi-Finished Products?'], min_value=0, max_value=max_n_ingredients, step=1, key="n_semi_finished_prod_ingr")
        grid_semi_finished_prod_ingr = grid_semi_finished_prod_ingr_placeholder.columns(2)

        raw_material_ingredients_placeholders = [grid_raw_material_ingr[0].empty() for _ in range(max_n_ingredients)] # column 1
        raw_materials_ingredient_quantity_placeholders = [grid_raw_material_ingr[1].empty() for _ in range(max_n_ingredients)] # column 2
        semi_finished_products_as_ingredients_placeholders = [grid_semi_finished_prod_ingr[0].empty() for _ in range(max_n_ingredients)] # column 1
        semi_finished_products_as_ingredients_quantity_placeholders = [grid_semi_finished_prod_ingr[1].empty() for _ in range(max_n_ingredients)] # column 2

        semi_finished_products = models.query_collection(models.SemiFinishedProduct, models.semi_finished_product_collection, **{})

        name_options = list(set([instance.name.strip() for instance in semi_finished_products]))
        name_options.insert(0, trad["Insert new..."])
        # name = name_placeholder.text_input(trad["Name"], key="semi_finished_product_name", value=st.session_state.get("form_semi_finished_product", {}).get("name", None))

        name = name_placeholder.selectbox(trad["Name"], key="semi_finished_product_name", options=name_options, index=None)

        # Create text input for user entry
        if name == trad["Insert new..."]:
            name = name_placeholder.text_input(trad["Enter your other option..."])

        # # Just to show the selected option
        # if name != "Another option...":
        #     st.info(f":white_check_mark: The selected option is {selection} ")
        # else:
        #     st.info(f":white_check_mark: The written option is {otherOption} ")

        prod_date = date_placeholder.date_input(trad["Production Date"], key="semi_finished_product_date", format=lang.datetime_format, value=st.session_state.get("form_semi_finished_product", {}).get("date", None))  # this must be before the query since it is used to filter the expiration date
        if prod_date:
            prod_date = datetime.combine(prod_date, datetime.min.time())
        # if st.session_state.get("form_semi_finished_product") is None:
        semi_finished_products_as_ingredients = models.query_collection(models.SemiFinishedProduct,
                                                                        models.semi_finished_product_collection, **{
                "is_finished": False,
                "expiration_date": {"$gte": prod_date if prod_date is not None else datetime.now()}
            })
        semi_finished_products_as_ingredients_id_to_name = {semi_finished_product.id: f"{semi_finished_product.name} - {semi_finished_product.batch_number}" for
                                             semi_finished_product in semi_finished_products_as_ingredients}
        semi_finished_products_as_ingredients_name_to_id = {f"{semi_finished_product.name} - {semi_finished_product.batch_number}": semi_finished_product.id for
                                             semi_finished_product in semi_finished_products_as_ingredients}

        raw_materials = models.query_collection(models.RawMaterial, models.raw_material_collection, **{
                "is_finished": False,
                "expiration_date": {"$gte": prod_date if prod_date is not None else datetime.now()}
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
            # else:
            #     pass

        expiration_date = expiration_date_placeholder.date_input(trad["Expiration Date"], key="semi_finished_product_expiration_date", format=lang.datetime_format, value=st.session_state.get("form_semi_finished_product", {}).get("expiration_date", None))
        if prod_date is not None:
            bn = f'{prod_date.strftime("%y%m%d")}{str(uuid4().int)[:4]}'
        else:
            bn = None
        st.session_state["semi_finished_product_batch_number"] = bn
        batch_number = batch_number_placeholder.text_input(trad["batch number"],  key="semi_finished_product_batch_number", disabled=True)#st.session_state.get("form_semi_finished_product", {}).get("batch_number", None))

        quantity = quantity_placeholder.number_input(trad["Quantity"], key="semi_finished_product_quantity", value=st.session_state.get("form_semi_finished_product", {}).get("quantity", None))
        try:
            index = list(models.QuantityEnum).index(st.session_state.get("form_semi_finished_product", {}).get("quantity_unit", None))
        except ValueError:
            index = None
        quantity_unit = quantity_unit_placeholder.selectbox(trad["Unit"], models.QuantityEnum.__members__.keys(), index=index, key="semi_finished_product_quantity_unit")


        # Function to create a row of widgets (with row number input to assure unique keys)
        def add_ingr_placeholder(row, options, key, placeholder, max_quantity_value=None, index=None, value=None):
            # i = st.selectbox(trad["Ingredient"], options, index=None, key=f'ingredient_{row}{id(grid)}')
            st.session_state["all_ingredients"][f"ingredient_{row}{key}"] = placeholder[0][row].selectbox(
                f'{trad["Ingredient"]} {row+1}',
                options,
                index=index,
                key=f"ingredient_{row}{key}",
            )
            max_value = max_quantity_value.get(st.session_state["all_ingredients"][f"ingredient_{row}{key}"])
            type_ = type(max_value) if max_value is not None else int
            st.session_state["all_ingredients"][f"ingredient_quantity_{row}{key}"] = \
            placeholder[1][row].number_input(
                trad["Quantity"], step=type_(1), min_value=type_(0), max_value=max_value, #max value non funziona
                key=f"ingredient_quantity_{row}{key}",
                value=value, placeholder=f"{max_value} {trad['available']}")

        # def generate_ingr_elements(max_quantity_value_raw_material):
        # Loop to create rows of input widgets
        if st.session_state.get("all_ingredients") is None:
            st.session_state["all_ingredients"] = {}

        for r in range(n_raw_material_ingr):
            # if st.session_state["all_ingredients"].get(f'ingredient_{r}{id(grid_raw_material_ingr)}', 'None') == 'None':
            # if st.session_state.get(f'ingredient_{r}{id(grid_raw_material_ingr)}') is None:
            # add_ingr(r, grid_raw_material_ingr, list(raw_materials_id_to_name.values()), key="grid_raw_material_ingr", max_quantity_value=max_quantity_value_raw_material, placeholder=raw_material_ingredients_placeholders[r])
            add_ingr_placeholder(r, list(raw_materials_id_to_name.values()), key="grid_raw_material_ingr", max_quantity_value=max_quantity_value_raw_material, placeholder=(raw_material_ingredients_placeholders, raw_materials_ingredient_quantity_placeholders))

        for r in range(n_semi_finished_prod_ingr):
            # if st.session_state["all_ingredients"].get(f'ingredient_{r}{id(grid_semi_finished_prod_ingr)}', 'None') == 'None':
            # if st.session_state.get(f'ingredient_{r}{id(grid_semi_finished_prod_ingr)}') is None:
            # add_ingr(r, grid_semi_finished_prod_ingr, list(semi_finished_products_as_ingredients_id_to_name.values()), key="semi_finished_products_as_ingredients_id_to_name", max_quantity_value=max_quantity_value_semi_finished_products, placeholder=semi_finished_products_as_ingredients_placeholders[r])
            add_ingr_placeholder(r, list(semi_finished_products_as_ingredients_id_to_name.values()), key="semi_finished_products_as_ingredients_id_to_name", max_quantity_value=max_quantity_value_semi_finished_products, placeholder=(semi_finished_products_as_ingredients_placeholders, semi_finished_products_as_ingredients_quantity_placeholders))

        # generate_ingr_elements(max_quantity_value_raw_material)
        # --------------------------------------------------------------
        st.markdown("<hr>", unsafe_allow_html=True)

        add_vertical_space(1)

        # ---- pulsante centrato e verde
        with stylable_container(
                "green",
                css_styles="""
            button {
                background-color: #00FF00;
                color: black;
            }""",
        ):
            col1, col2, col3, col4, col5 = st.columns(5) # odd number of columns to center the button
            with col1:
                pass
            with col2:
                pass
            with col4:
                pass
            with col5:
                pass
            with col3: # center the button in the middle column
                submit = st.button(trad["Done"], key="add_semi_finished_product")
            # submit = st.button(trad["Done"], key="add_semi_finished_product")
            # ----- fine definizione pulsante centrato e verde
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
                        # name=st.session_state["form_semi_finished_product"]["name"],
                        # date=st.session_state["form_semi_finished_product"]["date"],
                        # expiration_date=st.session_state["form_semi_finished_product"]["expiration_date"],
                        # batch_number=st.session_state["form_semi_finished_product"]["batch_number"],
                        # quantity=st.session_state["form_semi_finished_product"]["quantity"],
                        # quantity_unit=st.session_state["form_semi_finished_product"]["quantity_unit"],
                        # ingredients=all_ingredients,
                        name=name,
                        date=prod_date,
                        expiration_date=expiration_date,
                        batch_number=batch_number,
                        quantity=quantity,
                        quantity_unit=quantity_unit,
                        ingredients=all_ingredients
                    )
                    instance.insert()
                    def update_quantity(ingredient_id, quantity, get_id_function):
                        ing = get_id_function(ingredient_id)
                        ing.consumed_quantity += quantity
                        assert ing.consumed_quantity <= ing.quantity # should never happen because max available quantity is checked in the form at input time
                        if ing.consumed_quantity == ing.quantity:
                            ing.is_finished = True
                        ing.insert(update=True)

                    for ingredient_id, quantity in all_ingredients1.items():
                        update_quantity(ingredient_id, quantity, models.get_raw_material_by_id)
                    for ingredient_id, quantity in all_ingredients2.items():
                        update_quantity(ingredient_id, quantity, models.get_semi_finished_product_by_id)

                    st.success(trad["Semi-Finished Product added successfully"])
                    st.success(trad["Ingredients consumed successfully"])
                    st.balloons()
                except Exception as e:
                    error = True
                    st.error(f"Error adding semi-finished product {e}")

        # with st.sidebar:
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            # search_word = st.text_input(trad["Search"])
            #
            # all_semi_finished_products = models.query_collection(models.SemiFinishedProduct,
            #                                                      models.semi_finished_product_collection, mode='OR', **{"name": search_word, "batch_number": search_word})
            # semi_finished_products_id_to_name = {semi_finished_product.id: f"{semi_finished_product.name} - {semi_finished_product.batch_number}" for
            #                                      semi_finished_product in all_semi_finished_products}
            # semi_finished_products_name_to_id = {f"{semi_finished_product.name} - {semi_finished_product.batch_number}": semi_finished_product.id for
            #                                      semi_finished_product in all_semi_finished_products}
            #
            # # selection = st.selectbox(trad["Select Semi-Finished Product"], list(semi_finished_products_id_to_name.values()), index=None)
            # selection = st.radio(trad["Select Semi-Finished Product"], list(semi_finished_products_id_to_name.values())[:20], index=None,)
            o = manage_barcode(models.SemiFinishedProduct, models.semi_finished_product_collection, trad["Select Semi-Finished Product"])
            selection = o[0]
            semi_finished_products_name_to_id = o[2]
        with col2:
            # load_selected = st.button(trad["Load Selected"])
            delete_selected = st.button(trad["Delete this product"])
            if selection:
                semi_finished_product = models.get_semi_finished_product_by_id(semi_finished_products_name_to_id[selection])
                # st.session_state["form_semi_finished_product"] = semi_finished_product.dict()
                # st.session_state["form_semi_finished_product"]["all_ingredients_raw_material"] = {}
                # st.session_state["form_semi_finished_product"]["all_ingredients_semi_finished_product"] = {}
                # get all ingredients
                # for ingredient_id, quantity in semi_finished_product.ingredients.items():
                #     if ingredient_id in raw_materials_id_to_name:
                #         st.session_state["form_semi_finished_product"]["all_ingredients_raw_material"][raw_materials_id_to_name[ingredient_id]] = quantity
                #     if ingredient_id in semi_finished_products_as_ingredients_id_to_name:
                #         st.session_state["form_semi_finished_product"]["all_ingredients_semi_finished_product"][semi_finished_products_as_ingredients_id_to_name[ingredient_id]] = quantity

                qi = semi_finished_product.quantity_unit.value


                # create a vertical markdown table with all the semi-finished product data and ingredients
                # with st.sidebar:
                st.markdown(f"""
                | {trad["Field"]} | {trad["Value"]} |
                | --- | --- |
                | {trad["Name"]} | {semi_finished_product.name} |
                | {trad["Production Date"]} | {semi_finished_product.date} |
                | {trad["Expiration Date"]} | {semi_finished_product.expiration_date} |
                | {trad["batch number"]} | {semi_finished_product.batch_number} |
                | {trad["Quantity"]} | {semi_finished_product.quantity} |
                | {trad["Unit"]} | {qi} |
                """)
                # | {trad["Ingredients"]} | {semi_finished_product.ingredients} |
                # """)
                # for ingredeint table use the column: name, batch, quantity, unit
                st.write(f'## {trad["Ingredients"]}')
                ingredient_founds = [0, 0]
                for i, (n, f) in enumerate(zip([trad["Raw Materials"], trad["Semi-Finished Products"]], [models.get_raw_material_by_id, models.get_semi_finished_product_by_id])):
                    # table intestation
                    md = f"""
    | {trad["name"]} | {trad["batch number"]} |  {trad["Quantity"]} | {trad["Unit"]} |
    | --- | --- | --- | --- |"""

                    for ingredient_id, quantity in semi_finished_product.ingredients.items():
                        ing = f(ingredient_id)
                        if ing:
                            md += f"""
    | {ing.name} | {ing.batch_number} | {quantity} | {ing.quantity_unit.value} |
    """
                            ingredient_founds[i] += 1
                            break
                    if ingredient_founds[i] > 0:
                        st.markdown(n)
                        st.markdown(md)

            if delete_selected and selection:
                semi_finished_product = models.get_semi_finished_product_by_id(semi_finished_products_name_to_id[selection])
                for ingredient_id, quantity in semi_finished_product.ingredients.items():
                    if ingredient_id in raw_materials_id_to_name:
                        update_quantity(ingredient_id, -quantity, models.get_raw_material_by_id)
                    if ingredient_id in semi_finished_products_as_ingredients_id_to_name:
                        update_quantity(ingredient_id, -quantity, models.get_semi_finished_product_by_id)
                models.delete_semi_finished_product_by_id(semi_finished_products_name_to_id[selection])

if __name__ == "__main__":
    main()

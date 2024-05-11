import streamlit as st

# Placeholder per l'input del codice a barre
barcode_input_placeholder = st.empty()
# Placeholder per l'input del numero
input_number_placeholder = st.empty()


def manage_barcode_reader():
    # Ottieni il valore del codice a barre da session_state
    barcode = st.session_state.barcode
    print(barcode)

    # Aggiorna il valore di un altro widget tramite session_state
    if barcode:
        try:
            barcode_value = float(barcode)
            # Imposta il valore di session_state per il numero
            st.session_state.barcode_number = barcode_value   # esempio di calcolo
            st.session_state.barcode = ""   # esempio di calcolo
        except ValueError:
            st.error("Please enter a valid number for barcode.")

# Assicurati che il valore iniziale del numero sia gestito tramite session_state
if 'barcode_number' not in st.session_state:
    st.session_state.barcode_number = 0  # valore iniziale predefinito
if 'barcode' not in st.session_state:
    st.session_state.barcode = ""  # valore iniziale predefinito
# Widget per l'input del codice a barre
# barcode = barcode_input_placeholder.text_area("Enter some text", key="barcode", on_change=manage_barcode_reader)
barcode = barcode_input_placeholder.text_input("Enter some text", key="barcode", on_change=manage_barcode_reader, value=st.session_state.barcode)



# Widget per l'input del numero, con valore impostato da session_state
input_number = input_number_placeholder.number_input("Enter a number", key="barcode_number",
                                                     value=st.session_state.barcode_number)



# List of options for the select box
options = ["Apple", "Banana", "Cherry"]

# Key for the select box
select_key = 'fruit_selection'

def on_select_change():
    # Update the session_state value when the select box value changes
    st.session_state[select_key] = selected_fruit
# Assigning a value programmatically using st.session_state
# Check if the select_key is not already in session_state to avoid overwriting user input
# if select_key not in st.session_state:
st.session_state[select_key] = "Banana"

# Creating the select box
selected_fruit = st.selectbox("Choose a fruit:", options, key=select_key, on_change=on_select_change)



import cv2
import numpy as np
import streamlit as st

image = st.camera_input("Show QR code")

if image is not None:
    bytes_data = image.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    detector = cv2.QRCodeDetector()

    data, bbox, straight_qrcode = detector.detectAndDecode(cv2_img)

    st.write("Here!")
    st.write(data)
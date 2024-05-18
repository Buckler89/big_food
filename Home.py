import streamlit as st
st.set_page_config(page_title="Big Food", page_icon="https://www.livafritta.it/wp-content/uploads/2019/12/cropped-favicon-04-32x32.png", layout="wide")

import lang
import models
import numpy as np

# Initialization
trad = lang.get_translations(lang.lang_choice)

st.sidebar.image("https://www.livafritta.it/wp-content/uploads/2020/02/logo-livafritta-01.png")

st.title(trad["software name"])
st.balloons()
# st.success("This is a success message")
# st.error("This is an error message")
st.image("https://www.livafritta.it/wp-content/uploads/2020/06/slide-iniziale-desktop_c.jpg", width=600)
st.page_link("Home.py", label=trad["Home"], icon="🏠")
st.page_link("pages/Prodotti_e_Semilavorati.py", label=trad["Products and Semi-finished Products"], icon="🍞")
st.page_link("pages/Materie_Prime.py", label=trad["Raw Materials"], icon="🌾")
st.page_link("pages/Fornitori.py", label=trad["Suppliers"], icon="👨‍🌾")
st.page_link("http://www.google.com", label=trad["Google"], icon="🌎")



# image = st.camera_input("Show QR code")
#
# if image is not None:
#     bytes_data = image.getvalue()
#     cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
#
#     detector = cv2.QRCodeDetector()
#
#     data, bbox, straight_qrcode = detector.detectAndDecode(cv2_img)
#
#     st.write("Here!")
#     st.write(data)
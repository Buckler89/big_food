import streamlit as st
import lang
# Initialization
trad = lang.get_translations(lang.lang_choice)

st.sidebar.image("https://www.livafritta.it/wp-content/uploads/2020/02/logo-livafritta-01.png")

st.title(trad["software name"])
st.balloons()
# st.success("This is a success message")
# st.error("This is an error message")
st.image("https://www.livafritta.it/wp-content/uploads/2020/06/slide-iniziale-desktop_c.jpg")
st.page_link("Home.py", label=trad["Home"], icon="🏠")
st.page_link("pages/Prodotti_e_Semilavorati.py", label=trad["Products and Semi-finished Products"], icon="🍞")
st.page_link("pages/Materie_Prime.py", label=trad["Raw Materials"], icon="🌾")
st.page_link("pages/Fornitori.py", label=trad["Suppliers"], icon="👨‍🌾")
st.page_link("http://www.google.com", label=trad["Google"], icon="🌎")

import streamlit as st
from lang import get_translations
lang_choice = 'it'
trad = get_translations(lang_choice)
# Initialization
if 'trad' not in st.session_state:
    st.session_state['trad'] = trad
trad = st.session_state['trad']
st.sidebar.image("https://www.livafritta.it/wp-content/uploads/2020/02/logo-livafritta-01.png")

st.title(trad["software name"])
st.balloons()
# st.success("This is a success message")
# st.error("This is an error message")
st.page_link("st_app.py", label=trad["Home"], icon="🏠")
st.page_link("pages/database_management.py", label=trad["Database Management"], icon="1️⃣")
# st.page_link("pages/page_2.py", label="Page 2", icon="2️⃣", disabled=True)
st.page_link("http://www.google.com", label=trad["Google"], icon="🌎")

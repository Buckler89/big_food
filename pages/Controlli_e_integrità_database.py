import streamlit as st
import models
import lang
trad = lang.get_translations(lang.lang_choice)


b = st.button(trad["Check db integrity"])
if b:
    st.write(trad["Checking db integrity..."])
    final_error_table = models.check_db_integrity()
    # transofrm the final_error_table into a markdown table
    if len(final_error_table) == 0:
        st.success(trad["No errors found"])
    else:
        st.error(trad["Errors found"])
        st.write(final_error_table)

b = st.button(trad["Fix db integrity"])
if b:
    st.write(trad["Fixing db integrity..."])
    models.fix_db_strip()
    st.success(trad["Database integrity fixed"])


#
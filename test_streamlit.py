import streamlit as st
import pandas as pd

# Lista prestabilita di ingredienti
ingredienti_prestabiliti = ["Pasta", "Pomodoro", "Basilico", "Olio d'oliva", "Sale", "Pepe", "Formaggio"]


# Funzione per salvare i dati
def salva_piatto(nome_piatto, descrizione, ingredienti):
    piatti = st.session_state.get('piatti', [])
    piatto = {"nome": nome_piatto, "descrizione": descrizione, "ingredienti": ingredienti}
    piatti.append(piatto)
    st.session_state['piatti'] = piatti


# Funzione per caricare un piatto
def carica_piatto(nome_piatto):
    piatti = st.session_state.get('piatti', [])
    for piatto in piatti:
        if piatto['nome'] == nome_piatto:
            return piatto
    return None


# Funzione per aggiornare un piatto
def aggiorna_piatto(nome_piatto, descrizione, ingredienti):
    piatti = st.session_state.get('piatti', [])
    for piatto in piatti:
        if piatto['nome'] == nome_piatto:
            piatto['descrizione'] = descrizione
            piatto['ingredienti'] = ingredienti
    st.session_state['piatti'] = piatti


# Funzione per aggiungere un nuovo ingrediente
def aggiungi_ingrediente():
    if 'nuovi_ingredienti' not in st.session_state:
        st.session_state['nuovi_ingredienti'] = [{'ingrediente': '', 'quantità': 0}]
    else:
        st.session_state['nuovi_ingredienti'].append({'ingrediente': '', 'quantità': 0})


# Funzione per eliminare un ingrediente
def elimina_ingrediente(index):
    if 'nuovi_ingredienti' in st.session_state:
        st.session_state['nuovi_ingredienti'].pop(index)


# Form per inserire o modificare un piatto
st.title("Gestione Piatti")

# Selezione piatto esistente o nuovo piatto
piatti = st.session_state.get('piatti', [])
nomi_piatti = [piatto['nome'] for piatto in piatti]
nome_piatto_selezionato = st.selectbox("Seleziona un piatto da modificare o crea un nuovo piatto",
                                       ["Nuovo Piatto"] + nomi_piatti)

if nome_piatto_selezionato == "Nuovo Piatto":
    nome_piatto = st.text_input("Nome del Piatto")
    descrizione = st.text_area("Descrizione del Piatto")
    st.session_state['nuovi_ingredienti'] = []
else:
    piatto = carica_piatto(nome_piatto_selezionato)
    nome_piatto = piatto['nome']
    descrizione = piatto['descrizione']
    st.session_state['nuovi_ingredienti'] = [{'ingrediente': ing, 'quantità': qty} for ing, qty in
                                             piatto['ingredienti'].items()]

descrizione = st.text_area("Descrizione del Piatto", descrizione, key="descrizione")

# Gestione ingredienti
st.subheader("Ingredienti")
if 'nuovi_ingredienti' not in st.session_state:
    st.session_state['nuovi_ingredienti'] = []

# Aggiungi nuovo ingrediente
if st.button("Aggiungi Ingrediente"):
    aggiungi_ingrediente()

# Mostra ingredienti
ingredienti_modificati = {}
for index, ingrediente in enumerate(st.session_state['nuovi_ingredienti']):
    col1, col2, col3 = st.columns([4, 2, 1])
    with col1:
        ingrediente_selezionato = st.selectbox(f"Ingrediente {index + 1}", ingredienti_prestabiliti,
                                               key=f"ingrediente_{index}",
                                               index=ingredienti_prestabiliti.index(ingrediente['ingrediente']) if
                                               ingrediente['ingrediente'] else 0)
    with col2:
        quantità = st.number_input(f"Quantità {index + 1}", value=ingrediente['quantità'], key=f"quantità_{index}")
    with col3:
        if st.button("Elimina", key=f"elimina_{index}"):
            elimina_ingrediente(index)
            st.experimental_rerun()

    ingredienti_modificati[ingrediente_selezionato] = quantità
    st.session_state['nuovi_ingredienti'][index]['ingrediente'] = ingrediente_selezionato
    st.session_state['nuovi_ingredienti'][index]['quantità'] = quantità

# Pulsante per salvare il piatto
if st.button("Salva Piatto"):
    if nome_piatto_selezionato == "Nuovo Piatto":
        salva_piatto(nome_piatto, descrizione, ingredienti_modificati)
        st.success("Piatto salvato con successo!")
    else:
        aggiorna_piatto(nome_piatto, descrizione, ingredienti_modificati)
        st.success("Piatto aggiornato con successo!")

# Visualizza i piatti salvati
st.subheader("Piatti Salvati")
piatti = st.session_state.get('piatti', [])
if piatti:
    df = pd.DataFrame(piatti)
    st.table(df)
else:
    st.write("Nessun piatto salvato.")

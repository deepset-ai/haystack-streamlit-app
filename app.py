
import streamlit as st
import logging
import os

from json import JSONDecodeError
from utils.haystack import start_document_store, start_haystack_pipeline, query
from utils.ui import reset_results, set_initial_state, sidebar

try:
    set_initial_state()
    document_store = start_document_store()
    pipeline = start_haystack_pipeline(document_store)
    
    sidebar()
    st.write("# My Haystack App")
    
    # For speech-to-text
    # audio_value = st.audio_input("Record a voice message")
    
    # For text-to-speech
    # st.audio("recording.mp3", format="audio/mpeg", loop=True)
    
    # Search bar
    question = st.text_input("Ask a question, try 'How long should the demo video be?'", placeholder="Enter your query", value=st.session_state.question, max_chars=100, on_change=reset_results)

    run_pressed = st.button("Run")

    run_query = (
        run_pressed or question != st.session_state.question
    )

    # Get results for query
    if run_query and question:
        reset_results()
        st.session_state.question = question
        with st.spinner("🔎 &nbsp;&nbsp; Running your pipeline"):
            try:
                st.session_state.results = query(pipeline, question)
            except JSONDecodeError as je:
                st.error(
                    "👓 &nbsp;&nbsp; An error occurred reading the results. Is the document store working?"
                )    
            except Exception as e:
                logging.exception(e)
                st.error("🐞 &nbsp;&nbsp; An error occurred during the request.")

    if st.session_state.results:
        results = st.session_state.results

        st.write(results["chat_generator"]["replies"][0].text)
except SystemExit as e:
    # This exception will be raised if --help or invalid command line arguments
    # are used. Currently streamlit prevents the program from exiting normally
    # so we have to do a hard exit.
    os._exit(e.code)
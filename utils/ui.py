import streamlit as st
from dotenv import load_dotenv

def set_state_if_absent(key, value):
    if key not in st.session_state:
        st.session_state[key] = value

def set_initial_state():
    load_dotenv()
    set_state_if_absent("question", "")
    set_state_if_absent("results", None)

def reset_results(*args):
    st.session_state.results = None
    
def sidebar():
    with st.sidebar:
        st.image('logo/haystack-logo.png')
        st.markdown("**{tech: Berlin} AI Hackathon**")
        
        st.markdown("## 📚 Useful Haystack Resources\n"
                    "* [Get Started](https://haystack.deepset.ai/overview/quick-start)\n"
                    "* [Docs](https://docs.haystack.deepset.ai/docs/intro)\n"
                    "* [Tutorials](https://haystack.deepset.ai/tutorials)\n"
                    "* [Integrations](https://haystack.deepset.ai/integrations)\n"
        )
        st.markdown("Try **deepset Studio**, the development environment for Haystack.\n\n"
                    "It's free and open to everyone, sign up [here](https://landing.deepset.ai/deepset-studio-signup) to start using now."
                    )
        

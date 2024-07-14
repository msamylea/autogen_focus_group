import streamlit as st
from streamlit_extras.stylable_container import stylable_container

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import config as cfg

st.set_page_config(page_title="Virtual Focus Group", page_icon=":tada:", layout="wide")

with open("./docs/chat_summary.txt", 'r') as f:
    summary = f.read()

with stylable_container(
        key="green_button",
        css_styles="""
            button {
                box-shadow: 2px 0 7px 0 grey;
            }
            """,
    ):  
    submit = st.button("Generate Analysis of Focus Group")



    if submit:
        if not summary:
            st.error("No chat data available. Please run a focus group before generating an analysis.")
        else:
            with st.spinner("Processing Analysis..."):
                with stylable_container(
                    key="title_container",
                    css_styles="""
                        {
                            border: 2px solid rgba(49, 51, 63, 0.2);
                            border-radius: 0.5rem;
                            padding: calc(1em - 1px);
                            box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
                        }
                        """,
                ):
                    st.markdown("<h1 style='text-align: center; ;'>Analysis of Group Chat</h1>", unsafe_allow_html=True)
                    st.markdown("<h4 style='text-align: center; color: grey;'>The following is a summary of the focus group chat.</h4>", unsafe_allow_html=True)

                llm = cfg.completions_model

                response = llm.chat.completions.create(
                    messages = [
                        {"role": "system",
                        "content": f"Analyze the focus group chat and provide a detailed summary and analysis of the discussion in markdown format. Chat: {summary}"},
                    ],
                    model=cfg.llama_model
                )

                analysis = response.choices[0].message.content
                
                with stylable_container(
                    key="outer_container",
                    css_styles="""
                        {
                            border: 2px solid rgba(49, 51, 63, 0.2);
                            border-radius: 0.5rem;
                            padding: calc(1em - 1px);
                            box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
                        }
                        """,
                ):
                    with st.container(height=800):

                        st.markdown(analysis, unsafe_allow_html=True)

                with open("./docs/final_analysis.md", 'w') as f:
                    f.write(analysis)

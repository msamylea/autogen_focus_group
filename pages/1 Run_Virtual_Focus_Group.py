import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from typing import Union, Literal
import json
import autogen
from autogen import AssistantAgent, UserProxyAgent, Agent
import persona_handler as ph
import random

import config as cfg

with open('./docs/personas.json', 'r') as f:
    personas = json.load(f)

llm_config={
            "config_list": [
                {
                    "model": cfg.llama_model,
                    "api_key": "ollama", 
                    "base_url": "http://localhost:11434/v1",
                    "max_tokens": 8192, 
                }
            ],
            "cache_seed": None,
        }

# setup page title and description
st.set_page_config(page_title="Virtual Focus Group", page_icon="🤖", layout="wide")
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

    st.markdown("<h4 style='text-align: center; '>To begin, describe your product in detail and explain the type of feedback you are looking for from the group.</h4>", unsafe_allow_html=True)
    st.markdown("<h6 style='text-align: center; '>The focus group will consist of a moderator and a group of personas. The moderator will guide the discussion, while the personas will provide feedback based on their unique characteristics and perspectives.</h6>", unsafe_allow_html=True)

class CustomGroupChatManager(autogen.GroupChatManager):
    def _process_received_message(self, message, sender, silent):
        formatted_message = ""  # Initialize formatted_message as an empty string
        with stylable_container(
            key="container_with_border",
            css_styles="""
                {
                    border: 1px solid rgba(49, 51, 63, 0.2);
                    border-radius: 0.5rem;
                    padding: calc(1em - 1px);
                    box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
                }
                """,
        ):
            # Handle the case when message is a dictionary
            if isinstance(message, dict):
                if 'content' in message and message['content'].strip():
                    formatted_message = f"**{sender.name}**: {message['content']}"
                    st.session_state.setdefault("displayed_messages", []).append(message['content'])
                else:
                    return super()._process_received_message(message, sender, silent)
            # Handle the case when message is a string
            elif isinstance(message, str) and message.strip():
                formatted_message = f"**{sender.name}**: {message}"
                st.session_state.setdefault("displayed_messages", []).append(message)
            else:
                return super()._process_received_message(message, sender, silent)
        
            # Only format and display the message if the sender is not the manager
            if sender != manager and formatted_message:
                with st.chat_message(sender.name):
                    st.markdown(formatted_message + "\n")
                    time.sleep(2)
    
        filename = "./docs/chat_summary.txt"

        with open(filename, 'a') as f:
            f.write(formatted_message + "\n")
        return super()._process_received_message(message, sender, silent)
    
class CustomGroupChat(autogen.GroupChat):
    @staticmethod
    def custom_speaker_selection_func(last_speaker: Agent, groupchat: autogen.GroupChat) -> Union[Agent, Literal['auto', 'manual', 'random', 'round_robin'], None]:
        
        if last_speaker == moderator_agent:
            return random.choice(personas_agents)
        else:
            return random.choice([moderator_agent] + personas_agents)
    select_speaker_message_template = """You are in a focus group. The following roles are available:
                {roles}.
                Read the following conversation.
                Then select the next role from {agentlist} to play. Only return the role."""
       
personas_agents = []
for persona_name, persona_data in personas.items():
    persona_name = persona_data['Name']
    persona_prompt = ph.persona_prompt
    persona_description = json.dumps(personas)
    persona_agent = AssistantAgent(
        name=persona_name,
        system_message=persona_prompt,
        llm_config=llm_config,
        human_input_mode="NEVER",
        description=f"A virtual focus group participant named {persona_name}. They do not know anything about the product beyond what they are told. They should be called on to give opinions.",
    )
    personas_agents.append(persona_agent)


moderator_agent = AssistantAgent(
    name="Moderator",
    system_message=''' 
    You keep the conversation flowing between group members.
    Do not reply more than once before another group member speaks again.
    You can answer group members questions, but you do not offer additional information.
    Do not offer opinions about the topic or user_input, only moderate the conversation.
    Do not say thank you or the end.''',
    default_auto_reply="Reply `TERMINATE` if the task is done.",
    llm_config=llm_config,
    description="A Focus Group moderator.",
    is_termination_msg=lambda x: True if "TERMINATE" in x.get("content") else False,
    human_input_mode="NEVER",
)

user_proxy = UserProxyAgent(
    name="Admin",
    human_input_mode= "NEVER",
    system_message="Human Admin for the Focus Group.",
    max_consecutive_auto_reply=5,
    default_auto_reply="Reply `TERMINATE` if the task is done.",
    is_termination_msg=lambda x: True if "TERMINATE" in x.get("content") else False,
    code_execution_config={"use_docker":False}
)


groupchat = CustomGroupChat(agents=[user_proxy, moderator_agent] + personas_agents, messages=[], speaker_selection_method=CustomGroupChat.custom_speaker_selection_func, max_round=20, select_speaker_message_template=CustomGroupChat.select_speaker_message_template)


manager = CustomGroupChatManager(groupchat=groupchat, llm_config=llm_config)
with stylable_container(
        key="chat_container",
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
        user_input = st.text_area("Describe your product and the topic of discussion to the group:")
        with stylable_container(
            key="green_button",
            css_styles="""
                button {
                    box-shadow: 2px 0 7px 0 grey;
                }
                """,
        ): 
            kickoff = st.button("Start Group Chat")
        
        if kickoff:
        
            llm_config={
                "config_list": [
                    {
                        "model": cfg.llama_model,
                        "api_key": "ollama", 
                        "base_url": "http://localhost:11434/v1",
                        "max_tokens": 8192, 
                    }
                ],
                "cache_seed": None,
            }

        
            if "chat_initiated" not in st.session_state:
                st.session_state.chat_initiated = False
                if not st.session_state.chat_initiated:
                    moderator_agent.initiate_chat(
                        manager,
                        message=user_input,
                    )
                    st.session_state.chat_initiated = True


    st.stop()

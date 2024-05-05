# autogen_focus_group
Virtual focus group with multiple custom personas, product details, and final analysis created with AutoGen, Ollama/Llama3, and Streamlit. 

Uses custom GroupChat and custom GroupChatManager to output the content to Streamlit in an organized, clean chat by removing blank messages and formatting content to use sender name.

Create up to 5 Personas (you can change the data used in demographics_dict.py).  They are saved to docs/personas.json.

Run a virtual focus group with the personas by entering a topic of discussion and kicking it off.  To change the discussion length, edit max_round in './pages/1 Run Virtual Focus Group.py' groupchat entry.  The final chat will be saved to './docs/chat_summary.txt'.

To analyze the discussion, run analysis from Analyze Final Results. 

The TERMINATE function does not trigger well with this code and Llama3, so if you're able to fix that part, let me know how you did it.

The 'l3custom' model mentioned is just the standard Ollama llama3:latest rebuilt with this Modelfile:


  FROM llama3:latest
  TEMPLATE """{{ if .System }}<|start_header_id|>system<|end_header_id|>
  
  {{ .System }}<|eot_id|>{{ end }}{{ if .Prompt }}<|start_header_id|>user<|end_header_id|>
  
  {{ .Prompt }}<|eot_id|>{{ end }}<|start_header_id|>assistant<|end_header_id|>
  
  {{ .Response }}<|eot_id|>"""
  PARAMETER num_keep 24
  PARAMETER stop "<|start_header_id|>"
  PARAMETER stop "<|end_header_id|>"
  PARAMETER stop "<|eot_id|>"
  PARAMETER stop Human:
  PARAMETER stop Assistant:

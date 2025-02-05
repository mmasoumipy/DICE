import base64
import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.beta.assistant_stream_event import (ThreadMessageCreated,
                                                      ThreadMessageDelta,
                                                      ThreadRunStepCompleted,
                                                      ThreadRunStepCreated,
                                                      ThreadRunStepDelta)
from openai.types.beta.threads.runs.code_interpreter_tool_call import (
    CodeInterpreterOutputImage, CodeInterpreterOutputLogs)
from openai.types.beta.threads.runs.tool_calls_step_details import \
    ToolCallsStepDetails
from openai.types.beta.threads.text_delta_block import TextDeltaBlock

# Set page config
st.set_page_config(page_title="DICE", layout="wide")

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

# Initialize OpenAI client and retrieve the assistant
client = OpenAI(api_key=OPENAI_API_KEY)
assistant = client.beta.assistants.retrieve(ASSISTANT_ID)

# Apply custom CSS
st.html("""
    <style>
        #MainMenu, #header, #footer { visibility: hidden; }
        .block-container { padding: 3rem 3rem 2rem 3rem; }
    </style>
""")

# Initialize session state
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False
if "files" not in st.session_state:
    st.session_state.files = []
if "file_id" not in st.session_state:
    st.session_state.file_id = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# Moderation check
def moderation_endpoint(text: str) -> bool:
    """
    Check if the text triggers OpenAI's moderation endpoint.
    
    :param text: The text to check for moderation.

    :return: A boolean indicating if the text was flagged.
    """
    response = client.moderations.create(input=text)
    return response.results[0].flagged

# UI
st.subheader("🪄 DICE: Data Interpretation & Computation Engine")

# File upload section
if not st.session_state.file_uploaded:
    uploaded_files = st.file_uploader(
        "Please upload your dataset(s)", accept_multiple_files=True, type=["csv"]
    )
    if st.button("Upload"):
        for file in uploaded_files:
            oai_file = client.files.create(file=file, purpose="assistants")
            st.session_state.file_id.append(oai_file.id)
            print(f"Uploaded new file: {oai_file.id}")

        st.toast("File(s) uploaded successfully", icon="🚀")
        st.session_state.file_uploaded = True
        st.rerun()

# Main chat functionality
if st.session_state.file_uploaded:
    # Create a new thread if one doesn't exist
    if not st.session_state.thread_id:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id
        print(f"Thread ID: {st.session_state.thread_id}")

    # Attach files to the thread
    client.beta.threads.update(
        thread_id=st.session_state.thread_id,
        tool_resources={"code_interpreter": {"file_ids": st.session_state.file_id}},
    )

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            for item in message["items"]:
                if item["type"] == "text":
                    st.markdown(item["content"])
                elif item["type"] == "image":
                    for image in item["content"]:
                        st.html(image)
                elif item["type"] == "code_input":
                    with st.status("Code", state="complete"):
                        st.code(item["content"])
                elif item["type"] == "code_output":
                    with st.status("Results", state="complete"):
                        st.code(item["content"])

    # Chat input
    if prompt := st.chat_input("Ask me a question about your dataset"):
        if moderation_endpoint(prompt):
            st.toast("Your message was flagged. Please try again.", icon="⚠️")
            st.stop()

        # Add user message to session state and send to OpenAI
        st.session_state.messages.append({"role": "user", "items": [{"type": "text", "content": prompt}]})
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id, role="user", content=prompt
        )

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response
        with st.chat_message("assistant"):
            stream = client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=ASSISTANT_ID,
                tool_choice={"type": "code_interpreter"},
                stream=True,
            )

            assistant_output = []

            for event in stream:
                print(event)

                # Handle code input
                if isinstance(event, ThreadRunStepCreated):
                    if event.data.step_details.type == "tool_calls":
                        assistant_output.append({"type": "code_input", "content": ""})
                        code_input_expander = st.status("Writing code ⏳ ...", expanded=True)
                        code_input_block = code_input_expander.empty()

                elif isinstance(event, ThreadRunStepDelta):
                    if event.data.delta.step_details.tool_calls[0].code_interpreter is not None:
                        code_interpretor = event.data.delta.step_details.tool_calls[0].code_interpreter
                        code_input_delta = code_interpretor.input
                        if code_input_delta:
                            assistant_output[-1]["content"] += code_input_delta
                            code_input_block.code(assistant_output[-1]["content"])

                # Handle code output
                elif isinstance(event, ThreadRunStepCompleted):
                    if isinstance(event.data.step_details, ToolCallsStepDetails):
                        code_interpretor = event.data.step_details.tool_calls[0].code_interpreter
                        if code_interpretor.outputs:
                            code_input_expander.update(label="Code", state="complete", expanded=False)
                            for output in code_interpretor.outputs:
                                if isinstance(output, CodeInterpreterOutputImage):
                                    image_html_list = []
                                    image_file_id = output.image.file_id
                                    image_data = client.files.content(image_file_id).read()
                                    with open(f"images/{image_file_id}.png", "wb") as file:
                                        file.write(image_data)
                                    with open(f"images/{image_file_id}.png", "rb") as file:
                                        data_url = base64.b64encode(file.read()).decode("utf-8")
                                    image_html = f'<p align="center"><img src="data:image/png;base64,{data_url}" width=600></p>'
                                    st.html(image_html)
                                    image_html_list.append(image_html)
                                    assistant_output.append({"type": "image", "content": image_html_list})
                                elif isinstance(output, CodeInterpreterOutputLogs):
                                    code_output = output.logs
                                    with st.status("Results", state="complete"):
                                        st.code(code_output)
                                    assistant_output.append({"type": "code_output", "content": code_output})
                        else:
                            st.warning("No results were generated by the code interpreter.")

                # Handle text output
                elif isinstance(event, ThreadMessageCreated):
                    assistant_output.append({"type": "text", "content": ""})
                    assistant_text_box = st.empty()

                elif isinstance(event, ThreadMessageDelta):
                    if isinstance(event.data.delta.content[0], TextDeltaBlock):
                        assistant_text_box.empty()
                        assistant_output[-1]["content"] += event.data.delta.content[0].text.value
                        assistant_text_box.markdown(assistant_output[-1]["content"])

            # Add assistant response to session state
            st.session_state.messages.append({"role": "assistant", "items": assistant_output})
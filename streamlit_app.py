import streamlit as st
from typing import Generator
from groq import Groq

st.set_page_config(page_icon="💬", layout="wide", page_title="Groq Goes Brrrrrrrr...")

def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )

icon("💊")

st.subheader("LLM Project Calculatr", divider="rainbow", anchor=False)

st.write("## Welcome!")
st.write("This app suports you on estimate cost of project. It is necessary to provide:")
#st.write("It is necessary to provide:")
st.write("position level (i.e. developer python junior), objectives (i.e. create a landing page), funcionalities (i.e. shopping cart),")
#st.write("objectives (i.e. create a landing page)")
st.write("technologies required (i.e. python), team (i.e. 1 ux/ui, 1 junior js developer")
#st.write("technologies required (i.e. python)")
#st.write("team (i.e. 1 ux/ui, 1 junior js developer)")
st.write('Example of prompt:::  Position: junior developer python, objectives: 1. create a landing page 2. create a flyer, functionalities: python, team: 1 ui/ux junior')

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"],
)

# Initialize chat history and selected model
if "messages" not in st.session_state:
    st.session_state.messages = []

# Set the model directly (e.g., "llama3-70b-8192")
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "llama3-70b-8192"  # Set your desired model directly here

# Define model details
models = {
    "llama3-70b-8192": {
        "name": "LLaMA3-70b-Instruct",
        "tokens": 8192,
        "developer": "Meta",
    },
    "llama3-8b-8192": {
        "name": "LLaMA3-8b-Instruct",
        "tokens": 8192,
        "developer": "Meta",
    },
    "mixtral-8x7b-32768": {
        "name": "Mixtral-8x7b-Instruct-v0.1",
        "tokens": 32768,
        "developer": "Mistral",
    },
    "gemma-7b-it": {"name": "Gemma-7b-it", "tokens": 8192, "developer": "Google"},
}

# The selected model is already set, so no need for a dropdown
selected_model = st.session_state.selected_model  # This will always be the fixed model you've set

# Show the selected model
# st.write(f"Selected model: {models[selected_model]['name']}")

# Set max_tokens directly to the maximum value for the selected model
max_tokens = models[selected_model]["tokens"]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👨‍💻"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])  

def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
    """Yield chat response content from the Groq API response."""
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# Get the prompt from the user
if prompt := st.chat_input("Enter your prompt here..."):
    # Add the user's message to the session history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display the user's message
    with st.chat_message("user", avatar="👨‍💻"):
        st.markdown(prompt)

    # Check if the input matches the expected pattern
    if "Position:" not in prompt or "objectives" not in prompt:
        # If the input doesn't match the expected pattern, show an error message
        st.chat_message("assistant", avatar="🤖").markdown("Please follow the pattern: `Position level: <patient_id>, objectives: <objectives> .")
    else:
        try:
            # Extract position
            position = prompt.split("Position:")[1].split(",")[0].strip()  # Extract position
            print(f"Position: {position}")

            # Extract objectives (as a single string)
            objectives = prompt.split("objectives:")[1].split(",")[0].strip()  # Extract objectives as a single string
            print(f"Objectives: {objectives}")

            # Extract functionalities
            functionalities = prompt.split("functionalities:")[1].split(",")[0].strip()  # Extract functionalities
            print(f"Functionalities: {functionalities}")

            # Extract technologies
            technologies = prompt.split("functionalities:")[1].split(",")[-1].strip()  # Extract technologies
            print(f"Technologies: {technologies}")

            # Extract team
            team = prompt.split("team:")[1].strip()  # Extract team
            print(f"Team: {team}")
                  
            # Fill the context template if patient is found

            language = """Voce fala portugues."""
            context = f"""
                    "Sou {position}, e estou trabalhando em uma estimativa de tempo e custos para desenvolver um projeto de software com as seguintes características:

                    Objetivo: {objectives}.
                    Funcionalidades principais: {functionalities}.
                    Tecnologias planejadas: {technologies}.
                    Equipe: {team}.
                    Com base nessas informações:

                    Ajude-me a dividir o projeto em etapas detalhadas.
                    Sugira uma estimativa de tempo para cada etapa com base na complexidade típica.
                    Proponha uma estrutura de custos considerando o tempo estimado e custos médios por hora (ex.: Reais 50/hora por desenvolvedor).
                    Adicione sugestões sobre como otimizar recursos e prever possíveis riscos ou atrasos no cronograma.
                    Se precisar de mais detalhes para fornecer uma estimativa precisa, avise-me e pergunte!
                    """
            #print(context)                

            context_filled = context.format(position=position, 
                                            objectives=objectives, 
                                            technologies=technologies,
                                            team=team)
            
            #print(f"""Context: {context_filled}""")

            try:
                chat_completion = client.chat.completions.create(
                    model=selected_model,  # Use the fixed selected model here
                    messages=[{
                        "role": "user",  # Still specifying role as "user" for the new message
                        "content": language+context_filled  # Pass the context string as content
                    }],
                    max_tokens=max_tokens,  # Use the pre-set max_tokens value
                    stream=True,
                )

                # Use the generator function with st.write_stream to display the response in real-time
                with st.chat_message("assistant", avatar="🤖"):
                    chat_responses_generator = generate_chat_responses(chat_completion)
                    full_response = st.write_stream(chat_responses_generator)

                # Append the assistant's full response to session_state.messages
                if isinstance(full_response, str):
                    st.session_state.messages.append(
                        {"role": "assistant", "content": full_response}
                    )
                else:
                    # Handle the case where full_response is not a string
                    combined_response = "\n".join(str(item) for item in full_response)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": combined_response}
                    )

            except Exception as e:
                st.error(e, icon="🚨")

        except Exception as e:
            st.error(f"An error occurred: {e}", icon="🚨")


# Debugging output (you can remove this in production)
print(f'Full messages: {st.session_state.messages}')
print('--' * 10)
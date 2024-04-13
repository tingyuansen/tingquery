import streamlit as st
import json

# Load your JSON data
def load_data(filename):
    with open(filename, "r") as file:
        data = json.load(file)
    return data

# Function to get compressed text by arXiv ID
def get_compressed_text_by_id(data, arxiv_id):
    for entry in data['arxiv-id'].items():
        if entry[1] == arxiv_id:
            index = entry[0]
            compressed_text = data['compressed_text'][index]
            return compressed_text
    return None

# Streamlit interface
def main():
    st.title("Astrobytes")
    st.markdown("### - the astro-ph machine's digest")
    st.markdown("")

    # Load data
    data = load_data('./astro-ph.ga_streamlit.json')

    # Dropdown menu of arXiv IDs
    arxiv_ids = list(data['arxiv-id'].values())
    dropdown_selection = st.selectbox("Select an arXiv ID from the dropdown:", arxiv_ids)

    # Entry box for arXiv ID
    text_input_selection = st.text_input("...or enter an arXiv ID:")

    # Determine the arXiv ID to use
    arxiv_id = text_input_selection if text_input_selection else dropdown_selection

    # Show the corresponding compressed text and provide a link to the PDF
    if arxiv_id:
        compressed_text = get_compressed_text_by_id(data, arxiv_id)

        if compressed_text:
            st.markdown(compressed_text, unsafe_allow_html=True)

            arxiv_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            st.markdown(f"**arXiv Paper PDF:** [View/Download PDF]({arxiv_url})", unsafe_allow_html=True)
        else:
            st.write("No data found for this arXiv ID")

if __name__ == "__main__":
    main()

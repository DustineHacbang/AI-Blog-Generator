import streamlit as st

st.set_page_config(layout="wide")

st.title("AI Blog Writer")

st.subheader("Enter your blog topic")

with st.sidebar:
    st.title("Input Your Blog Details")
    st.subheader("Enter your blog topic")

    blog_title = st.text_input("Blog Title")
    keywords = st.text_input("Keywords")

    numb_words = st.slider("Number of Words", min_value=250, max_value=1000, value=250)
    num_images = st.number_input("Number of Images", min_value=1, max_value=5, value=1)

    submit_button = st.button("Submit")

# if submit_button:
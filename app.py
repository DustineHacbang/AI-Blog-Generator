import streamlit as st
import requests
import json
from apikey import openai_api_key, ollama_api_key

st.set_page_config(layout="wide")

st.title("AI Blog Writer")

def check_ollama_connection():
    """Check if Ollama is running and accessible"""
    try:
        response = requests.get(f"{ollama_api_key}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return True, [model.get("name", "") for model in models]
        return False, []
    except requests.exceptions.RequestException:
        return False, []

def generate_blog_with_ollama(blog_title, keywords, num_words, model="llama2"):
    """
    Generate blog content using local Ollama LLM
    
    Args:
        blog_title: Title of the blog
        keywords: Keywords for the blog
        num_words: Target number of words
        model: Ollama model name (default: llama2)
    
    Returns:
        Generated blog content or error message
    """
    # Check if Ollama is running first
    is_running, available_models = check_ollama_connection()
    if not is_running:
        return f"❌ **Error: Cannot connect to Ollama**\n\n" \
               f"Make sure Ollama is running. Start it with:\n" \
               f"```bash\nollama serve\n```"
    
    # Check if model exists
    model_names = [m.split(":")[0] for m in available_models]  # Remove version tags
    if model not in model_names:
        return f"❌ **Error: Model '{model}' not found**\n\n" \
               f"Available models: {', '.join(model_names) if model_names else 'None'}\n\n" \
               f"Install the model with:\n" \
               f"```bash\nollama pull {model}\n```"
    
    # Construct the prompt
    prompt = f"""Write a comprehensive blog post with the following details:
    
Title: {blog_title}
Keywords: {keywords}
Target word count: {num_words} words

Please write a well-structured blog post that:
1. Has an engaging introduction
2. Covers the topic thoroughly
3. Uses the provided keywords naturally
4. Has clear sections and paragraphs
5. Includes a conclusion

Blog post:"""

    # Ollama API endpoint
    url = f"{ollama_api_key}/api/generate"
    
    # Prepare the request payload
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        # Make the API request
        response = requests.post(url, json=payload, timeout=300)  # 5 minute timeout for long generations
        
        if response.status_code == 404:
            # Try to get more details from the error
            try:
                error_data = response.json()
                error_msg = error_data.get("error", "Model not found")
            except:
                error_msg = "404 Not Found - Model may not exist or endpoint is incorrect"
            
            return f"❌ **404 Error: {error_msg}**\n\n" \
                   f"Make sure:\n" \
                   f"1. The model '{model}' is installed: `ollama pull {model}`\n" \
                   f"2. Ollama is running: `ollama serve`\n" \
                   f"3. The endpoint is correct: {url}"
        
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        return result.get("response", "Error: No response from Ollama")
    
    except requests.exceptions.Timeout:
        return f"⏱️ **Timeout Error**\n\n" \
               f"The request took too long. Try reducing the word count or using a smaller model."
    
    except requests.exceptions.ConnectionError:
        return f"❌ **Connection Error**\n\n" \
               f"Cannot connect to Ollama at {ollama_api_key}\n\n" \
               f"Make sure Ollama is running:\n" \
               f"```bash\nollama serve\n```"
    
    except requests.exceptions.RequestException as e:
        return f"❌ **Error: {str(e)}**\n\n" \
               f"Check that Ollama is running on {ollama_api_key}"

with st.sidebar:
    st.title("Input Your Blog Details")
    st.subheader("Enter your blog topic")
    
    # Check Ollama connection status
    is_connected, available_models = check_ollama_connection()
    if is_connected:
        st.success(f"✅ Ollama Connected ({len(available_models)} models)")
    else:
        st.error("❌ Ollama Not Connected")
        st.info("Start Ollama with: `ollama serve`")

    blog_title = st.text_input("Blog Title")
    keywords = st.text_input("Keywords")
    
    numb_words = st.slider("Number of Words", min_value=250, max_value=1000, value=250)
    num_images = st.number_input("Number of Images", min_value=1, max_value=5, value=1)
    
    # Model selection for Ollama - use available models or default list
    if available_models:
        # Extract base model names (remove version tags like :latest, :7b, etc.)
        model_options = [m.split(":")[0] for m in available_models]
        model_options = list(dict.fromkeys(model_options))  # Remove duplicates while preserving order
        default_model = model_options[0] if model_options else "llama2"
    else:
        model_options = ["llama2", "llama3", "mistral", "codellama", "phi", "neural-chat"]
        default_model = "llama2"
    
    ollama_model = st.selectbox(
        "Ollama Model",
        options=model_options,
        index=0 if model_options else None,
        help="Select the Ollama model to use. Make sure the model is installed locally."
    )
    
    if available_models:
        st.caption(f"Available: {', '.join(model_options)}")

    submit_button = st.button("Generate Blog")

# Main content area
if submit_button:
    if not blog_title:
        st.warning("Please enter a blog title")
    else:
        with st.spinner("Generating your blog post with Ollama..."):
            blog_content = generate_blog_with_ollama(
                blog_title=blog_title,
                keywords=keywords or "",
                num_words=numb_words,
                model=ollama_model
            )
        
        # Check if the response is an error (starts with ❌ or ⏱️)
        if blog_content.startswith("❌") or blog_content.startswith("⏱️"):
            st.error(blog_content)
        else:
            st.subheader(f"Generated Blog: {blog_title}")
            st.write(blog_content)
            
            # Download button
            st.download_button(
                label="Download Blog",
                data=blog_content,
                file_name=f"{blog_title.replace(' ', '_')}_blog.txt",
                mime="text/plain"
            )
else:
    st.info("👈 Enter your blog details in the sidebar and click 'Generate Blog' to get started!")
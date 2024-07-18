import streamlit as st
import toggles_helper
import prompt_helper
import ppl_api

# Define story blocks
story_blocks = ["Introduction", "Main", "Conclusion"]

st.set_page_config(page_title="AI Article Generator", layout="wide")

# Main title
st.title("Openplexity Pages")

left_column, middle_column, right_column = st.columns([1, 1, 1])

with left_column:
    st.header("Generate New Article")

    # Global settings
    try:
        default_title = prompt_helper.get_global_prompt_element("story_title", "The Future of AI")
    except Exception as e:
        st.error(f"Error loading story title: {str(e)}")
        default_title = "The Future of AI"
    
    story_title = st.text_input("Story Title", default_title)
    prompt_helper.update_global_prompt_element("story_title", story_title)
    
    # Global toggles
    for toggle, label in [("style", "Tone Style"), ("target_audience", "Audience"), ("persona", "Role"), ("exemplars", "Example Tone")]:
        toggle_key = f"tgl_{toggle}"
        if st.checkbox(f"Toggle {label}", key=f"toggle_{toggle}", value=toggles_helper.get_global_toggle_state(toggle_key)):
            toggles_helper.update_global_toggle_state(toggle_key, True)
            if toggle == "style":
                tone_style = st.selectbox("Tone", ["Professional", "Friendly"])
                prompt_helper.update_global_prompt_element("tone_style", tone_style)
            elif toggle == "target_audience":
                audience = st.selectbox("Audience", ["Students", "Tech Enthusiasts", "General Public"])
                prompt_helper.update_global_prompt_element("audience", audience)
            elif toggle == "persona":
                role = st.selectbox("Role", ["Shakespeare", "Martin", "Tolkien"])
                prompt_helper.update_global_prompt_element("role", role)
            elif toggle == "exemplars":
                example_tone = st.text_area("Example Tone")
                prompt_helper.update_global_prompt_element("example_tone", example_tone)
        else:
            toggles_helper.update_global_toggle_state(toggle_key, False)
            if toggle == "style":
                prompt_helper.update_global_prompt_element("tone_style", "")
            elif toggle == "target_audience":
                prompt_helper.update_global_prompt_element("audience", "")
            elif toggle == "persona":
                prompt_helper.update_global_prompt_element("role", "")
            elif toggle == "exemplars":
                prompt_helper.update_global_prompt_element("example_tone", "")

    # Story blocks
    for block in story_blocks:
        with st.expander(f"{block} Block", expanded=True):
            title = st.text_input(f"{block} Block Title", prompt_helper.get_block_prompt_element(block, "title"), key=f"{block}_title_input")
            prompt_helper.update_block_prompt_element(block, "title", title)
            
            word_count = st.slider("Word Count", 100, 1000, prompt_helper.get_block_prompt_element(block, "word_count", 300), key=f"{block}_word_count_slider")
            prompt_helper.update_block_prompt_element(block, "word_count", word_count)
            
            keywords = st.text_input("Keywords", prompt_helper.get_block_prompt_element(block, "keywords"), key=f"{block}_keywords_input")
            prompt_helper.update_block_prompt_element(block, "keywords", keywords)
            
            if st.checkbox("Toggle Keywords", key=f"{block}_tgl_keywords", value=toggles_helper.get_block_toggle_state(block, "tgl_keywords")):
                toggles_helper.update_block_toggle_state(block, "tgl_keywords", True)
            else:
                toggles_helper.update_block_toggle_state(block, "tgl_keywords", False)
                prompt_helper.update_block_prompt_element(block, "keywords", "")

    # Generate button
    if st.button("Generate Article"):
        st.success("Article generation requested!")
        for block in story_blocks:
            with st.spinner(f"Generating {block}..."):
                prompt = prompt_helper.get_formatted_prompt(block)
                st.write(f"Debug: Prompt for {block}: {prompt}")  # Debug information
                response = ppl_api.ppl_query_api(prompt)
            st.session_state[f"{block}_response"] = response
            st.success(f"{block} generated successfully!")

with middle_column:
    st.header("Debug column")

    for block in story_blocks:
        st.subheader(f"{block} Prompt")
        prompt = prompt_helper.get_formatted_prompt(block)
        st.text_area(f"{block} Prompt", prompt, height=300, key=f"{block}_prompt_display", disabled=True)
        
        if st.button(f"Run {block} Prompt"):
            with st.spinner(f"Generating {block}..."):
                response = ppl_api.ppl_query_api(prompt)
            st.session_state[f"{block}_response"] = response
            st.success(f"{block} generated successfully!")

with right_column:
    st.header("Formatted Article")

    formatted_article = ""

    for block in story_blocks:
        if f"{block}_response" in st.session_state:
            formatted_article += f"## {prompt_helper.get_block_prompt_element(block, 'title')}\n\n"
            formatted_article += f"![Alt text](https://placehold.co/600x400)  \n"
            formatted_article += st.session_state[f"{block}_response"] + "\n\n"

    st.markdown(formatted_article)
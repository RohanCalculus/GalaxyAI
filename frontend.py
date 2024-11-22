import streamlit as st
import requests
from PIL import Image
import time  
import io
import os
from main import RGB_DIR, GALAXY_DIR, L_CHANNEL_DIR

# API endpoints
GENERATE_API = "http://localhost:8000/generate/"  # Endpoint for generating galaxy images
COLORIZE_API = "http://localhost:8000/colorize/"  # Endpoint for colorizing images

# Set up the Streamlit page layout
st.set_page_config(page_title="Galactic AI", layout="wide", page_icon="🌌")

# Add custom CSS for the background image
background_url = "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/5eae36e3-278f-4731-be00-1440d36eca76/d30idy4-9a4a96ed-33be-4941-99c1-8b77adb23288.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwic3ViIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsImF1ZCI6WyJ1cm46c2VydmljZTpmaWxlLmRvd25sb2FkIl0sIm9iaiI6W1t7InBhdGgiOiIvZi81ZWFlMzZlMy0yNzhmLTQ3MzEtYmUwMC0xNDQwZDM2ZWNhNzYvZDMwaWR5NC05YTRhOTZlZC0zM2JlLTQ5NDEtOTljMS04Yjc3YWRiMjMyODguanBnIn1dXX0.urB7x7zyDCCRhro0z1HDVMWXZ9HJi9NgdXurlCon43Q"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{background_url}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        min-height: 100vh;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Then define the styles for each header in CSS
st.markdown(
    """
    <style>
    .header1 {
        color: #add8e6;
        text-align: left;
        font-family: 'Trebuchet MS', sans-serif;
        letter-spacing: 4px;
        text-transform: uppercase;
        background: linear-gradient(to right, #8a2be2, #9370db, #dda0dd);
        -webkit-background-clip: text;
        color: transparent;
        padding: 10px 0;
        font-size: 38px;
    }

    .header2 {
        text-align: left;
        font-family: 'Trebuchet MS', sans-serif;
        letter-spacing: 4px;
        text-transform: uppercase;
        background: linear-gradient(to right, #ffdf00, #ffffff, #9370db);
        -webkit-background-clip: text;
        color: transparent;
        padding: 10px 0;
        font-size: 38px;
    }
    </style>
    """, 
    unsafe_allow_html=True
)


# Sidebar setup
st.sidebar.image("media/logo1.png", use_column_width=True)  # Display logo image in the sidebar

st.sidebar.markdown(
    """
    <div style="
        background-color: #1e1e2f; 
        border-radius: 10px; 
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);">
        <h2 style="
            text-align: center; 
            color: #f4c430; 
            font-family: 'Trebuchet MS', sans-serif; 
            letter-spacing: 2px;">
            🌌 Galactic AI 🌌
        </h2>
    </div>
    """, 
    unsafe_allow_html=True
)

st.sidebar.markdown(
    """
    <br><br>
    <p style="text-align: center; font-size: 20px;">
        Made with <span style="color: red;">&hearts;</span> by 
        <a href="https://github.com/RohanCalculus/GalaxyAI" target="_blank" style="text-decoration: none; color: black;"><u>Rohan</u></a>
    </p>
    """, 
    unsafe_allow_html=True
)

# Adding vertical space between sections
st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.markdown(
    """
    <h3 style="
        color: #f4c430; 
        text-align: center; 
        font-family: 'Trebuchet MS', sans-serif; 
        letter-spacing: 1px; 
        text-transform: uppercase; 
        background: linear-gradient(to right, #ff7e5f, #feb47b);
        -webkit-background-clip: text;
        color: transparent;">
        🚀 Cosmic Navigation
    </h3>
    """, 
    unsafe_allow_html=True
)



# Initialize page variable in session state
if 'page' not in st.session_state:
    st.session_state.page = "Galaxy Generator"  # Default page when first loaded

# Initialize the upload counter in session state
if 'upload_counter' not in st.session_state:
    st.session_state.upload_counter = 0  # Counter to track uploads

# Navigation buttons in the sidebar
# Sidebar Update: Add "About the App" button
if st.sidebar.button("💫 Galaxy Generator"):
    st.session_state.page = "Galaxy Generator"  # Change page to generate image
    st.rerun() 
if st.sidebar.button("🎨 Galaxy Colorizer"):
    # Reset counter when navigating to colorization page
    st.session_state.page = "Galaxy Colorizer"
    st.session_state.upload_counter = 0  # Reset the upload counter
if st.sidebar.button("🌌 About the App"):
    st.session_state.page = "About the App"  # Switch to About the App page


# Page 1: Generate and Color the Random Galaxy Images
if st.session_state.page == "Galaxy Generator":
    st.markdown(
    """
    <h1 class="header1">
        Refresh to Generate a New Galaxy Image
    </h1>
    """, 
    unsafe_allow_html=True
    )

    st.text(" ")

    # Function to load the latest galaxy image from the directory
    def load_latest_galaxy_image():
        latest_image_path = sorted(os.listdir(GALAXY_DIR))[-1]  # Get the most recent file
        return Image.open(os.path.join(GALAXY_DIR, latest_image_path))  # Open the image file

    # Create columns for layout
    col1, col2 = st.columns(2)  # Create two columns for displaying images

    # Trigger image generation on first load
    if 'galaxy_image' not in st.session_state:
        with st.spinner("Generating your galaxy image..."):  # Show spinner while generating
            response = requests.post(GENERATE_API)  # POST request to generate galaxy image
            if response.status_code == 200:  # Check if the request was successful
                st.session_state.galaxy_image = load_latest_galaxy_image()  # Load the generated image
                st.session_state.image_displayed = True  # Track if an image has been displayed

    # Display the generated image if it exists
    if st.session_state.get('image_displayed', False):
        with col1:
            st.image(st.session_state.galaxy_image, caption="AI Generated Galaxy Image", use_column_width=True)  # Display generated image

            # Button to colorize the currently displayed image
            if st.button("Colorize it"):
                img_byte_arr = io.BytesIO()  # Create a byte stream for the image
                st.session_state.galaxy_image.save(img_byte_arr, format='PNG')  # Save the image to the byte stream
                img_byte_arr.seek(0)  # Seek to the beginning of the stream
                files = {'file': img_byte_arr.getvalue()}  # Prepare file for POST request
                
                with col2:
                    with st.spinner("AI is colorizing the generated Galaxy..."):  # Show spinner while colorizing
                        colorize_response = requests.post(COLORIZE_API, files=files)  # POST request to colorize the image

                        if colorize_response.status_code == 200:  # Check if colorization was successful
                            # Load and display the latest RGB image
                            rgb_image_path = sorted(os.listdir(RGB_DIR))[-1]  # Get the most recent colorized image
                            colorized_image = Image.open(os.path.join(RGB_DIR, rgb_image_path))  # Open the image file
                            
                            # Display colorized image in the second column
                            st.image(colorized_image, caption="AI Colorized Image", use_column_width=True)
    else:
        st.info("Generating your galaxy image...")  # Inform user that the galaxy image is being generated



# Page 2: Colorize an Image of Galaxy (Galaxy Zoo Format)
if st.session_state.page == "Galaxy Colorizer":
    st.markdown( 
    """
    <h1 class="header2">
        Let AI Paint the Galaxy!
    </h1>
    """, 
    unsafe_allow_html=True
    )


    st.text(" ")


    # Reset the upload counter when the file uploader is activated
    uploaded_file = st.file_uploader(
        "Upload an image", type=["png", "jpg", "jpeg"],
        on_change=lambda: setattr(st.session_state, 'upload_counter', 0)  # Reset counter on upload
    )


    if uploaded_file is not None:  # Check if a file has been uploaded
        # Prepare to colorize the uploaded image
        img_byte_arr = io.BytesIO()  # Create a byte stream
        uploaded_image = Image.open(uploaded_file)  # Open the uploaded image file
        uploaded_image.save(img_byte_arr, format='PNG')  # Save it to the byte stream
        img_byte_arr.seek(0)  # Seek to the beginning of the stream
        files = {'file': img_byte_arr.getvalue()}  # Prepare file for POST request

        # Increment upload counter
        st.session_state.upload_counter += 1

        # Create two columns for the spinners and images
        col1, col2 = st.columns(2)

        # Show a global spinner for uploading/colorizing process
        with st.spinner("Uploading the B/W Galaxy Image..."):
            colorize_response = requests.post(COLORIZE_API, files=files)  # POST request to colorize the image

        if colorize_response.status_code == 200:  # Check if colorization was successful
            # Get the most recent L channel image
            l_channel_image_path = sorted(os.listdir(L_CHANNEL_DIR))[-1]  # Get the most recent L channel image
            l_channel_image = Image.open(os.path.join(L_CHANNEL_DIR, l_channel_image_path))  # Open the image file

            # Display the L channel image in the first column
            with col1:
                st.image(l_channel_image, caption="Black and White Image", use_column_width=True)  # Display L channel image
            

            # Show the spinner in the second column while waiting for the colorized image
            with col2:
                with st.spinner("AI is colorizing the Galaxy..."):  # Show spinner in the second column
                    # Simulate a delay for the colorized image (2 seconds)
                    time.sleep(2)  # Delay before displaying the colorized image
                    # Get the most recent RGB image (to display later)
                    rgb_image_path = sorted(os.listdir(RGB_DIR))[-1]  # Get the most recent colorized image
                    rgb_image = Image.open(os.path.join(RGB_DIR, rgb_image_path))  # Open the image file

                    # Display the colorized image after the delay
                    st.image(rgb_image, caption="AI Generated Colorized Image", use_column_width=True)  # Display colorized image

# Page 3: About the App
if st.session_state.page == "About the App":
    # Custom Styling for the About Page
    st.markdown(
    """
    <style>
    
    .about-description {
        color: black;
        font-size: 20px;
        font-family: 'Arial', sans-serif;
        line-height: 1.6;
        text-align: left;
        text-shadow: none;  /* Removed the shadow */
        margin-bottom: 0px;
    }

    .about-section {
        text-align: left;
        padding: 10px;
        border-radius: 20px;
        color: white;
        box-shadow: 0 0 50px rgba(0, 0, 0, 0.7);
        margin: 20px auto;
        max-width: 800px;
    }

    .about-section1 {
        background-color: rgba(250, 200, 0, 0.7);  /* Purple */
    }

    .about-section2 {
        background-color: rgba(255, 126, 95, 0.7);  /* Coral */
    }

    .about-section3 {
        background-color: rgba(60, 179, 113, 0.7);  /* Medium Sea Green */
    }

    .about-header {
    text-align: center;
    font-family: 'Trebuchet MS', sans-serif;
    font-size: 38px;
    letter-spacing: 4px;
    text-transform: uppercase;
    padding: 30px 0px 0px 0px;
    text-shadow: none;  /* Removed the shadow */
    background: linear-gradient(to left, #00b4db, #0083b0); /* Ocean Blue to Sky Blue */
    -webkit-background-clip: text;
    color: transparent;  /* Ensure text is transparent so gradient shows */
    }

    </style>
    """, 
    unsafe_allow_html=True
    )

    # Title and Introduction inside a container
    st.markdown(
    """
    <h1 class="about-header">Welcome to Galactic AI</h1>
    """, 
    unsafe_allow_html=True
    )
    with st.container():
        st.markdown(
        """
        <div class="about-section about-section1">
            <p class="about-description">
                Explore the universe like never before with our <b>AI-powered</b> galaxy generator and colorizer. 
                This app allows you to <b>create stunning galaxy images</b> and bring them to life with <b>vibrant colors</b>, 
                all powered by cutting-edge <b>Generative Adverserial Networks</b>. Whether you're a space enthusiast or just looking 
                for some cosmic fun, this app is a must try for you! By the way, generated images will get stored in your local system.
            </p>
        </div>
        """, 
        unsafe_allow_html=True
        )

    # How to use section inside a container
    st.markdown(
    """
    <h1 class="about-header">How to Use Galactic AI</h1>
    """, 
    unsafe_allow_html=True
    )
    with st.container():
        st.markdown(
        """
        <div class="about-section about-section2">
            <p class="about-description">
                <b>Galaxy Generator</b>: Generate random, breathtaking galaxy images created by AI.
                <br>
                <b>Galaxy Colorizer</b>: Upload B/W Galaxy Image, let AI colorize it.
            </p>
        </div>
        """, 
        unsafe_allow_html=True
        )

    # How to use section inside a container
    st.markdown(
    """
    <h1 class="about-header">Tools used in the Project</h1>
    """, 
    unsafe_allow_html=True
    )
    with st.container():
        st.markdown(
        """
        <div class="about-section about-section3">
            <p class="about-description">
                <b>Tensorflow & Keras</b>: Training of Galaxy Generator using Wasserstein GAN.
                <br>
                <b>Pytorch</b>: Training of Galaxy Colorizer using Pix2Pix GAN.
                <br>
                <b>FastAPI</b>: Backend of the App.
                <br>
                <b>Streamlit</b>: Frontent of the App.
            </p>
        </div>
        """, 
        unsafe_allow_html=True
        )
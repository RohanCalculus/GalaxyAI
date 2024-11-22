# Welcome to the Galaxy Image Colorizer!

This project mainly does two things with the help of AI:-
1. Generates an image of the galaxy 
2. Can color an image of the galaxy 

## Follow the steps to setup
1. Create your virtual environment `python -m venv <venv_name>`
2. Activate the virtual environment `.\<venv_name>\Scripts\activate`
3. Install the requirements `python -m pip install -r requirements.txt`
4. Now, run the API `uvicorn main:app --reload`
5. Then run the streamlit app `streamlit run frontend.py`

You are all set now to use the app!

## How to use the app
1. Refresh the first page of the app to keep generating images of galaxies (as we saw during our training)
2. There is a button to `colorize` this generated image based on our pretrained `pix2pix Generator`
3. Now, you can explore the second page where you can manually upload the images from galaxy zoo test set
4. The images will be converted to L channel and get you the RGB output both displayed on the app

## Database
1. `Generated_Galaxy_Images` will store the image generated by AI of the galaxy whenever we refresh the app
2. `L_channel_Images` will store the black-white images of the galaxy uploaded in page 2
3. `RGB_Generated_Images` will store the RGB output generated by the app

## Namings of the images in the database
- To give unique names, we have used current date time to store it in the respective directory!

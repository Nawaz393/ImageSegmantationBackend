# ImageSegmantationBackend

## Description

This project is a backend implementation for image segmentation Model using Flask. It provides an API endpoint to perform image segmentation on user-provided images.


## Model Download Link
you can download the model from the below link
[Model Download Link](https://drive.google.com/file/d/1HTo4d28g0rzQwXVv-ecK2_87mdi4zPVw/view?usp=sharing)


## Note 
This Repository contains the code for the backend of the image segmentation model.
To run the complete application You will have to clone the frontend repository and backend app Repository from the below link

[Frontend Repository](  hthht)

[Backend Repository](jjfjf)

*Please download the model and change the path in the  `helpers.py` load model method.*



## Installation

1. Clone the repository: `git clone https://github.com/Nawaz393/ImageSegmantationBackend.git`
2. Navigate to the project directory: `cd ImageSegmantationBackend`
3. Install the required dependencies: `pip install -r requirements.txt`


## Usage

1. Start the Flask server: `python app.py`
2. Now the Api  End point will be Open on `http://localhost:5000`
3. Upload an image file to perform image segmentation
4. Now upload image name provided by image upload api along with other details
4. Wait for the segmentation process to complete
5. Download the segmented image

## Technical Details

The project directory structure contains the following components:

- `ImagePipline`: This directory contains the preprocessing for 2d images and 3d Images Reconstruction and Predicting scripts for image segmentation.

- `app.py`: This is the main Flask application file that handles the API endpoints and image   segmentation process.

- `requirements.txt`: This file lists all the required dependencies for the project.

## Project Workflow

1. The user uploads an image file to the API endpoint.

2. The Flask server receives the image and passes and Save it on disk and returns the Image path.

3. The image path is then passed to image segmanatation api on receiving  it passes path to segmentation pipeline.

3. The image is preprocessed using the scripts in the `preprocessing` directory.

4. The preprocessed image is then passed through the machine learning model in the `predic` file  for segmentation.

5. The segmented image is Reconstructed by `Reconstruction` script.

6. The segmented image is saved on disk.

7. The data is inserted to the mongo db database.

8. The user can download the segmented image from the API endpoint






## Contributing

Contributions are welcome! If you would like to contribute to this project, please follow these steps:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes and commit them: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Submit a pull request

## License

This project is licensed under the [MIT License](https://github.com/git/git-scm.com/blob/main/MIT-LICENSE.txt).

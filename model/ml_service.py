import json
import os
import time
from PIL import Image

import numpy as np
import redis
from model import settings
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import decode_predictions, preprocess_input
from tensorflow.keras.preprocessing import image

# TODO
# Connect to Redis and assign to variable `db``
# Make use of settings.py module to get Redis settings like host, port, etc.
try:
    # Prioritize environment variable REDIS_IP if available
    db = redis.StrictRedis(host=settings.REDIS_IP, port=settings.REDIS_PORT, db=settings.REDIS_DB_ID)
    
except redis.exceptions.ConnectionError as e:
    print(f"Error connecting to Redis: {e}")

# TODO
# Load your ML model and assign to variable `model`
# See https://drive.google.com/file/d/1ADuBSE4z2ZVIdn66YDSwxKv-58U7WEOn/view?usp=sharing
# for more information about how to use this model.
model = ResNet50(include_top=True, weights="imagenet")
model.summary()

def predict(image_name):
    """
    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.

    Parameters
    ----------
    image_name : str
        Image filename.

    Returns
    -------
    class_name, pred_probability : tuple(str, float)
        Model predicted class as a string and the corresponding confidence
        score as a number.
    """
    # Cargar la imagen y preprocesarla
    image_path = os.path.join(settings.UPLOAD_FOLDER, image_name)
    img = image.load_img(image_path, target_size=(224, 224))

    img_array = np.expand_dims(np.array(img), axis=0)
    img_array = preprocess_input(img_array)

    # Realizar la predicción
    predictions = model.predict(img_array, batch_size=256)
    decoded_predictions = decode_predictions(predictions, top=1)[0]  # Obtener las predicciones más probables

    # Obtener la clase predicha y la probabilidad asociada
    class_id, class_name, pred_probability = decoded_predictions[0]
    
    pred_probability = round(pred_probability, 4)

    return class_name, pred_probability

def classify_process():
    """
    Loop indefinitely asking Redis for new jobs.
    When a new job arrives, takes it from the Redis queue, uses the loaded ML
    model to get predictions and stores the results back in Redis using
    the original job ID so other services can see it was processed and access
    the results.

    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.
    """
    while True:
        # Inside this loop you should add the code to:
        #   1. Take a new job from Redis
        #   2. Run your ML model on the given data
        #   3. Store model prediction in a dict with the following shape:
        #      {
        #         "prediction": str,
        #         "score": float,
        #      }
        #   4. Store the results on Redis using the original job ID as the key
        #      so the API can match the results it gets to the original job
        #      sent
        # Hint: You should be able to successfully implement the communication
        #       code with Redis making use of functions `brpop()` and `set()`.
        # TODO

        while True:
            # Take a new job from Redis
            job_data_str = db.brpop(settings.REDIS_QUEUE)
            job_data_dict = json.loads(job_data_str[1].decode("utf-8"))
            job_id = job_data_dict["id"]
            image_name = job_data_dict["image_name"]

            # Run the ML model on the given data
            class_name, pred_probability = predict(image_name)

            # Store model prediction in a dict
            prediction_result = {
                "prediction": class_name,
                "score": float(pred_probability)
            }

            # Store the results on Redis using the original job ID as the key
            prediction_result_json = json.dumps(prediction_result)

            # Store the results on Redis using the original job ID as the key
            db.set(job_id, prediction_result_json)

            # Sleep for a bit
            time.sleep(settings.SERVER_SLEEP)


if __name__ == "__main__":
    # Now launch process
    print("Launching ML service...")
    classify_process()

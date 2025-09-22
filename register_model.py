import mlflow
from app.definitions import (
    EXPERIMENT_NAME,
    REGISTERED_MODEL_NAME,
    MODEL_ALIAS,
    REMOTE_SERVER_URI
)
from app.sql_model import SQLGenerator  # Import the model class

from dotenv import load_dotenv

load_dotenv()

# Connect to MLflow
mlflow.set_tracking_uri(REMOTE_SERVER_URI)
mlflow.set_experiment(EXPERIMENT_NAME)

with mlflow.start_run():
    # Log the model by referencing the class directly
    # Provide an input_example to help MLflow infer the signature
    input_example = {"conn": None, "cursor": None, "vector_store": None}
    logged_model_info = mlflow.pyfunc.log_model(
        name="sql_generator",
        python_model=SQLGenerator(),
        input_example=input_example,
    )

# Register the logged model artifact under the registered model name
# This returns a ModelVersion object with a version we can use
registered_mv = mlflow.register_model(logged_model_info.model_uri, REGISTERED_MODEL_NAME)

# Create client and set alias using the returned version
client = mlflow.tracking.MlflowClient(tracking_uri=REMOTE_SERVER_URI)
client.set_registered_model_alias(
    REGISTERED_MODEL_NAME,
    MODEL_ALIAS,
    registered_mv.version
)

print("Model registered successfully!")
print(f"Model Name: {REGISTERED_MODEL_NAME}, Alias: {MODEL_ALIAS}")
# --- IGNORE ---
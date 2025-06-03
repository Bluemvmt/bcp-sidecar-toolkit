import mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri(uri="http://127.0.0.1:5000")

client = MlflowClient()
registered_models = client.search_registered_models()  # Correct method

# Print registered models
for model in registered_models:
    print()
    print(f"Model Name: {model.name}, Versions: {model.latest_versions}")
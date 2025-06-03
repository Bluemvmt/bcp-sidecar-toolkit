import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification

mlflow.set_tracking_uri(uri="http://127.0.0.1:5000")

# Generate sample data
X, y = make_classification(n_samples=1000, n_features=4, random_state=42)

# Start an MLflow run
with mlflow.start_run(run_name="RandomForest_Experiment"):
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    # Log parameters and metrics
    mlflow.log_param("n_estimators", 100)
    mlflow.log_metric("accuracy", model.score(X, y))

    # Log the model
    mlflow.sklearn.log_model(model, "model")

    # Get run ID
    run_id = mlflow.active_run().info.run_id

# Register the model
model_uri = f"runs:/{run_id}/model"
mlflow.register_model(model_uri, "RandomForestModeltest3")
# MLflow Model Registry - List Registered Models

This script demonstrates how to connect to an MLflow tracking server and retrieve information about registered models.

## Overview

The script connects to a local MLflow tracking server and lists all registered models along with their latest versions.

## Prerequisites

- MLflow installed (`pip install mlflow`)
- MLflow tracking server running on `http://127.0.0.1:5000`

## Setup

### 1. Install MLflow
```bash
pip install mlflow
```

### 2. Start MLflow Tracking Server
```bash
mlflow server --host 127.0.0.1 --port 5000
```

## Code Explanation

```python
import mlflow
from mlflow.tracking import MlflowClient

# Set the tracking URI to connect to the MLflow server
mlflow.set_tracking_uri(uri="http://127.0.0.1:5000")

# Create a client to interact with the MLflow tracking server
client = MlflowClient()

# Search for all registered models
registered_models = client.search_registered_models()

# Print registered models information
for model in registered_models:
    print()
    print(f"Model Name: {model.name}, Versions: {model.latest_versions}")
```

## What the Script Does

1. **Connects to MLflow Server**: Establishes connection to the local MLflow tracking server
2. **Creates MLflow Client**: Initializes the client for API interactions
3. **Searches Registered Models**: Retrieves all models registered in the model registry
4. **Displays Model Information**: Prints model names and their latest versions

## Expected Output

```
Model Name: my_model, Versions: [<ModelVersion: ...>]

Model Name: another_model, Versions: [<ModelVersion: ...>]
```

## Usage

1. Ensure MLflow server is running
2. Run the script:
   ```bash
   python list_models.py
   ```

## Configuration Options

### Different Tracking URI
```python
# For remote server
mlflow.set_tracking_uri("http://your-server:5000")

# For database backend
mlflow.set_tracking_uri("sqlite:///mlflow.db")

# For file-based storage
mlflow.set_tracking_uri("file:///path/to/mlruns")
```

### Additional Model Information
```python
# Get more detailed model information
for model in registered_models:
    print(f"Model: {model.name}")
    print(f"Description: {model.description}")
    print(f"Tags: {model.tags}")
    print(f"Latest Versions: {model.latest_versions}")
    print("-" * 50)
```

## Troubleshooting

### Common Issues

1. **Connection Error**: Ensure MLflow server is running on the specified URI
2. **No Models Found**: Check if models are registered in the model registry
3. **Permission Issues**: Verify access rights to the MLflow server

### Error Handling
```python
try:
    registered_models = client.search_registered_models()
    if not registered_models:
        print("No registered models found.")
except Exception as e:
    print(f"Error connecting to MLflow: {e}")
```

## Related Commands

- `mlflow models serve`: Serve a registered model
- `mlflow models list`: List models via CLI
- `mlflow ui`: Launch MLflow UI

## Documentation

- [MLflow Model Registry](https://mlflow.org/docs/latest/model-registry.html)
- [MLflow Python API](https://mlflow.org/docs/latest/python_api/index.html)
- [MLflow Tracking](https://mlflow.org/docs/latest/tracking.html)
import mlflow
from workflow import get_workflow
from typing import Any, List, Dict

class SQLGenerator(mlflow.pyfunc.PythonModel):
    def predict(self, context: Any, model_input: List[Dict[str, Any]]) -> Any:
        """
        context: MLflow runtime context
        model_input: list of dictionaries containing {conn, cursor, vector_store}
        Returns a single compiled LangGraph workflow.
        """
        input_instance = model_input[0]  # Take the first dict
        return get_workflow(
            input_instance["conn"],
            input_instance["cursor"],
            input_instance["vector_store"]
        )


#mlflow.models.set_model(SQLGenerator())
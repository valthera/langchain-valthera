from typing import Optional, Type, Dict, Any, List
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

# Import Valthera models and agents (assumes these modules are in your environment)
from valthera.models import UserContext
from valthera.agents.behavioral.fogg_model.trigger_decision_agent.agent import TriggerDecisionAgent  # Adjust as needed


class BehaviorModel(BaseModel):
    behavior_id: str = Field(..., description="Unique identifier for the behavior")
    name: str = Field(..., description="Name of the behavior")
    description: str = Field(..., description="Detailed description of the behavior")


class ConnectorData(BaseModel):
    """
    ConnectorData encapsulates connector-specific data.
    Customize this model by adding additional fields as required.
    """
    data: Dict[str, Any] = Field(default_factory=dict, description="Connector-specific data")


class ValtheraToolInput(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the user")
    connector_data: ConnectorData = Field(..., description="Structured connector data")
    behavior: BehaviorModel = Field(..., description="Behavior details including id, name, and description")


class ValtheraTool(BaseTool):
    """
    ValtheraTool

    This tool leverages the Valthera Fogg model-based decision engine to determine
    if a trigger should be sent to a user for a specific behavior. It takes user context
    and behavior details as input, scores the user's state, and returns a trigger recommendation.
    """
    name: str = "ValtheraTool"
    description: str = (
        "Determines if a trigger should be sent based on the Fogg model using Valthera's "
        "scoring and reasoning engine."
    )
    args_schema: Type[BaseModel] = ValtheraToolInput

    def _run(
        self,
        user_id: str,
        connector_data: ConnectorData,
        behavior: BehaviorModel,
        *,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        # Convert behavior data using pydantic model
        behavior_data = behavior.dict() if hasattr(behavior, "dict") else behavior

        # Set behavior_weights as needed for your use case.
        behavior_weights: List[Dict[str, Any]] = []  # Customize these weights if needed.
        
        # Instantiate the trigger decision agent.
        agent = TriggerDecisionAgent(behavior_weights=behavior_weights)
        
        # Convert the input to the respective data objects.
        user_context_obj = UserContext(
            user_id=user_id,
            connector_data=connector_data.dict()  # Convert ConnectorData to a dict
        )
        behavior_obj = BehaviorModel(**behavior_data)
        
        # Run the agent to get a trigger recommendation.
        recommendation = agent.run(user_context_obj, behavior_obj)
        
        if recommendation is None:
            result = "No trigger recommendation."
        else:
            # If the recommendation is a dict, use dictionary access.
            if isinstance(recommendation, dict):
                trigger_message = recommendation.get("trigger_message", "No trigger message")
                confidence = recommendation.get("confidence")
                channel = recommendation.get("channel")
                rationale = recommendation.get("rationale")
            else:
                trigger_message = recommendation.trigger_message
                confidence = recommendation.confidence
                channel = recommendation.channel
                rationale = recommendation.rationale
            
            result = f"Trigger: {trigger_message}"
            if confidence is not None:
                result += f", Confidence: {confidence}"
            if channel:
                result += f", Channel: {channel}"
            if rationale:
                result += f", Rationale: {rationale}"
        return result

    async def _arun(
        self,
        input_data: dict,
        *,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        # Parse the input data using the defined args_schema
        parsed_input = self.args_schema.parse_obj(input_data)
        return self._run(
            user_id=parsed_input.user_id,
            connector_data=parsed_input.connector_data,
            behavior=parsed_input.behavior,
            run_manager=run_manager
        )

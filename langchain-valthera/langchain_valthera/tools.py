from typing import Optional, Type, Dict, Any, List
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

# Import Valthera models and agents (assumes these modules are in your environment)
from valthera.models import UserContext, Behavior
from valthera.agents.behavioral.fogg_model.trigger_decision_agent.agent import TriggerDecisionAgent  # Adjust as needed

# Define Pydantic models for the tool's input data.
class UserContextModel(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the user")
    connector_data: Dict[str, Dict] = Field(default_factory=dict, description="Connector data from various sources")
    engagement_score: float = Field(0.0, description="Engagement score of the user")
    funnel_stage: Optional[str] = Field(None, description="Current funnel stage of the user")
    usage_frequency: float = Field(0.0, description="Usage frequency of the user")

class BehaviorModel(BaseModel):
    behavior_id: str = Field(..., description="Unique identifier for the behavior")
    name: str = Field(..., description="Name of the behavior")
    description: str = Field(..., description="Detailed description of the behavior")

class ValtheraToolInput(BaseModel):
    user_context: UserContextModel = Field(..., description="Aggregated user context data")
    behavior: BehaviorModel = Field(..., description="Details of the target behavior")

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
        user_context: dict,
        behavior: dict,
        *,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        # Convert Pydantic models to dictionaries if necessary.
        if hasattr(user_context, "dict"):
            user_context_data = user_context.dict()
        else:
            user_context_data = user_context

        if hasattr(behavior, "dict"):
            behavior_data = behavior.dict()
        else:
            behavior_data = behavior

        # Set behavior_weights as needed for your use case.
        behavior_weights: List[Dict[str, Any]] = []  # Customize these weights if needed.
        
        # Instantiate the trigger decision agent.
        agent = TriggerDecisionAgent(behavior_weights=behavior_weights)
        
        # Convert the input dictionaries to the respective data objects.
        user_context_obj = UserContext(**user_context_data)
        behavior_obj = Behavior(**behavior_data)
        
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
        user_context: dict,
        behavior: dict,
        *,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        return self._run(user_context, behavior, run_manager=run_manager)

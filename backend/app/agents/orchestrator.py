"""
Agent Orchestrator

Coordinates multiple AI agents and manages agent execution.
"""

import logging
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.triage_agent import TriageAgent
from app.agents.scheduling_agent import SchedulingAgent
from app.agents.scribe_agent import ScribeAgent
from app.agents.followup_agent import FollowUpAgent
from app.agents.billing_agent import BillingAgent
from app.models.agent_run import AgentRun, AgentStatus
from app.core.config import settings

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orchestrates AI agent execution.

    Routes requests to appropriate agents and tracks execution.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the orchestrator.

        Args:
            db: Database session
        """
        self.db = db
        self.agents = {
            "triage": TriageAgent(db),
            "scheduling": SchedulingAgent(db),
            "scribe": ScribeAgent(db),
            "follow_up": FollowUpAgent(db),
            "billing": BillingAgent(db),
            "general": TriageAgent(db),  # Default to triage
        }

    async def process_message(
        self,
        conversation_id: UUID,
        message: str,
        agent_type: str = "general",
        user_id: Optional[UUID] = None,
    ) -> dict[str, Any]:
        """
        Process a message through the appropriate agent.

        Args:
            conversation_id: Conversation ID
            message: User message
            agent_type: Type of agent to use
            user_id: User ID for tracking

        Returns:
            Agent response dict with content and metadata
        """
        agent = self.agents.get(agent_type, self.agents["general"])

        # Track agent run
        run = AgentRun(
            agent_type=agent_type,
            status=AgentStatus.STARTED,
            input_data={"message": message, "conversation_id": str(conversation_id)},
            user_id=user_id,
        )
        self.db.add(run)
        await self.db.flush()

        try:
            # Process the message
            response = await agent.process(
                message=message,
                conversation_id=conversation_id,
            )

            # Update run status
            run.status = AgentStatus.COMPLETED
            run.output_data = response

            # Check for escalation
            if response.get("escalated"):
                run.status = AgentStatus.FAILED
                run.error_message = "Escalated to human"

            await self.db.commit()

            return response

        except Exception as e:
            logger.error(f"Agent execution failed: {e}", exc_info=True)
            run.status = AgentStatus.FAILED
            run.error_message = str(e)
            await self.db.commit()

            # Return error response
            return {
                "content": "I apologize, but I encountered an error processing your request.",
                "metadata": {"error": True, "escalated": True},
                "escalated": True,
            }

    async def route_agent(self, message: str, context: dict) -> str:
        """
        Determine which agent should handle a request.

        Args:
            message: User message
            context: Conversation context

        Returns:
            Agent type to use
        """
        message_lower = message.lower()

        # Check for scheduling keywords
        if any(word in message_lower for word in ["appointment", "schedule", "book", "available", "when"]):
            return "scheduling"

        # Check for medical/symptom keywords
        if any(word in message_lower for word in ["pain", "hurt", "symptom", "feel", "sick", "worry"]):
            return "triage"

        # Check for billing keywords
        if any(word in message_lower for word in ["bill", "cost", "insurance", "pay", "charge"]):
            return "billing"

        # Default to general
        return "general"

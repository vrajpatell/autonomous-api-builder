from app.services.agents.base import Agent
from app.services.agents.coder_agent import CoderAgent
from app.services.agents.deployer_agent import DeployerAgent
from app.services.agents.planner_agent import PlannerAgent
from app.services.agents.reviewer_agent import ReviewerAgent
from app.services.agents.tester_agent import TesterAgent


def build_default_agents() -> list[Agent]:
    return [PlannerAgent(), CoderAgent(), TesterAgent(), ReviewerAgent(), DeployerAgent()]

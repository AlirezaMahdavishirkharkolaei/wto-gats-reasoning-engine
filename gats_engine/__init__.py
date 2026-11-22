"""WTO–GATS Reasoning Engine: structured, explainable analysis of measures affecting trade in services."""

from .engine import Assessment, StepResult, assess
from .questions import QUESTIONS, template

__all__ = ["assess", "Assessment", "StepResult", "QUESTIONS", "template"]
__version__ = "2.1.0"

"""Random Task Tool Matcher Implementation."""

import hashlib
import random

from casa_auth_server.pipelines.task_tool_matcher.task_tool_matcher import (
    TaskToolMatcher,
    TaskToolMatchInput,
    TaskToolMatchOutput,
)
from casa_auth_server.pipelines.task_tool_matcher.types import TaskToolMatchReason


class RandomTaskToolMatcher(TaskToolMatcher):
    """A random task-tool matcher that randomly decides if a tool matches a task."""

    def __init__(self, match_probability: float = 0.5):
        """Initialize the random matcher.

        Args:
            match_probability: Probability of returning a match (0.0 to 1.0)
        """
        if not 0.0 <= match_probability <= 1.0:
            raise ValueError("match_probability must be between 0.0 and 1.0")
        self.match_probability = match_probability

    def match(
        self,
        input: TaskToolMatchInput,
    ) -> TaskToolMatchOutput:
        """Randomly determine if a requested tool matches the given task.

        Uses deterministic randomness based on task, requested tool and available tools
        to ensure reproducible results for the same inputs.

        Args:
            input (TaskToolMatchInput): The task description, requested tool, available tools, and MCP tools.

        Returns:
            TaskToolMatchResult with random match decision

        Raises:
            PipelineValidationError: If input validation fails
        """
        # Run common validations first - will raise exception if validation fails
        self._validate_input(input)

        # Create deterministic seed based on task, requested tool, and mcp server tools
        seed_string = f"{input.task}|{input.requested_tool}|{','.join({tool.name for tool in input.mcp_server.tools})}"

        # Generate a hash from the seed string
        seed_hash = hashlib.sha256(seed_string.encode("utf-8")).hexdigest()

        # Use first 8 characters of hash as seed (convert to int)
        seed = int(seed_hash[:8], 16)

        # Create a local Random instance with the deterministic seed
        local_random = random.Random(seed)

        # Random decision based on probability using the seeded random instance
        matches = local_random.random() < self.match_probability

        if matches:
            return TaskToolMatchOutput(task_tool_match=True)
        else:
            return TaskToolMatchOutput(task_tool_match=False, reason=TaskToolMatchReason.RANDOM_NO_MATCH)

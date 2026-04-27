# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utility functions for working with embeddings and tool matching."""

import heapq
import logging
from typing import List

import numpy as np
from openai import OpenAI
from pydantic import BaseModel


class EmbeddingTopNMatches(BaseModel):
    """Model for storing top N matches for embeddings."""

    index: int
    distance: float


class EmbeddingService:
    """Service for managing embeddings."""

    def __init__(self, config):
        """Initialize the embedding service."""
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        self.logger = logging.getLogger(__name__)
        self.client = OpenAI(
            api_key=config.get("OPENAI_TXT_EMB_3_LARGE_API_JWT_TOKEN"),
            base_url=config.get("OPENAI_TXT_EMB_3_LARGE_API_BASE_URL"),
        )
        self.model_id = config.get("OPENAI_TXT_EMB_3_LARGE_MODEL_ID")

    def get_embeddings(self, input: List[str]) -> List[np.ndarray]:
        """Get embeddings for a list of input texts.

        Args:
            input: A list of input texts to embed

        Returns:
            List[np.ndarray]: A list of embeddings for the input texts
        """
        response = self.client.embeddings.create(input=input, model=self.model_id).data
        return [np.array(data.embedding) for data in response]

    def get_top_n_matches(self, task: np.ndarray, tools: np.ndarray, n: int = 1) -> List[EmbeddingTopNMatches]:
        """Get the top N matches from the distance array.

        Args:
            task: The embedded task vector
            tools: The embedded tools matrix
            n: The number of top matches to return

        Returns:
            List[EmbeddingTopNMatches]: A list of top N matches for the embeddings.
        """
        task_norm = np.linalg.norm(task)
        tools_norm = np.linalg.norm(tools, axis=1, keepdims=True)
        if not np.isclose(task_norm, 1.0):
            task = task / task_norm
        if not np.isclose(tools_norm, 1.0).all():
            tools = tools / tools_norm
        distances = np.dot(task, tools.T).flatten()
        top_n_indices = heapq.nlargest(n, range(len(distances)), key=distances.__getitem__)
        return [EmbeddingTopNMatches(index=i, distance=distances[i]) for i in top_n_indices]

"""Hello World Agent Executor Implementation."""

import asyncio

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import Part, TaskState, TextPart
from a2a.utils import (
    new_agent_text_message,
    new_task,
)
from agent import call


class HelloWorldAgent:
    """Hello World Agent."""

    def __init__(self):
        """Initialize the HelloWorldAgent."""
        self.cancelled = False

    async def invoke(self, query: str, updater: TaskUpdater = None, context_id: str = "", task_id: str = "") -> str:
        """Invoke the Hello World Agent."""
        self.cancelled = False

        # Call the agent instead of simulating work with sleep
        try:
            agent_result = await call(query=query)
        except Exception as e:
            print(f"Error invoking agent: {e}")
            raise e

        if updater and not self.cancelled:
            await updater.add_artifact(
                [Part(root=TextPart(text=agent_result))],
                name="agent result",
            )

        return agent_result if not self.cancelled else "Cancelled"

    def cancel(self):
        """Cancel the agent's execution."""
        self.cancelled = True
        print("Agent execution was cancelled")


class HelloWorldAgentExecutor(AgentExecutor):
    """Test AgentProxy Implementation."""

    def __init__(self):
        """Initialize the HelloWorldAgentExecutor with a HelloWorldAgent instance."""
        self.agent = HelloWorldAgent()
        self.running = False

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Execute the agent with the given context and event queue."""
        task = context.current_task
        query = context.get_user_input()

        print(f"Current task: {task}")
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)
            print(f"New task created: {task}")

        # Set running state
        self.running = True

        # Create TaskUpdater for streaming updates
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)

        print(f"TaskUpdater created for task {context.task_id} in context {context.context_id}")
        await updater.submit()

        try:
            # Delegate work to the agent, passing the updater
            try:
                result = await self.agent.invoke(query, updater, context.context_id, context.task_id)

                print(f"Agent invoked for task {context.task_id}, result: {result}")

                await updater.complete(message=new_agent_text_message(result, context.context_id, context.task_id))

            except asyncio.CancelledError:
                # Handle cancellation gracefully
                self.agent.cancel()
                print(f"Task {context.task_id} was cancelled via CancelledError")
                await updater.update_status(
                    TaskState.canceled,
                    new_agent_text_message("Task was cancelled", context.context_id, context.task_id),
                    final=True,
                )

            except Exception as e:
                # Handle any exceptions from the agent invocation
                print(f"Error during agent invocation for task {context.task_id}: {e}")
                await updater.update_status(
                    TaskState.failed,
                    new_agent_text_message(f"Task failed: {e!s}", context.context_id, context.task_id),
                    final=True,
                )

        except Exception as e:
            # Handle any other exceptions
            print(f"Error during agent execution for task {context.task_id}: {e}")
            await updater.update_status(
                TaskState.failed,
                new_agent_text_message(f"Task failed: {e!s}", context.context_id, context.task_id),
                final=True,
            )
        finally:
            # Clean up the running state
            self.running = False

    async def cancel(self, context: RequestContext, _: EventQueue) -> None:
        """Cancel the agent's execution if it is running."""
        if self.running:
            self.agent.cancel()
        else:
            raise ValueError(f"Cannot cancel task {context.task_id} because it is not running.")

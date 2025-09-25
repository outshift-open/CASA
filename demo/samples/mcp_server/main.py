"""Web and File System MCP Server Example."""

import logging
import os

import httpx
import uvicorn
from fastapi import FastAPI
from identityservice.auth.starlette import IdentityServiceMCPMiddleware
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=os.getenv("LOG_LEVEL", "DEBUG").upper())

mcp = FastMCP("Web and File System MCP", stateless_http=True)


@mcp.tool()
def read_file(path: str) -> str:
    """Read the contents of the file provided in the path argument.

    Args:
        path: The file path to read.

    Returns:
        The contents of the file as a string, or an error message if the file cannot be read.
    """
    logging.info(f"Reading file at path: {path}")
    try:
        with open(path, "r") as file:
            content = file.read()
        return content
    except Exception as e:
        return f"Error reading file: {e}"


@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Write the provided content to the file at the specified path. If the file does not exist, create it.

    Args:
        path: The file path to write to.
        content: The content to write to the file.

    Returns:
        A success message or an error message if the write operation fails.
    """
    logging.info(f"Writing to file at path: {path}")
    try:
        with open(path, "w") as file:
            file.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing to file: {e}"


@mcp.tool()
def append_content_to_file(path: str, content: str) -> str:
    """Append the provided content to the file at the specified path. If the file does not exist, create it.

    Args:
        path: The file path to append to.
        content: The content to append to the file.

    Returns:
        A success message or an error message if the append operation fails.
    """
    logging.info(f"Appending to file at path: {path}")
    try:
        with open(path, "a") as file:
            file.write(content)
        return f"Successfully appended to {path}"
    except Exception as e:
        return f"Error appending to file: {e}"


@mcp.tool()
def list_directory(path: str) -> list[dict]:
    """List the contents of the directory at the specified path with details.

    Args:
        path: The directory path to list.

    Returns:
        A list of dictionaries with details of the contents of the directory, or an error message if the directory cannot be accessed.
    """
    logging.info(f"Listing directory with details at path: {path}")
    try:
        entries = os.listdir(path)
        detailed_list = []
        for entry in entries:
            full_path = os.path.join(path, entry)
            is_dir = os.path.isdir(full_path)
            size = os.path.getsize(full_path) if not is_dir else None
            detailed_list.append({"name": entry, "is_directory": is_dir, "size": size})
        return detailed_list
    except Exception as e:
        return [{"error": f"Error listing directory: {e}"}]


@mcp.tool()
def fetch_url(url: str) -> str:
    """Fetch the content from the specified URL.

    Args:
        url: The URL to fetch.

    Returns:
        The content of the URL as a string, or an error message if the request fails.
    """
    logging.info(f"Fetching URL: {url}")
    try:
        response = httpx.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error fetching URL: {e}"


app = FastAPI(lifespan=lambda _: mcp.session_manager.run())

# Add IdentityServiceMiddleware for authentication
app.add_middleware(
    IdentityServiceMCPMiddleware,
)

app.mount("/", mcp.streamable_http_app())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)

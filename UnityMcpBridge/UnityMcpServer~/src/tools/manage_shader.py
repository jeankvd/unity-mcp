from mcp.server.fastmcp import FastMCP, Context
from typing import Dict, Any
from unity_connection import get_unity_connection, send_command_with_retry
from config import config
import time
import os
import base64

from telemetry_decorator import telemetry_tool

def register_manage_shader_tools(mcp: FastMCP):
    """Register all shader script management tools with the MCP server."""

    def _send_shader_command(action: str, name: str, path: str, contents: str = None) -> Dict[str, Any]:
        """Helper function to send shader commands to Unity."""
        try:
            # Prepare parameters for Unity
            params = {
                "action": action,
                "name": name,
                "path": path,
            }
            
            # Base64 encode the contents if they exist to avoid JSON escaping issues
            if contents is not None:
                if action in ['create', 'update']:
                    # Encode content for safer transmission
                    params["encodedContents"] = base64.b64encode(contents.encode('utf-8')).decode('utf-8')
                    params["contentsEncoded"] = True
                else:
                    params["contents"] = contents
            
            # Remove None values so they don't get sent as null
            params = {k: v for k, v in params.items() if v is not None}

            # Send command via centralized retry helper
            response = send_command_with_retry("manage_shader", params)
            
            # Process response from Unity
            if isinstance(response, dict) and response.get("success"):
                # If the response contains base64 encoded content, decode it
                if response.get("data", {}).get("contentsEncoded"):
                    decoded_contents = base64.b64decode(response["data"]["encodedContents"]).decode('utf-8')
                    response["data"]["contents"] = decoded_contents
                    del response["data"]["encodedContents"]
                    del response["data"]["contentsEncoded"]
                
                return {"success": True, "message": response.get("message", "Operation successful."), "data": response.get("data")}
            return response if isinstance(response, dict) else {"success": False, "message": str(response)}

        except Exception as e:
            # Handle Python-side errors (e.g., connection issues)
            return {"success": False, "message": f"Python error managing shader: {str(e)}"}

    @mcp.tool(description="Create a new shader script in Unity.")
    @telemetry_tool("create_shader")
    def create_shader(
        ctx: Context,
        name: str,
        path: str,
        contents: str,
    ) -> Dict[str, Any]:
        """Create a new shader script in Unity.

        Args:
            ctx: The MCP context.
            name: Shader name (no .cs extension).
            path: Asset path (e.g., "Assets/Shaders/").
            contents: Shader code to create.

        Returns:
            Dictionary with results ('success', 'message', 'data').
        """
        return _send_shader_command("create", name, path, contents)

    @mcp.tool(description="Read the contents of an existing shader script.")
    @telemetry_tool("read_shader")
    def read_shader(
        ctx: Context,
        name: str,
        path: str,
    ) -> Dict[str, Any]:
        """Read the contents of an existing shader script.

        Args:
            ctx: The MCP context.
            name: Shader name (no .cs extension).
            path: Asset path (e.g., "Assets/Shaders/").

        Returns:
            Dictionary with results ('success', 'message', 'data').
        """
        return _send_shader_command("read", name, path)

    @mcp.tool(description="Update an existing shader script with new contents.")
    @telemetry_tool("update_shader")
    def update_shader(
        ctx: Context,
        name: str,
        path: str,
        contents: str,
    ) -> Dict[str, Any]:
        """Update an existing shader script with new contents.

        Args:
            ctx: The MCP context.
            name: Shader name (no .cs extension).
            path: Asset path (e.g., "Assets/Shaders/").
            contents: New shader code.

        Returns:
            Dictionary with results ('success', 'message', 'data').
        """
        return _send_shader_command("update", name, path, contents)

    @mcp.tool(description="Delete a shader script from Unity.")
    @telemetry_tool("delete_shader")
    def delete_shader(
        ctx: Context,
        name: str,
        path: str,
    ) -> Dict[str, Any]:
        """Delete a shader script from Unity.

        Args:
            ctx: The MCP context.
            name: Shader name (no .cs extension).
            path: Asset path (e.g., "Assets/Shaders/").

        Returns:
            Dictionary with results ('success', 'message', 'data').
        """
        return _send_shader_command("delete", name, path)

    @mcp.tool(description="Compatibility router for legacy shader operations.")
    @telemetry_tool("manage_shader")
    def manage_shader(
        ctx: Any,
        action: str,
        name: str,
        path: str,
        contents: str,
    ) -> Dict[str, Any]:
        """Compatibility router for legacy shader operations.

        DEPRECATED: Use create_shader, read_shader, update_shader, or delete_shader instead.

        Args:
            action: Operation ('create', 'read', 'update', 'delete').
            name: Shader name (no .cs extension).
            path: Asset path (default: "Assets/").
            contents: Shader code for 'create'/'update'.

        Returns:
            Dictionary with results ('success', 'message', 'data').
        """
        return _send_shader_command(action, name, path, contents)
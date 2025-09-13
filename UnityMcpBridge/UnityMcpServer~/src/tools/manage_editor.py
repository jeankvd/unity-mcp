from mcp.server.fastmcp import FastMCP, Context
import time
from typing import Dict, Any
from unity_connection import get_unity_connection, send_command_with_retry
from config import config

from telemetry_decorator import telemetry_tool
from telemetry import is_telemetry_enabled, record_tool_usage

def register_manage_editor_tools(mcp: FastMCP):
    """Register all editor management tools with the MCP server."""

    def _send_editor_command(action: str, wait_for_completion: bool = None, tool_name: str = None, tag_name: str = None, layer_name: str = None) -> Dict[str, Any]:
        """Helper function to send editor commands to Unity."""
        try:
            # Diagnostics: quick telemetry checks
            if action == "telemetry_status":
                return {"success": True, "telemetry_enabled": is_telemetry_enabled()}

            if action == "telemetry_ping":
                record_tool_usage("diagnostic_ping", True, 1.0, None)
                return {"success": True, "message": "telemetry ping queued"}
            
            # Prepare parameters, removing None values
            params = {
                "action": action,
                "waitForCompletion": wait_for_completion,
                "toolName": tool_name, # Corrected parameter name to match C#
                "tagName": tag_name,   # Pass tag name
                "layerName": layer_name, # Pass layer name
            }
            params = {k: v for k, v in params.items() if v is not None}
            
            # Send command using centralized retry helper
            response = send_command_with_retry("manage_editor", params)

            # Preserve structured failure data; unwrap success into a friendlier shape
            if isinstance(response, dict) and response.get("success"):
                return {"success": True, "message": response.get("message", "Editor operation successful."), "data": response.get("data")}
            return response if isinstance(response, dict) else {"success": False, "message": str(response)}

        except Exception as e:
            return {"success": False, "message": f"Python error managing editor: {str(e)}"}

    @mcp.tool(description="Start play mode in the Unity editor.")
    @telemetry_tool("play_editor")
    def play_editor(
        ctx: Context,
        wait_for_completion: bool = None,
    ) -> Dict[str, Any]:
        """Start play mode in the Unity editor.

        Args:
            ctx: The MCP context.
            wait_for_completion: If True, waits for the action to complete.

        Returns:
            Dictionary with operation results ('success', 'message', 'data').
        """
        return _send_editor_command("play", wait_for_completion)

    @mcp.tool(description="Pause play mode in the Unity editor.")
    @telemetry_tool("pause_editor")
    def pause_editor(
        ctx: Context,
        wait_for_completion: bool = None,
    ) -> Dict[str, Any]:
        """Pause play mode in the Unity editor.

        Args:
            ctx: The MCP context.
            wait_for_completion: If True, waits for the action to complete.

        Returns:
            Dictionary with operation results ('success', 'message', 'data').
        """
        return _send_editor_command("pause", wait_for_completion)

    @mcp.tool(description="Get the current state of the Unity editor.")
    @telemetry_tool("get_editor_state")
    def get_editor_state(
        ctx: Context,
    ) -> Dict[str, Any]:
        """Get the current state of the Unity editor.

        Args:
            ctx: The MCP context.

        Returns:
            Dictionary with operation results ('success', 'message', 'data').
        """
        return _send_editor_command("get_state")

    @mcp.tool(description="Set the active tool in the Unity editor.")
    @telemetry_tool("set_editor_active_tool")
    def set_editor_active_tool(
        ctx: Context,
        tool_name: str,
        wait_for_completion: bool = None,
    ) -> Dict[str, Any]:
        """Set the active tool in the Unity editor.

        Args:
            ctx: The MCP context.
            tool_name: Name of the tool to activate.
            wait_for_completion: If True, waits for the action to complete.

        Returns:
            Dictionary with operation results ('success', 'message', 'data').
        """
        return _send_editor_command("set_active_tool", wait_for_completion, tool_name)

    @mcp.tool(description="Add a tag to the Unity editor.")
    @telemetry_tool("add_editor_tag")
    def add_editor_tag(
        ctx: Context,
        tag_name: str,
        wait_for_completion: bool = None,
    ) -> Dict[str, Any]:
        """Add a tag to the Unity editor.

        Args:
            ctx: The MCP context.
            tag_name: Name of the tag to add.
            wait_for_completion: If True, waits for the action to complete.

        Returns:
            Dictionary with operation results ('success', 'message', 'data').
        """
        return _send_editor_command("add_tag", wait_for_completion, tag_name=tag_name)

    @mcp.tool(description="Get telemetry status from the Unity editor.")
    @telemetry_tool("get_editor_telemetry_status")
    def get_editor_telemetry_status(
        ctx: Context,
    ) -> Dict[str, Any]:
        """Get telemetry status from the Unity editor.

        Args:
            ctx: The MCP context.

        Returns:
            Dictionary with operation results ('success', 'message', 'data').
        """
        return _send_editor_command("telemetry_status")

    @mcp.tool(description="Send a telemetry ping to the Unity editor.")
    @telemetry_tool("ping_editor_telemetry")
    def ping_editor_telemetry(
        ctx: Context,
    ) -> Dict[str, Any]:
        """Send a telemetry ping to the Unity editor.

        Args:
            ctx: The MCP context.

        Returns:
            Dictionary with operation results ('success', 'message', 'data').
        """
        return _send_editor_command("telemetry_ping")

    @mcp.tool(description="Compatibility router for legacy editor operations.")
    @telemetry_tool("manage_editor")
    def manage_editor(
        ctx: Context,
        action: str,
        wait_for_completion: bool = None,
        # --- Parameters for specific actions ---
        tool_name: str = None, 
        tag_name: str = None,
        layer_name: str = None,
    ) -> Dict[str, Any]:
        """Compatibility router for legacy editor operations.

        DEPRECATED: Use specific editor tools like play_editor, pause_editor, get_editor_state, etc.

        Args:
            ctx: Context object (required)
            action: Operation (e.g., 'play', 'pause', 'get_state', 'set_active_tool', 'add_tag')
            wait_for_completion: Optional. If True, waits for certain actions
            tool_name: Tool name for specific actions
            tag_name: Tag name for specific actions
            layer_name: Layer name for specific actions

        Returns:
            Dictionary with operation results ('success', 'message', 'data').
        """
        return _send_editor_command(action, wait_for_completion, tool_name, tag_name, layer_name)
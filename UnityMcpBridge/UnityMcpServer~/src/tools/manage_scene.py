from mcp.server.fastmcp import FastMCP, Context
from typing import Dict, Any
from unity_connection import get_unity_connection, send_command_with_retry
from config import config
import time

from telemetry_decorator import telemetry_tool

def register_manage_scene_tools(mcp: FastMCP):
    """Register all scene management tools with the MCP server."""

    def _coerce_int(value, default=None):
        """Helper to coerce numeric inputs defensively."""
        if value is None:
            return default
        try:
            if isinstance(value, bool):
                return default
            if isinstance(value, int):
                return int(value)
            s = str(value).strip()
            if s.lower() in ("", "none", "null"):
                return default
            return int(float(s))
        except Exception:
            return default

    def _send_scene_command(action: str, name: str = "", path: str = "", build_index: Any = None) -> Dict[str, Any]:
        """Helper function to send scene commands to Unity."""
        try:
            coerced_build_index = _coerce_int(build_index, default=None)

            params = {"action": action}
            if name:
                params["name"] = name
            if path:
                params["path"] = path
            if coerced_build_index is not None:
                params["buildIndex"] = coerced_build_index
            
            # Use centralized retry helper
            response = send_command_with_retry("manage_scene", params)

            # Preserve structured failure data; unwrap success into a friendlier shape
            if isinstance(response, dict) and response.get("success"):
                return {"success": True, "message": response.get("message", "Scene operation successful."), "data": response.get("data")}
            return response if isinstance(response, dict) else {"success": False, "message": str(response)}

        except Exception as e:
            return {"success": False, "message": f"Python error managing scene: {str(e)}"}

    @mcp.tool(description="Load a Unity scene by name or build index.")
    @telemetry_tool("load_scene")
    def load_scene(
        ctx: Context,
        name: str = "",
        build_index: Any = None,
    ) -> Dict[str, Any]:
        """Load a Unity scene by name or build index.

        Args:
            ctx: The MCP context.
            name: Scene name (no extension) to load.
            build_index: Build index for load operation.

        Returns:
            Dictionary with results ('success', 'message', 'data').
        """
        return _send_scene_command("load", name=name, build_index=build_index)

    @mcp.tool(description="Save the current Unity scene.")
    @telemetry_tool("save_scene")
    def save_scene(
        ctx: Context,
        name: str = "",
        path: str = "",
    ) -> Dict[str, Any]:
        """Save the current Unity scene.

        Args:
            ctx: The MCP context.
            name: Scene name (no extension) for save operation.
            path: Asset path for scene operations (default: "Assets/").

        Returns:
            Dictionary with results ('success', 'message', 'data').
        """
        return _send_scene_command("save", name=name, path=path)

    @mcp.tool(description="Create a new Unity scene.")
    @telemetry_tool("create_scene")
    def create_scene(
        ctx: Context,
        name: str = "",
        path: str = "",
    ) -> Dict[str, Any]:
        """Create a new Unity scene.

        Args:
            ctx: The MCP context.
            name: Scene name (no extension) for the new scene.
            path: Asset path for scene creation (default: "Assets/").

        Returns:
            Dictionary with results ('success', 'message', 'data').
        """
        return _send_scene_command("create", name=name, path=path)

    @mcp.tool(description="Get the hierarchy of objects in the current Unity scene.")
    @telemetry_tool("get_scene_hierarchy")
    def get_scene_hierarchy(
        ctx: Context,
    ) -> Dict[str, Any]:
        """Get the hierarchy of objects in the current Unity scene.

        Args:
            ctx: The MCP context.

        Returns:
            Dictionary with results ('success', 'message', 'data').
        """
        return _send_scene_command("get_hierarchy")

    @mcp.tool(description="Compatibility router for legacy scene operations.")
    @telemetry_tool("manage_scene")
    def manage_scene(
        ctx: Context,
        action: str,
        name: str = "",
        path: str = "",
        build_index: Any = None,
    ) -> Dict[str, Any]:
        """Compatibility router for legacy scene operations.

        DEPRECATED: Use load_scene, save_scene, create_scene, or get_scene_hierarchy instead.

        Args:
            action: Operation (e.g., 'load', 'save', 'create', 'get_hierarchy').
            name: Scene name (no extension) for create/load/save.
            path: Asset path for scene operations (default: "Assets/").
            build_index: Build index for load/build settings actions.

        Returns:
            Dictionary with results ('success', 'message', 'data').
        """
        return _send_scene_command(action, name, path, build_index)
"""
Defines the manage_menu_item tool for executing and reading Unity Editor menu items.
"""
import asyncio
from typing import Annotated, Any, Literal

from mcp.server.fastmcp import FastMCP, Context
from telemetry_decorator import telemetry_tool

from unity_connection import get_unity_connection, async_send_command_with_retry


def register_manage_menu_item_tools(mcp: FastMCP):
    """Registers the manage_menu_item tools with the MCP server."""

    async def _send_menu_command(action: str, menu_path: str | None = None, search: str | None = None, refresh: bool | None = None) -> dict[str, Any]:
        """Helper function to send menu commands to Unity."""
        # Prepare parameters for the C# handler
        params_dict: dict[str, Any] = {
            "action": action,
            "menuPath": menu_path,
            "search": search,
            "refresh": refresh,
        }
        # Remove None values
        params_dict = {k: v for k, v in params_dict.items() if v is not None}

        # Get the current asyncio event loop
        loop = asyncio.get_running_loop()
        # Touch the connection to ensure availability (mirrors other tools' pattern)
        _ = get_unity_connection()

        # Use centralized async retry helper
        result = await async_send_command_with_retry("manage_menu_item", params_dict, loop=loop)
        return result if isinstance(result, dict) else {"success": False, "message": str(result)}

    @mcp.tool(description="Execute a Unity Editor menu item by its menu path.")
    @telemetry_tool("execute_menu_item")
    async def execute_menu_item(
        ctx: Context,
        menu_path: Annotated[str, "Menu path to execute (e.g., 'File/Save Project')"],
    ) -> dict[str, Any]:
        """Execute a Unity Editor menu item by its menu path.

        Args:
            ctx: The MCP context.
            menu_path: Menu path to execute (e.g., "File/Save Project").

        Returns:
            A dictionary with operation results ('success', 'data', 'error').
        """
        return await _send_menu_command("execute", menu_path)

    @mcp.tool(description="List available Unity Editor menu items, optionally filtered by search term.")
    @telemetry_tool("list_menu_items")
    async def list_menu_items(
        ctx: Context,
        search: Annotated[str | None, "Optional filter string (e.g., 'Save')"] = None,
        refresh: Annotated[bool | None, "Optional flag to force refresh of the menu cache"] = None,
    ) -> dict[str, Any]:
        """List available Unity Editor menu items.

        Args:
            ctx: The MCP context.
            search: Optional filter string to narrow down results.
            refresh: Optional flag to force refresh of the menu cache.

        Returns:
            A dictionary with operation results ('success', 'data', 'error').
        """
        return await _send_menu_command("list", search=search, refresh=refresh)

    @mcp.tool(description="Check if a Unity Editor menu item exists.")
    @telemetry_tool("check_menu_item_exists")
    async def check_menu_item_exists(
        ctx: Context,
        menu_path: Annotated[str, "Menu path to check (e.g., 'File/Save Project')"],
    ) -> dict[str, Any]:
        """Check if a Unity Editor menu item exists.

        Args:
            ctx: The MCP context.
            menu_path: Menu path to check (e.g., "File/Save Project").

        Returns:
            A dictionary with operation results ('success', 'data', 'error').
        """
        return await _send_menu_command("exists", menu_path)

    @mcp.tool(description="Compatibility router for legacy menu item operations.")
    @telemetry_tool("manage_menu_item")
    async def manage_menu_item(
        ctx: Context,
        action: Annotated[Literal["execute", "list", "exists"], "One of 'execute', 'list', 'exists'"],
        menu_path: Annotated[str | None,
                             "Menu path for 'execute' or 'exists' (e.g., 'File/Save Project')"] = None,
        search: Annotated[str | None,
                          "Optional filter string for 'list' (e.g., 'Save')"] = None,
        refresh: Annotated[bool | None,
                           "Optional flag to force refresh of the menu cache when listing"] = None,
    ) -> dict[str, Any]:
        """Compatibility router for legacy menu item operations.

        DEPRECATED: Use execute_menu_item, list_menu_items, or check_menu_item_exists instead.

        Args:
            ctx: The MCP context.
            action: One of 'execute', 'list', 'exists'.
            menu_path: Menu path for 'execute' or 'exists' (e.g., "File/Save Project").
            search: Optional filter string for 'list'.
            refresh: Optional flag to force refresh of the menu cache when listing.

        Returns:
            A dictionary with operation results ('success', 'data', 'error').
        """
        return await _send_menu_command(action, menu_path, search, refresh)

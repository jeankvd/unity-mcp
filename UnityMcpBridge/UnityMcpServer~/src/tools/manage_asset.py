"""
Defines the manage_asset tool for interacting with Unity assets.
"""
import asyncio  # Added: Import asyncio for running sync code in async
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP, Context
# from ..unity_connection import get_unity_connection  # Original line that caused error
from unity_connection import get_unity_connection, async_send_command_with_retry  # Use centralized retry helper
from config import config
import time

from telemetry_decorator import telemetry_tool

def register_manage_asset_tools(mcp: FastMCP):
    """Registers the manage_asset tools with the MCP server."""

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

    async def _send_asset_command(
        action: str,
        path: str,
        asset_type: str = None,
        properties: Dict[str, Any] = None,
        destination: str = None,
        generate_preview: bool = False,
        search_pattern: str = None,
        filter_type: str = None,
        filter_date_after: str = None,
        page_size: Any = None,
        page_number: Any = None
    ) -> Dict[str, Any]:
        """Helper function to send asset commands to Unity."""
        # Ensure properties is a dict if None
        if properties is None:
            properties = {}

        page_size = _coerce_int(page_size)
        page_number = _coerce_int(page_number)

        # Prepare parameters for the C# handler
        params_dict = {
            "action": action.lower(),
            "path": path,
            "assetType": asset_type,
            "properties": properties,
            "destination": destination,
            "generatePreview": generate_preview,
            "searchPattern": search_pattern,
            "filterType": filter_type,
            "filterDateAfter": filter_date_after,
            "pageSize": page_size,
            "pageNumber": page_number
        }
        
        # Remove None values to avoid sending unnecessary nulls
        params_dict = {k: v for k, v in params_dict.items() if v is not None}

        # Get the current asyncio event loop
        loop = asyncio.get_running_loop()
        # Get the Unity connection instance
        connection = get_unity_connection()
        
        # Use centralized async retry helper to avoid blocking the event loop
        result = await async_send_command_with_retry("manage_asset", params_dict, loop=loop)
        # Return the result obtained from Unity
        return result if isinstance(result, dict) else {"success": False, "message": str(result)}

    @mcp.tool(description="Import an asset into Unity from an external source.")
    @telemetry_tool("import_asset")
    async def import_asset(
        ctx: Any,
        path: str,
        properties: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Import an asset into Unity from an external source.

        Args:
            ctx: The MCP context.
            path: Source path for the asset to import.
            properties: Dictionary of import properties/settings.

        Returns:
            A dictionary with operation results ('success', 'data', 'error').
        """
        return await _send_asset_command("import", path, properties=properties)

    @mcp.tool(description="Create a new asset in Unity.")
    @telemetry_tool("create_asset")
    async def create_asset(
        ctx: Any,
        path: str,
        asset_type: str,
        properties: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Create a new asset in Unity.

        Args:
            ctx: The MCP context.
            path: Asset path where to create the asset (e.g., "Materials/MyMaterial.mat").
            asset_type: Asset type (e.g., 'Material', 'Texture', 'PhysicsMaterial').
            properties: Dictionary of asset properties.
                Example for Material: {"color": [1, 0, 0, 1], "shader": "Standard"}
                Example for Texture: {"width": 1024, "height": 1024, "format": "RGBA32"}

        Returns:
            A dictionary with operation results ('success', 'data', 'error').
        """
        return await _send_asset_command("create", path, asset_type, properties)

    @mcp.tool(description="Modify an existing asset in Unity.")
    @telemetry_tool("modify_asset")
    async def modify_asset(
        ctx: Any,
        path: str,
        properties: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Modify an existing asset in Unity.

        Args:
            ctx: The MCP context.
            path: Asset path to modify (e.g., "Materials/MyMaterial.mat").
            properties: Dictionary of properties to modify.

        Returns:
            A dictionary with operation results ('success', 'data', 'error').
        """
        return await _send_asset_command("modify", path, properties=properties)

    @mcp.tool(description="Delete an asset from Unity.")
    @telemetry_tool("delete_asset")
    async def delete_asset(
        ctx: Any,
        path: str,
    ) -> Dict[str, Any]:
        """Delete an asset from Unity.

        Args:
            ctx: The MCP context.
            path: Asset path to delete (e.g., "Materials/MyMaterial.mat").

        Returns:
            A dictionary with operation results ('success', 'data', 'error').
        """
        return await _send_asset_command("delete", path)

    @mcp.tool(description="Duplicate an asset in Unity.")
    @telemetry_tool("duplicate_asset")
    async def duplicate_asset(
        ctx: Any,
        path: str,
        destination: str,
    ) -> Dict[str, Any]:
        """Duplicate an asset in Unity.

        Args:
            ctx: The MCP context.
            path: Source asset path to duplicate.
            destination: Target path for the duplicated asset.

        Returns:
            A dictionary with operation results ('success', 'data', 'error').
        """
        return await _send_asset_command("duplicate", path, destination=destination)

    @mcp.tool(description="Move an asset to a new location in Unity.")
    @telemetry_tool("move_asset")
    async def move_asset(
        ctx: Any,
        path: str,
        destination: str,
    ) -> Dict[str, Any]:
        """Move an asset to a new location in Unity.

        Args:
            ctx: The MCP context.
            path: Source asset path to move.
            destination: Target path for the asset.

        Returns:
            A dictionary with operation results ('success', 'data', 'error').
        """
        return await _send_asset_command("move", path, destination=destination)

    @mcp.tool(description="Rename an asset in Unity.")
    @telemetry_tool("rename_asset")
    async def rename_asset(
        ctx: Any,
        path: str,
        destination: str,
    ) -> Dict[str, Any]:
        """Rename an asset in Unity.

        Args:
            ctx: The MCP context.
            path: Current asset path.
            destination: New asset path/name.

        Returns:
            A dictionary with operation results ('success', 'data', 'error').
        """
        return await _send_asset_command("rename", path, destination=destination)

    @mcp.tool(description="Search for assets in Unity.")
    @telemetry_tool("search_asset")
    async def search_asset(
        ctx: Any,
        path: str,
        search_pattern: str = None,
        filter_type: str = None,
        filter_date_after: str = None,
        page_size: Any = None,
        page_number: Any = None,
    ) -> Dict[str, Any]:
        """Search for assets in Unity.

        Args:
            ctx: The MCP context.
            path: Search scope/directory.
            search_pattern: Search pattern (e.g., '*.prefab').
            filter_type: Filter by asset type.
            filter_date_after: Filter by date (assets modified after this date).
            page_size: Number of results per page.
            page_number: Page number for pagination.

        Returns:
            A dictionary with operation results ('success', 'data', 'error').
        """
        return await _send_asset_command("search", path, search_pattern=search_pattern, 
                                       filter_type=filter_type, filter_date_after=filter_date_after,
                                       page_size=page_size, page_number=page_number)

    @mcp.tool(description="Get information about an asset in Unity.")
    @telemetry_tool("get_asset_info")
    async def get_asset_info(
        ctx: Any,
        path: str,
        generate_preview: bool = False,
    ) -> Dict[str, Any]:
        """Get information about an asset in Unity.

        Args:
            ctx: The MCP context.
            path: Asset path to get info for.
            generate_preview: Whether to generate a preview of the asset.

        Returns:
            A dictionary with operation results ('success', 'data', 'error').
        """
        return await _send_asset_command("get_info", path, generate_preview=generate_preview)

    @mcp.tool(description="Create a folder in Unity's asset directory.")
    @telemetry_tool("create_asset_folder")
    async def create_asset_folder(
        ctx: Any,
        path: str,
    ) -> Dict[str, Any]:
        """Create a folder in Unity's asset directory.

        Args:
            ctx: The MCP context.
            path: Folder path to create.

        Returns:
            A dictionary with operation results ('success', 'data', 'error').
        """
        return await _send_asset_command("create_folder", path, asset_type="Folder")

    @mcp.tool(description="Get components attached to an asset (for GameObjects/Prefabs).")
    @telemetry_tool("get_asset_components")
    async def get_asset_components(
        ctx: Any,
        path: str,
    ) -> Dict[str, Any]:
        """Get components attached to an asset (for GameObjects/Prefabs).

        Args:
            ctx: The MCP context.
            path: Asset path to get components for.

        Returns:
            A dictionary with operation results ('success', 'data', 'error').
        """
        return await _send_asset_command("get_components", path)

    @mcp.tool(description="Compatibility router for legacy asset operations.")
    @telemetry_tool("manage_asset")
    async def manage_asset(
        ctx: Any,
        action: str,
        path: str,
        asset_type: str = None,
        properties: Dict[str, Any] = None,
        destination: str = None,
        generate_preview: bool = False,
        search_pattern: str = None,
        filter_type: str = None,
        filter_date_after: str = None,
        page_size: Any = None,
        page_number: Any = None
    ) -> Dict[str, Any]:
        """Compatibility router for legacy asset operations.

        DEPRECATED: Use specific asset tools like create_asset, delete_asset, search_asset, etc.

        Args:
            ctx: The MCP context.
            action: Operation to perform (e.g., 'import', 'create', 'modify', 'delete', 'duplicate', 'move', 'rename', 'search', 'get_info', 'create_folder', 'get_components').
            path: Asset path (e.g., "Materials/MyMaterial.mat") or search scope.
            asset_type: Asset type (e.g., 'Material', 'Folder') - required for 'create'.
            properties: Dictionary of properties for 'create'/'modify'.
            destination: Target path for 'duplicate'/'move'.
            search_pattern: Search pattern (e.g., '*.prefab').
            filter_type: Filter by asset type.
            filter_date_after: Filter by date.
            page_size: Results per page.
            page_number: Page number.

        Returns:
            A dictionary with operation results ('success', 'data', 'error').
        """
        return await _send_asset_command(action, path, asset_type, properties, destination,
                                       generate_preview, search_pattern, filter_type, 
                                       filter_date_after, page_size, page_number)

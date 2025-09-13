from mcp.server.fastmcp import FastMCP, Context
from typing import Dict, Any, List
from unity_connection import get_unity_connection, send_command_with_retry
from config import config
import time

from telemetry_decorator import telemetry_tool

def register_manage_gameobject_tools(mcp: FastMCP):
    """Register all GameObject management tools with the MCP server."""

    @mcp.tool(description="Find GameObjects in the Unity scene.")
    @telemetry_tool("find_gameobject") 
    def find_gameobject(
        ctx: Any,
        search_term: str,
        search_method: str = None,
        find_all: bool = False,
        search_in_children: bool = False,
        search_inactive: bool = False,
    ) -> Dict[str, Any]:
        """Find GameObjects in the Unity scene.

        Args:
            ctx: The MCP context.
            search_term: What to search for.
            search_method: How to search ('by_name', 'by_id', 'by_path', etc.).
            find_all: Whether to find all matches or just the first.
            search_in_children: Whether to search in child objects.
            search_inactive: Whether to include inactive objects.

        Returns:
            Dictionary with operation results ('success', 'message', 'data').
        """
        try:
            params = {
                "action": "find",
                "searchTerm": search_term,
                "searchMethod": search_method,
                "findAll": find_all,
                "searchInChildren": search_in_children,
                "searchInactive": search_inactive,
            }
            params = {k: v for k, v in params.items() if v is not None}
            
            response = send_command_with_retry("manage_gameobject", params)
            
            if isinstance(response, dict) and response.get("success"):
                return {"success": True, "message": response.get("message", "GameObject search successful."), "data": response.get("data")}
            return response if isinstance(response, dict) else {"success": False, "message": str(response)}
        except Exception as e:
            return {"success": False, "message": f"Python error finding GameObject: {str(e)}"}

    @mcp.tool(description="Get components attached to a GameObject.")
    @telemetry_tool("get_gameobject_components")
    def get_gameobject_components(
        ctx: Any,
        target: str,
        search_method: str = None,
        includeNonPublicSerialized: bool = None,
    ) -> Dict[str, Any]:
        """Get components attached to a GameObject.

        Args:
            ctx: The MCP context.
            target: GameObject identifier (name or path).
            search_method: How to find the target ('by_name', 'by_id', 'by_path').
            includeNonPublicSerialized: Include private [SerializeField] fields.

        Returns:
            Dictionary with operation results ('success', 'message', 'data').
        """
        try:
            params = {
                "action": "get_components",
                "target": target,
                "searchMethod": search_method,
                "includeNonPublicSerialized": includeNonPublicSerialized,
            }
            params = {k: v for k, v in params.items() if v is not None}
            
            response = send_command_with_retry("manage_gameobject", params)
            
            if isinstance(response, dict) and response.get("success"):
                return {"success": True, "message": response.get("message", "GameObject components retrieved."), "data": response.get("data")}
            return response if isinstance(response, dict) else {"success": False, "message": str(response)}
        except Exception as e:
            return {"success": False, "message": f"Python error getting GameObject components: {str(e)}"}

    @mcp.tool(description="Create a new GameObject.")
    @telemetry_tool("create_gameobject")
    def create_gameobject(
        ctx: Any,
        name: str,
        tag: str = None,
        parent: str = None,
        layer: str = None,
        component_properties: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Create a new GameObject.

        Args:
            ctx: The MCP context.
            name: GameObject name.
            tag: Tag name (optional).
            parent: Parent GameObject reference (optional).
            layer: Layer name (optional).
            component_properties: Dict mapping Component names to their properties.
            params: Additional parameters (optional).

        Returns:
            A dictionary with operation results ('success', 'data', 'error').
        """
        try:
            request_params = {
                "action": "create",
                "name": name,
            }
            if tag:
                request_params["tag"] = tag
            if parent:
                request_params["parent"] = parent
            if layer:
                request_params["layer"] = layer
            if component_properties:
                request_params["componentProperties"] = component_properties
            if params:
                request_params.update(params)
            
            response = send_command_with_retry("manage_gameobject", request_params)
            return response if isinstance(response, dict) else {"success": False, "message": str(response)}
        except Exception as e:
            return {"success": False, "message": f"Error creating GameObject: {str(e)}"}

    @mcp.tool(description="Modify an existing GameObject.")
    @telemetry_tool("modify_gameobject")
    def modify_gameobject(
        ctx: Any,
        target: str,
        search_method: str = "by_name",
        name: str = None,
        tag: str = None,
        parent: str = None,
        layer: str = None,
        component_properties: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Modify an existing GameObject.

        Args:
            ctx: The MCP context.
            target: GameObject identifier (name or path string).
            search_method: How to find the object ('by_name', 'by_id', 'by_path', etc.).
            name: New name (optional).
            tag: New tag (optional).
            parent: New parent GameObject reference (optional).
            layer: New layer (optional).
            component_properties: Dict mapping Component names to their properties.

        Returns:
            A dictionary with operation results ('success', 'data', 'error').
        """
        try:
            request_params = {
                "action": "modify",
                "target": target,
                "searchMethod": search_method,
            }
            if name:
                request_params["name"] = name
            if tag:
                request_params["tag"] = tag
            if parent:
                request_params["parent"] = parent
            if layer:
                request_params["layer"] = layer
            if component_properties:
                request_params["componentProperties"] = component_properties
            
            response = send_command_with_retry("manage_gameobject", request_params)
            return response if isinstance(response, dict) else {"success": False, "message": str(response)}
        except Exception as e:
            return {"success": False, "message": f"Error modifying GameObject: {str(e)}"}

    @mcp.tool(description="Add a component to a GameObject.")
    @telemetry_tool("add_gameobject_component")
    def add_gameobject_component(
        ctx: Any,
        target: str,
        component_type: str,
        search_method: str = "by_name",
        component_properties: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Add a component to a GameObject.

        Args:
            ctx: The MCP context.
            target: GameObject identifier (name or path string).
            component_type: Type of component to add (e.g., 'Rigidbody', 'MeshRenderer').
            search_method: How to find the object ('by_name', 'by_id', 'by_path', etc.).
            component_properties: Dict of properties to set on the new component.

        Returns:
            A dictionary with operation results ('success', 'data', 'error').
        """
        try:
            request_params = {
                "action": "add_component",
                "target": target,
                "searchMethod": search_method,
                "componentType": component_type,
            }
            if component_properties:
                request_params["componentProperties"] = component_properties
            
            response = send_command_with_retry("manage_gameobject", request_params)
            return response if isinstance(response, dict) else {"success": False, "message": str(response)}
        except Exception as e:
            return {"success": False, "message": f"Error adding component: {str(e)}"}

    @mcp.tool(description="Remove a component from a GameObject.")
    @telemetry_tool("remove_gameobject_component")
    def remove_gameobject_component(
        ctx: Any,
        target: str,
        component_type: str,
        search_method: str = "by_name",
    ) -> Dict[str, Any]:
        """Remove a component from a GameObject.

        Args:
            ctx: The MCP context.
            target: GameObject identifier (name or path string).
            component_type: Type of component to remove (e.g., 'Rigidbody', 'MeshRenderer').
            search_method: How to find the object ('by_name', 'by_id', 'by_path', etc.).

        Returns:
            A dictionary with operation results ('success', 'data', 'error').
        """
        try:
            request_params = {
                "action": "remove_component",
                "target": target,
                "searchMethod": search_method,
                "componentType": component_type,
            }
            
            response = send_command_with_retry("manage_gameobject", request_params)
            return response if isinstance(response, dict) else {"success": False, "message": str(response)}
        except Exception as e:
            return {"success": False, "message": f"Error removing component: {str(e)}"}

    @mcp.tool(description="Set properties on a GameObject component.")
    @telemetry_tool("set_gameobject_component_property")
    def set_gameobject_component_property(
        ctx: Any,
        target: str,
        component_type: str,
        property_name: str,
        property_value: Any,
        search_method: str = "by_name",
    ) -> Dict[str, Any]:
        """Set properties on a GameObject component.

        Args:
            ctx: The MCP context.
            target: GameObject identifier (name or path string).
            component_type: Type of component (e.g., 'Rigidbody', 'MeshRenderer').
            property_name: Name of the property to set.
            property_value: Value to set the property to.
            search_method: How to find the object ('by_name', 'by_id', 'by_path', etc.).

        Returns:
            A dictionary with operation results ('success', 'data', 'error').
        """
        try:
            request_params = {
                "action": "set_component_property",
                "target": target,
                "searchMethod": search_method,
                "componentType": component_type,
                "propertyName": property_name,
                "propertyValue": property_value,
            }
            
            response = send_command_with_retry("manage_gameobject", request_params)
            return response if isinstance(response, dict) else {"success": False, "message": str(response)}
        except Exception as e:
            return {"success": False, "message": f"Error setting component property: {str(e)}"}

    @mcp.tool()
    @telemetry_tool("manage_gameobject")
    def manage_gameobject(
        ctx: Any,
        action: str,
        target: str = None,  # GameObject identifier by name or path
        search_method: str = None,
        # --- Combined Parameters for Create/Modify ---
        name: str = None,  # Used for both 'create' (new object name) and 'modify' (rename)
        tag: str = None,  # Used for both 'create' (initial tag) and 'modify' (change tag)
        parent: str = None,  # Used for both 'create' (initial parent) and 'modify' (change parent)
        position: List[float] = None,
        rotation: List[float] = None,
        scale: List[float] = None,
        components_to_add: List[str] = None,  # List of component names to add
        primitive_type: str = None,
        save_as_prefab: bool = False,
        prefab_path: str = None,
        prefab_folder: str = "Assets/Prefabs",
        # --- Parameters for 'modify' ---
        set_active: bool = None,
        layer: str = None,  # Layer name
        components_to_remove: List[str] = None,
        component_properties: Dict[str, Dict[str, Any]] = None,
        # --- Parameters for 'find' ---
        search_term: str = None,
        find_all: bool = False,
        search_in_children: bool = False,
        search_inactive: bool = False,
        # -- Component Management Arguments --
        component_name: str = None,
        includeNonPublicSerialized: bool = None, # Controls serialization of private [SerializeField] fields
    ) -> Dict[str, Any]:
        """Manages GameObjects: create, modify, delete, find, and component operations.

        Args:
            action: Operation (e.g., 'create', 'modify', 'find', 'add_component', 'remove_component', 'set_component_property', 'get_components').
            target: GameObject identifier (name or path string) for modify/delete/component actions.
            search_method: How to find objects ('by_name', 'by_id', 'by_path', etc.). Used with 'find' and some 'target' lookups.
            name: GameObject name - used for both 'create' (initial name) and 'modify' (rename).
            tag: Tag name - used for both 'create' (initial tag) and 'modify' (change tag).
            parent: Parent GameObject reference - used for both 'create' (initial parent) and 'modify' (change parent).
            layer: Layer name - used for both 'create' (initial layer) and 'modify' (change layer).
            component_properties: Dict mapping Component names to their properties to set.
                                  Example: {"Rigidbody": {"mass": 10.0, "useGravity": True}},
                                  To set references:
                                  - Use asset path string for Prefabs/Materials, e.g., {"MeshRenderer": {"material": "Assets/Materials/MyMat.mat"}}
                                  - Use a dict for scene objects/components, e.g.:
                                    {"MyScript": {"otherObject": {"find": "Player", "method": "by_name"}}} (assigns GameObject)
                                    {"MyScript": {"playerHealth": {"find": "Player", "component": "HealthComponent"}}} (assigns Component)
                                  Example set nested property:
                                  - Access shared material: {"MeshRenderer": {"sharedMaterial.color": [1, 0, 0, 1]}}
            components_to_add: List of component names to add.
            Action-specific arguments (e.g., position, rotation, scale for create/modify;
                     component_name for component actions;
                     search_term, find_all for 'find').
            includeNonPublicSerialized: If True, includes private fields marked [SerializeField] in component data.

            Action-specific details:
            - For 'get_components':
                Required: target, search_method
                Optional: includeNonPublicSerialized (defaults to True)
                Returns all components on the target GameObject with their serialized data.
                The search_method parameter determines how to find the target ('by_name', 'by_id', 'by_path').

        Returns:
            Dictionary with operation results ('success', 'message', 'data').
            For 'get_components', the 'data' field contains a dictionary of component names and their serialized properties.
        """
        try:
            # --- Early check for attempting to modify a prefab asset ---
            # ----------------------------------------------------------

            # Prepare parameters, removing None values
            params = {
                "action": action,
                "target": target,
                "searchMethod": search_method,
                "name": name,
                "tag": tag,
                "parent": parent,
                "position": position,
                "rotation": rotation,
                "scale": scale,
                "componentsToAdd": components_to_add,
                "primitiveType": primitive_type,
                "saveAsPrefab": save_as_prefab,
                "prefabPath": prefab_path,
                "prefabFolder": prefab_folder,
                "setActive": set_active,
                "layer": layer,
                "componentsToRemove": components_to_remove,
                "componentProperties": component_properties,
                "searchTerm": search_term,
                "findAll": find_all,
                "searchInChildren": search_in_children,
                "searchInactive": search_inactive,
                "componentName": component_name,
                "includeNonPublicSerialized": includeNonPublicSerialized
            }
            params = {k: v for k, v in params.items() if v is not None}
            
            # --- Handle Prefab Path Logic ---
            if action == "create" and params.get("saveAsPrefab"): # Check if 'saveAsPrefab' is explicitly True in params
                if "prefabPath" not in params:
                    if "name" not in params or not params["name"]:
                        return {"success": False, "message": "Cannot create default prefab path: 'name' parameter is missing."}
                    # Use the provided prefab_folder (which has a default) and the name to construct the path
                    constructed_path = f"{prefab_folder}/{params['name']}.prefab"
                    # Ensure clean path separators (Unity prefers '/')
                    params["prefabPath"] = constructed_path.replace("\\", "/")
                elif not params["prefabPath"].lower().endswith(".prefab"):
                    return {"success": False, "message": f"Invalid prefab_path: '{params['prefabPath']}' must end with .prefab"}
            # Ensure prefabFolder itself isn't sent if prefabPath was constructed or provided
            # The C# side only needs the final prefabPath
            params.pop("prefabFolder", None) 
            # --------------------------------
            
            # Use centralized retry helper
            response = send_command_with_retry("manage_gameobject", params)

            # Check if the response indicates success
            # If the response is not successful, raise an exception with the error message
            if isinstance(response, dict) and response.get("success"):
                return {"success": True, "message": response.get("message", "GameObject operation successful."), "data": response.get("data")}
            return response if isinstance(response, dict) else {"success": False, "message": str(response)}

        except Exception as e:
            return {"success": False, "message": f"Python error managing GameObject: {str(e)}"} 
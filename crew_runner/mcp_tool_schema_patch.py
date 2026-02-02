from __future__ import annotations

from pydantic import Field, create_model


def patch_crewai_mcp_tool_schemas(tools) -> None:
    """
    CrewAI's MCPServerAdapter may generate args schemas that some LLM providers reject.
    This patches DynamicModel-derived schemas into proper Pydantic models.
    """
    print("[PATCH] Fixing MCP tool schemas for LLM compatibility...")

    for tool in tools:
        if not hasattr(tool, "args_schema"):
            continue

        schema = tool.args_schema
        schema_name = schema.__name__ if hasattr(schema, "__name__") else str(type(schema))
        if "DynamicModel" not in schema_name:
            continue

        try:
            original_schema = schema.model_json_schema()
            properties = original_schema.get("properties", {})

            fields = {}
            for prop_name, prop_def in properties.items():
                prop_type = prop_def.get("type", "string")
                default_val = prop_def.get("default", ...)
                description = prop_def.get("description", "")

                type_mapping = {
                    "integer": int,
                    "string": str,
                    "number": float,
                    "boolean": bool,
                    "object": dict,
                    "array": list,
                }
                python_type = type_mapping.get(prop_type, str)

                if default_val is not ...:
                    fields[prop_name] = (
                        python_type,
                        Field(default=default_val, description=description),
                    )
                else:
                    fields[prop_name] = (python_type, Field(description=description))

            model_name = f"{tool.name.replace('_', ' ').title().replace(' ', '')}Input"
            NewModel = create_model(model_name, **fields)
            tool.args_schema = NewModel

            print(f"[PATCH] ✓ Fixed schema for tool: {tool.name}")
        except Exception as e:
            print(f"[PATCH] ⚠ Could not patch {tool.name}: {e}")



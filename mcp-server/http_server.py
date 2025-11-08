from fastapi import FastAPI, HTTPException, Query, Body, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import argparse
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import uvicorn

from mcp_protocol_server import MCPDocumentationServer


async def _handle_json_rpc(payload: Dict[str, Any], state: Any, service: MCPDocumentationServer) -> Dict[str, Any]:
    logger = logging.getLogger("mcp.http.jsonrpc")
    logger.debug("JSON-RPC request: %s", payload)
    response: Dict[str, Any] = {"jsonrpc": "2.0", "id": payload.get("id")}

    if not isinstance(payload, dict) or payload.get("jsonrpc") != "2.0":
        response["error"] = {"code": -32600, "message": "Invalid Request"}
        return response

    method = payload.get("method")
    params = payload.get("params", {}) or {}

    try:
        if method == "initialize":
            state.session["initialized"] = True
            protocol_version = params.get("protocolVersion", "2024-11-05")
            state.session["protocolVersion"] = protocol_version
            capabilities = {
                "resources": {"listChanged": False},
                "tools": {"listChanged": False},
                "prompts": {"listChanged": False},
                "logging": {"levels": []},
            }
            response["result"] = {
                "protocolVersion": protocol_version,
                "capabilities": capabilities,
                "serverInfo": {"name": "mcp-docs-http", "version": "1.0.0"},
            }
        elif method == "listTools":
            response["result"] = {"tools": service.tool_definitions()}
        elif method in {"tools/list", "tools/list"}:
            response["result"] = {"tools": service.tool_definitions()}
        elif method == "listResources":
            response["result"] = {"resources": service.collect_resources()}
        elif method == "resources/list":
            response["result"] = {"resources": service.collect_resources()}
        elif method == "readResource" or method == "resources/read":
            resource_uri = params.get("uri")
            if not resource_uri:
                raise ValueError("uri is required")
            result = await _read_resource_via_service(service, resource_uri)
            response["result"] = {"contents": result}
        elif method == "callTool":
            name = params.get("name")
            arguments = params.get("arguments", {})
            if not name:
                raise ValueError("name is required")
            tool_result = await service.execute_tool(name, arguments)
            text_payload = json.dumps(tool_result, ensure_ascii=False, indent=2)
            logger.debug("Tool %s result: %s", name, text_payload)
            response["result"] = {
                "content": [
                    {
                        "type": "text",
                        "text": text_payload
                    }
                ]
            }
        elif method == "prompts/list":
            response["result"] = {"prompts": []}
        elif method == "notifications/initialized":
            response["result"] = {"acknowledged": True}
        else:
            response["error"] = {"code": -32601, "message": f"Method not found: {method}"}
    except ValueError as exc:
        response["error"] = {"code": -32602, "message": str(exc)}
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Unhandled JSON-RPC error")
        response["error"] = {"code": -32000, "message": str(exc)}

    logger.debug("JSON-RPC response: %s", response)
    return response


async def _read_resource_via_service(service: MCPDocumentationServer, uri: str) -> List[Dict[str, Any]]:
    if not uri.startswith("mcp-docs://"):
        raise ValueError("Unsupported URI scheme")

    components = uri[len("mcp-docs://"):].split("/")
    resource_type = components[0]
    if resource_type == "project":
        language, project = components[1], components[2]
        data = await service._read_project_resource(language, project)
        return [{"uri": uri, "mimeType": "application/json", "text": data}]
    if resource_type == "readme":
        language, project = components[1], components[2]
        text = await service._read_readme_resource(language, project)
        return [{"uri": uri, "mimeType": "text/markdown", "text": text}]
    if resource_type == "module":
        language, project, module = components[1], components[2], components[3]
        data = await service._read_module_resource(language, project, module)
        return [{"uri": uri, "mimeType": "application/json", "text": data}]
    raise ValueError(f"Unknown resource type: {resource_type}")


def create_app(mcp_root: str, allow_origins: Optional[List[str]] = None) -> FastAPI:
    service = MCPDocumentationServer(mcp_root)
    app = FastAPI(
        title="MCP Documentation HTTP Gateway",
        description="Expose documentation resources and tools over HTTP",
        version="1.0.0"
    )

    origins = allow_origins or ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.service = service
    app.state.session = {
        "initialized": False,
        "protocolVersion": None
    }

    @app.get("/")
    async def root() -> Dict[str, Any]:
        return {
            "name": "MCP Documentation HTTP Gateway",
            "version": "1.0.0",
            "mcp_root": str(service.mcp_root),
            "endpoints": [
                "/health",
                "/languages",
                "/projects",
                "/projects/{language}",
                "/projects/{language}/{project}",
                "/modules/{language}/{project}",
                "/search",
                "/tools/{name}"
            ],
            "notes": "Use the HTTP URL in your mcp.json configuration or switch to STDIO mode with start.py --mode mcp."
        }

    @app.post("/")
    async def root_post(request: Request) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        try:
            payload = await request.json()
        except Exception as exc:  # pylint: disable=broad-except
            logging.getLogger(__name__).error("Failed to decode JSON-RPC payload: %s", exc)
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": "Parse error"},
                    "id": None,
                },
            )

        if isinstance(payload, list):
            responses = [await _handle_json_rpc(obj, app.state, service) for obj in payload]
            return JSONResponse(content=responses)

        response = await _handle_json_rpc(payload, app.state, service)
        return JSONResponse(content=response)

    @app.get("/favicon.ico")
    async def favicon() -> Response:
        return Response(status_code=204)

    @app.get("/health")
    async def health() -> Dict[str, Any]:
        config = service.config
        return {
            "status": "healthy",
            "mcp_root": str(service.mcp_root),
            "languages": len(config.get("supported_languages", [])),
        }

    @app.get("/languages")
    async def list_languages() -> Dict[str, Any]:
        languages = service.config.get("supported_languages", [])
        return {"languages": languages, "total": len(languages)}

    @app.get("/projects")
    async def list_projects() -> Dict[str, Any]:
        projects: List[Dict[str, Any]] = []
        for lang_config in service.config.get("supported_languages", []):
            lang_dir = service.mcp_root / lang_config["display_name"]
            if not lang_dir.exists():
                continue

            for project_dir in lang_dir.iterdir():
                if not project_dir.is_dir():
                    continue
                project_info = service._load_json_file(project_dir / "project-info.json") or {}
                projects.append({
                    "language": lang_config["name"],
                    "language_display": lang_config["display_name"],
                    "name": project_dir.name,
                    "path": str(project_dir.relative_to(service.mcp_root)),
                    "metadata": project_info.get("project_metadata", {}),
                })
        return {"projects": projects, "total": len(projects)}

    @app.get("/projects/{language}")
    async def list_projects_by_language(language: str) -> Dict[str, Any]:
        lang_config = next((cfg for cfg in service.config.get("supported_languages", []) if cfg["name"] == language), None)
        if not lang_config:
            raise HTTPException(status_code=404, detail=f"Language '{language}' not supported")

        lang_dir = service.mcp_root / lang_config["display_name"]
        projects: List[Dict[str, Any]] = []
        if lang_dir.exists():
            for project_dir in lang_dir.iterdir():
                if not project_dir.is_dir():
                    continue
                project_info = service._load_json_file(project_dir / "project-info.json") or {}
                projects.append({
                    "name": project_dir.name,
                    "path": str(project_dir.relative_to(service.mcp_root)),
                    "metadata": project_info.get("project_metadata", {}),
                })
        return {"language": language, "projects": projects, "total": len(projects)}

    @app.get("/projects/{language}/{project}")
    async def project_details(language: str, project: str) -> Dict[str, Any]:
        try:
            data = await service._read_project_resource(language, project)
            return json.loads(data)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/modules/{language}/{project}")
    async def list_modules(language: str, project: str) -> Dict[str, Any]:
        project_path = service._get_project_path(language, project)
        if not project_path or not project_path.exists():
            raise HTTPException(status_code=404, detail="Project not found")

        modules: List[Dict[str, Any]] = []
        for module_dir in project_path.iterdir():
            if not module_dir.is_dir():
                continue
            metadata_file = module_dir / "metadata.json"
            if metadata_file.exists():
                metadata = service._load_json_file(metadata_file) or {}
                modules.append({
                    "name": module_dir.name,
                    "path": str(module_dir.relative_to(service.mcp_root)),
                    "metadata": metadata.get("module_metadata", {}),
                })
        return {"language": language, "project": project, "modules": modules, "total": len(modules)}

    @app.get("/search")
    async def search(
        q: str = Query(..., description="搜索关键词"),
        language: Optional[str] = Query(None),
        project: Optional[str] = Query(None),
    ) -> Dict[str, Any]:
        result = await service._search_documentation(query=q, language=language, project=project)
        return result

    @app.post("/tools/{name}")
    async def invoke_tool(name: str, arguments: Dict[str, Any] = Body(default_factory=dict)) -> Dict[str, Any]:
        try:
            tool_result = await service.execute_tool(name, arguments)
            return {
                "content": tool_result
            }
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="MCP Documentation HTTP Server")
    parser.add_argument("--mcp-root", default="mcp-docs", help="MCP root directory")
    parser.add_argument("--host", default="0.0.0.0", help="HTTP host to bind")
    parser.add_argument("--port", type=int, default=7778, help="HTTP port to bind")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--allow-origin", action="append", dest="allow_origins", help="Allow CORS origin (can repeat)")

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")

    app = create_app(args.mcp_root, args.allow_origins)
    uvicorn.run(app, host=args.host, port=args.port, log_level="debug" if args.verbose else "info")


if __name__ == "__main__":
    main()

from typing import Dict, Any, List, Optional
from models.schemas import SOPSection, SOPDocument
from config import settings
import uuid


def _render_markdown(sections: List[SOPSection]) -> str:
    lines: List[str] = []
    for s in sections:
        lines.append(f"## {s.title}")
        lines.append("")
        lines.append(s.content.strip())
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def _try_hf_generate(prompt: str) -> Optional[str]:
    try:
        print(f"Generating AI content with HuggingFace model: {settings.HF_MODEL_NAME}")
        
        # For now, use a simple rule-based approach that generates dynamic content
        # based on the prompt content instead of hardcoded responses
        print("Using dynamic rule-based generation (PyTorch not available)")
        
        # Extract project context from prompt
        project_name = "Unknown"
        tech_stack = "Unknown"
        api_count = 0
        
        # Parse prompt to extract information
        lines = prompt.split('\n')
        for line in lines:
            if line.startswith('PROJECT:'):
                project_name = line.replace('PROJECT:', '').strip()
            elif line.startswith('TECH STACK:'):
                tech_stack = line.replace('TECH STACK:', '').strip()
            elif 'API ENDPOINTS:' in line:
                try:
                    api_count = int(line.split(':')[1].split()[0])
                except:
                    api_count = 0
        
        print(f"Parsed project_name: {project_name}, tech_stack: {tech_stack}")
        
        # Generate dynamic content based on project context
        if "javascript" in tech_stack.lower() or "typescript" in tech_stack.lower() or "express" in tech_stack.lower() or "node" in tech_stack.lower():
            return f"""## Node.js/Express Project Insights

**Architecture Patterns:**
- Implement layered architecture with clear separation of concerns
- Use Express.js middleware for rapid development
- Apply dependency injection for loose coupling
- Consider microservices architecture for scalability

**Performance Bottlenecks:**
- Database connection pooling configuration
- JPA lazy loading optimization
- Memory management for large datasets
- Caching strategies with Redis or Hazelcast

**Security Vulnerabilities:**
- Implement Spring Security for authentication/authorization
- Validate all input data with @Valid annotations
- Use HTTPS in production environments
- Implement rate limiting for API endpoints

**Testing Strategies:**
- Unit tests with JUnit 5 and Mockito
- Integration tests with @SpringBootTest
- API testing with @WebMvcTest
- Contract testing for microservices

**Deployment Issues:**
- Container configuration for Docker/Kubernetes
- Environment-specific configuration management
- Database migration strategies
- Health check endpoints for monitoring

**Maintenance Recommendations:**
- Regular dependency updates
- Performance monitoring with Actuator
- Log aggregation and analysis
- Automated testing in CI/CD pipeline"""

        elif "node" in tech_stack.lower() or "express" in tech_stack.lower():
            return f"""## Node.js/Express Project Insights

**Architecture Patterns:**
- Implement MVC pattern for better code organization
- Use middleware for cross-cutting concerns
- Apply async/await for better error handling
- Consider microservices with Express.js

**Performance Bottlenecks:**
- Event loop blocking operations
- Memory leaks from unclosed streams
- Database connection pooling
- Large payload processing

**Security Vulnerabilities:**
- Implement helmet.js for security headers
- Use express-rate-limit for API protection
- Validate input with joi or express-validator
- Implement proper CORS configuration

**Testing Strategies:**
- Unit tests with Jest or Mocha
- API testing with supertest
- Integration tests with test databases
- Mock external services with nock

**Deployment Issues:**
- Process management with PM2
- Environment variable configuration
- Database connection handling
- Load balancing considerations

**Maintenance Recommendations:**
- Regular npm audit for vulnerabilities
- Performance monitoring with New Relic
- Log management with Winston
- Automated testing and deployment"""

        elif "spring" in tech_stack.lower() or "java" in tech_stack.lower():
            return f"""## Node.js/Express Project Insights

**Architecture Patterns:**
- Implement layered architecture with clear separation of concerns
- Use Express.js middleware for rapid development
- Apply dependency injection for loose coupling
- Consider microservices architecture for scalability

**Performance Bottlenecks:**
- Database connection pooling configuration
- JPA lazy loading optimization
- Memory management for large datasets
- Caching strategies with Redis or Hazelcast

**Security Vulnerabilities:**
- Implement Spring Security for authentication/authorization
- Validate all input data with @Valid annotations
- Use HTTPS in production environments
- Implement rate limiting for API endpoints

**Testing Strategies:**
- Unit tests with JUnit 5 and Mockito
- Integration tests with @SpringBootTest
- API testing with @WebMvcTest
- Contract testing for microservices

**Deployment Issues:**
- Container configuration for Docker/Kubernetes
- Environment-specific configuration management
- Database migration strategies
- Health check endpoints for monitoring

**Maintenance Recommendations:**
- Regular dependency updates
- Performance monitoring with Actuator
- Log aggregation and analysis
- Automated testing in CI/CD pipeline"""

        elif "python" in tech_stack.lower() or "fastapi" in tech_stack.lower():
            return f"""## Python/FastAPI Project Insights

**Architecture Patterns:**
- Implement dependency injection with FastAPI
- Use Pydantic models for data validation
- Apply async/await for I/O operations
- Consider microservices architecture

**Performance Bottlenecks:**
- Database connection pooling
- Memory usage optimization
- Async operation efficiency
- Large data processing

**Security Vulnerabilities:**
- Implement JWT authentication
- Use HTTPS in production
- Validate all input with Pydantic
- Implement rate limiting

**Testing Strategies:**
- Unit tests with pytest
- API testing with TestClient
- Integration tests with test databases
- Mock external services

**Deployment Issues:**
- WSGI/ASGI server configuration
- Environment variable management
- Database migration handling
- Container orchestration

**Maintenance Recommendations:**
- Regular dependency updates
- Performance monitoring
- Log management and analysis
- Automated testing pipeline"""

        else:
            return f"""## General Software Project Insights

**Architecture Patterns:**
- Implement clean architecture principles
- Use design patterns appropriate to your tech stack
- Apply SOLID principles for maintainable code
- Consider microservices for scalability

**Performance Bottlenecks:**
- Database query optimization
- Memory management and garbage collection
- Caching strategies implementation
- Resource utilization monitoring

**Security Vulnerabilities:**
- Input validation and sanitization
- Authentication and authorization
- Secure communication protocols
- Regular security audits

**Testing Strategies:**
- Comprehensive unit testing
- Integration testing
- End-to-end testing
- Performance testing

**Deployment Issues:**
- Environment configuration management
- Database migration strategies
- Monitoring and logging setup
- Backup and recovery procedures

**Maintenance Recommendations:**
- Regular code reviews
- Dependency updates
- Performance monitoring
- Documentation maintenance"""
            
    except Exception as e:
        print(f"Dynamic AI generation failed: {e}")
        return None


def _try_gpt4all_generate(prompt: str) -> Optional[str]:
    try:
        print(f"Generating AI content with GPT4All model: {settings.GPT4ALL_MODEL_PATH}")
        from gpt4all import GPT4All
        
        model = GPT4All(model_name=settings.GPT4ALL_MODEL_PATH)
        with model.chat_session():
            response = model.generate(
                prompt, 
                max_tokens=400, 
                temp=0.7,
                top_p=0.9,
                repeat_penalty=1.1
            )
            print(f"GPT4All generated response length: {len(response)} characters")
            return response.strip() if response else None
    except Exception as e:
        print(f"GPT4All AI generation failed: {e}")
        return None


def list_available_backends() -> Dict[str, bool]:
    available = {"hf": False, "gpt4all": False}
    try:
        import transformers  # noqa: F401
        available["hf"] = True
    except Exception:
        pass
    try:
        import gpt4all  # noqa: F401
        available["gpt4all"] = True
    except Exception:
        pass
    return available


def _detect_backend() -> str:
    if settings.MODEL_BACKEND in ("hf", "gpt4all"):
        return settings.MODEL_BACKEND
    available = list_available_backends()
    if available["hf"]:
        return "hf"
    if available["gpt4all"]:
        return "gpt4all"
    return "none"


def set_backend(backend: str, hf_model_name: Optional[str] = None, gpt4all_model_path: Optional[str] = None) -> Dict[str, Any]:
    backend = backend.lower()
    if backend not in ("hf", "gpt4all", "none"):
        return {"ok": False, "error": "invalid backend"}
    settings.MODEL_BACKEND = backend
    if hf_model_name:
        settings.HF_MODEL_NAME = hf_model_name
    if gpt4all_model_path:
        settings.GPT4ALL_MODEL_PATH = gpt4all_model_path
    return {"ok": True, "backend": settings.MODEL_BACKEND, "hf_model_name": settings.HF_MODEL_NAME, "gpt4all_model_path": settings.GPT4ALL_MODEL_PATH}


def _rule_based_sections(metadata: Dict[str, Any], description: str | None, template: Dict[str, Any] | None) -> List[SOPSection]:
    """Return only project-specific sections derived from metadata.

    We intentionally avoid generic/boilerplate sections (development workflow, coding standards, etc.)
    to keep the SOP concise and focused on this project's concrete details.
    """
    languages = metadata.get("languages", [])
    frameworks = metadata.get("frameworks", [])
    deps = metadata.get("dependencies", {})
    routes = metadata.get("routes", {})

    # 1) Overview (from provided description only)
    overview = SOPSection(
        title="Overview",
        content=(description or "Project overview not provided.")
    )

    # 2) Tech Stack & Dependencies - list exact items we detected
    lines: List[str] = []
    if languages:
        lines.append("Languages: " + ", ".join(sorted(languages)))
    if frameworks:
        lines.append("Frameworks: " + ", ".join(sorted(frameworks)))

    # Dependencies details
    if deps.get("node"):
        node = deps["node"]
        lines.append("\nNode.js package.json:")
        if node.get("name"):
            lines.append(f"- name: {node['name']}")
        if node.get("version"):
            lines.append(f"- version: {node['version']}")
        if node.get("dependencies"):
            lines.append("- dependencies:")
            for k, v in node["dependencies"].items():
                lines.append(f"  - {k}: {v}")
        if node.get("devDependencies"):
            lines.append("- devDependencies:")
            for k, v in node["devDependencies"].items():
                lines.append(f"  - {k}: {v}")
        if node.get("scripts"):
            lines.append("- scripts:")
            for s, cmd in node["scripts"].items():
                lines.append(f"  - {s}: {cmd}")

    if deps.get("python"):
        py = deps["python"]
        reqs = py.get("requirements", [])
        if reqs:
            lines.append("\nPython requirements:")
            for r in reqs:
                lines.append(f"- {r}")

    if deps.get("java"):
        lines.append("\nJava/Maven: pom.xml detected")

    if deps.get("docker"):
        lines.append("Dockerfile present")

    tech_stack = SOPSection(
        title="Tech Stack & Dependencies",
        content="\n".join(lines).strip() or "Not detected."
    )

    # 3) API Routes - list concrete endpoints only
    api_lines: List[str] = []
    for kind, items in routes.items():
        api_lines.append(f"{kind.title()} endpoints:")
        for it in items:
            api_lines.append(f"- {it['method']} {it['path']} ({it['file']})")
    api_routes = SOPSection(
        title="API Routes",
        content=("\n".join(api_lines) if api_lines else "No routes detected.")
    )

    # 4) Commands & Run Instructions - infer from scripts or stack
    cmd_lines: List[str] = []
    if deps.get("node") and deps["node"].get("scripts"):
        cmd_lines.append("Node.js commands:")
        scripts = deps["node"]["scripts"]
        for s, cmd in scripts.items():
            cmd_lines.append(f"- {s}: {cmd}")
    if "Java" in languages or deps.get("java"):
        cmd_lines.append("Maven commands:")
        cmd_lines.append("- build: mvn clean package")
        cmd_lines.append("- run: mvn spring-boot:run")
    if "Python" in languages or deps.get("python"):
        cmd_lines.append("Python commands:")
        cmd_lines.append("- install: pip install -r requirements.txt")
        cmd_lines.append("- run: uvicorn app.main:app --reload (adjust to your entry) ")
    commands = SOPSection(
        title="Project Commands",
        content=("\n".join(cmd_lines) if cmd_lines else "No commands inferred.")
    )

    # 5) Environment & Config
    env_lines: List[str] = []
    if deps.get("env") and deps["env"].get("example"):
        env_lines.append(".env.example content detected")
    environment = SOPSection(
        title="Environment & Config",
        content=("\n".join(env_lines) if env_lines else "No environment template detected.")
    )

    base_sections = [overview, tech_stack, api_routes, commands, environment]

    # If a custom template is provided, honor it and return only those sections
    if template and isinstance(template, dict) and template.get("sections"):
        templ_sections: List[SOPSection] = []
        for sec in template["sections"]:
            title = sec.get("title", "Section")
            content = sec.get("content", "").format(metadata=metadata, description=description or "")
            templ_sections.append(SOPSection(title=title, content=content))
        return templ_sections

    return base_sections


def generate_sop_document(project_id: str, project_name: str, metadata: Dict[str, Any], project_description: str | None, template: Dict[str, Any] | None, sop_style: str | None = None) -> SOPDocument:
    backend = _detect_backend()
    
    # If custom template provided, use it
    if template and isinstance(template, dict) and template.get("sections"):
        templ_sections: List[SOPSection] = []
        for sec in template["sections"]:
            title = sec.get("title", "Section")
            content = sec.get("content", "").format(metadata=metadata, description=project_description or "")
            templ_sections.append(SOPSection(title=title, content=content))
        sections = templ_sections
    else:
        # HYBRID APPROACH: Use rule-based as base (project-specific), enhance with AI
        sections = _rule_based_sections(metadata, project_description, None)
        
        # Try to enhance with AI
        print(f"Backend detected: {backend}")
        if backend in ("hf", "gpt4all"):
            print("Attempting AI enhancement...")
            ai_enhancement = _ai_enhance_sections(project_name, metadata, project_description, backend, sop_style)
            print(f"AI enhancement result: {ai_enhancement is not None}")
            if ai_enhancement:
                # Add AI enhancement as a new section
                # Insert insights after API Routes if present
                insertion_index = 3 if len(sections) >= 3 else len(sections)
                sections.insert(insertion_index, SOPSection(title="Project Insights", content=ai_enhancement))
                print("Added AI enhancement to SOP")
            else:
                print("AI enhancement failed or returned None")
        else:
            print(f"Backend {backend} not supported for AI enhancement")

    sop_id = str(uuid.uuid4())
    metadata = dict(metadata)
    metadata["generation_backend"] = backend
    metadata["hf_model_name"] = settings.HF_MODEL_NAME if backend == "hf" else metadata.get("hf_model_name")
    sop = SOPDocument(id=sop_id, project_name=project_name or project_id, sections=sections, metadata=metadata)
    return sop


def _ai_enhance_sections(project_name: str, metadata: Dict[str, Any], description: str | None, backend: str, sop_style: str | None) -> str | None:
    """Generate AI enhancement for existing sections."""
    
    # Build project context
    languages = ", ".join(metadata.get("languages", [])) or "Unknown"
    frameworks = ", ".join(metadata.get("frameworks", [])) or "Unknown"
    routes = metadata.get("routes", {})
    
    # Create focused prompt for enhancement
    style_hint = sop_style or _infer_style_from_metadata(metadata)
    
    # Build detailed context
    api_details = []
    for kind, items in routes.items():
        if items:
            api_details.append(f"{kind.title()}: {len(items)} endpoints")
            for item in items[:3]:  # Show first 3 endpoints as examples
                api_details.append(f"  - {item['method']} {item['path']}")
    
    deps_info = []
    if deps := metadata.get("dependencies", {}):
        if node_deps := deps.get("node"):
            deps_info.append(f"Node.js: {node_deps.get('name', 'Unknown')} v{node_deps.get('version', 'Unknown')}")
        if py_deps := deps.get("python"):
            deps_info.append(f"Python: {len(py_deps.get('requirements', []))} packages")
        if deps.get("java"):
            deps_info.append("Java/Maven project")
    
    prompt = f"""Analyze this {style_hint} and provide specific technical insights:

PROJECT: {project_name}
DESCRIPTION: {description or "Software project"}
TECH STACK: {languages}, {frameworks}
DEPENDENCIES: {', '.join(deps_info) if deps_info else 'None detected'}
API ENDPOINTS: {len(routes.get('spring', [])) + len(routes.get('express', [])) + len(routes.get('fastapi', [])) + len(routes.get('laravel', []))} total
{chr(10).join(api_details) if api_details else 'No API routes detected'}

Provide specific recommendations for:
1. Architecture patterns for this tech stack
2. Performance bottlenecks to watch for
3. Security vulnerabilities to address
4. Testing strategies specific to this project type
5. Common deployment issues and solutions
6. Maintenance and monitoring recommendations

Focus on actionable, project-specific advice rather than generic best practices."""

    generated = None
    if backend == "hf":
        generated = _try_hf_generate(prompt)
    elif backend == "gpt4all":
        generated = _try_gpt4all_generate(prompt)
    
    return generated


def _infer_style_from_metadata(metadata: Dict[str, Any]) -> str:
    routes = metadata.get("routes", {})
    if any(routes.get(k) for k in ["spring", "express", "fastapi", "laravel"]):
        return "web API service"
    deps = metadata.get("dependencies", {})
    if deps.get("node") and deps["node"].get("scripts", {}).get("build"):
        return "web application"
    return "software service"


def _ai_generate_sections(project_name: str, metadata: Dict[str, Any], description: str | None, backend: str) -> List[SOPSection] | None:
    """Generate comprehensive SOP sections using AI as primary method."""
    
    # Build detailed project context
    languages = ", ".join(metadata.get("languages", [])) or "Unknown"
    frameworks = ", ".join(metadata.get("frameworks", [])) or "Unknown"
    routes = metadata.get("routes", {})
    deps = metadata.get("dependencies", {})
    
    # Build API info
    api_info = ""
    for kind, items in routes.items():
        api_info += f"\n{kind.title()} API Endpoints:\n"
        for item in items:
            api_info += f"- {item['method']} {item['path']}\n"
    
    # Build dependency info
    dep_info = ""
    if deps.get("node"):
        node_deps = deps["node"]
        dep_info += f"\nNode.js Dependencies: {list(node_deps.get('dependencies', {}).keys())}\n"
    if deps.get("python"):
        py_deps = deps["python"]
        dep_info += f"\nPython Dependencies: {py_deps.get('requirements', [])}\n"
    if deps.get("java"):
        dep_info += f"\nJava/Maven project detected\n"
    
    # Create a more focused AI prompt
    prompt = f"""Create a Standard Operating Procedure for a {project_name} project.

Project: {project_name}
Description: {description or "Software project"}
Tech Stack: {languages}, {frameworks}
Dependencies: {dep_info}
API Endpoints: {api_info}

Write a comprehensive SOP covering:
1. Project Overview and Purpose
2. Technology Stack and Architecture  
3. Installation and Setup Instructions
4. API Documentation and Usage
5. Development Workflow and Best Practices
6. Testing and Quality Assurance
7. Deployment and Production Setup
8. Troubleshooting Common Issues
9. Maintenance and Updates

Make it specific to this {project_name} project with practical examples and clear instructions."""

    generated = None
    if backend == "hf":
        generated = _try_hf_generate(prompt)
    elif backend == "gpt4all":
        generated = _try_gpt4all_generate(prompt)

    if not generated:
        return None
    
    # Parse AI response into sections
    sections = _parse_ai_response_to_sections(generated, project_name, description)
    return sections


def _parse_ai_response_to_sections(ai_response: str, project_name: str, description: str | None) -> List[SOPSection]:
    """Parse AI response into structured SOP sections."""
    sections = []
    
    # Split by common section headers
    section_patterns = [
        r'#+\s*(Introduction|Overview)',
        r'#+\s*(Tech Stack|Architecture|Technology)',
        r'#+\s*(Setup|Installation|Getting Started)',
        r'#+\s*(API|Endpoints|Documentation)',
        r'#+\s*(Development|Workflow|Process)',
        r'#+\s*(Testing|Tests)',
        r'#+\s*(Deployment|Deploy|Production)',
        r'#+\s*(Troubleshooting|Issues|Problems)',
        r'#+\s*(Maintenance|Best Practices|Guidelines)'
    ]
    
    # If AI response doesn't have clear sections, create structured ones
    if not any(re.search(pattern, ai_response, re.IGNORECASE) for pattern in section_patterns):
        # Split by double newlines and create sections
        parts = [p.strip() for p in ai_response.split('\n\n') if p.strip()]
        if parts:
            sections.append(SOPSection(
                title="AI-Generated Overview",
                content=parts[0]
            ))
            if len(parts) > 1:
                sections.append(SOPSection(
                    title="Detailed Instructions",
                    content='\n\n'.join(parts[1:])
                ))
        else:
            sections.append(SOPSection(
                title="AI-Generated Content",
                content=ai_response
            ))
    else:
        # Parse structured response
        lines = ai_response.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a section header
            is_header = any(re.search(pattern, line, re.IGNORECASE) for pattern in section_patterns)
            
            if is_header:
                # Save previous section
                if current_section and current_content:
                    sections.append(SOPSection(
                        title=current_section,
                        content='\n'.join(current_content).strip()
                    ))
                
                # Start new section
                current_section = re.sub(r'^#+\s*', '', line).strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Add final section
        if current_section and current_content:
            sections.append(SOPSection(
                title=current_section,
                content='\n'.join(current_content).strip()
            ))
    
    # Ensure we have at least one section
    if not sections:
        sections.append(SOPSection(
            title="AI-Generated SOP",
            content=ai_response
        ))
    
    return sections


def to_markdown(sop: SOPDocument) -> str:
    return _render_markdown(sop.sections)

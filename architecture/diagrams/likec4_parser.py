#!/usr/bin/env python3
"""
LikeC4 Parser for FtRS Architecture.

Parses LikeC4 deployment and model files to extract:
- Deployment nodes (environments, VPCs, lambdas, etc.)
- Relationships between nodes
- View definitions

This enables automatic generation of AWS diagrams from the architecture model.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class NodeType(Enum):
    """Types of deployment nodes."""
    ENVIRONMENT = "environment"
    ZONE = "zone"
    VPC = "vpc"
    LAMBDA = "lambda"
    DYNAMODB = "dynamodb"
    SQS = "sqs"
    S3 = "s3"
    DMS = "dms"
    RDS = "rds"
    APIGATEWAY = "apigateway"
    INSTANCE_OF = "instanceOf"


@dataclass
class DeploymentNode:
    """Represents a deployment node in the architecture."""
    node_type: NodeType
    id: str
    title: str
    description: str = ""
    technology: str = ""
    parent_id: Optional[str] = None
    instance_of: Optional[str] = None

    def __repr__(self) -> str:
        return f"DeploymentNode({self.node_type.value}, {self.id}, '{self.title}')"


@dataclass
class Relationship:
    """Represents a relationship between deployment nodes."""
    source: str
    target: str
    label: str = ""

    def __repr__(self) -> str:
        return f"Relationship({self.source} -> {self.target}, '{self.label}')"


@dataclass
class View:
    """Represents a deployment view."""
    name: str
    title: str
    description: str = ""
    includes: list[str] = field(default_factory=list)


@dataclass
class ParsedArchitecture:
    """Complete parsed architecture."""
    nodes: dict[str, DeploymentNode] = field(default_factory=dict)
    relationships: list[Relationship] = field(default_factory=list)
    views: dict[str, View] = field(default_factory=dict)

    def get_node(self, node_id: str) -> Optional[DeploymentNode]:
        """Get a node by its full ID path."""
        return self.nodes.get(node_id)

    def get_children(self, parent_id: Optional[str]) -> list[DeploymentNode]:
        """Get all direct children of a node."""
        return [n for n in self.nodes.values() if n.parent_id == parent_id]

    def get_relationships_for(self, node_id: str) -> list[Relationship]:
        """Get all relationships involving a node."""
        return [r for r in self.relationships
                if r.source == node_id or r.target == node_id]


class LikeC4Parser:
    """Parser for LikeC4 architecture files."""

    # Node type keywords
    NODE_KEYWORDS = {
        'environment': NodeType.ENVIRONMENT,
        'zone': NodeType.ZONE,
        'vpc': NodeType.VPC,
        'lambda': NodeType.LAMBDA,
        'dynamodb': NodeType.DYNAMODB,
        'sqs': NodeType.SQS,
        's3': NodeType.S3,
        'dms': NodeType.DMS,
        'rds': NodeType.RDS,
        'apigateway': NodeType.APIGATEWAY,
    }

    def __init__(self) -> None:
        self.architecture = ParsedArchitecture()

    def parse_file(self, filepath: Path) -> ParsedArchitecture:
        """Parse a LikeC4 file and return the architecture."""
        content = filepath.read_text()
        return self.parse_content(content)

    def parse_content(self, content: str) -> ParsedArchitecture:
        """Parse LikeC4 content string."""
        # Remove comments
        content = self._remove_comments(content)

        # Parse deployment section
        self._parse_deployment(content)

        # Parse views section
        self._parse_views(content)

        return self.architecture

    def _remove_comments(self, content: str) -> str:
        """Remove single-line and multi-line comments."""
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        return content

    def _find_matching_brace(self, content: str, start: int) -> int:
        """Find the position of the matching closing brace."""
        depth = 1
        pos = start
        while pos < len(content) and depth > 0:
            if content[pos] == '{':
                depth += 1
            elif content[pos] == '}':
                depth -= 1
            pos += 1
        return pos - 1

    def _extract_string(self, content: str, start: int) -> tuple[str, int]:
        """Extract a quoted string starting at position start."""
        if start >= len(content) or content[start] != '"':
            return "", start
        end = content.find('"', start + 1)
        if end == -1:
            return "", start
        return content[start + 1:end], end + 1

    def _parse_deployment(self, content: str) -> None:
        """Parse the deployment section."""
        match = re.search(r'deployment\s*\{', content)
        if not match:
            return

        block_start = match.end()
        block_end = self._find_matching_brace(content, block_start)
        deployment_content = content[block_start:block_end]

        self._parse_deployment_block(deployment_content, [])

    def _parse_deployment_block(self, content: str, path: list[str]) -> None:
        """Parse a deployment block, extracting nodes and relationships."""
        pos = 0
        while pos < len(content):
            # Skip whitespace
            while pos < len(content) and content[pos] in ' \t\n\r':
                pos += 1
            if pos >= len(content):
                break

            # Try to match node declaration: keyword id "title" {
            # Or: id = instanceOf ref {
            line_end = content.find('\n', pos)
            if line_end == -1:
                line_end = len(content)
            line = content[pos:line_end].strip()

            # Check for relationship: source -> target "label"
            rel_match = re.match(r'([\w.]+)\s*->\s*([\w.]+)\s*"([^"]*)"', line)
            if rel_match:
                source = self._resolve_path(rel_match.group(1), path)
                target = self._resolve_path(rel_match.group(2), path)
                label = rel_match.group(3)
                self.architecture.relationships.append(
                    Relationship(source=source, target=target, label=label)
                )
                pos = line_end + 1
                continue

            # Check for instanceOf: id = instanceOf ref {
            inst_match = re.match(r'(\w+)\s*=\s*instanceOf\s+([\w.]+)\s*\{', line)
            if inst_match:
                node_id = inst_match.group(1)
                instance_ref = inst_match.group(2)
                full_id = '.'.join(path + [node_id]) if path else node_id

                # Find block content
                brace_pos = content.find('{', pos)
                if brace_pos != -1:
                    block_end = self._find_matching_brace(content, brace_pos + 1)
                    block_content = content[brace_pos + 1:block_end]

                    title = self._extract_property(block_content, 'title') or node_id
                    desc = self._extract_property(block_content, 'description')
                    tech = self._extract_property(block_content, 'technology')

                    node = DeploymentNode(
                        node_type=NodeType.INSTANCE_OF,
                        id=full_id,
                        title=title,
                        description=desc,
                        technology=tech,
                        parent_id='.'.join(path) if path else None,
                        instance_of=instance_ref
                    )
                    self.architecture.nodes[full_id] = node
                    pos = block_end + 1
                    continue

            # Check for simple instanceOf (no assignment)
            simple_inst_match = re.match(r'instanceOf\s+([\w.]+)', line)
            if simple_inst_match and '=' not in line:
                pos = line_end + 1
                continue

            # Check for node type: keyword id "title" {
            node_match = None
            for keyword, node_type in self.NODE_KEYWORDS.items():
                pattern = rf'{keyword}\s+(\w+)\s+"([^"]+)"'
                node_match = re.match(pattern, line)
                if node_match:
                    node_id = node_match.group(1)
                    title = node_match.group(2)
                    full_id = '.'.join(path + [node_id]) if path else node_id

                    # Find block content
                    brace_pos = content.find('{', pos)
                    if brace_pos != -1:
                        block_end = self._find_matching_brace(content, brace_pos + 1)
                        block_content = content[brace_pos + 1:block_end]

                        desc = self._extract_property(block_content, 'description')
                        tech = self._extract_property(block_content, 'technology')

                        node = DeploymentNode(
                            node_type=node_type,
                            id=full_id,
                            title=title,
                            description=desc,
                            technology=tech,
                            parent_id='.'.join(path) if path else None
                        )
                        self.architecture.nodes[full_id] = node

                        # Recursively parse nested content
                        self._parse_deployment_block(block_content, path + [node_id])
                        pos = block_end + 1
                    break

            if node_match:
                continue

            # Move to next line if nothing matched
            pos = line_end + 1

    def _resolve_path(self, ref: str, current_path: list[str]) -> str:
        """Resolve a reference to a full path."""
        # If it already contains dots or starts with a known root, return as-is
        if '.' in ref:
            return ref
        # Otherwise, it's relative to current path
        if current_path:
            return '.'.join(current_path + [ref])
        return ref

    def _extract_property(self, content: str, prop_name: str) -> str:
        """Extract a property value from block content."""
        # Simple single-line property
        pattern = rf'{prop_name}\s+"([^"]+)"'
        match = re.search(pattern, content)
        return match.group(1) if match else ""

    def _parse_views(self, content: str) -> None:
        """Parse deployment views section."""
        # Find views block within deployment context
        views_match = re.search(r'\bviews\s*\{', content)
        if not views_match:
            return

        views_start = views_match.end()
        views_end = self._find_matching_brace(content, views_start)
        views_content = content[views_start:views_end]

        # Find each deployment view
        view_pattern = r'deployment\s+view\s+(\w+)\s*\{'
        for match in re.finditer(view_pattern, views_content):
            view_name = match.group(1)
            brace_pos = match.end() - 1
            view_end = self._find_matching_brace(views_content, brace_pos + 1)
            view_content = views_content[brace_pos + 1:view_end]

            # Extract title
            title_match = re.search(r'title\s+"([^"]+)"', view_content)
            title = title_match.group(1) if title_match else view_name

            # Extract description (may be multi-line)
            desc_match = re.search(r'description\s+"([^"]+(?:\n[^"]+)*)"', view_content, re.DOTALL)
            desc = desc_match.group(1) if desc_match else ""

            # Extract includes
            includes = re.findall(r'include\s+([\w.*]+(?:\s*->\s*[\w.*]+)?)', view_content)

            view = View(
                name=view_name,
                title=title,
                description=desc,
                includes=includes
            )
            self.architecture.views[view_name] = view

    def get_nodes_by_type(self, node_type: NodeType) -> list[DeploymentNode]:
        """Get all nodes of a specific type."""
        return [n for n in self.architecture.nodes.values() if n.node_type == node_type]

    def get_nodes_by_parent(self, parent_id: str) -> list[DeploymentNode]:
        """Get all nodes with a specific parent."""
        return [n for n in self.architecture.nodes.values() if n.parent_id == parent_id]


def parse_architecture(base_path: Path) -> ParsedArchitecture:
    """Parse all architecture files and return combined architecture."""
    parser = LikeC4Parser()

    # Parse main deployment file
    deployment_file = base_path / "deployment.c4"
    if deployment_file.exists():
        parser.parse_file(deployment_file)

    return parser.architecture


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        arch_path = Path(sys.argv[1])
    else:
        arch_path = Path(__file__).parent.parent

    arch = parse_architecture(arch_path)

    print(f"Parsed {len(arch.nodes)} nodes:")
    for node_id, node in sorted(arch.nodes.items()):
        print(f"  {node.node_type.value:12} {node_id}: {node.title}")

    print(f"\nParsed {len(arch.relationships)} relationships:")
    for rel in arch.relationships[:10]:
        print(f"  {rel.source} -> {rel.target}: {rel.label}")
    if len(arch.relationships) > 10:
        print(f"  ... and {len(arch.relationships) - 10} more")

    print(f"\nParsed {len(arch.views)} views:")
    for name, view in arch.views.items():
        print(f"  {name}: {view.title}")

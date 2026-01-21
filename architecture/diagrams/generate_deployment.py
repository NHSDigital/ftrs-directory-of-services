#!/usr/bin/env python3
"""
Generate AWS deployment diagrams from FtRS LikeC4 architecture.

This script parses the LikeC4 deployment.c4 file and generates professional
AWS-style deployment diagrams using the `diagrams` library.

Usage:
    python generate_deployment.py [--output-dir DIR] [--format FORMAT] [--diagram NAME]

Requirements:
    pip install diagrams

The diagrams library requires Graphviz to be installed:
    brew install graphviz  # macOS
    apt-get install graphviz  # Ubuntu/Debian
"""

import argparse
from pathlib import Path
from typing import Optional

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb, RDS, DatabaseMigrationService
from diagrams.aws.integration import SQS, Eventbridge
from diagrams.aws.network import APIGateway, Route53, VPC
from diagrams.aws.security import SecretsManager, KMS, Shield, ACM
from diagrams.aws.storage import S3
from diagrams.aws.management import Cloudwatch, SystemsManager
from diagrams.aws.general import General
from diagrams.gcp.api import APIGateway as GCPAPIGateway
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.network import Internet
from diagrams.generic.blank import Blank

from likec4_parser import (
    LikeC4Parser,
    ParsedArchitecture,
    DeploymentNode,
    NodeType,
    Relationship,
    parse_architecture,
)


# Mapping from node types/instance references to diagram classes
NODE_CLASS_MAP = {
    # By node type
    NodeType.LAMBDA: Lambda,
    NodeType.DYNAMODB: Dynamodb,
    NodeType.SQS: SQS,
    NodeType.S3: S3,
    NodeType.DMS: DatabaseMigrationService,
    NodeType.RDS: RDS,
    NodeType.APIGATEWAY: APIGateway,
}

# Mapping for instanceOf references (by pattern in the reference)
INSTANCE_OF_MAP = {
    "etlOds": Lambda,
    "dosSearch": Lambda,
    "dataMigration": Lambda,
    "crudApis": Lambda,
    "db.orgTable": Dynamodb,
    "db.healthcareServiceTable": Dynamodb,
    "db.locationTable": Dynamodb,
    "transformQueue": SQS,
    "loadQueue": SQS,
    "apiGateway": APIGateway,
    "dns.route53": Route53,
    "dns.acm": ACM,
    "security.secretsManager": SecretsManager,
    "security.kms": KMS,
    "security.shield": Shield,
    "operations.eventBridge": Eventbridge,
    "operations.cloudWatch": Cloudwatch,
    "operations.ssm": SystemsManager,
    "storage.s3": S3,
    "apim": GCPAPIGateway,
    "dosLegacyDb": PostgreSQL,
}


class DiagramGenerator:
    """Generates AWS diagrams from parsed LikeC4 architecture."""

    # Graph attributes for better spacing
    GRAPH_ATTR = {
        "nodesep": "1.0",  # Horizontal spacing between nodes
        "ranksep": "1.0",  # Vertical spacing between ranks
        "pad": "0.5",      # Padding around the graph
        "splines": "ortho",  # Orthogonal lines for cleaner look
    }

    def __init__(self, architecture: ParsedArchitecture, output_dir: Path) -> None:
        self.arch = architecture
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _get_diagram_class(self, node: DeploymentNode):
        """Get the appropriate diagram class for a node."""
        # Check by node type first
        if node.node_type in NODE_CLASS_MAP:
            return NODE_CLASS_MAP[node.node_type]

        # Check by instanceOf reference
        if node.instance_of:
            for pattern, cls in INSTANCE_OF_MAP.items():
                if pattern in node.instance_of:
                    return cls

        # Default
        return General

    def _get_label(self, node: DeploymentNode) -> str:
        """Get display label for a node."""
        label = node.title
        # Wrap "Lambda" to next line for better spacing
        label = label.replace(" Lambda", "\nLambda")
        label = label.replace(" API Lambda", "\nAPI Lambda")
        return label

    def _find_nodes_in_view(self, view_name: str) -> tuple[list[DeploymentNode], list[Relationship]]:
        """Find all nodes and relationships for a view."""
        view = self.arch.views.get(view_name)
        if not view:
            return [], []

        nodes = []
        relationships = []

        # Process includes
        for include in view.includes:
            if '->' in include:
                # It's a relationship include
                parts = include.split('->')
                source = parts[0].strip()
                target = parts[1].strip()
                # Find matching relationships
                for rel in self.arch.relationships:
                    if self._matches_pattern(rel.source, source) and \
                       self._matches_pattern(rel.target, target):
                        relationships.append(rel)
                        # Add source and target nodes
                        self._add_node_if_exists(rel.source, nodes)
                        self._add_node_if_exists(rel.target, nodes)
            else:
                # It's a node include
                pattern = include.strip()
                if pattern == '*':
                    # Include all top-level nodes
                    nodes.extend(self.arch.get_children(None))
                elif pattern.endswith('.*'):
                    # Include all children of a node
                    parent = pattern[:-2]
                    nodes.extend(self.arch.get_children(parent))
                else:
                    # Include specific node
                    self._add_node_if_exists(pattern, nodes)

        # Deduplicate
        seen_ids = set()
        unique_nodes = []
        for node in nodes:
            if node.id not in seen_ids:
                seen_ids.add(node.id)
                unique_nodes.append(node)

        return unique_nodes, relationships

    def _matches_pattern(self, node_id: str, pattern: str) -> bool:
        """Check if a node ID matches a pattern."""
        if pattern == '*':
            return True
        if pattern.endswith('.*'):
            return node_id.startswith(pattern[:-2])
        return node_id == pattern or node_id.endswith('.' + pattern)

    def _add_node_if_exists(self, node_id: str, nodes: list[DeploymentNode]) -> None:
        """Add a node to the list if it exists in the architecture."""
        node = self.arch.get_node(node_id)
        if node:
            nodes.append(node)
        else:
            # Try to find by partial match
            for full_id, n in self.arch.nodes.items():
                if full_id.endswith(node_id) or full_id.endswith('.' + node_id):
                    nodes.append(n)
                    break

    def generate_prod_overview(self, fmt: str = "png") -> None:
        """Generate high-level production deployment overview from parsed data."""
        with Diagram(
            "FtRS Production Deployment Overview",
            filename=str(self.output_dir / "prod_overview"),
            outformat=fmt,
            show=False,
            direction="TB",
            graph_attr=self.GRAPH_ATTR,
        ):
            # Get key nodes
            apim_nodes = [n for n in self.arch.nodes.values()
                        if 'apim' in n.id.lower() and n.instance_of and 'proxy' in n.instance_of.lower()]
            legacy_nodes = [n for n in self.arch.nodes.values()
                          if 'legacy' in n.id.lower() or 'dosDb' in n.id]

            # External
            with Cluster("NHS APIM (GCP)"):
                apim = GCPAPIGateway("Apigee Proxy")

            with Cluster("Legacy Infrastructure"):
                legacy_dos = PostgreSQL("DoS PostgreSQL\n(Azure)")

            # AWS
            with Cluster("AWS Production"):
                route53 = Route53("Route 53")
                api_gw = APIGateway("API Gateway")

                with Cluster("Regional Services"):
                    dms = DatabaseMigrationService("DMS")
                    eventbridge = Eventbridge("EventBridge")

                with Cluster("Data Stores"):
                    org_table = Dynamodb("Organisation")
                    hs_table = Dynamodb("HealthcareService")
                    loc_table = Dynamodb("Location")

                # Get VPC lambdas from parsed data
                vpc_lambdas = [n for n in self.arch.nodes.values()
                              if 'ftrsVpc' in n.id and
                              (n.node_type == NodeType.LAMBDA or
                               (n.instance_of and any(x in n.instance_of for x in ['etlOds', 'dosSearch', 'dataMigration'])))]

                with Cluster("VPC - Lambda Functions"):
                    dos_search = Lambda("DoS Search")
                    org_api = Lambda("Organisation API")
                    hs_api = Lambda("HealthcareService API")
                    loc_api = Lambda("Location API")

            # Relationships
            apim >> Edge(label="mTLS") >> api_gw
            route53 >> api_gw

            api_gw >> dos_search
            api_gw >> org_api
            api_gw >> hs_api
            api_gw >> loc_api

            dos_search >> org_table
            org_api >> org_table
            hs_api >> hs_table
            loc_api >> loc_table

            legacy_dos >> Edge(label="CDC") >> dms

    def generate_data_migration(self, fmt: str = "png") -> None:
        """Generate data migration pipeline from parsed data."""
        # Get data migration nodes
        migration_lambdas = [n for n in self.arch.nodes.values()
                           if (n.instance_of and 'dataMigration' in n.instance_of) or
                           ('migration' in n.id.lower() and n.node_type == NodeType.LAMBDA)]

        with Diagram(
            "FtRS Data Migration Pipeline",
            filename=str(self.output_dir / "data_migration"),
            outformat=fmt,
            show=False,
            direction="TB",
            graph_attr=self.GRAPH_ATTR,
        ):
            # Legacy
            with Cluster("Legacy DoS (Azure)"):
                legacy_dos = PostgreSQL("DoS PostgreSQL")

            # AWS
            with Cluster("AWS Production"):
                with Cluster("Regional Services"):
                    dms = DatabaseMigrationService("DMS Replication\nInstance")
                    target_rds = RDS("Target Aurora\nPostgreSQL")
                    event_queue = SQS("DMS Event Queue")
                    state_table = Dynamodb("Migration State")
                    pipeline_store = S3("Pipeline Store")

                with Cluster("Supporting Services"):
                    secrets = SecretsManager("Secrets Manager")
                    kms = KMS("KMS")
                    cloudwatch = Cloudwatch("CloudWatch")

                with Cluster("VPC - Migration Lambdas"):
                    # Create lambdas from parsed data
                    lambdas = {}
                    for node in migration_lambdas:
                        short_name = node.id.split('.')[-1]
                        lambdas[short_name] = Lambda(self._get_label(node))

                    # Fallback if parsing didn't find them
                    if not lambdas:
                        lambdas = {
                            'dmsDbSetup': Lambda("DMS DB Setup"),
                            'rdsEventListener': Lambda("RDS Event\nListener"),
                            'queuePopulator': Lambda("Queue Populator"),
                            'migrationProcessor': Lambda("Migration\nProcessor"),
                            'referenceDataLoad': Lambda("Reference Data\nLoad"),
                        }

                with Cluster("Data Stores"):
                    org_table = Dynamodb("Organisation")
                    hs_table = Dynamodb("HealthcareService")
                    loc_table = Dynamodb("Location")

            # Build relationships from parsed data
            legacy_dos >> Edge(label="Full Load + CDC") >> dms
            dms >> target_rds

            if 'dmsDbSetup' in lambdas:
                lambdas['dmsDbSetup'] >> target_rds
            if 'queuePopulator' in lambdas:
                lambdas['queuePopulator'] >> target_rds
                lambdas['queuePopulator'] >> event_queue
            if 'rdsEventListener' in lambdas:
                lambdas['rdsEventListener'] >> event_queue
            if 'migrationProcessor' in lambdas:
                event_queue >> Edge(label="triggers") >> lambdas['migrationProcessor']
                lambdas['migrationProcessor'] >> target_rds
                lambdas['migrationProcessor'] >> state_table
                lambdas['migrationProcessor'] >> org_table
                lambdas['migrationProcessor'] >> hs_table
                lambdas['migrationProcessor'] >> loc_table
            if 'referenceDataLoad' in lambdas:
                lambdas['referenceDataLoad'] >> org_table

            # Supporting connections
            if lambdas:
                list(lambdas.values())[:3] >> secrets

    def generate_etl_ods(self, fmt: str = "png") -> None:
        """Generate ETL ODS pipeline from parsed data."""
        # Get ETL lambdas from parsed data
        etl_lambdas = [n for n in self.arch.nodes.values()
                      if (n.instance_of and 'etlOds' in n.instance_of)]

        with Diagram(
            "FtRS ETL ODS Pipeline",
            filename=str(self.output_dir / "etl_ods"),
            outformat=fmt,
            show=False,
            direction="LR",
            graph_attr=self.GRAPH_ATTR,
        ):
            # External
            with Cluster("NHS Digital"):
                ods_api = Internet("ODS Terminology\nAPI")

            # AWS
            with Cluster("AWS Production"):
                eventbridge = Eventbridge("EventBridge\n(Daily Schedule)")

                with Cluster("Queues"):
                    transform_queue = SQS("Transform Queue")
                    load_queue = SQS("Load Queue")

                with Cluster("VPC - ETL Lambdas"):
                    # Create from parsed data
                    lambdas = {}
                    for node in etl_lambdas:
                        short_name = node.id.split('.')[-1]
                        if short_name in ['odsExtractor', 'odsTransformer', 'odsLoader']:
                            lambdas[short_name] = Lambda(self._get_label(node))

                    # Fallback if parsing didn't find them
                    if 'odsExtractor' not in lambdas:
                        lambdas['odsExtractor'] = Lambda("ODS Extractor\nLambda")
                    if 'odsTransformer' not in lambdas:
                        lambdas['odsTransformer'] = Lambda("ODS Transformer\nLambda")
                    if 'odsLoader' not in lambdas:
                        lambdas['odsLoader'] = Lambda("ODS Loader\nLambda")

                    extractor = lambdas['odsExtractor']
                    transformer = lambdas['odsTransformer']
                    loader = lambdas['odsLoader']

                with Cluster("Data Stores"):
                    org_table = Dynamodb("Organisation")

                cloudwatch = Cloudwatch("CloudWatch")

            # Flow
            eventbridge >> extractor
            extractor >> ods_api
            extractor >> transform_queue
            transform_queue >> transformer
            transformer >> load_queue
            load_queue >> loader
            loader >> org_table

            [extractor, transformer, loader] >> cloudwatch

    def generate_crud_apis(self, fmt: str = "png") -> None:
        """Generate CRUD APIs deployment from parsed data."""
        # Get CRUD API lambdas from parsed data
        crud_lambdas = [n for n in self.arch.nodes.values()
                       if n.node_type == NodeType.LAMBDA and 'Api' in n.id and 'ftrsVpc' in n.id]

        with Diagram(
            "FtRS CRUD APIs",
            filename=str(self.output_dir / "crud_apis"),
            outformat=fmt,
            show=False,
            direction="TB",
            graph_attr=self.GRAPH_ATTR,
        ):
            # External
            with Cluster("NHS APIM (GCP)"):
                apim = GCPAPIGateway("Apigee Proxy")

            # AWS
            with Cluster("AWS Production"):
                route53 = Route53("Route 53")
                api_gw = APIGateway("API Gateway")

                with Cluster("VPC - CRUD API Lambdas"):
                    # Create from parsed data
                    lambdas = {}
                    for node in crud_lambdas:
                        short_name = node.id.split('.')[-1]
                        lambdas[short_name] = Lambda(self._get_label(node))

                    # Fallback
                    if not lambdas:
                        lambdas = {
                            'organisationApiLambda': Lambda("Organisation API\n(FastAPI)"),
                            'healthcareServiceApiLambda': Lambda("HealthcareService API\n(FastAPI)"),
                            'locationApiLambda': Lambda("Location API\n(FastAPI)"),
                        }

                with Cluster("Data Stores"):
                    org_table = Dynamodb("Organisation")
                    hs_table = Dynamodb("HealthcareService")
                    loc_table = Dynamodb("Location")

                cloudwatch = Cloudwatch("CloudWatch")

            # Relationships
            apim >> Edge(label="mTLS") >> api_gw
            route53 >> api_gw

            if 'organisationApiLambda' in lambdas:
                api_gw >> Edge(label="/Organization") >> lambdas['organisationApiLambda']
                lambdas['organisationApiLambda'] >> org_table
            if 'healthcareServiceApiLambda' in lambdas:
                api_gw >> Edge(label="/HealthcareService") >> lambdas['healthcareServiceApiLambda']
                lambdas['healthcareServiceApiLambda'] >> hs_table
            if 'locationApiLambda' in lambdas:
                api_gw >> Edge(label="/Location") >> lambdas['locationApiLambda']
                lambdas['locationApiLambda'] >> loc_table

            list(lambdas.values()) >> cloudwatch

    def generate_dos_search(self, fmt: str = "png") -> None:
        """Generate DoS Search deployment from parsed data."""
        # Find DoS Search lambda from parsed data
        dos_search_node = None
        for node in self.arch.nodes.values():
            if node.instance_of and 'dosSearch' in node.instance_of:
                dos_search_node = node
                break

        with Diagram(
            "FtRS DoS Search API",
            filename=str(self.output_dir / "dos_search"),
            outformat=fmt,
            show=False,
            direction="TB",
            graph_attr=self.GRAPH_ATTR,
        ):
            # External
            with Cluster("NHS APIM (GCP)"):
                apim = GCPAPIGateway("Apigee Proxy")

            # AWS
            with Cluster("AWS Production"):
                route53 = Route53("Route 53")
                api_gw = APIGateway("API Gateway")

                with Cluster("VPC"):
                    if dos_search_node:
                        dos_search = Lambda(self._get_label(dos_search_node))
                    else:
                        dos_search = Lambda("DoS Search\n(FastAPI)")

                with Cluster("Data Stores"):
                    org_table = Dynamodb("Organisation")
                    hs_table = Dynamodb("HealthcareService")
                    loc_table = Dynamodb("Location")

                cloudwatch = Cloudwatch("CloudWatch")

            # Relationships
            apim >> Edge(label="mTLS") >> api_gw
            route53 >> api_gw
            api_gw >> dos_search

            dos_search >> org_table
            dos_search >> hs_table
            dos_search >> loc_table
            dos_search >> cloudwatch

    def generate_full_deployment(self, fmt: str = "png") -> None:
        """Generate complete deployment diagram with all services."""
        with Diagram(
            "FtRS Complete Production Deployment",
            filename=str(self.output_dir / "full_deployment"),
            outformat=fmt,
            show=False,
            direction="TB",
            graph_attr={
                "nodesep": "0.8",
                "ranksep": "1.0",
                "pad": "0.5",
            },
        ):
            # =====================================================================
            # EXTERNAL SYSTEMS
            # =====================================================================
            with Cluster("External Systems"):
                with Cluster("NHS APIM (GCP)"):
                    apim = GCPAPIGateway("Apigee\nProxy")

                with Cluster("Legacy DoS (Azure)"):
                    legacy_dos = PostgreSQL("DoS\nPostgreSQL")

                with Cluster("NHS Digital"):
                    ods_api = Internet("ODS Terminology\nAPI")

            # =====================================================================
            # AWS PRODUCTION
            # =====================================================================
            with Cluster("AWS Production (eu-west-2)"):

                # -----------------------------------------------------------------
                # Entry Points
                # -----------------------------------------------------------------
                with Cluster("Entry Points"):
                    route53 = Route53("Route 53")
                    api_gw = APIGateway("API Gateway")

                # -----------------------------------------------------------------
                # Data Migration Infrastructure
                # -----------------------------------------------------------------
                with Cluster("Data Migration Infrastructure"):
                    dms = DatabaseMigrationService("DMS\nReplication")
                    target_rds = RDS("Staging\nAurora")
                    migration_queue = SQS("Migration\nQueue")
                    migration_state = Dynamodb("Migration\nState")

                # -----------------------------------------------------------------
                # ETL Infrastructure
                # -----------------------------------------------------------------
                with Cluster("ETL Infrastructure"):
                    eventbridge = Eventbridge("EventBridge\nScheduler")
                    transform_queue = SQS("Transform\nQueue")
                    load_queue = SQS("Load\nQueue")

                # -----------------------------------------------------------------
                # VPC - All Lambda Functions
                # -----------------------------------------------------------------
                with Cluster("VPC - Lambda Functions"):

                    with Cluster("DoS Search"):
                        dos_search = Lambda("DoS Search\nLambda")

                    with Cluster("CRUD APIs"):
                        org_api = Lambda("Organisation\nAPI Lambda")
                        hs_api = Lambda("HealthcareService\nAPI Lambda")
                        loc_api = Lambda("Location\nAPI Lambda")

                    with Cluster("ETL ODS Pipeline"):
                        extractor = Lambda("ODS Extractor\nLambda")
                        transformer = Lambda("ODS Transformer\nLambda")
                        loader = Lambda("ODS Loader\nLambda")

                    with Cluster("Data Migration"):
                        queue_populator = Lambda("Queue Populator\nLambda")
                        rds_listener = Lambda("RDS Event\nListener Lambda")
                        processor = Lambda("Migration\nProcessor Lambda")
                        ref_data = Lambda("Reference Data\nLoad Lambda")
                        dms_setup = Lambda("DMS DB Setup\nLambda")

                # -----------------------------------------------------------------
                # Data Stores
                # -----------------------------------------------------------------
                with Cluster("DynamoDB Tables"):
                    org_table = Dynamodb("Organisation")
                    hs_table = Dynamodb("HealthcareService")
                    loc_table = Dynamodb("Location")

                # -----------------------------------------------------------------
                # Supporting Services
                # -----------------------------------------------------------------
                with Cluster("Supporting Services"):
                    secrets = SecretsManager("Secrets\nManager")
                    kms = KMS("KMS")
                    cloudwatch = Cloudwatch("CloudWatch")

            # =====================================================================
            # RELATIONSHIPS
            # =====================================================================

            # External access
            apim >> Edge(label="mTLS") >> api_gw
            route53 >> api_gw

            # API Gateway to Lambdas
            api_gw >> dos_search
            api_gw >> org_api
            api_gw >> hs_api
            api_gw >> loc_api

            # DoS Search reads
            dos_search >> org_table
            dos_search >> hs_table
            dos_search >> loc_table

            # CRUD APIs to tables
            org_api >> org_table
            hs_api >> hs_table
            loc_api >> loc_table

            # ETL Pipeline flow
            eventbridge >> extractor
            extractor >> ods_api
            extractor >> transform_queue
            transform_queue >> transformer
            transformer >> load_queue
            load_queue >> loader
            loader >> apim  # Loader calls CRUD APIs via APIM

            # Data Migration flow
            legacy_dos >> Edge(label="CDC") >> dms
            dms >> target_rds
            queue_populator >> target_rds
            queue_populator >> migration_queue
            rds_listener >> migration_queue
            migration_queue >> processor
            processor >> target_rds
            processor >> migration_state
            processor >> org_table
            processor >> hs_table
            processor >> loc_table
            ref_data >> org_table
            dms_setup >> target_rds

            # Supporting services
            [extractor, transformer, loader] >> secrets
            [dos_search, org_api, hs_api, loc_api, processor] >> cloudwatch

    def generate_all(self, fmt: str = "png") -> None:
        """Generate all diagrams."""
        print("Generating full-deployment...")
        self.generate_full_deployment(fmt)
        print("Generating overview...")
        self.generate_prod_overview(fmt)
        print("Generating data-migration...")
        self.generate_data_migration(fmt)
        print("Generating etl-ods...")
        self.generate_etl_ods(fmt)
        print("Generating crud-apis...")
        self.generate_crud_apis(fmt)
        print("Generating dos-search...")
        self.generate_dos_search(fmt)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate AWS deployment diagrams from LikeC4 architecture"
    )
    parser.add_argument(
        "--architecture-dir",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Directory containing LikeC4 architecture files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent / "output",
        help="Output directory for generated diagrams",
    )
    parser.add_argument(
        "--format",
        choices=["png", "svg", "pdf"],
        default="png",
        help="Output format (default: png)",
    )
    parser.add_argument(
        "--diagram",
        choices=["all", "full-deployment", "overview", "data-migration", "etl-ods", "crud-apis", "dos-search"],
        default="all",
        help="Which diagram to generate (default: all)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print parsed architecture for debugging",
    )

    args = parser.parse_args()

    # Parse architecture
    print(f"Parsing architecture from {args.architecture_dir}...")
    architecture = parse_architecture(args.architecture_dir)

    if args.debug:
        print(f"\nParsed {len(architecture.nodes)} nodes:")
        for node_id, node in sorted(architecture.nodes.items()):
            print(f"  {node.node_type.value:12} {node_id}: {node.title}")
        print(f"\nParsed {len(architecture.relationships)} relationships")
        print(f"Parsed {len(architecture.views)} views: {list(architecture.views.keys())}")
        print()

    # Generate diagrams
    generator = DiagramGenerator(architecture, args.output_dir)

    generators = {
        "full-deployment": generator.generate_full_deployment,
        "overview": generator.generate_prod_overview,
        "data-migration": generator.generate_data_migration,
        "etl-ods": generator.generate_etl_ods,
        "crud-apis": generator.generate_crud_apis,
        "dos-search": generator.generate_dos_search,
    }

    if args.diagram == "all":
        generator.generate_all(args.format)
    else:
        print(f"Generating {args.diagram}...")
        generators[args.diagram](args.format)

    print(f"Diagrams generated in {args.output_dir}")


if __name__ == "__main__":
    main()

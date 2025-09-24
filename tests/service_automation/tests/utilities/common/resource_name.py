from loguru import logger


def get_resource_name(project, workspace, env, stack, resource):
    logger.debug(f"project: {project},  resource: {resource}, stack: {stack}, env: {env}, workspace: {workspace}")
    workspace_suffix = f"-{workspace}" if workspace else ""
    resource_name = f"{project}-{env}-{stack}-{resource}{workspace_suffix}"
    logger.debug("resource name {}", resource_name)
    return resource_name


def get_proxy_name(api_name,):
    logger.debug(f"project: {project},  resource: {resource}, stack: {stack}, env: {env}, workspace: {workspace}")
    workspace_suffix = f"-{workspace}" if workspace else ""
    resource_name = f"{project}-{env}-{stack}-{resource}{workspace_suffix}"
    logger.debug("resource name {}", resource_name)
    return resource_name

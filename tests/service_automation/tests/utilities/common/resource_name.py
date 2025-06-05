from loguru import logger


def get_resource_name(project, workspace, env, stack, resource):
    logger.info(f"project: {project},  resource: {resource}, stack: {stack}, env: {env}, workspace: {workspace}")
    if workspace == "default":
        resource_name = project + "-" + env + "-" + stack + "-" + resource
    else:
        resource_name = project + "-" + env + "-" + stack + "-" + resource + "-" + workspace
    logger.info("resource name {}", resource_name)
    return resource_name


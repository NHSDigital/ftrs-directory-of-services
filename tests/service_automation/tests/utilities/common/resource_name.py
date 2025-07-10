from loguru import logger


def get_resource_name(project, workspace, env, stack, resource):
    logger.info(f"project: {project},  resource: {resource}, stack: {stack}, env: {env}, workspace: {workspace}")
    if workspace == "default":
        resource_name = project + "-" + env + "-" + stack + "-" + resource
    else:
        resource_name = project + "-" + env + "-" + stack + "-" + resource + "-" + workspace
    return resource_name


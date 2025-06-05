from loguru import logger

def get_resource_name(self, project, workspace, env, stack, resource):
    logger.debug(f"project: {project},  resource: {resource}, stack: {stack}, env: {env}, workspace: {workspace}")
    if workspace == "default":
        lambda_name = project + "-" + env + "-" + stack + "-" + resource
    else:
        lambda_name = project + "-" + env + "-" + stack + "-" + resource + "-" + workspace
    logger.debug("resource name {}", lambda_name)
    return lambda_name


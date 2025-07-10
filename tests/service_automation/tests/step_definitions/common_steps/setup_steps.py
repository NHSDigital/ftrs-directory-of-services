from loguru import logger
from pytest_bdd import given, parsers, scenarios

scenarios("./is_api_features/gp_search_api.feature")


@given(parsers.parse('that the stack is "{stack}"'), target_fixture='fstack_name')
def set_stack_name(stack):
    logger.info(f"Setting stack name to: {stack}")
    fstack_name = stack
    return fstack_name

from pytest_bdd import scenarios, given, when, then

scenarios("../features/data_migration_features/data_migration.feature")

@given("the data migration system is ready")
def data_migration_system_ready():
    pass

@when("I run the hello world data migration test")
def run_hello_world_test():
    pass

@then("I see a hello world result")
def see_hello_world_result():
    print("Hello, world! Data migration test ran successfully.")

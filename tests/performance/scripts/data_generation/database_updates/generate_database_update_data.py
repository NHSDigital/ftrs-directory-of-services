import csv
import pandas
import random

from faker import Faker

GENERATED_CHANGES_FOR_FEED = 50000
GENERATED_CHANGES_FOR_BULK = 10000

service_type_chances = [
    (132, "Pharmacy Enhanced", 21.06, True),
    (131, "Pharmacy Urgent Medicines Supply", 6.59, True),
    (12, "Dental Practice", 6.06, False),
    (100, "GP Practice", 5.04, False),
    (20, "Community Based", 4.92, False),
    (13, "Pharmacy", 4.63, True),
    (149, "Pharmacy Contraception", 3.98, True),
    (7, "Mental Health", 3.91, False),
    (148, "Pharmacy Blood Pressure Check", 3.84, True),
    (21, "Retired", 3.37, False),
    (112, "Optical Enhanced", 3, False),
    (14, "Optical", 2.92, False),
    (29, "Sexual Health", 2.1, False),
    (48, "Specialist", 1.95, False),
    (25, "Integrated Urgent Care (IUC) Treatment", 1.88, False),
    (11, "Voluntary", 1.87, False),
    (140, "Same Day Emergency Care (SDEC)", 1.36, False),
    (38, "Community/District Nursing", 1.31, False),
    (156, "Dental Urgent Care", 1.27, False),
    (50, "Palliative Care", 1.14, False),
    (135, "Urgent Treatment Centre (UTC)", 1.10, False),
    (105, "Emergency Department (ED)", 1.04, False),
    (146, "Urgent Community Response (UCR)", 1.04, False),
]


bulk_update_action_chances = [
    ("cmssgsdid", 70.00),
    #("specifiedopeningtimesnewdays", 30.00),  # skipping for now
]

pharma_type_action_chances = [
    ("cmsorgname", 22.91),
    ("cmspublicname", 17.56),
    ("cmsorgstatus", 14.02),
    ("cmscontact", 12.36),
    ("postaladdress", 9.08),
    ("cmsorgtype", 6.62),
    # ("cmscontactdetails", 6.20), skiping until we get some data
    ("cmsurl", 5.89),
    # ("cmsopentimefriday", 5.32), skpping for now
]

other_type_actions_chances = [
    ("cmstepephoneno", 18.82),
    ("cmsorgname", 10.77),
    ("cmspublicname", 9.84),
    ("cmsorgstatus", 9.68),
    ("postaladdress", 8.67),
    ("cmssgsdid", 9.96),
    # ("cmsdispositioninstructions", 8.71), skipping for now
    ("cmsreferraltext", 8.37),
    # ("cmsopentimespecified", 7.61), skipping for now
    # ("cmspatientaccess", 7.56), skipping for now
]


def get_next_line(file_handles, table_name, service_type):
    file_path = f"./database_updates/test_data_exports/{table_name}_{service_type}.csv"

    # Open the file if not already opened
    if file_path not in file_handles:
        file_handles[file_path] = open(file_path, "r")
        # Skip the header line
        next(file_handles[file_path])

    # Read the next line for the service type
    current_file = file_handles[file_path]
    line = next(current_file, None)
    if line:
        return line.strip()
    else:
        # Wrap around to the beginning of the file
        current_file.seek(0)
        next(current_file)  # Skip the header line again
        line = next(current_file, None)
        return line.strip() if line else None



def handle_action(service_type, scenario, file_handles, faker, output_writer, reference_data):
    data = None
    row_id = None

    match scenario:
        case "cmstepephoneno":
            row_id = get_next_line(file_handles, 'services', service_type)
            data = faker.phone_number()

        case "cmsorgname":
            row_id = get_next_line(file_handles, 'services', service_type)
            data = faker.company()

        case "cmspublicname":
            row_id = get_next_line(file_handles, 'services', service_type)
            data = faker.company()

        case "cmsorgstatus":
            row_id = get_next_line(file_handles, 'services', service_type)
            data = faker.random_element(["1", "2", "3"])

        case "cmscontact":
            row_id = get_next_line(file_handles, 'services', service_type)
            data = faker.email()

        case "postaladdress":
            row_id = get_next_line(file_handles, 'services', service_type)
            data = faker.address().replace("\n", "$")

        case "cmsorgtype":
            row_id = get_next_line(file_handles, 'services', service_type)
            data = faker.random_element(["148", "149", "131", "132"])

        case "cmscontactdetails":
            row_id = get_next_line(file_handles, 'services', service_type)
            data = faker.unique.random_int()

        case "cmsurl":
            row_id = get_next_line(file_handles, 'services', service_type)
            data = faker.url()

        case "cmsreferraltext":
            row_id = get_next_line(file_handles, 'services', service_type)
            data = faker.sentence().replace("\n", " ")

        case "cmssgsdid":
            row = get_next_line(file_handles, 'servicesgsds', service_type)
            if not row:
                print(f"Skipping cmssgsdid to no data for service type: {service_type}")
                return

            row_id = row.split(",")[0]
            sds_stored = row.split(",")[1].split("|")
            data = None

            for i in range(1, 1000):
                random_sgsd = faker.random_element(reference_data["sgsds"])
                if random_sgsd[1] not in sds_stored:
                    data = random_sgsd[0] + "#" + random_sgsd[1]
                    break

            if not data:
                return

        case _:
            print(f"Skipping due to unknown or unsupported scenario: {scenario}")
            return

        # TODO: skipping for now
        # case "cmsopentimespecified":
        # case "cmspatientaccess":
        # case "cmsopentimefriday":
        # case "cmsdispositioninstructions":

    if data is None:
        print(f"Failed to generate for {scenario}, service_type: {service_type}")
        return

    output_writer.writerow([service_type, scenario, row_id, data])


def extract_action_data(action_chances):
    return [action[0] for action in action_chances], [action[1] for action in action_chances]


def find_stats(file_alias, file_path):
    print(f"Stats for generated {file_alias} file:")
    df = pandas.read_csv(file_path)
    total_count = len(df)
    count_by_service_type = df.groupby('service_type_id').size()
    percent_count = 100 * (count_by_service_type / total_count)

    print(f"Generated {total_count} rows of {file_alias} data")
    print(f"Group percentage: {percent_count}")

    percent_count_dict = percent_count.to_dict()

    # Check for differences greater than 3 percent points
    for service_type, defined_percentage in [(item[0], item[2]) for item in service_type_chances]:
        actual_percentage = percent_count_dict.get(service_type, 0)
        difference = abs(actual_percentage - defined_percentage)
        if difference > 3:
            print(
                f"Service Type {service_type}: Difference between expected and generated amount of updates exceeds "
                f"3 percent points (Actual: {actual_percentage:.2f}%, Defined: {defined_percentage:.2f}%)"
            )

def generate_feed_file(faker: Faker, file_handles, reference_data):
    feed_file_path =  "../../parameter_files/dos/feed_data.csv"
    output_csv_file = open(feed_file_path, "w")
    output_writer = csv.writer(output_csv_file)
    output_writer.writerow(['service_type_id', 'scenario', 'row_id', 'data'])

    service_type_weights = [item[2] for item in service_type_chances]
    service_types = [item[0] for item in service_type_chances]

    pharma_action_names, pharma_action_weights = extract_action_data(pharma_type_action_chances)
    other_action_names, other_action_weights = extract_action_data(other_type_actions_chances)

    service_type_is_pharma = {item[0]: item[3] for item in service_type_chances}

    random_service_types = random.choices(service_types, weights=service_type_weights, k=GENERATED_CHANGES_FOR_FEED)

    for service_type in random_service_types:
        is_pharma = service_type_is_pharma.get(service_type, False)

        if is_pharma:
            selected_action = random.choices(pharma_action_names, weights=pharma_action_weights, k=1)[0]
        else:
            selected_action = random.choices(other_action_names, weights=other_action_weights, k=1)[0]

        handle_action(service_type, selected_action, file_handles, faker, output_writer, reference_data)

    output_csv_file.close()
    find_stats("feed", feed_file_path)


def generate_bulk_file(faker: Faker, file_handles, reference_data):
    bulk_file_path = "../../parameter_files/dos/bulk_data.csv"
    output_csv_file = open(bulk_file_path, "w")
    output_writer = csv.writer(output_csv_file)
    output_writer.writerow(['service_type_id', 'scenario', 'row_id', 'data'])

    service_type_weights = [item[2] for item in service_type_chances]
    service_types = [item[0] for item in service_type_chances]
    bulk_action_names, bulk_action_weights = extract_action_data(bulk_update_action_chances)
    random_service_types = random.choices(service_types, weights=service_type_weights, k=GENERATED_CHANGES_FOR_BULK)

    for service_type in random_service_types:
        selected_action = random.choices(bulk_action_names, weights=bulk_action_weights, k=1)[0]
        handle_action(service_type, selected_action, file_handles, faker, output_writer, reference_data)

    output_csv_file.close()
    find_stats("bulk", bulk_file_path)

def main():
    faker = Faker("en_GB")

    # keep track of open files with row ids
    file_handlers = {}

    sgsds = pandas.read_csv("./database_updates/test_data_exports/symptomgroupsymptomdiscriminators.csv", dtype=str)
    reference_data = {
        "sgsds": sgsds.values.tolist()
    }

    generate_feed_file(faker, file_handlers, reference_data)
    generate_bulk_file(faker, file_handlers, reference_data)

    for handle in file_handlers.values():
        handle.close()


if __name__ == "__main__":
    main()

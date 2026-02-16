import csv
import random

from faker import Faker

GENERATED_UPDATES = 50000

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
    # ("cmssgsdid", 9.96), skip for now
    # ("cmsdispositioninstructions", 8.71), skipping for now
    ("cmsreferraltext", 8.37),
    # ("cmsopentimespecified", 7.61), skipping for now
    # ("cmspatientaccess", 7.56), skipping for now
]


def get_next_line(file_handles, table_name, service_type):
    file_path = f"./database_updates/test_data_exports/{table_name}_{service_type}.csv"
    try:
        # Open the file if not already opened
        if service_type not in file_handles:
            file_handles[service_type] = open(file_path, "r")
            # Skip the header line
            next(file_handles[service_type])

        # Read the next line for the service type
        current_file = file_handles[service_type]
        line = next(current_file, None)
        if line:
            return line.strip()
        else:
            # Wrap around to the beginning of the file
            current_file.seek(0)
            next(current_file)  # Skip the header line again
            line = next(current_file, None)
            return line.strip() if line else "No data available"
    except FileNotFoundError:
        return "File not found"


def handle_action(service_type, action, file_handles, faker, output_writer):
    match action:
        case "cmstepephoneno":
            table = 'services'
            row_id = get_next_line(file_handles, table, service_type)
            field = 'nonpublicphone'
            update_value = faker.phone_number()

        case "cmsorgname":
            table = 'services'
            row_id = get_next_line(file_handles, table, service_type)
            field = 'name'
            update_value = faker.company()

        case "cmspublicname":
            table = 'services'
            row_id = get_next_line(file_handles, table, service_type)
            field = 'publicname'
            update_value = faker.company()

        case "cmsorgstatus":
            table = 'services'
            row_id = get_next_line(file_handles, table, service_type)
            field = 'statusid'
            update_value = faker.random_element(["1", "2", "3"])

        case "cmscontact":
            table = 'services'
            row_id = get_next_line(file_handles, table, service_type)
            field = 'email'
            update_value = faker.email()

        case "postaladdress":
            table = 'services'
            row_id = get_next_line(file_handles, table, service_type)
            field = 'address'
            update_value = faker.address().replace("\n", "$")

        case "cmsorgtype":
            table = 'services'
            row_id = get_next_line(file_handles, table, service_type)
            field = 'typeid'
            update_value = faker.random_element(["148", "149", "131", "132"])

        case "cmscontactdetails":
            table = 'serviceendpoints'
            row_id = get_next_line(file_handles, 'endpoints', service_type)
            field = 'address'
            update_value = faker.unique.random_int()

        case "cmsurl":
            table = 'services'
            row_id = get_next_line(file_handles, 'services', service_type)
            field = 'web'
            update_value = faker.url()

        case "cmsreferraltext":
            table = 'services'
            row_id = get_next_line(file_handles, table, service_type)
            field = 'publicreferralinstructions'
            update_value = faker.sentence().replace("\n", " ")

        # TODO: skipping for now
        # case "cmsopentimespecified":
        # case "cmspatientaccess":
        # case "cmsopentimefriday":
        # case "cmsdispositioninstructions":

    output_writer.writerow([service_type, table, row_id, field, update_value])


def extract_action_data(action_chances):
    return [action[0] for action in action_chances], [action[1] for action in action_chances]


def main():
    faker = Faker("en_GB")

    output_csv_file = open("../../parameter_files/dos/service_updates.csv", "w+")
    output_writer = csv.writer(output_csv_file)
    output_writer.writerow(['service_type_id', 'update_table','row_id','update_field','update_value'])

    # keep track of open files with row ids
    file_handles = {}

    service_type_weights = [item[2] for item in service_type_chances]
    service_types = [item[0] for item in service_type_chances]

    pharma_action_names, pharma_action_weights = extract_action_data(pharma_type_action_chances)
    other_action_names, other_action_weights = extract_action_data(other_type_actions_chances)

    service_type_is_pharma = {item[0]: item[3] for item in service_type_chances}

    random_service_types = random.choices(service_types, weights=service_type_weights, k=GENERATED_UPDATES)

    for service_type in random_service_types:
        is_pharma = service_type_is_pharma.get(service_type, False)

        if is_pharma:
            selected_action = random.choices(pharma_action_names, weights=pharma_action_weights, k=1)[0]
        else:
            selected_action = random.choices(other_action_names, weights=other_action_weights, k=1)[0]

        handle_action(service_type, selected_action, file_handles, faker, output_writer)


    for handle in file_handles.values():
        handle.close()


if __name__ == "__main__":
    main()
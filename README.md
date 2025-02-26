# Find the right service

[![CI/CD Pull Request](https://github.com/nhs-england-tools/repository-template/actions/workflows/cicd-1-pull-request.yaml/badge.svg)](https://github.com/nhs-england-tools/repository-template/actions/workflows/cicd-1-pull-request.yaml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=repository-template&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=repository-template)

Find the right service (FTRS) helps direct patients to the most appropriate NHS service for their urgent care

The system is commissioned, developed and hosted by NHS England

The service consists of a number of key components

- a directory of services (DOS)
- search APIs
- data sourcing

## The Directory of Services (DOS)

The DOS holds data for Urgent and Emergency, Primary, Secondary and Tertiary Sector care services. The data held for each service includes its location, availability and treatment/care
provided. The data is maintained via an admin user interface and some APIs

## Search APIs

Known collectively as search APIs there are a number of APIs that can be used to interrogate the DOS and find details of clinically appropriate service/services. The most important of these currently is the triage search used in support of 111 and 999 call handlers

## Data sourcing

Some data for certain types of service may be available from some third parties. The data sourcing sub-project looks to bring in this data where it is possible and clinically safe to do so.

Currently supported technologies are:

- Terraform
- Docker
- Podman
- Python

## Table of Contents

- [Find the right service](#find-the-right-service)
  - [The Directory of Services (DOS)](#the-directory-of-services-dos)
  - [Search APIs](#search-apis)
  - [Data sourcing](#data-sourcing)
  - [Table of Contents](#table-of-contents)
  - [Setup](#setup)
    - [Prerequisites](#prerequisites)
    - [Configuration](#configuration)
  - [Usage](#usage)
    - [Testing](#testing)
  - [Design](#design)
    - [Diagrams](#diagrams)
    - [Modularity](#modularity)
  - [Contributing](#contributing)
    - [Branch naming convention](#branch-naming-convention)
    - [Commit message convention](#commit-message-convention)
    - [Release process](#release-process)
  - [Contacts](#contacts)
  - [Licence](#licence)

## Setup

Clone the repository

```shell
git clone https://github.com/NHSDigital/ftrs-directory-of-services.git
```

### Prerequisites

The following software packages, or their equivalents, are expected to be installed and configured:

- [Docker](https://www.docker.com/) container runtime or a compatible tool, e.g. [Podman](https://podman.io/),
- [asdf](https://asdf-vm.com/) version manager,
- [Homebrew](https://brew.sh/) (for macOS),
- [GNU make](https://www.gnu.org/software/make/) 3.82 or later,

> [!NOTE]<br>
> The version of GNU make available by default on macOS is earlier than 3.82. You will need to upgrade it or certain `make` tasks will fail. On macOS, you will need [Homebrew](https://brew.sh/) installed, then to install `make`, like so:
>
> ```shell
> brew install make
> ```
>
> You will then see instructions to fix your [`$PATH`](https://github.com/nhs-england-tools/dotfiles/blob/main/dot_path.tmpl) variable to make the newly installed version available. If you are using [dotfiles](https://github.com/nhs-england-tools/dotfiles), this is all done for you.

- [GNU sed](https://www.gnu.org/software/sed/) and [GNU grep](https://www.gnu.org/software/grep/) are required for the scripted command-line output processing,
- [GNU coreutils](https://www.gnu.org/software/coreutils/) and [GNU binutils](https://www.gnu.org/software/binutils/) may be required to build dependencies like Python, which may need to be compiled during installation,

> [!NOTE]<br>
> For macOS users, installation of the GNU toolchain has been scripted and automated as part of the `dotfiles` project. Please see this [script](https://github.com/nhs-england-tools/dotfiles/blob/main/assets/20-install-base-packages.macos.sh) for details.

- [Python](https://www.python.org/) required to run Git hooks,
- [`jq`](https://jqlang.github.io/jq/) a lightweight and flexible command-line JSON processor.

### Configuration

To install and configure the toolchain dependencies

```shell
make config
```

## Usage

To follow

### Testing

To follow

## Design

### Diagrams

[C4 model](https://c4model.com/) digrams documenting all the system interfaces, external dependencies and integration points will follow

The source for these diagrams will be in Git for change control and review purposes.

### Modularity

To follow

## Contributing

Describe or link templates on how to raise an issue, feature request or make a contribution to the codebase. Reference the other documentation files, like

### Branch naming convention

A valid branch name is made up of these elements - in this order

- branch type - must be one of task, hotfix
- jira ref    - the unique identifier of the Jira ticket prompting the change
- separator   - either a hyphen or an underscore
- description - Must start with an alphanumeric and contain only alphanumerics/hyphens/underscores with a min length of 10 characters and a max length of 45

Examples of valid branch names

- task/XXX-123_My_valid_branch_name - words of description separated by underscores
- task/XXX-123-My-valid-branch-name - words of description separated by hyphens
- task/XXX-123_MyValidBranchName    - camelcase description
- task/XXX-123-My-valid_branch_name - description with mix of underscores and hyphens

Examples of invalid branch names

- XXX-123_My_Invalid_branch_name  - does not start with branch type of ie - task or hotfix
- task/MyInvalidbranchName        - does not include JIRA reference
- task/XXX-123MyInvalidBranchName - no separator after JIRA reference

### Commit message convention

A valid commit message must

- start with a valid Jira reference (to aid traceability of changes eg when building a release) and
- consist of at least three words (to prompt a meaningful description of the commit)
- not exceed 100 characters (encouraging concise wording for readability essentially)

If the contributor does not include the JIRA reference a githook will insert it at the start of the message, deriving it from the branch name

### Release process

To follow

## Contacts

To follow

## Licence

> The [LICENCE.md](./LICENCE.md) file will need to be updated with the correct year and owner

Unless stated otherwise, the codebase is released under the MIT License. This covers both the codebase and any sample code in the documentation.

Any HTML or Markdown documentation is [© Crown Copyright](https://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/uk-government-licensing-framework/crown-copyright/) and available under the terms of the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

# Local index setup

To set up dynamo follow the instructions as noted in:
services/data-migration/README.md

When you have the data loaded across you can now continue with this README.

To set up the opensearch instance, run the following commands inside the data-migration directory as well:
    ```
    export ENABLE_OPENSEARCH=enabled
    # Enable OpenSearch when starting the services
    docker compose --profile enabled up
    ```

Once this is done, do initial set-up for the dos-search directory (parent of this directory).

With this you can now run the Python file 'temporary_sgsd_setup.py'
Every time this file is ran, the index will be rebuilt from scratch, meaning the data will be updated to align with what's in dynamo. Although this will take several minutes to run.

You can run the file by using the following command in the parent directory:
    ```
    poetry run Python opensearch_local_index_populator/temporary_sgsd_setup.py
    ```

from typing import List

from ruamel import yaml

import great_expectations as ge
from great_expectations.core.batch import Batch, BatchRequest, RuntimeBatchRequest

context = ge.get_context()

datasource_config = {
    "name": "my_gcs_datasource",
    "class_name": "Datasource",
    "execution_engine": {"class_name": "PandasExecutionEngine"},
    "data_connectors": {
        "default_runtime_data_connector_name": {
            "class_name": "RuntimeDataConnector",
            "batch_identifiers": ["default_identifier_name"],
        },
        "default_inferred_data_connector_name": {
            "class_name": "InferredAssetGCSDataConnector",
            "bucket_or_name": "<YOUR_GCS_BUCKET_HERE>",
            "prefix": "<BUCKET_PATH_TO_DATA>",
            "default_regex": {
                "pattern": "(.*)\\.csv",
                "group_names": ["data_asset_name"],
            },
        },
    },
}

# Please note this override is only to provide good UX for docs and tests.
# In normal usage you'd set your path directly in the yaml above.
datasource_config["data_connectors"]["default_inferred_data_connector_name"][
    "bucket_or_name"
] = "superconductive-integration-tests"
datasource_config["data_connectors"]["default_inferred_data_connector_name"][
    "prefix"
] = "data/taxi_yellow_trip_data_samples/"

context.test_yaml_config(yaml.dump(datasource_config))

context.add_datasource(**datasource_config)

# Here is a RuntimeBatchRequest using a path to a single CSV file
batch_request = RuntimeBatchRequest(
    datasource_name="my_gcs_datasource",
    data_connector_name="default_runtime_data_connector_name",
    data_asset_name="<YOUR_MEANGINGFUL_NAME>",  # this can be anything that identifies this data_asset for you
    runtime_parameters={"path": "<PATH_TO_YOUR_DATA_HERE>"},  # Add your GCS path here.
    batch_identifiers={"default_identifier_name": "default_identifier"},
)

# Please note this override is only to provide good UX for docs and tests.
# In normal usage you'd set your path directly in the BatchRequest above.
batch_request.runtime_parameters[
    "path"
] = f"gs://superconductive-integration-tests/data/taxi_yellow_trip_data_samples/yellow_trip_data_sample_2019-01.csv"

context.create_expectation_suite(
    expectation_suite_name="test_suite", overwrite_existing=True
)
validator = context.get_validator(
    batch_request=batch_request, expectation_suite_name="test_suite"
)
print(validator.head())

# NOTE: The following code is only for testing and can be ignored by users.
assert isinstance(validator, ge.validator.validator.Validator)

batch_list: List[Batch] = context.get_batch_list(batch_request=batch_request)
assert len(batch_list) == 1

batch: Batch = batch_list[0]
assert batch.data.dataframe.shape[0] == 10000

# Here is a BatchRequest naming a data_asset
batch_request = BatchRequest(
    datasource_name="my_gcs_datasource",
    data_connector_name="default_inferred_data_connector_name",
    data_asset_name="<YOUR_DATA_ASSET_NAME>",
)

# Please note this override is only to provide good UX for docs and tests.
# In normal usage you'd set your data asset name directly in the BatchRequest above.
batch_request.data_asset_name = (
    "data/taxi_yellow_trip_data_samples/yellow_trip_data_sample_2019-01"
)

context.create_expectation_suite(
    expectation_suite_name="test_suite", overwrite_existing=True
)
validator = context.get_validator(
    batch_request=batch_request, expectation_suite_name="test_suite"
)
print(validator.head())

# NOTE: The following code is only for testing and can be ignored by users.
assert isinstance(validator, ge.validator.validator.Validator)
assert [ds["name"] for ds in context.list_datasources()] == ["my_gcs_datasource"]
assert set(
    context.get_available_data_asset_names()["my_gcs_datasource"][
        "default_inferred_data_connector_name"
    ]
) == {
    "data/taxi_yellow_trip_data_samples/yellow_trip_data_sample_2019-01",
    "data/taxi_yellow_trip_data_samples/yellow_trip_data_sample_2019-02",
    "data/taxi_yellow_trip_data_samples/yellow_trip_data_sample_2019-03",
}

batch_list: List[Batch] = context.get_batch_list(batch_request=batch_request)
assert len(batch_list) == 1

batch: Batch = batch_list[0]
assert batch.data.dataframe.shape[0] == 10000

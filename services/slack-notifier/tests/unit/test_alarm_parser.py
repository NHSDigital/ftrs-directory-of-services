import json

from functions.alarm_parser import flatten_dict, parse_cloudwatch_alarm


class TestFlattenDict:
    def test_flatten_simple_dict(self):
        data = {"key1": "value1", "key2": "value2"}
        result = flatten_dict(data)
        assert result == {"key1": "value1", "key2": "value2"}

    def test_flatten_nested_dict(self):
        data = {"parent": {"child": "value"}}
        result = flatten_dict(data)
        assert result == {"parent_child": "value"}

    def test_flatten_list_with_primitives(self):
        data = {"items": ["a", "b", "c"]}
        result = flatten_dict(data)
        assert result == {"items_0": "a", "items_1": "b", "items_2": "c"}

    def test_flatten_list_with_dicts(self):
        data = {"items": [{"name": "first"}, {"name": "second"}]}
        result = flatten_dict(data)
        assert result == {"items_0_name": "first", "items_1_name": "second"}

    def test_flatten_complex_nested(self):
        data = {"level1": {"level2": {"level3": "value"}}}
        result = flatten_dict(data)
        assert result == {"level1_level2_level3": "value"}

    def test_flatten_empty_dict(self):
        result = flatten_dict({})
        assert result == {}

    def test_flatten_with_custom_separator(self):
        data = {"parent": {"child": "value"}}
        result = flatten_dict(data, sep="-")
        assert result == {"parent-child": "value"}

    def test_flatten_with_parent_key(self):
        data = {"child": "value"}
        result = flatten_dict(data, parent_key="parent")
        assert result == {"parent_child": "value"}


class TestParseCloudwatchAlarm:
    def test_parse_valid_json(self):
        message = json.dumps({"AlarmName": "test-alarm", "NewStateValue": "ALARM"})
        result = parse_cloudwatch_alarm(message)
        assert result == {"AlarmName": "test-alarm", "NewStateValue": "ALARM"}

    def test_parse_invalid_json(self):
        message = "not valid json"
        result = parse_cloudwatch_alarm(message)
        assert result == {"raw_message": "not valid json"}

    def test_parse_empty_string(self):
        result = parse_cloudwatch_alarm("")
        assert result == {"raw_message": ""}

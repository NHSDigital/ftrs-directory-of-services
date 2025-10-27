# from unittest.mock import Mock, patch

# import pytest
# from sqlalchemy import Engine
# from sqlmodel import Session

# from pipeline.utils.dbutil import iter_records


# @pytest.fixture
# def mock_engine() -> Mock:
#     return Mock(spec=Engine)


# @pytest.fixture
# def mock_session() -> Mock:
#     mock = Mock(spec=Session)
#     return mock


# @pytest.mark.parametrize("batch_size", [100, 1000, 5000])
# def test_select_statement_uses_correct_batch_size(
#     mock_engine: Mock, batch_size: int
# ) -> None:
#     mock_model = Mock()

#     with (
#         patch("pipeline.utils.dbutil.Session") as mock_session_cls,
#         patch("pipeline.utils.dbutil.select") as mock_select,
#     ):
#         # Create a proper iterator for the scalar result
#         mock_result = []

#         mock_session_instance = Mock()
#         mock_session_cls.return_value.__enter__.return_value = mock_session_instance
#         mock_session_instance.scalars.return_value = mock_result

#         # Start iteration to trigger statement creation
#         list(iter_records(mock_engine, mock_model, batch_size))

#         # Verify select was called with the model
#         mock_select.assert_called_once_with(mock_model)

#         # Verify execution_options was called with the correct batch size
#         select_stmt = mock_select.return_value
#         select_stmt.execution_options.assert_called_once_with(yield_per=batch_size)


# def test_select_statement_defaults_to_1000_batch_size(mock_engine: Mock) -> None:
#     mock_model = Mock()

#     with (
#         patch("pipeline.utils.dbutil.Session") as mock_session_cls,
#         patch("pipeline.utils.dbutil.select") as mock_select,
#     ):
#         # Create a proper iterator for the scalar result
#         mock_result = []

#         mock_session_instance = Mock()
#         mock_session_cls.return_value.__enter__.return_value = mock_session_instance
#         mock_session_instance.scalars.return_value = mock_result

#         # Start iteration to trigger statement creation
#         list(iter_records(mock_engine, mock_model))

#         # Verify execution_options was called with the default batch size
#         select_stmt = mock_select.return_value
#         select_stmt.execution_options.assert_called_once_with(yield_per=1000)


# def test_select_statement_executes_within_session_context(mock_engine: Mock) -> None:
#     mock_model = Mock()

#     with (
#         patch("pipeline.utils.dbutil.Session") as mock_session_cls,
#         patch("pipeline.utils.dbutil.select") as mock_select,
#     ):
#         # Set up the select mock to return a proper statement mock
#         mock_stmt = Mock()
#         mock_select.return_value = mock_stmt

#         # Create a proper iterator for the scalar result
#         mock_result = []

#         mock_session_instance = Mock()
#         mock_session_cls.return_value.__enter__.return_value = mock_session_instance
#         mock_session_instance.scalars.return_value = mock_result

#         # Start iteration
#         list(iter_records(mock_engine, mock_model))

#         # Verify session was created with the engine
#         mock_session_cls.assert_called_once_with(mock_engine)

#         # Verify select was called with the model
#         mock_select.assert_called_once_with(mock_model)

#         # Verify scalars were called on the session
#         mock_session_instance.scalars.assert_called_once()


# @pytest.mark.parametrize("record_count", [0, 1, 5])
# def test_select_statement_yields_correct_number_of_records(
#     mock_engine: Mock, record_count: int
# ) -> None:
#     mock_model = Mock()
#     mock_records = [Mock() for _ in range(record_count)]

#     with (
#         patch("pipeline.utils.dbutil.Session") as mock_session_cls,
#         patch("pipeline.utils.dbutil.select") as mock_select,
#     ):
#         # Set up the select mock to return a proper statement mock
#         mock_stmt = Mock()
#         mock_select.return_value = mock_stmt

#         mock_session_instance = Mock()
#         mock_session_cls.return_value.__enter__.return_value = mock_session_instance

#         # Use the record list directly as the return value
#         mock_session_instance.scalars.return_value = mock_records

#         # Consume the iterator and count results
#         results = list(iter_records(mock_engine, mock_model))

#         assert len(results) == record_count
#         assert results == mock_records

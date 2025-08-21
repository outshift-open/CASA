"""Tests for identity_auth_server.pipelines.exceptions module."""

import pytest

from identity_auth_server.pipelines.exceptions import PipelineValidationError


class TestPipelineValidationError:
    """Tests for PipelineValidationError exception class."""

    def test_init_with_message(self):
        """Test that PipelineValidationError initializes correctly with a message."""
        error_message = "Test validation error message"
        error = PipelineValidationError(error_message)

        assert error.message == error_message
        assert str(error) == error_message

    def test_init_with_empty_message(self):
        """Test that PipelineValidationError handles empty message."""
        error_message = ""
        error = PipelineValidationError(error_message)

        assert error.message == error_message
        assert str(error) == error_message

    def test_init_with_multiline_message(self):
        """Test that PipelineValidationError handles multiline message."""
        error_message = "This is a multiline\nerror message\nwith multiple lines"
        error = PipelineValidationError(error_message)

        assert error.message == error_message
        assert str(error) == error_message

    def test_inheritance_from_exception(self):
        """Test that PipelineValidationError inherits from Exception."""
        error = PipelineValidationError("test message")

        assert isinstance(error, Exception)
        assert isinstance(error, PipelineValidationError)

    def test_can_be_raised_and_caught(self):
        """Test that PipelineValidationError can be raised and caught."""
        error_message = "This is a test error"

        with pytest.raises(PipelineValidationError) as exc_info:
            raise PipelineValidationError(error_message)

        assert exc_info.value.message == error_message
        assert str(exc_info.value) == error_message

    def test_can_be_caught_as_generic_exception(self):
        """Test that PipelineValidationError can be caught as generic Exception."""
        error_message = "Generic exception test"

        with pytest.raises(Exception) as exc_info:
            raise PipelineValidationError(error_message)

        assert isinstance(exc_info.value, PipelineValidationError)
        assert exc_info.value.message == error_message

    def test_equality_comparison(self):
        """Test equality comparison between PipelineValidationError instances."""
        message = "Test error"
        error1 = PipelineValidationError(message)
        error2 = PipelineValidationError(message)
        error3 = PipelineValidationError("Different message")

        # Note: Exception instances are not equal by default, even with same message
        assert error1 is not error2
        assert error1.message == error2.message
        assert error1.message != error3.message

    def test_repr_string_representation(self):
        """Test string representation of PipelineValidationError."""
        error_message = "Test repr message"
        error = PipelineValidationError(error_message)

        # Test that repr contains the class name and message
        repr_str = repr(error)
        assert "PipelineValidationError" in repr_str
        assert error_message in repr_str

    def test_message_attribute_is_accessible(self):
        """Test that the message attribute is accessible and correct."""
        test_messages = [
            "Simple message",
            "Message with special chars: !@#$%^&*()",
            "123456789",
            "Unicode message: 🚀 🎉 ✨",
            "   Message with whitespace   ",
        ]

        for message in test_messages:
            error = PipelineValidationError(message)
            assert error.message == message
            assert hasattr(error, "message")

    def test_args_tuple_contains_message(self):
        """Test that the args tuple contains the message (standard Exception behavior)."""
        error_message = "Args tuple test"
        error = PipelineValidationError(error_message)

        assert error.args == (error_message,)
        assert len(error.args) == 1
        assert error.args[0] == error_message

    def test_with_various_data_types_as_message(self):
        """Test PipelineValidationError with different data types converted to string."""
        # Test with different types that should be converted to string
        test_cases = [
            ("string message", str),
            (123, int),
            (45.67, float),
            (True, bool),
            (None, type(None)),
        ]

        for test_value, expected_type in test_cases:
            # Convert to string as expected by the constructor
            error = PipelineValidationError(str(test_value))
            assert error.message == str(test_value)
            assert isinstance(error.message, str)

    def test_docstring_exists(self):
        """Test that PipelineValidationError has proper docstring."""
        assert PipelineValidationError.__doc__ is not None
        assert len(PipelineValidationError.__doc__.strip()) > 0
        assert "Exception raised when input validation fails" in PipelineValidationError.__doc__

    def test_init_method_docstring_exists(self):
        """Test that PipelineValidationError.__init__ has proper docstring."""
        assert PipelineValidationError.__init__.__doc__ is not None
        assert len(PipelineValidationError.__init__.__doc__.strip()) > 0
        assert "Args:" in PipelineValidationError.__init__.__doc__
        assert "message:" in PipelineValidationError.__init__.__doc__

import os
import shutil
import zipfile
from datetime import datetime
from io import BytesIO

from server.app import download_and_extract_zip, TEXT_FILES_DIR, generate_metadata


class TestDownloadAndExtractZip:
    """Tests are organized such that each app function is tested in a different test
      class. Each method within each test class represents a specific test case
      for each of the app's functions. This way we can clearly distinguish
      between test cases for different functions, and also we avoid having long
      test case function names."""

    # noinspection PyMethodMayBeStatic
    def teardown_method(self):
        """Cleanup after each test by removing the 'sample-files-main' directory.
          This is run automatically by pytest after each test."""

        if os.path.exists(TEXT_FILES_DIR):
            shutil.rmtree(TEXT_FILES_DIR)

    @staticmethod
    def set_mock_content(mocker, content_dict):
        """Helper function for some common test operations and mocking resources."""

        # Create an in-memory ZIP file with custom text files.
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for filename, content in content_dict.items():
                zip_file.writestr(filename, content)
        zip_buffer.seek(0)

        mock_response = mocker.Mock()
        mock_response.content = zip_buffer.getvalue()
        mock_response.raise_for_status = mocker.Mock()
        mocker.patch('requests.get', return_value=mock_response)

    @staticmethod
    def run_test(content_dict, mocker):
        """Convenience method that allows us to write many test cases with minimal boilerplate."""

        file_names = content_dict.keys()
        TestDownloadAndExtractZip.set_mock_content(mocker, content_dict)
        download_and_extract_zip()
        assert os.path.exists(TEXT_FILES_DIR)
        for file_name in file_names:
            file_path = os.path.join(TEXT_FILES_DIR, file_name)

            # Verify file existence.
            assert os.path.exists(file_path)

            # Verify file content
            with open(file_path, 'r') as f:
                assert f.read() == content_dict[file_name]

    def test_case_1(self, mocker):
        # Test a regular case
        content_dict = {
            "sample_file_0.txt": "word11 word12     word13	word14",
            "sample_file_1.txt": "This is the content of file_1"
        }
        self.run_test(content_dict, mocker)

    def test_case_2(self, mocker):
        # Test case where there is a single file and it's empty.
        content_dict = {
            "sample_file_0.txt": "",
        }
        self.run_test(content_dict, mocker)

    def test_case_3(self, mocker):
        # Test case where there is 1 file, with multi-line content.
        content_dict = {
            "abbsjsjdjfaa.txt": """
word11 word12     word13	word14
   word21 word22   
word31 word32
word41

            """,
        }
        self.run_test(content_dict, mocker)


class TestGenerateMetadata:
    """Test the 'generate_metadata' app function."""

    # noinspection PyMethodMayBeStatic
    def teardown_method(self):
        if os.path.exists(TEXT_FILES_DIR):
            shutil.rmtree(TEXT_FILES_DIR)

    @staticmethod
    def set_mock_content(mocker, content_dict):
        """Helper function for some common test operations and mocking resources."""

        # Create an in-memory ZIP file with custom text files.
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for filename, content in content_dict.items():
                zip_file.writestr(filename, content)
        zip_buffer.seek(0)

        # Mock the API response
        mock_response = mocker.Mock()
        mock_response.content = zip_buffer.getvalue()
        mock_response.raise_for_status = mocker.Mock()
        mocker.patch('requests.get', return_value=mock_response)

        # Mock the datetime value
        mock_datetime = mocker.patch('server.app.datetime', wraps=datetime)
        mock_datetime.now.return_value = datetime(2024, 6, 1)

    @staticmethod
    def run_test(content_dict, mocker, expected):
        """Convenience method that allows us to write many test cases with minimal boilerplate."""

        TestGenerateMetadata.set_mock_content(mocker, content_dict)
        observed = generate_metadata()
        assert observed == expected

    def test_case_1(self, mocker):
        # Test a single file
        content_dict = {
            "sample_file_0.txt": "word11 word12     word13	word14 word14",
            "sample_file_1.txt": "This is the content of file_1"
        }
        expected = [
            {
                "file_name": "sample_file_0.txt",
                "sha256": "c477511240ea0a17979a3b8e7acc30f13456cf97cfe58c41941aa6fe1ceeebc9",
                "file_size": 38,
                "word_count": 5,
                "unique_word_count": 4,
                "date": "2024-06-01",
            },
            {
                "file_name": "sample_file_1.txt",
                "sha256": "637177c0469d8922fead71e19424c79db0de91d6968a6dc092a6d7a7a00fcce0",
                "file_size": 29,
                "unique_word_count": 6,
                "word_count": 6,
                "date": "2024-06-01",
            },
        ]
        self.run_test(content_dict, mocker, expected)

    def test_case_2(self, mocker):
        # Test an empty file
        content_dict = {
            "some_file_name.txt": "",
        }
        expected = [
            {
                "file_name": "some_file_name.txt",
                "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "file_size": 0,
                "word_count": 0,
                "unique_word_count": 0,
                "date": "2024-06-01",
            },
        ]
        self.run_test(content_dict, mocker, expected)

    def test_case_3(self, mocker):
        # Test case where there is 1 file, with multiline content.
        content_dict = {
            "some_other_file.txt": """
word11 word12     word13	word14
   word21 word22            word22              word22
word31 word32
word41

            """,
        }
        expected = [
            {
                "file_name": "some_other_file.txt",
                "sha256": "fdf3f6ed6f27721fc58e3c89e5a167744dc986dd2dd22f95f7237dbdf4d07120",
                "file_size": 122,
                "word_count": 11,
                "unique_word_count": 9,
                "date": "2024-06-01",
            },
        ]
        self.run_test(content_dict, mocker, expected)

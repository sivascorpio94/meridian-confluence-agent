import os
import unittest
from unittest.mock import patch

from src.run_api import main


class RunApiTests(unittest.TestCase):
    @patch("src.run_api.uvicorn.run")
    def test_host_and_port_are_configurable_for_container(self, run):
        with patch.dict(os.environ, {"API_HOST": "0.0.0.0", "API_PORT": "9000"}):
            main()
        run.assert_called_once_with(
            "src.api:app", host="0.0.0.0", port=9000, reload=False
        )


if __name__ == "__main__":
    unittest.main()

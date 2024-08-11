import logging
import socket
from pathlib import Path
from typing import Callable

import livereload


class PreviewRunner:
    """
    Runs a livereload server to preview changes in specified targets.

    Args:
        port (int | None): The port number to run the server on. If None, an available port will be used.
        targets (list[Path]): A list of target paths to watch for changes.

    Raises:
        ValueError: If the port number is out of range (0-65535).
    """
    
    DEFAULT_PORT = 35729


    def __init__(self, hook: Callable, port: int | None = None, targets: list[Path] = [], header_set: dict = {}):
        self._setup_logging()

        self.hook = hook
        self.port = self._fix_port(port)
        self.targets = targets
        self.header_set = header_set

        

    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _is_available_port(self, port: int) -> bool:
        """
        Checks if the port is available.

        Args:
            port (int): The port number to check.

        Returns:
            bool: True if the port is available, False otherwise.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0
        

    def _fix_port(self, port: int | None) -> int:
        """
        Fixes the port number if it is None by finding an available port.

        Args:
            port (int | None): The port number to fix.

        Returns:
            int: The fixed port number.

        Raises:
            ValueError: If the port number is out of range (0-65535).
        """
        if port is None:
            # Check DEFAULT_PORT first
            if self._is_available_port(self.DEFAULT_PORT):
                return self.DEFAULT_PORT
            
            # If DEFAULT_PORT is not available, find an available port
            self.logger.info("Port not specified. Finding an available port.")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('', 0))
            port = s.getsockname()[1]
            s.close()
            self.logger.info(f"Using port {port}.")

        elif port < 0 or port > 65535:
            raise ValueError("Port number must be between 0 and 65535")
        else:
            self.logger.info(f"Using specified port {port}.")

        return port

    def run(self):
        """
        Runs the livereload server and watches the specified targets for changes.
        """
        self.logger.info(f"Starting livereload server on port {self.port}")
        server = livereload.Server()
        for target in self.targets:
            server.watch(str(target), self.hook)
            self.logger.info(f"Watching target: {target}")

        for key, value in self.header_set.items():
            server.setHeader(key, value)

        server.serve(port=self.port)

                     
    

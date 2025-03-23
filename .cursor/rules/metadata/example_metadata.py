#!/usr/bin/env python3

"""
@file example_metadata.py
@version 1.0.0
@author MetadataTeam
@date 2023-09-15
@license MIT

@description
This file demonstrates the proper implementation of metadata standards in Python files.
It includes examples of file-level metadata, module-level metadata, function-level
metadata, and class-level metadata.

@example
```python
from example_metadata import MetadataProcessor

processor = MetadataProcessor('config.json')
metadata = processor.extract_metadata('source_file.py')
```

@dependencies
- json
- os
- typing
- logging

@stability stable
@performance O(n) where n is the number of lines in the source file
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Module-level metadata
__version__ = '1.0.0'
__author__ = 'MetadataTeam'
__all__ = ['MetadataProcessor', 'MetadataExtractor', 'MetadataValidator']


class MetadataProcessor:
    """
    @class MetadataProcessor
    @description Processes files to extract, validate, and store metadata.
    
    This class provides a comprehensive interface for working with metadata
    in source code files. It can extract metadata from comments, validate
    it against defined standards, and store it in a structured format.
    
    @stability stable
    @since 1.0.0
    @author MetadataTeam
    """
    
    def __init__(self, config_path: str):
        """
        @method __init__
        @description Initialize the metadata processor with configuration.
        
        @param config_path Path to the configuration file
        
        @throws FileNotFoundError If the configuration file doesn't exist
        @throws json.JSONDecodeError If the configuration file is invalid JSON
        """
        self.config = self._load_config(config_path)
        self.extractor = MetadataExtractor(self.config.get('extraction_rules', {}))
        self.validator = MetadataValidator(self.config.get('validation_rules', {}))
        self.storage_path = self.config.get('storage_path', './metadata')
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_path, exist_ok=True)
        
        logger.info(f"Initialized MetadataProcessor with config from {config_path}")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        @method _load_config
        @description Load the configuration from a JSON file.
        
        @param config_path Path to the configuration file
        @return Dictionary containing the configuration
        
        @private
        """
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            return {}
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        @method extract_metadata
        @description Extract metadata from a file.
        
        @param file_path Path to the file to extract metadata from
        @return Dictionary containing the extracted metadata
        
        @example
        ```python
        processor = MetadataProcessor('config.json')
        metadata = processor.extract_metadata('source_file.py')
        print(metadata['version'])  # Prints the version from the file metadata
        ```
        
        @complexity O(n) where n is the number of lines in the file
        """
        logger.info(f"Extracting metadata from {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return {}
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Use the extractor to get metadata
        metadata = self.extractor.extract(content, file_path)
        
        # Store the extracted metadata
        self._store_metadata(file_path, metadata)
        
        return metadata
    
    def validate_metadata(self, metadata: Dict[str, Any]) -> List[str]:
        """
        @method validate_metadata
        @description Validate metadata against defined rules.
        
        @param metadata Dictionary containing metadata to validate
        @return List of validation errors, empty if validation passed
        
        @complexity O(m) where m is the number of validation rules
        """
        return self.validator.validate(metadata)
    
    def _store_metadata(self, file_path: str, metadata: Dict[str, Any]) -> None:
        """
        @method _store_metadata
        @description Store metadata in the configured storage location.
        
        @param file_path Path to the source file
        @param metadata Dictionary containing metadata to store
        
        @private
        """
        # Create a filename based on the source file
        base_name = os.path.basename(file_path)
        storage_file = os.path.join(self.storage_path, f"{base_name}.metadata.json")
        
        # Store the metadata as JSON
        with open(storage_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Stored metadata in {storage_file}")


class MetadataExtractor:
    """
    @class MetadataExtractor
    @description Extracts metadata from file content.
    
    @private This class is meant to be used internally by MetadataProcessor
    """
    
    def __init__(self, rules: Dict[str, Any]):
        """
        @method __init__
        @description Initialize the extractor with rules.
        
        @param rules Dictionary containing extraction rules
        """
        self.rules = rules
    
    def extract(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        @method extract
        @description Extract metadata from file content.
        
        @param content String containing the file content
        @param file_path Path to the file (for reference)
        @return Dictionary containing extracted metadata
        """
        # Implementation would extract metadata from docstrings and comments
        # This is a simplified example
        metadata = {
            'file_path': file_path,
            'size': len(content),
            'type': os.path.splitext(file_path)[1],
            'extracted_at': os.path.getmtime(file_path)
        }
        
        # In a real implementation, we would parse docstrings to extract:
        # - @file, @version, @author, etc.
        
        return metadata


class MetadataValidator:
    """
    @class MetadataValidator
    @description Validates metadata against defined rules.
    
    @private This class is meant to be used internally by MetadataProcessor
    """
    
    def __init__(self, rules: Dict[str, Any]):
        """
        @method __init__
        @description Initialize the validator with rules.
        
        @param rules Dictionary containing validation rules
        """
        self.rules = rules
    
    def validate(self, metadata: Dict[str, Any]) -> List[str]:
        """
        @method validate
        @description Validate metadata against defined rules.
        
        @param metadata Dictionary containing metadata to validate
        @return List of validation errors, empty if validation passed
        """
        errors = []
        
        # Check required fields
        required_fields = self.rules.get('required_fields', [])
        for field in required_fields:
            if field not in metadata:
                errors.append(f"Missing required field: {field}")
        
        # Check field formats
        # In a real implementation, we would have more sophisticated validation
        
        return errors


def example_usage():
    """
    @function example_usage
    @description Demonstrate usage of the metadata processor.
    
    @example
    ```python
    example_usage()  # Processes example files in the current directory
    ```
    """
    # Create a processor
    processor = MetadataProcessor("config.json")
    
    # Process a file
    metadata = processor.extract_metadata(__file__)
    
    # Validate the metadata
    errors = processor.validate_metadata(metadata)
    if errors:
        print(f"Validation errors: {errors}")
    else:
        print("Metadata validation passed!")
    
    # Print the extracted metadata
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    example_usage() 
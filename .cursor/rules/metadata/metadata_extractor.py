#!/usr/bin/env python3

"""
@file metadata_extractor.py
@version 1.0.0
@author MetadataTeam
@date 2023-11-25
@license MIT

@description
Tool for extracting and validating metadata from different file types.
This script can process JavaScript, Python, and Markdown files to extract
metadata, validate it against defined standards, and generate reports.

@example
```bash
python metadata_extractor.py --source ./src --config metadata_config.json --report
```

@dependencies
- json
- os
- re
- argparse
- yaml
- colorama
- tabulate

@stability beta
@performance O(n) where n is the number of files processed
"""

import os
import re
import json
import yaml
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

try:
    from colorama import init, Fore, Style
    COLORAMA_AVAILABLE = True
    init()
except ImportError:
    COLORAMA_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class MetadataExtractor:
    """
    @class MetadataExtractor
    @description Extracts metadata from different file types and validates it
    
    This class provides capabilities to extract metadata from JavaScript, 
    Python, and Markdown files, validate it against standards, and generate
    reports on metadata coverage and quality.
    
    @stability beta
    @since 1.0.0
    @author MetadataTeam
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        @method __init__
        @description Initialize the metadata extractor with configuration
        
        @param config_path Path to the configuration file (JSON)
        """
        self.config = self._load_config(config_path) if config_path else self._default_config()
        self.results = {
            'processed_files': 0,
            'files_with_metadata': 0,
            'files_with_complete_metadata': 0,
            'missing_fields': {},
            'invalid_formats': {},
            'file_results': {},
            'by_language': {},
            'by_file_extension': {}
        }
        
        logger.info(f"Initialized MetadataExtractor{' with config from ' + config_path if config_path else ''}")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        @method _load_config
        @description Load the configuration from a JSON file
        
        @param config_path Path to the configuration file
        @return Dictionary containing the configuration
        
        @private
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """
        @method _default_config
        @description Create a default configuration
        
        @return Dictionary containing the default configuration
        
        @private
        """
        return {
            "version": "1.0.0",
            "description": "Default metadata extraction configuration",
            "requiredFields": {
                "all": ["version", "description"],
                "javascript": ["file", "version", "author", "description"],
                "python": ["file", "version", "author", "description"],
                "markdown": ["title", "version", "status"]
            },
            "formatValidation": {
                "version": r"^\d+\.\d+\.\d+$",
                "email": r"^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$",
                "date": r"^\d{4}-\d{2}-\d{2}$"
            },
            "extractionRules": {
                "javascript": {
                    "filePattern": r"\.js$|\.jsx$|\.ts$|\.tsx$",
                    "commentStyle": "jsdoc",
                    "tagPrefix": "@"
                },
                "python": {
                    "filePattern": r"\.py$",
                    "commentStyle": "docstring",
                    "tagPrefix": "@"
                },
                "markdown": {
                    "filePattern": r"\.md$|\.mdx$",
                    "commentStyle": "frontmatter",
                    "tagPrefix": ""
                }
            },
            "outputSettings": {
                "format": "json",
                "outputDir": "./metadata-output",
                "createIndexFile": True,
                "includeStats": True,
                "prettify": True
            }
        }
    
    def process_directory(self, directory_path: str, recursive: bool = True) -> Dict[str, Any]:
        """
        @method process_directory
        @description Process all files in a directory
        
        @param directory_path Path to the directory to process
        @param recursive Whether to process subdirectories
        @return Dictionary containing the extraction results
        """
        logger.info(f"Processing directory: {directory_path}")
        
        # Reset results
        self.results = {
            'processed_files': 0,
            'files_with_metadata': 0,
            'files_with_complete_metadata': 0,
            'missing_fields': {},
            'invalid_formats': {},
            'file_results': {},
            'by_language': {},
            'by_file_extension': {}
        }
        
        # Process files
        for path in self._find_files(directory_path, recursive):
            self._process_file(path)
        
        # Calculate statistics
        self._calculate_statistics()
        
        return self.results
    
    def _find_files(self, directory_path: str, recursive: bool = True) -> List[str]:
        """
        @method _find_files
        @description Find files to process in a directory
        
        @param directory_path Path to the directory to process
        @param recursive Whether to process subdirectories
        @return List of file paths to process
        
        @private
        """
        files = []
        
        # Create patterns for file types
        patterns = []
        for language, rules in self.config['extractionRules'].items():
            patterns.append(rules['filePattern'])
        
        # Compile the regex patterns
        pattern_regexes = [re.compile(pattern) for pattern in patterns]
        
        # Walk through directory
        for root, dirs, filenames in os.walk(directory_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                
                # Check if file matches any pattern
                if any(pattern.search(filename) for pattern in pattern_regexes):
                    files.append(file_path)
            
            if not recursive:
                break
        
        logger.info(f"Found {len(files)} files to process")
        return files
    
    def _process_file(self, file_path: str) -> Dict[str, Any]:
        """
        @method _process_file
        @description Process a single file
        
        @param file_path Path to the file to process
        @return Dictionary containing the extraction results for the file
        
        @private
        """
        try:
            logger.debug(f"Processing file: {file_path}")
            
            # Determine file type
            file_type = self._determine_file_type(file_path)
            if not file_type:
                logger.warning(f"Unknown file type for {file_path}, skipping")
                return {}
            
            # Increment processed files count
            self.results['processed_files'] += 1
            
            # Extract metadata
            metadata = self._extract_metadata(file_path, file_type)
            
            # Check if any metadata was found
            if metadata:
                self.results['files_with_metadata'] += 1
                
                # Validate metadata
                validation_result = self._validate_metadata(metadata, file_type)
                
                # Store results
                file_result = {
                    'file_path': file_path,
                    'file_type': file_type,
                    'metadata': metadata,
                    'validation': validation_result
                }
                
                self.results['file_results'][file_path] = file_result
                
                # Update language and extension statistics
                ext = os.path.splitext(file_path)[1].lstrip('.')
                self.results['by_file_extension'][ext] = self.results['by_file_extension'].get(ext, 0) + 1
                self.results['by_language'][file_type] = self.results['by_language'].get(file_type, 0) + 1
                
                # Check if all required fields are present
                if validation_result['valid']:
                    self.results['files_with_complete_metadata'] += 1
                
                return file_result
            else:
                logger.warning(f"No metadata found in {file_path}")
                return {}
                
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            return {}
    
    def _determine_file_type(self, file_path: str) -> Optional[str]:
        """
        @method _determine_file_type
        @description Determine the type of a file
        
        @param file_path Path to the file
        @return String identifying the file type or None if unknown
        
        @private
        """
        for language, rules in self.config['extractionRules'].items():
            pattern = rules['filePattern']
            if re.search(pattern, file_path):
                return language
        return None
    
    def _extract_metadata(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        @method _extract_metadata
        @description Extract metadata from a file
        
        @param file_path Path to the file
        @param file_type Type of the file
        @return Dictionary containing the extracted metadata
        
        @private
        """
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading {file_path}: {str(e)}")
            return {}
        
        # Extract metadata based on file type
        if file_type == 'javascript':
            return self._extract_jsdoc_metadata(content)
        elif file_type == 'python':
            return self._extract_python_metadata(content)
        elif file_type == 'markdown':
            return self._extract_markdown_metadata(content)
        else:
            return {}
    
    def _extract_jsdoc_metadata(self, content: str) -> Dict[str, Any]:
        """
        @method _extract_jsdoc_metadata
        @description Extract metadata from JSDoc comments
        
        @param content Content of the file
        @return Dictionary containing the extracted metadata
        
        @private
        """
        metadata = {}
        
        # Find the JSDoc block at the top of the file
        jsdoc_pattern = r'/\*\*(.*?)\*/'
        match = re.search(jsdoc_pattern, content, re.DOTALL)
        
        if match:
            jsdoc_content = match.group(1)
            
            # Extract tags
            tag_pattern = r'@(\w+)\s+(.*?)(?=\s+@\w+|\s*$)'
            tags = re.findall(tag_pattern, jsdoc_content, re.DOTALL)
            
            for tag_name, tag_value in tags:
                # Clean up multi-line values
                tag_value = tag_value.strip().replace('\n *', '\n')
                metadata[tag_name] = tag_value
        
        return metadata
    
    def _extract_python_metadata(self, content: str) -> Dict[str, Any]:
        """
        @method _extract_python_metadata
        @description Extract metadata from Python docstrings
        
        @param content Content of the file
        @return Dictionary containing the extracted metadata
        
        @private
        """
        metadata = {}
        
        # Find the docstring at the top of the file
        docstring_pattern = r'"""(.*?)"""'
        match = re.search(docstring_pattern, content, re.DOTALL)
        
        if match:
            docstring_content = match.group(1)
            
            # Extract tags
            tag_pattern = r'@(\w+)(?:\s+(.+?)(?=\s+@\w+|\s*$)|\s*$)'
            tags = re.findall(tag_pattern, docstring_content, re.DOTALL)
            
            for tag_name, tag_value in tags:
                # Clean up multi-line values
                tag_value = tag_value.strip()
                metadata[tag_name] = tag_value
        
        return metadata
    
    def _extract_markdown_metadata(self, content: str) -> Dict[str, Any]:
        """
        @method _extract_markdown_metadata
        @description Extract metadata from Markdown frontmatter
        
        @param content Content of the file
        @return Dictionary containing the extracted metadata
        
        @private
        """
        # Find the frontmatter block
        frontmatter_pattern = r'^---\s+(.*?)\s+---'
        match = re.search(frontmatter_pattern, content, re.DOTALL)
        
        if match:
            frontmatter_content = match.group(1)
            
            try:
                # Parse YAML frontmatter
                metadata = yaml.safe_load(frontmatter_content)
                return metadata if metadata else {}
            except Exception as e:
                logger.error(f"Error parsing frontmatter: {str(e)}")
        
        return {}
    
    def _validate_metadata(self, metadata: Dict[str, Any], file_type: str) -> Dict[str, Any]:
        """
        @method _validate_metadata
        @description Validate metadata against the configuration
        
        @param metadata Dictionary containing the metadata
        @param file_type Type of the file
        @return Dictionary containing the validation results
        
        @private
        """
        result = {
            'valid': True,
            'missing_fields': [],
            'invalid_formats': []
        }
        
        # Check required fields
        required_fields = self.config['requiredFields'].get('all', []).copy()
        if file_type in self.config['requiredFields']:
            required_fields.extend(self.config['requiredFields'][file_type])
        
        for field in required_fields:
            if field not in metadata or not metadata[field]:
                result['missing_fields'].append(field)
                result['valid'] = False
                
                # Update global statistics
                self.results['missing_fields'][field] = self.results['missing_fields'].get(field, 0) + 1
        
        # Check format validation
        for field, pattern in self.config['formatValidation'].items():
            if field in metadata and metadata[field]:
                if not re.match(pattern, str(metadata[field])):
                    result['invalid_formats'].append({
                        'field': field,
                        'value': metadata[field],
                        'pattern': pattern
                    })
                    result['valid'] = False
                    
                    # Update global statistics
                    self.results['invalid_formats'][field] = self.results['invalid_formats'].get(field, 0) + 1
        
        return result
    
    def _calculate_statistics(self) -> None:
        """
        @method _calculate_statistics
        @description Calculate statistics about the processed files
        
        @private
        """
        # Calculate percentages
        if self.results['processed_files'] > 0:
            self.results['metadata_coverage'] = (self.results['files_with_metadata'] / self.results['processed_files']) * 100
            self.results['complete_metadata_coverage'] = (self.results['files_with_complete_metadata'] / self.results['processed_files']) * 100
        else:
            self.results['metadata_coverage'] = 0
            self.results['complete_metadata_coverage'] = 0
        
        # Calculate most common issues
        self.results['most_common_missing_fields'] = sorted(
            self.results['missing_fields'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        self.results['most_common_invalid_formats'] = sorted(
            self.results['invalid_formats'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
    
    def generate_report(self, output_path: Optional[str] = None) -> str:
        """
        @method generate_report
        @description Generate a report of the metadata extraction results
        
        @param output_path Path where to save the report (optional)
        @return Path to the generated report
        """
        # Ensure we have results
        if self.results['processed_files'] == 0:
            logger.warning("No files were processed, cannot generate report")
            return ""
        
        # Create report data
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'processed_files': self.results['processed_files'],
                'files_with_metadata': self.results['files_with_metadata'],
                'files_with_complete_metadata': self.results['files_with_complete_metadata'],
                'metadata_coverage': self.results['metadata_coverage'],
                'complete_metadata_coverage': self.results['complete_metadata_coverage']
            },
            'by_language': self.results['by_language'],
            'by_file_extension': self.results['by_file_extension'],
            'most_common_missing_fields': dict(self.results['most_common_missing_fields']),
            'most_common_invalid_formats': dict(self.results['most_common_invalid_formats']),
            'file_results': {
                path: {
                    'metadata': data['metadata'],
                    'validation': data['validation']
                }
                for path, data in self.results['file_results'].items()
            }
        }
        
        # Determine output path
        if not output_path:
            output_dir = self.config['outputSettings']['outputDir']
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(output_dir, f"metadata_report_{timestamp}.json")
        
        # Save report
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2 if self.config['outputSettings']['prettify'] else None)
        
        logger.info(f"Report generated at {output_path}")
        return output_path
    
    def print_summary(self) -> None:
        """
        @method print_summary
        @description Print a summary of the metadata extraction results
        """
        if self.results['processed_files'] == 0:
            print("No files were processed.")
            return
        
        # Define colors if colorama is available
        GREEN = Fore.GREEN if COLORAMA_AVAILABLE else ''
        YELLOW = Fore.YELLOW if COLORAMA_AVAILABLE else ''
        RED = Fore.RED if COLORAMA_AVAILABLE else ''
        RESET = Style.RESET_ALL if COLORAMA_AVAILABLE else ''
        
        # Print summary
        print("\n" + "="*50)
        print(f"METADATA EXTRACTION SUMMARY")
        print("="*50)
        
        # Calculate color for coverage
        metadata_coverage = self.results['metadata_coverage']
        complete_coverage = self.results['complete_metadata_coverage']
        
        metadata_color = GREEN if metadata_coverage >= 80 else (YELLOW if metadata_coverage >= 50 else RED)
        complete_color = GREEN if complete_coverage >= 80 else (YELLOW if complete_coverage >= 50 else RED)
        
        print(f"\nProcessed {self.results['processed_files']} files:")
        print(f"- Files with metadata: {metadata_color}{self.results['files_with_metadata']} ({metadata_coverage:.1f}%){RESET}")
        print(f"- Files with complete metadata: {complete_color}{self.results['files_with_complete_metadata']} ({complete_coverage:.1f}%){RESET}")
        
        if self.results['most_common_missing_fields']:
            print("\nMost common missing fields:")
            for field, count in self.results['most_common_missing_fields']:
                print(f"- {field}: {count} files")
        
        if self.results['most_common_invalid_formats']:
            print("\nMost common invalid formats:")
            for field, count in self.results['most_common_invalid_formats']:
                print(f"- {field}: {count} files")
        
        if self.results['by_language']:
            print("\nFiles by language:")
            for language, count in self.results['by_language'].items():
                print(f"- {language}: {count} files")
        
        print("\n" + "="*50)


def main():
    """
    @function main
    @description Main entry point for the script
    """
    parser = argparse.ArgumentParser(description='Extract and validate metadata from files')
    parser.add_argument('--source', '-s', help='Source directory to scan', required=True)
    parser.add_argument('--config', '-c', help='Path to configuration file')
    parser.add_argument('--output', '-o', help='Output path for the report')
    parser.add_argument('--recursive', '-r', action='store_true', help='Process subdirectories recursively')
    parser.add_argument('--report', action='store_true', help='Generate a JSON report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create extractor
    extractor = MetadataExtractor(args.config)
    
    # Process directory
    extractor.process_directory(args.source, args.recursive)
    
    # Print summary
    extractor.print_summary()
    
    # Generate report if requested
    if args.report:
        report_path = extractor.generate_report(args.output)
        print(f"\nReport generated at: {report_path}")


if __name__ == "__main__":
    main() 
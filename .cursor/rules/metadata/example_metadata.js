/**
 * @file example_metadata.js
 * @version 1.0.0
 * @author MetadataTeam
 * @copyright 2023 Metadata Project
 * @license MIT
 * 
 * @description
 * This file demonstrates the proper implementation of metadata standards
 * in JavaScript files. It includes examples of file-level metadata,
 * function-level metadata, and class-level metadata.
 * 
 * @dependencies
 * - fs
 * - path
 * - chalk (for console output)
 * 
 * @stability stable
 * @performance O(n) where n is the number of lines in the source file
 */

const fs = require('fs');
const path = require('path');

/**
 * Configuration options for metadata extraction.
 * 
 * @typedef {Object} ExtractorOptions
 * @property {boolean} includePrivate - Whether to include private elements in extraction
 * @property {string[]} requiredFields - List of metadata fields that are required
 * @property {Object} formatRules - Rules for validating metadata formats
 * @property {string} outputDir - Directory to store extracted metadata
 */

/**
 * Metadata extraction result.
 * 
 * @typedef {Object} MetadataResult
 * @property {string} filePath - Path to the file that was processed
 * @property {string} version - Version from the file metadata
 * @property {string} author - Author from the file metadata
 * @property {string} description - Description from the file metadata
 * @property {string[]} dependencies - Dependencies from the file metadata
 * @property {Object} elements - Metadata for individual code elements (functions, classes)
 */

/**
 * Extracts metadata from source code files.
 * 
 * This class provides the core functionality for extracting and processing
 * metadata from JavaScript and TypeScript source files.
 * 
 * @class
 * @since 1.0.0
 * @author MetadataTeam
 * @stability stable
 */
class MetadataExtractor {
  /**
   * Create a new metadata extractor.
   * 
   * @param {ExtractorOptions} options - Configuration options
   */
  constructor(options = {}) {
    /**
     * Configuration options for the extractor.
     * 
     * @private
     * @type {ExtractorOptions}
     */
    this.options = {
      includePrivate: false,
      requiredFields: ['file', 'version', 'description'],
      formatRules: {
        version: /^\d+\.\d+\.\d+$/,  // Semantic versioning format
        author: /.+/,                // Non-empty author field
      },
      outputDir: './metadata',
      ...options
    };

    // Create output directory if it doesn't exist
    if (!fs.existsSync(this.options.outputDir)) {
      fs.mkdirSync(this.options.outputDir, { recursive: true });
    }

    console.log(`Initialized MetadataExtractor with options:`, this.options);
  }

  /**
   * Extract metadata from a file.
   * 
   * @param {string} filePath - Path to the file to extract metadata from
   * @returns {MetadataResult} Extracted metadata
   * @throws {Error} If the file doesn't exist or can't be read
   */
  extract(filePath) {
    console.log(`Extracting metadata from ${filePath}`);

    // Check if file exists
    if (!fs.existsSync(filePath)) {
      throw new Error(`File not found: ${filePath}`);
    }

    // Read file content
    const content = fs.readFileSync(filePath, 'utf8');
    
    // Extract file-level metadata
    const metadata = this._extractFileMetadata(content);
    metadata.filePath = filePath;
    
    // Extract element-level metadata (functions, classes)
    metadata.elements = this._extractElementMetadata(content);
    
    // Store the extracted metadata
    this._storeMetadata(filePath, metadata);
    
    return metadata;
  }

  /**
   * Extract file-level metadata from file content.
   * 
   * @private
   * @param {string} content - File content
   * @returns {Object} Extracted file metadata
   */
  _extractFileMetadata(content) {
    // This is a simplified example - in a real implementation,
    // we would use a parser to extract JSDoc comments
    
    const metadata = {
      version: this._extractTag(content, '@version'),
      author: this._extractTag(content, '@author'),
      description: this._extractTag(content, '@description'),
      dependencies: this._extractDependencies(content),
      stability: this._extractTag(content, '@stability'),
      performance: this._extractTag(content, '@performance')
    };
    
    return metadata;
  }

  /**
   * Extract element-level metadata from file content.
   * 
   * @private
   * @param {string} content - File content
   * @returns {Object} Extracted element metadata
   */
  _extractElementMetadata(content) {
    // In a real implementation, we would parse the code to identify
    // functions, classes, etc. and extract their JSDoc comments
    
    // This is a placeholder for demonstration
    return {
      // Example function metadata
      functions: [
        {
          name: 'extract',
          description: 'Extract metadata from a file',
          params: [
            { name: 'filePath', type: 'string', description: 'Path to the file' }
          ],
          returns: { type: 'MetadataResult', description: 'Extracted metadata' },
          examples: ['const metadata = extractor.extract("./file.js");']
        }
      ],
      // Example class metadata
      classes: [
        {
          name: 'MetadataExtractor',
          description: 'Extracts metadata from source code files',
          methods: ['extract', '_extractFileMetadata', '_extractElementMetadata']
        }
      ]
    };
  }

  /**
   * Extract a specific tag from file content.
   * 
   * @private
   * @param {string} content - File content
   * @param {string} tag - Tag to extract (e.g., '@version')
   * @returns {string} Tag value or empty string if not found
   */
  _extractTag(content, tag) {
    // Simple regex to extract tag content - in a real implementation,
    // we would use a more robust parser
    const regex = new RegExp(`${tag}\\s*(.+)`, 'i');
    const match = content.match(regex);
    return match ? match[1].trim() : '';
  }

  /**
   * Extract dependencies from file content.
   * 
   * @private
   * @param {string} content - File content
   * @returns {string[]} List of dependencies
   */
  _extractDependencies(content) {
    // In a real implementation, we would look for both require() and import statements,
    // as well as @dependencies tags in JSDoc
    
    // For this example, we'll return some placeholder dependencies
    return ['fs', 'path'];
  }

  /**
   * Store extracted metadata.
   * 
   * @private
   * @param {string} filePath - Source file path
   * @param {Object} metadata - Extracted metadata
   */
  _storeMetadata(filePath, metadata) {
    const basename = path.basename(filePath);
    const outputPath = path.join(this.options.outputDir, `${basename}.metadata.json`);
    
    fs.writeFileSync(
      outputPath,
      JSON.stringify(metadata, null, 2),
      'utf8'
    );
    
    console.log(`Metadata stored in ${outputPath}`);
  }
  
  /**
   * Validate metadata against defined rules.
   * 
   * @param {Object} metadata - Metadata to validate
   * @returns {string[]} Validation errors, empty array if valid
   */
  validate(metadata) {
    const errors = [];
    
    // Check required fields
    for (const field of this.options.requiredFields) {
      if (!metadata[field]) {
        errors.push(`Missing required field: ${field}`);
      }
    }
    
    // Check format rules
    for (const [field, pattern] of Object.entries(this.options.formatRules)) {
      if (metadata[field] && !pattern.test(metadata[field])) {
        errors.push(`Invalid format for ${field}: ${metadata[field]}`);
      }
    }
    
    return errors;
  }
}

/**
 * Configuration for the metadata collector.
 * 
 * @typedef {Object} CollectorOptions
 * @property {string} outputFormat - Format for collected metadata (json, yaml, etc.)
 * @property {boolean} validateMetadata - Whether to validate metadata during collection
 * @property {string} collectionPath - Path to store the collected metadata
 */

/**
 * Collects metadata from multiple files.
 * 
 * @class
 * @since 1.0.0
 * @author MetadataTeam
 */
class MetadataCollector {
  /**
   * Create a new metadata collector.
   * 
   * @param {CollectorOptions} options - Configuration options
   */
  constructor(options = {}) {
    this.options = {
      outputFormat: 'json',
      validateMetadata: true,
      collectionPath: './metadata-collection',
      ...options
    };
    
    this.extractor = new MetadataExtractor();
    this.collection = {};
    
    // Create collection directory
    if (!fs.existsSync(this.options.collectionPath)) {
      fs.mkdirSync(this.options.collectionPath, { recursive: true });
    }
  }
  
  /**
   * Collect metadata from files matching a pattern.
   * 
   * @param {string} pattern - Glob pattern for files to process
   * @returns {Object} Collected metadata by file
   */
  collectFromPattern(pattern) {
    // In a real implementation, we would use a glob library to match files,
    // then process each file with the extractor
    
    console.log(`Collecting metadata from files matching: ${pattern}`);
    
    // For this example, we'll just process the current file
    try {
      const metadata = this.extractor.extract(__filename);
      this.collection[__filename] = metadata;
    } catch (error) {
      console.error(`Error processing ${__filename}:`, error);
    }
    
    return this.collection;
  }
  
  /**
   * Generate a report from collected metadata.
   * 
   * @param {string} [outputPath] - Custom output path for the report
   * @returns {string} Path to the generated report
   */
  generateReport(outputPath) {
    const reportPath = outputPath || path.join(
      this.options.collectionPath,
      `metadata-report.${this.options.outputFormat}`
    );
    
    const report = {
      generated: new Date().toISOString(),
      fileCount: Object.keys(this.collection).length,
      files: this.collection
    };
    
    fs.writeFileSync(
      reportPath,
      JSON.stringify(report, null, 2),
      'utf8'
    );
    
    console.log(`Report generated at ${reportPath}`);
    return reportPath;
  }
}

/**
 * Example usage of the metadata functionality.
 */
function exampleUsage() {
  // Create an extractor
  const extractor = new MetadataExtractor({
    includePrivate: true,
    outputDir: './example-metadata'
  });
  
  // Extract metadata from this file
  try {
    const metadata = extractor.extract(__filename);
    console.log('Extracted metadata:', metadata);
    
    // Validate the metadata
    const errors = extractor.validate(metadata);
    if (errors.length > 0) {
      console.error('Validation errors:', errors);
    } else {
      console.log('Metadata validation passed!');
    }
  } catch (error) {
    console.error('Error extracting metadata:', error);
  }
  
  // Create a collector and generate a report
  const collector = new MetadataCollector();
  collector.collectFromPattern('./*.js');
  collector.generateReport();
}

// Export the classes
module.exports = {
  MetadataExtractor,
  MetadataCollector
};

// Run example if this file is executed directly
if (require.main === module) {
  exampleUsage();
} 
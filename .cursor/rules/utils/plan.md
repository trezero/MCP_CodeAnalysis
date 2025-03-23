# Rules System & MCP Integration Plan

## Overview

This document outlines the available scripts and tools in the rules system that could be used for:

1. Enhancing rule configuration and maintenance
2. Integration with MCP (Machine Coded Programmer) servers/clients
3. Extending AI capabilities with code analysis tools

## Available Scripts

### Rule Configuration & Maintenance

| Script               | Path                                       | Purpose                                                    | Status    |
| -------------------- | ------------------------------------------ | ---------------------------------------------------------- | --------- |
| check_all_rules.py   | `.cursor/rules/utils/check_all_rules.py`   | Checks rule files for proper frontmatter and configuration | ✅ Active |
| fix_all_rules.py     | `.cursor/rules/utils/fix_all_rules.py`     | Fixes rule files by adding proper frontmatter              | ✅ Active |
| check_frontmatter.py | `.cursor/rules/utils/check_frontmatter.py` | Identifies files missing frontmatter                       | ✅ Active |
| fix_frontmatter.py   | `.cursor/rules/utils/fix_frontmatter.py`   | Adds frontmatter to files missing it                       | ✅ Active |

### Code Quality Analysis (Potential MCP Tools)

| Script                    | Path                                                   | Purpose                      | MCP Potential |
| ------------------------- | ------------------------------------------------------ | ---------------------------- | ------------- |
| complexity_analyzer.py    | `.cursor/rules/code_quality/complexity_analyzer.py`    | Analyzes code complexity     | ⭐⭐⭐ High   |
| documentation_analyzer.py | `.cursor/rules/code_quality/documentation_analyzer.py` | Checks documentation quality | ⭐⭐⭐ High   |
| test_coverage_analyzer.py | `.cursor/rules/code_quality/test_coverage_analyzer.py` | Analyzes test coverage       | ⭐⭐ Medium   |
| duplication_detector.py   | `.cursor/rules/code_quality/duplication_detector.py`   | Identifies code duplication  | ⭐⭐⭐ High   |

### Code Health Metrics (Potential MCP Tools)

| Script       | Path                                     | Purpose                                      | MCP Potential |
| ------------ | ---------------------------------------- | -------------------------------------------- | ------------- |
| metrics.py   | `.cursor/rules/code_health/metrics.py`   | Calculates various code health metrics       | ⭐⭐⭐ High   |
| dashboard.py | `.cursor/rules/code_health/dashboard.py` | Generates an HTML dashboard for code metrics | ⭐ Low        |

### Debug History Tools (Potential MCP Tools)

| Script           | Path                                           | Purpose                                                | MCP Potential |
| ---------------- | ---------------------------------------------- | ------------------------------------------------------ | ------------- |
| vector_db.py     | `.cursor/rules/debug_history/vector_db.py`     | Vector database for semantic search of similar issues  | ⭐⭐⭐ High   |
| web_interface.py | `.cursor/rules/debug_history/web_interface.py` | Web interface for browsing and searching debug history | ⭐⭐ Medium   |

### Cross-Reference Tools (Potential MCP Tools)

| Script                        | Path                                                          | Purpose                                        | MCP Potential |
| ----------------------------- | ------------------------------------------------------------- | ---------------------------------------------- | ------------- |
| dependency_graph_generator.py | `.cursor/rules/cross_reference/dependency_graph_generator.py` | Generates dependency graphs between components | ⭐⭐⭐ High   |
| impact_analyzer.py            | `.cursor/rules/cross_reference/impact_analyzer.py`            | Analyzes impact of changes across codebase     | ⭐⭐⭐ High   |
| reference_extractor.py        | `.cursor/rules/cross_reference/reference_extractor.py`        | Extracts references between code components    | ⭐⭐ Medium   |

### Delta Analysis

The `.cursor/rules/delta` directory contains only the rule file (`delta.mdc`) with guidelines for tracking and managing code changes. It does not contain any Python scripts or tools that could be integrated with MCP.

### Documentation

The `.cursor/rules/documentation` directory contains only the rule file (`why_documentation.mdc`) with guidelines for including "Why" sections in documentation to explain the rationale behind design decisions. It does not contain any Python scripts or tools that could be integrated with MCP.

### Feedback Analysis Tools (Potential MCP Tools)

| Script                | Path                                           | Purpose                                                  | MCP Potential |
| --------------------- | ---------------------------------------------- | -------------------------------------------------------- | ------------- |
| feedback_collector.py | `.cursor/rules/feedback/feedback_collector.py` | Collects feedback from various sources and normalizes it | ⭐⭐⭐ High   |
| sentiment_analyzer.py | `.cursor/rules/feedback/sentiment_analyzer.py` | Analyzes sentiment in feedback and identifies themes     | ⭐⭐⭐ High   |
| feedback_dashboard.py | `.cursor/rules/feedback/feedback_dashboard.py` | Generates interactive dashboard for visualizing feedback | ⭐⭐ Medium   |

### Glossary Tools (Potential MCP Tools)

| Script                 | Path                                            | Purpose                                              | MCP Potential |
| ---------------------- | ----------------------------------------------- | ---------------------------------------------------- | ------------- |
| glossary_generator.py  | `.cursor/rules/glossary/glossary_generator.py`  | Generates formatted glossary from term definitions   | ⭐⭐ Medium   |
| term_extractor.py      | `.cursor/rules/glossary/term_extractor.py`      | Extracts domain-specific terms from the codebase     | ⭐⭐⭐ High   |
| term_usage_analyzer.py | `.cursor/rules/glossary/term_usage_analyzer.py` | Analyzes how glossary terms are used in the codebase | ⭐⭐⭐ High   |

### Knowledge Graph Tools (Potential MCP Tools)

| Script       | Path                                         | Purpose                                                           | MCP Potential |
| ------------ | -------------------------------------------- | ----------------------------------------------------------------- | ------------- |
| generator.py | `.cursor/rules/knowledge_graph/generator.py` | Generates a centralized knowledge graph from various data sources | ⭐⭐⭐ High   |
| visualize.py | `.cursor/rules/knowledge_graph/visualize.py` | Creates visualizations of the knowledge graph                     | ⭐⭐ Medium   |

### Maturity Model Tools (Potential MCP Tools)

| Script                | Path                                                 | Purpose                                                    | MCP Potential |
| --------------------- | ---------------------------------------------------- | ---------------------------------------------------------- | ------------- |
| maturity_analyzer.py  | `.cursor/rules/maturity_model/maturity_analyzer.py`  | Analyzes component maturity throughout the codebase        | ⭐⭐⭐ High   |
| maturity_dashboard.py | `.cursor/rules/maturity_model/maturity_dashboard.py` | Generates interactive dashboard for maturity visualization | ⭐⭐ Medium   |

### Memory Anchor Tools (Potential MCP Tools)

| Script                | Path                                                 | Purpose                                                      | MCP Potential |
| --------------------- | ---------------------------------------------------- | ------------------------------------------------------------ | ------------- |
| anchor_extractor.py   | `.cursor/rules/memory_anchors/anchor_extractor.py`   | Extracts memory anchors from the codebase                    | ⭐⭐⭐ High   |
| anchor_navigator.py   | `.cursor/rules/memory_anchors/anchor_navigator.py`   | Provides web-based interface for navigating memory anchors   | ⭐⭐ Medium   |
| anchor_search_tool.py | `.cursor/rules/memory_anchors/anchor_search_tool.py` | CLI tool for searching and navigating to memory anchors      | ⭐⭐⭐ High   |
| anchor_visualizer.py  | `.cursor/rules/memory_anchors/anchor_visualizer.py`  | Generates visualizations of memory anchors and relationships | ⭐⭐ Medium   |

### Pine Script Tools

| Script         | Path                                 | Purpose                                  | MCP Potential |
| -------------- | ------------------------------------ | ---------------------------------------- | ------------- |
| pine_linter.py | `.cursor/rules/utils/pine_linter.py` | Lints Pine Script files                  | ⭐⭐ Medium   |
| pine_fixer.py  | `.cursor/rules/utils/pine_fixer.py`  | Fixes common issues in Pine Script files | ⭐⭐ Medium   |

## Metadata Tools (Potential MCP Tools)

1. `.cursor/rules/metadata/metadata_extractor.py` - Extracts and validates metadata from different file types (MCP Potential: ⭐⭐⭐ High)
2. `.cursor/rules/metadata/metadata_dashboard.py` - Interactive dashboard for visualizing metadata coverage and quality (MCP Potential: ⭐⭐ Medium)

## Monetization Analysis Tools (Potential MCP Tools)

1. `.cursor/rules/monetization_analysis/revenue_potential_analyzer.py` - Analyzes codebase to identify monetization opportunities (MCP Potential: ⭐⭐⭐ High)
2. `.cursor/rules/monetization_analysis/pricing_strategy_analyzer.py` - Identifies pricing patterns and suggests pricing strategies (MCP Potential: ⭐⭐⭐ High)
3. `.cursor/rules/monetization_analysis/feature_value_analyzer.py` - Evaluates potential value of features for monetization (MCP Potential: ⭐⭐⭐ High)
4. `.cursor/rules/monetization_analysis/ab_testing_analyzer.py` - Analyzes A/B testing for monetization optimization (MCP Potential: ⭐⭐ Medium)

## Style Guide Tools (Potential MCP Tools)

| Script                     | Path                                                   | Purpose                                                  | MCP Potential |
| -------------------------- | ------------------------------------------------------ | -------------------------------------------------------- | ------------- |
| documentation_generator.py | `.cursor/rules/style_guide/documentation_generator.py` | Generates style guide documentation from code examples   | ⭐⭐ Medium   |
| linter_config_generator.py | `.cursor/rules/style_guide/linter_config_generator.py` | Creates linter configurations based on style guide rules | ⭐⭐⭐ High   |
| style_checker.py           | `.cursor/rules/style_guide/style_checker.py`           | Analyzes code adherence to style guidelines              | ⭐⭐⭐ High   |

## Web3 Security Tools (Potential MCP Tools)

| Script                   | Path                                                   | Purpose                                               | MCP Potential |
| ------------------------ | ------------------------------------------------------ | ----------------------------------------------------- | ------------- |
| contract_analyzer.py     | `.cursor/rules/web3_security/contract_analyzer.py`     | Analyzes smart contracts for security vulnerabilities | ⭐⭐⭐ High   |
| transaction_validator.py | `.cursor/rules/web3_security/transaction_validator.py` | Validates transaction patterns for security issues    | ⭐⭐⭐ High   |
| permission_analyzer.py   | `.cursor/rules/web3_security/permission_analyzer.py`   | Analyzes permission models in smart contracts         | ⭐⭐⭐ High   |
| api_security_scanner.py  | `.cursor/rules/web3_security/api_security_scanner.py`  | Scans Web3 APIs for security vulnerabilities          | ⭐⭐⭐ High   |
| gas_optimizer.py         | `.cursor/rules/web3_security/gas_optimizer.py`         | Optimizes gas usage while maintaining security        | ⭐⭐ Medium   |

## MCP Integration Plan

### Phase 1: Tool Adaptation

1. **Complexity Analyzer Integration**

   - Create a Flask/FastAPI wrapper around complexity_analyzer.py
   - Expose endpoint: `/analyze_complexity`
   - Add to MCP configuration in `.cursor/mcp.json`

2. **Documentation Analyzer Integration**

   - Create a Flask/FastAPI wrapper around documentation_analyzer.py
   - Expose endpoint: `/analyze_documentation`
   - Add to MCP configuration

3. **Code Duplication Detector Integration**

   - Create a Flask/FastAPI wrapper around duplication_detector.py
   - Expose endpoint: `/detect_duplication`
   - Add to MCP configuration

4. **Debug History Vector Search Integration**

   - Create a Flask/FastAPI wrapper around vector_db.py
   - Expose endpoint: `/search_similar_issues`
   - Add to MCP configuration

5. **Dependency Graph Generator Integration**

   - Create a Flask/FastAPI wrapper around dependency_graph_generator.py
   - Expose endpoint: `/generate_dependency_graph`
   - Add to MCP configuration

6. **Impact Analysis Integration**

   - Create a Flask/FastAPI wrapper around impact_analyzer.py
   - Expose endpoint: `/analyze_change_impact`
   - Add to MCP configuration

7. **Sentiment Analysis Integration**

   - Create a Flask/FastAPI wrapper around sentiment_analyzer.py
   - Expose endpoint: `/analyze_sentiment`
   - Add to MCP configuration

8. **Feedback Collection Integration**

   - Create a Flask/FastAPI wrapper around feedback_collector.py
   - Expose endpoint: `/collect_feedback`
   - Add to MCP configuration

9. **Term Extraction Integration**

   - Create a Flask/FastAPI wrapper around term_extractor.py
   - Expose endpoint: `/extract_terms`
   - Add to MCP configuration

10. **Term Usage Analysis Integration**

    - Create a Flask/FastAPI wrapper around term_usage_analyzer.py
    - Expose endpoint: `/analyze_term_usage`
    - Add to MCP configuration

11. **Knowledge Graph Generation Integration**

    - Create a Flask/FastAPI wrapper around generator.py
    - Expose endpoint: `/generate_knowledge_graph`
    - Add to MCP configuration

12. **Knowledge Graph Visualization Integration**

    - Create a Flask/FastAPI wrapper around visualize.py
    - Expose endpoint: `/visualize_knowledge_graph`
    - Add to MCP configuration

13. **Maturity Analysis Integration**

    - Create a Flask/FastAPI wrapper around maturity_analyzer.py
    - Expose endpoint: `/analyze_maturity`
    - Add to MCP configuration

14. **Maturity Dashboard Integration**

    - Create a Flask/FastAPI wrapper around maturity_dashboard.py
    - Expose endpoint: `/generate_maturity_dashboard`
    - Add to MCP configuration

15. **Memory Anchor Extraction Integration**

    - Create a Flask/FastAPI wrapper around anchor_extractor.py
    - Expose endpoint: `/extract_memory_anchors`
    - Add to MCP configuration

16. **Memory Anchor Search Integration**

    - Create a Flask/FastAPI wrapper around anchor_search_tool.py
    - Expose endpoint: `/search_memory_anchors`
    - Add to MCP configuration

17. **Memory Anchor Visualization Integration**

    - Create a Flask/FastAPI wrapper around anchor_visualizer.py
    - Expose endpoint: `/visualize_memory_anchors`
    - Add to MCP configuration

18. **Metadata Extraction Integration**

    - Create a Flask/FastAPI wrapper around metadata_extractor.py
    - Expose endpoint: `/extract_metadata`
    - Add to MCP configuration

19. **Metadata Dashboard Integration**

    - Create a Flask/FastAPI wrapper around metadata_dashboard.py
    - Expose endpoint: `/metadata_dashboard`
    - Add to MCP configuration

20. **Revenue Potential Analysis Integration**

    - Create a Flask/FastAPI wrapper around revenue_potential_analyzer.py
    - Expose endpoint: `/analyze_revenue_potential`
    - Add to MCP configuration

21. **Pricing Strategy Analysis Integration**

    - Create a Flask/FastAPI wrapper around pricing_strategy_analyzer.py
    - Expose endpoint: `/analyze_pricing_strategy`
    - Add to MCP configuration

22. **Feature Value Analysis Integration**

    - Create a Flask/FastAPI wrapper around feature_value_analyzer.py
    - Expose endpoint: `/analyze_feature_value`
    - Add to MCP configuration

23. **A/B Testing Analysis Integration**

    - Create a Flask/FastAPI wrapper around ab_testing_analyzer.py
    - Expose endpoint: `/analyze_ab_testing`
    - Add to MCP configuration

24. **Style Guide Documentation Generation Integration**

    - Create a Flask/FastAPI wrapper around documentation_generator.py
    - Expose endpoint: `/generate_style_documentation`
    - Add to MCP configuration

25. **Linter Configuration Generation Integration**

    - Create a Flask/FastAPI wrapper around linter_config_generator.py
    - Expose endpoint: `/generate_linter_config`
    - Add to MCP configuration

26. **Style Checking Integration**

    - Create a Flask/FastAPI wrapper around style_checker.py
    - Expose endpoint: `/check_style_adherence`
    - Add to MCP configuration

27. **Smart Contract Analysis Integration**

    - Create a Flask/FastAPI wrapper around contract_analyzer.py
    - Expose endpoint: `/analyze_contract`
    - Add to MCP configuration

28. **Transaction Validation Integration**

    - Create a Flask/FastAPI wrapper around transaction_validator.py
    - Expose endpoint: `/validate_transaction`
    - Add to MCP configuration

29. **Permission Analysis Integration**

    - Create a Flask/FastAPI wrapper around permission_analyzer.py
    - Expose endpoint: `/analyze_permissions`
    - Add to MCP configuration

30. **API Security Scanning Integration**

    - Create a Flask/FastAPI wrapper around api_security_scanner.py
    - Expose endpoint: `/scan_web3_api`
    - Add to MCP configuration

31. **Gas Optimization Integration**

    - Create a Flask/FastAPI wrapper around gas_optimizer.py
    - Expose endpoint: `/optimize_gas`
    - Add to MCP configuration

### Phase 2: MCP Server Setup

```json
// Example updated mcp.json
{
  "version": "1.0",
  "servers": [
    {
      "name": "Code Analysis MCP",
      "url": "http://localhost:7777/mcp",
      "description": "AI-powered code analysis and suggestions",
      "tools": [
        {
          "name": "analyze_complexity",
          "description": "Analyze code complexity and suggest improvements",
          "parameters": {
            "code": {
              "type": "string",
              "description": "Source code to analyze"
            },
            "language": {
              "type": "string",
              "description": "Programming language of the code"
            }
          }
        },
        {
          "name": "detect_duplication",
          "description": "Detect code duplication and suggest refactoring",
          "parameters": {
            "code": {
              "type": "string",
              "description": "Source code to analyze"
            },
            "threshold": {
              "type": "number",
              "description": "Similarity threshold (0.0-1.0)"
            }
          }
        },
        {
          "name": "analyze_documentation",
          "description": "Analyze code documentation quality",
          "parameters": {
            "code": {
              "type": "string",
              "description": "Source code to analyze"
            }
          }
        },
        {
          "name": "search_similar_issues",
          "description": "Find similar debugging issues using vector search",
          "parameters": {
            "issue_description": {
              "type": "string",
              "description": "Description of the current issue"
            },
            "code_context": {
              "type": "string",
              "description": "Code context where the issue occurs"
            }
          }
        },
        {
          "name": "generate_dependency_graph",
          "description": "Generate a dependency graph for code components",
          "parameters": {
            "file_path": {
              "type": "string",
              "description": "Path to the file to analyze"
            },
            "depth": {
              "type": "number",
              "description": "Depth of dependencies to analyze"
            }
          }
        },
        {
          "name": "analyze_change_impact",
          "description": "Analyze the impact of code changes across the codebase",
          "parameters": {
            "file_path": {
              "type": "string",
              "description": "Path to the file being changed"
            },
            "changes": {
              "type": "string",
              "description": "Description or diff of the changes"
            }
          }
        },
        {
          "name": "analyze_sentiment",
          "description": "Analyze sentiment in feedback and identify themes",
          "parameters": {
            "feedback": {
              "type": "string",
              "description": "Feedback text to analyze"
            }
          }
        },
        {
          "name": "collect_feedback",
          "description": "Collect feedback from various sources and normalize it",
          "parameters": {
            "source": {
              "type": "string",
              "description": "Source of feedback"
            }
          }
        },
        {
          "name": "extract_terms",
          "description": "Extract domain-specific terms from the codebase",
          "parameters": {
            "code": {
              "type": "string",
              "description": "Source code to analyze"
            }
          }
        },
        {
          "name": "analyze_term_usage",
          "description": "Analyze how glossary terms are used in the codebase",
          "parameters": {
            "code": {
              "type": "string",
              "description": "Source code to analyze"
            }
          }
        },
        {
          "name": "generate_knowledge_graph",
          "description": "Generate a centralized knowledge graph from various data sources",
          "parameters": {
            "data_sources": {
              "type": "array",
              "description": "List of data sources to include in the knowledge graph"
            }
          }
        },
        {
          "name": "visualize_knowledge_graph",
          "description": "Create visualizations of the knowledge graph",
          "parameters": {
            "graph_data": {
              "type": "string",
              "description": "Serialized graph data to visualize"
            }
          }
        },
        {
          "name": "analyze_maturity",
          "description": "Analyze component maturity throughout the codebase",
          "parameters": {
            "file_path": {
              "type": "string",
              "description": "Path to the file to analyze"
            }
          }
        },
        {
          "name": "generate_maturity_dashboard",
          "description": "Generate interactive dashboard for maturity visualization",
          "parameters": {
            "file_path": {
              "type": "string",
              "description": "Path to the file to analyze"
            }
          }
        },
        {
          "name": "extract_memory_anchors",
          "description": "Extract memory anchors from the codebase",
          "parameters": {
            "code": {
              "type": "string",
              "description": "Source code to analyze"
            }
          }
        },
        {
          "name": "search_memory_anchors",
          "description": "Search for memory anchors in the codebase",
          "parameters": {
            "query": {
              "type": "string",
              "description": "Query to search for memory anchors"
            }
          }
        },
        {
          "name": "visualize_memory_anchors",
          "description": "Visualize memory anchors in the codebase",
          "parameters": {
            "code": {
              "type": "string",
              "description": "Source code to visualize"
            }
          }
        },
        {
          "name": "extract_metadata",
          "description": "Extract metadata from the codebase",
          "parameters": {
            "source_dir": {
              "type": "string",
              "description": "Source directory to extract metadata from"
            },
            "config_options": {
              "type": "string",
              "description": "Configuration options for metadata extraction"
            }
          }
        },
        {
          "name": "metadata_dashboard",
          "description": "Generate a metadata dashboard",
          "parameters": {
            "report_path": {
              "type": "string",
              "description": "Path to the metadata report"
            },
            "visualization_options": {
              "type": "string",
              "description": "Visualization options for the metadata dashboard"
            }
          }
        },
        {
          "name": "analyze_revenue_potential",
          "description": "Analyze codebase to identify monetization opportunities",
          "parameters": {
            "codebase_path": {
              "type": "string",
              "description": "Path to the codebase to analyze"
            }
          }
        },
        {
          "name": "analyze_pricing_strategy",
          "description": "Identify pricing patterns and suggest pricing strategies",
          "parameters": {
            "codebase_path": {
              "type": "string",
              "description": "Path to the codebase to analyze"
            }
          }
        },
        {
          "name": "analyze_feature_value",
          "description": "Evaluate potential value of features for monetization",
          "parameters": {
            "feature_path": {
              "type": "string",
              "description": "Path to the feature to analyze"
            }
          }
        },
        {
          "name": "analyze_ab_testing",
          "description": "Analyze A/B testing for monetization optimization",
          "parameters": {
            "ab_testing_path": {
              "type": "string",
              "description": "Path to the A/B testing results"
            }
          }
        },
        {
          "name": "generate_style_documentation",
          "description": "Generate style guide documentation from code examples",
          "parameters": {
            "code": {
              "type": "string",
              "description": "Source code to analyze"
            }
          }
        },
        {
          "name": "generate_linter_config",
          "description": "Creates linter configurations based on style guide rules",
          "parameters": {
            "style_guide_path": {
              "type": "string",
              "description": "Path to the style guide to analyze"
            }
          }
        },
        {
          "name": "check_style_adherence",
          "description": "Analyzes code adherence to style guidelines",
          "parameters": {
            "code": {
              "type": "string",
              "description": "Source code to analyze"
            }
          }
        },
        {
          "name": "analyze_contract",
          "description": "Analyzes smart contracts for security vulnerabilities",
          "parameters": {
            "contract_path": {
              "type": "string",
              "description": "Path to the smart contract to analyze"
            }
          }
        },
        {
          "name": "validate_transaction",
          "description": "Validates transaction patterns for security issues",
          "parameters": {
            "transaction_path": {
              "type": "string",
              "description": "Path to the transaction to validate"
            }
          }
        },
        {
          "name": "analyze_permissions",
          "description": "Analyzes permission models in smart contracts",
          "parameters": {
            "contract_path": {
              "type": "string",
              "description": "Path to the smart contract to analyze"
            }
          }
        },
        {
          "name": "scan_web3_api",
          "description": "Scans Web3 APIs for security vulnerabilities",
          "parameters": {
            "api_url": {
              "type": "string",
              "description": "URL of the Web3 API to scan"
            }
          }
        },
        {
          "name": "optimize_gas",
          "description": "Optimizes gas usage while maintaining security",
          "parameters": {
            "contract_path": {
              "type": "string",
              "description": "Path to the smart contract to optimize"
            }
          }
        }
      ]
    }
  ]
}
```

### Phase 3: API Implementation

Create wrapper script `mcp_server.py` to implement the API endpoints:

```python
from flask import Flask, request, jsonify
import sys
import os

# Add parent directory to path to import from different modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from code_quality.complexity_analyzer import analyze_complexity
from code_quality.duplication_detector import detect_duplication
from code_quality.documentation_analyzer import analyze_documentation
from debug_history.vector_db import search_similar_issues
from cross_reference.dependency_graph_generator import generate_dependency_graph
from cross_reference.impact_analyzer import analyze_impact
from feedback.sentiment_analyzer import SentimentAnalyzer
from feedback.feedback_collector import FeedbackCollector

app = Flask(__name__)

@app.route('/mcp/analyze_complexity', methods=['POST'])
def complexity_endpoint():
    data = request.json
    code = data.get('code', '')
    language = data.get('language', 'python')

    results = analyze_complexity(code, language)
    return jsonify(results)

@app.route('/mcp/search_similar_issues', methods=['POST'])
def similar_issues_endpoint():
    data = request.json
    issue_description = data.get('issue_description', '')
    code_context = data.get('code_context', '')

    results = search_similar_issues(issue_description, code_context)
    return jsonify(results)

@app.route('/mcp/generate_dependency_graph', methods=['POST'])
def dependency_graph_endpoint():
    data = request.json
    file_path = data.get('file_path', '')
    depth = data.get('depth', 2)

    results = generate_dependency_graph(file_path, depth)
    return jsonify(results)

@app.route('/mcp/analyze_change_impact', methods=['POST'])
def impact_analysis_endpoint():
    data = request.json
    file_path = data.get('file_path', '')
    changes = data.get('changes', '')

    results = analyze_impact(file_path, changes)
    return jsonify(results)

@app.route('/mcp/analyze_sentiment', methods=['POST'])
def sentiment_analysis_endpoint():
    data = request.json
    feedback = data.get('feedback', '')

    analyzer = SentimentAnalyzer()
    results = analyzer._analyze_sentiment(feedback)
    return jsonify(results)

@app.route('/mcp/collect_feedback', methods=['POST'])
def feedback_collection_endpoint():
    data = request.json
    source = data.get('source', '')

    collector = FeedbackCollector(output_dir='./feedback_output')

    if source.endswith('.csv'):
        results = collector.collect_from_csv(source)
    elif source.endswith('.json'):
        results = collector.collect_from_json(source)
    elif source.endswith('.db'):
        results = collector.collect_from_database(source, 'SELECT * FROM feedback')
    else:
        return jsonify({"error": "Unsupported source format"})

    return jsonify({"message": f"Collected feedback from {source}", "count": len(results)})

@app.route('/mcp/extract_terms', methods=['POST'])
def term_extraction_endpoint():
    data = request.json
    code = data.get('code', '')

    # Create a temporary file to hold the code
    with open('temp_code.txt', 'w', encoding='utf-8') as f:
        f.write(code)

    # Define patterns for term extraction
    patterns = {
        "class": r'class\s+(\w+)',
        "function": r'function\s+(\w+)',
        "method": r'(\w+)\s*\([^)]*\)\s*{',
        "variable": r'(let|const|var)\s+(\w+)\s*=',
        "component": r'<(\w+)[^>]*>',
        "python_class": r'class\s+(\w+)',
        "python_function": r'def\s+(\w+)'
    }

    # Extract terms
    from glossary.term_extractor import extract_terms
    terms = extract_terms('temp_code.txt', patterns)

    # Generate glossary entries
    from glossary.term_extractor import generate_glossary_entry
    entries = [generate_glossary_entry(term, data) for term, data in terms.items()]

    # Remove the temporary file
    os.remove('temp_code.txt')

    return jsonify({"terms": entries})

@app.route('/mcp/analyze_term_usage', methods=['POST'])
def term_usage_analysis_endpoint():
    data = request.json
    code = data.get('code', '')
    glossary_file = data.get('glossary_file', '')

    if not os.path.exists(glossary_file):
        return jsonify({"error": "Glossary file not found"})

    # Create a temporary file to hold the code
    with open('temp_code.txt', 'w', encoding='utf-8') as f:
        f.write(code)

    # Analyze term usage
    from glossary.term_usage_analyzer import TermUsageAnalyzer
    analyzer = TermUsageAnalyzer(glossary_file)
    analyzer.analyze_file('temp_code.txt')

    # Generate report
    report = {
        'term_counts': dict(analyzer.term_counts),
        'term_usage': dict(analyzer.term_usage)
    }

    # Remove the temporary file
    os.remove('temp_code.txt')

    return jsonify(report)

@app.route('/mcp/generate_knowledge_graph', methods=['POST'])
def knowledge_graph_generation_endpoint():
    data = request.json
    data_sources = data.get('data_sources', [])

    # Create the necessary directory structure
    os.makedirs('./knowledge_graph', exist_ok=True)
    os.makedirs('./knowledge_graph/visualizations', exist_ok=True)

    # Import and use the knowledge graph generator
    from knowledge_graph.generator import generate_knowledge_graph, save_knowledge_graph

    # Generate the knowledge graph
    knowledge_graph = generate_knowledge_graph()

    # Save the knowledge graph to a file
    output_path = './knowledge_graph/graph.json'
    save_knowledge_graph(knowledge_graph, output_path)

    # Return basic stats about the knowledge graph
    node_count = len(knowledge_graph['nodes'])
    edge_count = len(knowledge_graph['edges'])

    return jsonify({
        "message": "Knowledge graph generated successfully",
        "stats": {
            "nodes": node_count,
            "edges": edge_count
        },
        "path": output_path
    })

@app.route('/mcp/visualize_knowledge_graph', methods=['POST'])
def knowledge_graph_visualization_endpoint():
    data = request.json
    graph_file = data.get('graph_file', './knowledge_graph/graph.json')

    # Check if the graph file exists
    if not os.path.exists(graph_file):
        return jsonify({"error": "Graph file not found"})

    # Create output directory
    output_dir = './knowledge_graph/visualizations'
    os.makedirs(output_dir, exist_ok=True)

    # Import and use the knowledge graph visualizer
    from knowledge_graph.visualize import (
        load_knowledge_graph,
        create_graph,
        visualize_full_graph,
        visualize_component_dependencies,
        visualize_error_solutions
    )

    # Load knowledge graph
    knowledge_graph = load_knowledge_graph(graph_file)
    if not knowledge_graph:
        return jsonify({"error": "Failed to load knowledge graph"})

    # Create NetworkX graph
    G = create_graph(knowledge_graph)

    # Generate visualizations
    visualizations = []

    # Full graph visualization
    full_graph_path = os.path.join(output_dir, "full_graph.png")
    visualize_full_graph(G, full_graph_path)
    visualizations.append({"type": "full_graph", "path": full_graph_path})

    # Component dependencies visualization
    component_deps_path = os.path.join(output_dir, "component_dependencies.png")
    visualize_component_dependencies(G, component_deps_path)
    visualizations.append({"type": "component_dependencies", "path": component_deps_path})

    # Error solutions visualization
    error_solutions_path = os.path.join(output_dir, "error_solutions.png")
    visualize_error_solutions(G, error_solutions_path)
    visualizations.append({"type": "error_solutions", "path": error_solutions_path})

    return jsonify({
        "message": "Knowledge graph visualizations generated successfully",
        "visualizations": visualizations
    })

@app.route('/mcp/analyze_maturity', methods=['POST'])
def maturity_analysis_endpoint():
    data = request.json
    file_path = data.get('file_path', '')

    if os.path.isfile(file_path):
        # Analyze a single file
        from maturity_model.maturity_analyzer import MaturityAnalyzer
        analyzer = MaturityAnalyzer()
        maturity = analyzer.analyze_file(Path(file_path))

        if maturity:
            return jsonify({
                "file": file_path,
                "maturity": maturity,
                "component": analyzer.components.get(file_path, {})
            })
        else:
            return jsonify({"error": f"No maturity information found in {file_path}"})

    elif os.path.isdir(file_path):
        # Analyze an entire directory
        from maturity_model.maturity_analyzer import MaturityAnalyzer
        analyzer = MaturityAnalyzer()
        analyzer.analyze_directory(file_path)

        # Generate report
        report = analyzer.generate_report()

        return jsonify({
            "message": f"Analyzed {len(analyzer.components)} components",
            "maturity_stats": analyzer.maturity_stats,
            "report_path": str(analyzer.output_dir / "maturity_report.json")
        })

    else:
        return jsonify({"error": f"Path not found: {file_path}"})

@app.route('/mcp/generate_maturity_dashboard', methods=['POST'])
def maturity_dashboard_endpoint():
    data = request.json
    report_path = data.get('report_path', '')

    if not os.path.exists(report_path):
        return jsonify({"error": f"Report file not found: {report_path}"})

    # Generate dashboard
    from maturity_model.maturity_dashboard import MaturityDashboard
    dashboard = MaturityDashboard()

    output_path = os.path.join(os.path.dirname(report_path), "maturity_dashboard.html")
    dashboard.generate_dashboard(report_path, output_path=output_path)

    return jsonify({
        "message": "Maturity dashboard generated successfully",
        "dashboard_path": output_path
    })

@app.route('/mcp/extract_memory_anchors', methods=['POST'])
def memory_anchor_extraction_endpoint():
    data = request.json
    code = data.get('code', '')

    # Create a temporary file to hold the code
    with open('temp_code.txt', 'w', encoding='utf-8') as f:
        f.write(code)

    # Extract memory anchors
    from memory_anchors.anchor_extractor import AnchorExtractor
    extractor = AnchorExtractor()
    extractor.extract_anchors('temp_code.txt')

    # Get the extracted anchors
    anchors = extractor.anchors

    # Remove the temporary file
    os.remove('temp_code.txt')

    return jsonify({
        "message": f"Extracted {len(anchors)} memory anchors",
        "anchors": anchors
    })

@app.route('/mcp/search_memory_anchors', methods=['POST'])
def memory_anchor_search_endpoint():
    data = request.json
    query = data.get('query', '')
    anchor_file = data.get('anchor_file', '')

    if not os.path.exists(anchor_file):
        # If no anchor file is provided or it doesn't exist, return empty results
        return jsonify({
            "message": "No anchor file found",
            "results": []
        })

    # Search for memory anchors
    from memory_anchors.anchor_search_tool import AnchorSearchTool
    search_tool = AnchorSearchTool()

    # Load anchors
    search_tool.load_anchors(anchor_file)

    # Search for anchors matching the query
    results = search_tool.search_anchors(query)

    return jsonify({
        "message": f"Found {len(results)} memory anchors matching '{query}'",
        "results": results
    })

@app.route('/mcp/visualize_memory_anchors', methods=['POST'])
def memory_anchor_visualization_endpoint():
    anchor_file = request.json.get('anchor_file')

    # Check if anchor file exists
    if not os.path.exists(anchor_file):
        return jsonify({"error": f"Anchor file not found: {anchor_file}"}), 404

    # Create output directory for visualizations
    output_dir = os.path.join(os.path.dirname(anchor_file), "visualizations")
    os.makedirs(output_dir, exist_ok=True)

    # Load anchors and build visualization
    try:
        visualizer = AnchorVisualizer(anchor_file)
        visualizer.build_graph()

        # Generate visualizations
        static_viz_path = os.path.join(output_dir, "anchors_static.png")
        interactive_viz_path = os.path.join(output_dir, "anchors_interactive.html")

        visualizer.generate_static_visualization(static_viz_path)
        visualizer.generate_interactive_visualization(interactive_viz_path)

        return jsonify({
            "message": "Memory anchor visualizations generated successfully",
            "static_visualization": static_viz_path,
            "interactive_visualization": interactive_viz_path
        })
    except Exception as e:
        return jsonify({"error": f"Failed to visualize memory anchors: {str(e)}"}), 500

@app.route('/mcp/extract_metadata', methods=['POST'])
def metadata_extraction_endpoint():
    source_dir = request.json.get('source_dir')
    config_path = request.json.get('config_path')

    if not os.path.exists(source_dir):
        return jsonify({"error": f"Source directory not found: {source_dir}"}), 404

    try:
        # Create extractor with optional config
        extractor = MetadataExtractor(config_path if config_path else None)

        # Process the directory
        results = extractor.process_directory(source_dir, recursive=True)

        # Generate report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = os.path.join(os.path.dirname(source_dir), f"metadata_report_{timestamp}.json")
        extractor.generate_report(report_path)

        return jsonify({
            "message": f"Metadata extracted from {results['processed_files']} files",
            "files_with_metadata": results['files_with_metadata'],
            "files_with_complete_metadata": results['files_with_complete_metadata'],
            "coverage_percentage": results['metadata_coverage'],
            "report_path": report_path
        })
    except Exception as e:
        return jsonify({"error": f"Failed to extract metadata: {str(e)}"}), 500

@app.route('/mcp/metadata_dashboard', methods=['POST'])
def metadata_dashboard_endpoint():
    report_path = request.json.get('report_path')
    port = request.json.get('port', 8050)

    if not os.path.exists(report_path):
        return jsonify({"error": f"Report file not found: {report_path}"}), 404

    try:
        # Start dashboard in a background thread
        def run_dashboard():
            dashboard = MetadataDashboard(report_path)
            dashboard.run_server(debug=False, port=port)

        thread = threading.Thread(target=run_dashboard)
        thread.daemon = True
        thread.start()

        return jsonify({
            "message": "Metadata dashboard started successfully",
            "dashboard_url": f"http://localhost:{port}/",
            "report_path": report_path
        })
    except Exception as e:
        return jsonify({"error": f"Failed to start metadata dashboard: {str(e)}"}), 500

@app.route('/mcp/analyze_revenue_potential', methods=['POST'])
def revenue_potential_analysis_endpoint():
    codebase_path = request.json.get('codebase_path')

    if not os.path.exists(codebase_path):
        return jsonify({"error": f"Codebase path not found: {codebase_path}"}), 404

    try:
        # Import the analyzer
        from monetization_analysis.revenue_potential_analyzer import RevenuePotentialAnalyzer

        # Create analyzer instance
        analyzer = RevenuePotentialAnalyzer(verbose=True)

        # Analyze the codebase
        analyzer.analyze_directory(codebase_path)

        # Generate report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = f"./revenue_potential_report_{timestamp}.html"
        analyzer.generate_report(report_path)

        # Return results
        return jsonify({
            "message": f"Analyzed {analyzer.results['summary']['total_opportunities']} monetization opportunities",
            "opportunities_by_type": analyzer.results['summary']['by_type'],
            "opportunities_by_priority": analyzer.results['summary']['by_priority'],
            "report_path": report_path
        })
    except Exception as e:
        return jsonify({"error": f"Failed to analyze revenue potential: {str(e)}"}), 500

@app.route('/mcp/analyze_pricing_strategy', methods=['POST'])
def pricing_strategy_analysis_endpoint():
    codebase_path = request.json.get('codebase_path')

    if not os.path.exists(codebase_path):
        return jsonify({"error": f"Codebase path not found: {codebase_path}"}), 404

    try:
        # Import the analyzer
        from monetization_analysis.pricing_strategy_analyzer import PricingStrategyAnalyzer

        # Create analyzer instance
        analyzer = PricingStrategyAnalyzer(verbose=True)

        # Analyze the codebase
        analyzer.analyze_directory(codebase_path)

        # Generate report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = f"./pricing_strategy_report_{timestamp}.html"
        analyzer.generate_report(report_path)

        # Return results
        return jsonify({
            "message": f"Analyzed {analyzer.results['summary']['total_pricing_elements']} pricing elements",
            "identified_pricing_models": analyzer.results['summary']['identified_pricing_models'],
            "recommendations": [rec['name'] for rec in analyzer.results['recommendations']],
            "report_path": report_path
        })
    except Exception as e:
        return jsonify({"error": f"Failed to analyze pricing strategy: {str(e)}"}), 500

@app.route('/mcp/analyze_feature_value', methods=['POST'])
def feature_value_analysis_endpoint():
    feature_path = request.json.get('feature_path')

    if not os.path.exists(feature_path):
        return jsonify({"error": f"Feature path not found: {feature_path}"}), 404

    try:
        # Import the analyzer
        from monetization_analysis.feature_value_analyzer import FeatureValueAnalyzer

        # Create analyzer instance
        analyzer = FeatureValueAnalyzer(verbose=True)

        # Analyze the feature
        if os.path.isdir(feature_path):
            analyzer.analyze_directory(feature_path)
        else:
            analyzer.analyze_file(feature_path)

        # Generate report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = f"./feature_value_report_{timestamp}.html"
        analyzer.generate_report(report_path)

        # Return results
        return jsonify({
            "message": f"Analyzed {len(analyzer.results['features'])} features",
            "high_value_features": [f['name'] for f in analyzer.results['features'] if f['value_score'] > 0.7],
            "monetization_recommendations": analyzer.results['recommendations'],
            "report_path": report_path
        })
    except Exception as e:
        return jsonify({"error": f"Failed to analyze feature value: {str(e)}"}), 500

@app.route('/mcp/analyze_ab_testing', methods=['POST'])
def ab_testing_analysis_endpoint():
    ab_testing_path = request.json.get('ab_testing_path')

    if not os.path.exists(ab_testing_path):
        return jsonify({"error": f"A/B testing path not found: {ab_testing_path}"}), 404

    try:
        # Import the analyzer
        from monetization_analysis.ab_testing_analyzer import ABTestingAnalyzer

        # Create analyzer instance
        analyzer = ABTestingAnalyzer(verbose=True)

        # Analyze the A/B testing results
        analyzer.analyze_results(ab_testing_path)

        # Generate report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = f"./ab_testing_report_{timestamp}.html"
        analyzer.generate_report(report_path)

        # Return results
        return jsonify({
            "message": f"Analyzed {len(analyzer.results['tests'])} A/B tests",
            "significant_results": [t['name'] for t in analyzer.results['tests'] if t['is_significant']],
            "recommended_variants": analyzer.results['recommendations'],
            "report_path": report_path
        })
    except Exception as e:
        return jsonify({"error": f"Failed to analyze A/B testing: {str(e)}"}), 500

@app.route('/mcp/generate_style_documentation', methods=['POST'])
def style_documentation_generation_endpoint():
    data = request.json
    code = data.get('code', '')
    language = data.get('language', 'python')
    output_format = data.get('output_format', 'markdown')

    # Create a temporary file to hold the code
    with open('temp_code.txt', 'w', encoding='utf-8') as f:
        f.write(code)

    try:
        # Import the documentation generator
        from style_guide.documentation_generator import StyleDocumentationGenerator

        # Create generator instance
        generator = StyleDocumentationGenerator(language=language)

        # Generate documentation
        documentation = generator.generate_documentation('temp_code.txt', output_format=output_format)

        # Generate output file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"./style_documentation_{timestamp}.{output_format}"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(documentation)

        # Remove temporary file
        os.remove('temp_code.txt')

        return jsonify({
            "message": "Style documentation generated successfully",
            "documentation_file": output_file
        })
    except Exception as e:
        # Clean up temp file if it exists
        if os.path.exists('temp_code.txt'):
            os.remove('temp_code.txt')
        return jsonify({"error": f"Failed to generate style documentation: {str(e)}"}), 500

@app.route('/mcp/generate_linter_config', methods=['POST'])
def linter_config_generation_endpoint():
    data = request.json
    style_guide_path = data.get('style_guide_path', '')
    linter_type = data.get('linter_type', 'eslint')

    if not os.path.exists(style_guide_path):
        return jsonify({"error": f"Style guide path not found: {style_guide_path}"}), 404

    try:
        # Import the linter config generator
        from style_guide.linter_config_generator import LinterConfigGenerator

        # Create generator instance
        generator = LinterConfigGenerator(linter_type=linter_type)

        # Generate linter config
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        config_file = f"./{linter_type}_config_{timestamp}.json"

        generator.generate_config(style_guide_path, output_file=config_file)

        return jsonify({
            "message": f"{linter_type} configuration generated successfully",
            "config_file": config_file
        })
    except Exception as e:
        return jsonify({"error": f"Failed to generate linter configuration: {str(e)}"}), 500

@app.route('/mcp/check_style_adherence', methods=['POST'])
def style_adherence_check_endpoint():
    data = request.json
    code = data.get('code', '')
    language = data.get('language', 'python')
    style_guide = data.get('style_guide', None)

    # Create a temporary file to hold the code
    with open('temp_code.txt', 'w', encoding='utf-8') as f:
        f.write(code)

    try:
        # Import the style checker
        from style_guide.style_checker import StyleChecker

        # Create checker instance
        checker = StyleChecker(language=language, style_guide=style_guide)

        # Check style adherence
        results = checker.check_file('temp_code.txt')

        # Remove temporary file
        os.remove('temp_code.txt')

        return jsonify({
            "message": f"Style check completed with {len(results['violations'])} violations",
            "violations": results['violations'],
            "statistics": results['statistics']
        })
    except Exception as e:
        # Clean up temp file if it exists
        if os.path.exists('temp_code.txt'):
            os.remove('temp_code.txt')
        return jsonify({"error": f"Failed to check style adherence: {str(e)}"}), 500

@app.route('/mcp/analyze_contract', methods=['POST'])
def contract_analysis_endpoint():
    data = request.json
    contract_path = data.get('contract_path', '')

    if not os.path.exists(contract_path):
        return jsonify({"error": f"Contract file not found: {contract_path}"}), 404

    try:
        # Import the contract analyzer
        from web3_security.contract_analyzer import ContractAnalyzer

        # Create analyzer instance
        analyzer = ContractAnalyzer()

        # Analyze the contract
        results = analyzer.analyze_contract(contract_path)

        # Generate report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = f"./contract_security_report_{timestamp}.html"
        analyzer.generate_report(report_path)

        return jsonify({
            "message": f"Smart contract analyzed with {len(results['vulnerabilities'])} vulnerabilities found",
            "vulnerabilities": results['vulnerabilities'],
            "risk_level": results['risk_level'],
            "report_path": report_path
        })
    except Exception as e:
        return jsonify({"error": f"Failed to analyze contract: {str(e)}"}), 500

@app.route('/mcp/validate_transaction', methods=['POST'])
def transaction_validation_endpoint():
    data = request.json
    transaction_path = data.get('transaction_path', '')

    if not os.path.exists(transaction_path):
        return jsonify({"error": f"Transaction file not found: {transaction_path}"}), 404

    try:
        # Import the transaction validator
        from web3_security.transaction_validator import TransactionValidator

        # Create validator instance
        validator = TransactionValidator()

        # Validate the transaction
        results = validator.validate_transaction(transaction_path)

        return jsonify({
            "message": f"Transaction validated with {len(results['issues'])} security issues found",
            "issues": results['issues'],
            "recommendations": results['recommendations']
        })
    except Exception as e:
        return jsonify({"error": f"Failed to validate transaction: {str(e)}"}), 500

@app.route('/mcp/analyze_permissions', methods=['POST'])
def permission_analysis_endpoint():
    data = request.json
    contract_path = data.get('contract_path', '')

    if not os.path.exists(contract_path):
        return jsonify({"error": f"Contract file not found: {contract_path}"}), 404

    try:
        # Import the permission analyzer
        from web3_security.permission_analyzer import PermissionAnalyzer

        # Create analyzer instance
        analyzer = PermissionAnalyzer()

        # Analyze permissions
        results = analyzer.analyze_permissions(contract_path)

        # Generate report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = f"./permission_analysis_report_{timestamp}.html"
        analyzer.generate_report(report_path)

        return jsonify({
            "message": f"Permission model analyzed with {len(results['permission_issues'])} issues found",
            "permission_model": results['permission_model'],
            "permission_issues": results['permission_issues'],
            "recommendations": results['recommendations'],
            "report_path": report_path
        })
    except Exception as e:
        return jsonify({"error": f"Failed to analyze permissions: {str(e)}"}), 500

@app.route('/mcp/scan_web3_api', methods=['POST'])
def api_security_scan_endpoint():
    data = request.json
    api_url = data.get('api_url', '')
    api_spec_path = data.get('api_spec_path', None)

    if not api_url:
        return jsonify({"error": "API URL is required"}), 400

    try:
        # Import the API security scanner
        from web3_security.api_security_scanner import APISecurityScanner

        # Create scanner instance
        scanner = APISecurityScanner()

        # Scan the API
        results = scanner.scan_api(api_url, api_spec_path)

        # Generate report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = f"./api_security_scan_report_{timestamp}.html"
        scanner.generate_report(report_path)

        return jsonify({
            "message": f"API security scan completed with {len(results['vulnerabilities'])} vulnerabilities found",
            "vulnerabilities": results['vulnerabilities'],
            "endpoints_scanned": results['endpoints_scanned'],
            "risk_level": results['risk_level'],
            "report_path": report_path
        })
    except Exception as e:
        return jsonify({"error": f"Failed to scan API: {str(e)}"}), 500

@app.route('/mcp/optimize_gas', methods=['POST'])
def gas_optimization_endpoint():
    data = request.json
    contract_path = data.get('contract_path', '')

    if not os.path.exists(contract_path):
        return jsonify({"error": f"Contract file not found: {contract_path}"}), 404

    try:
        # Import the gas optimizer
        from web3_security.gas_optimizer import GasOptimizer

        # Create optimizer instance
        optimizer = GasOptimizer()

        # Optimize the contract
        results = optimizer.optimize_contract(contract_path)

        # Generate optimized contract
        file_name = os.path.basename(contract_path)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        optimized_path = f"./optimized_{file_name}_{timestamp}"

        with open(optimized_path, 'w', encoding='utf-8') as f:
            f.write(results['optimized_code'])

        return jsonify({
            "message": f"Gas optimization completed with estimated savings of {results['gas_savings']} gas units",
            "original_gas": results['original_gas'],
            "optimized_gas": results['optimized_gas'],
            "gas_savings": results['gas_savings'],
            "optimization_techniques": results['optimization_techniques'],
            "optimized_contract_path": optimized_path
        })
    except Exception as e:
        return jsonify({"error": f"Failed to optimize gas: {str(e)}"}), 500

# Add other endpoints similarly

if __name__ == '__main__':
    app.run(port=7777)

## Next Steps

1. Review all available Python scripts to identify additional tools
2. Test each script to confirm functionality
3. Prioritize tools for MCP integration
4. Create API wrappers for highest priority tools
5. Update MCP configuration
6. Test integrated tools with AI assistance

## Rule Type Configuration

All rule files should be configured with proper rule types in the Cursor interface:

- **main.mdc**: Rule Type = "Always"
- **Category rules** (like accessibility.mdc, code_quality.mdc): Rule Type = "Auto Attached"
- **Specific sub-rules** (like a11y.mdc, typescript_workflow.mdc): Rule Type = "Manual"
```

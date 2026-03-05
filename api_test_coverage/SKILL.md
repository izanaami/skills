---
name: api_test_coverage
description: 自动识别代码仓库中的公共API，匹配测试用例并生成详细的覆盖率分析报告（Excel/Markdown），支持多语言并提供优化建议。
---

# Skill: API Test Coverage Analysis

## Overview

This skill provides comprehensive API test coverage analysis for code repositories. It automatically identifies public APIs, matches test cases, and generates detailed coverage reports with Excel spreadsheets and Markdown documentation.

## Capabilities

### Multi-Language Support
- **C/C++**: Analyzes header files with `extern "C"` and visibility macros
- **Python**: Analyzes module functions and class methods
- **Java**: Analyzes public classes and methods
- **Go**: Analyzes exported functions and methods
- **TypeScript/JavaScript**: Analyzes exported functions and types

### Automatic API Detection
- Identifies public APIs based on language-specific patterns
- Distinguishes between internal and external interfaces
- Categorizes APIs by functionality (Initialization, Memory, Network, etc.)

### Test Case Matching
- Scans test directories for API usage
- Supports multiple test frameworks (Google Test, pytest, JUnit, etc.)
- Matches test files to API definitions
- Identifies covered and uncovered APIs

### Comprehensive Reporting
- **Excel Reports**: Detailed API coverage tables with test file references
- **Markdown Reports**: Comprehensive analysis with statistics and recommendations
- **Coverage Metrics**: Total APIs, covered APIs, coverage percentage
- **Prioritization**: Uncovers APIs categorized by priority

## Usage

### Basic Analysis

```bash
# Analyze current directory
python -m skills.api_test_coverage analyze

# Analyze specific directory
python -m skills.api_test_coverage analyze --path /path/to/repo

# Specify programming language
python -m skills.api_test_coverage analyze --language cpp

# Specify include and test directories
python -m skills.api_test_coverage analyze \
  --include-dir include \
  --test-dir tests
```

### Advanced Options

```bash
# Generate both Excel and Markdown reports
python -m skills.api_test_coverage analyze \
  --output-format all \
  --output-dir ./reports

# Custom API categorization
python -m skills.api_test_coverage analyze \
  --categories config/categories.json

# Exclude specific patterns
python -m skills.api_test_coverage analyze \
  --exclude "internal_*" \
  --exclude "*_private"

# Set coverage threshold
python -m skills.api_test_coverage analyze \
  --coverage-threshold 80
```

### Report Generation

```bash
# Generate Excel report only
python -m skills.api_test_coverage analyze --output-format xlsx

# Generate Markdown report only
python -m skills.api_test_coverage analyze --output-format md

# Generate custom report template
python -m skills.api_test_coverage analyze \
  --template templates/custom_report.md
```

## Configuration

### Language-Specific Patterns

#### C/C++ Configuration
```json
{
  "language": "cpp",
  "api_patterns": [
    "ACLSHMEM_HOST_API",
    "ACLSHMEM_DEVICE_API",
    "__attribute__((visibility(\"default\"))"
  ],
  "include_dirs": ["include", "include/public"],
  "test_dirs": ["tests", "test", "unittest"],
  "test_frameworks": ["gtest", "gtest_lite"]
}
```

#### Python Configuration
```json
{
  "language": "python",
  "api_patterns": [
    "def public_*",
    "class.*:",
    "__all__"
  ],
  "include_dirs": ["src", "lib"],
  "test_dirs": ["tests", "test"],
  "test_frameworks": ["pytest", "unittest"]
}
```

### Category Mapping

```json
{
  "categories": {
    "init": ["init", "setup", "configure", "start"],
    "memory": ["malloc", "free", "alloc", "memory", "buffer"],
    "network": ["send", "recv", "connect", "network", "socket"],
    "data": ["get", "set", "put", "data", "value"],
    "sync": ["sync", "barrier", "wait", "signal", "lock"],
    "team": ["team", "group", "collective", "allreduce"],
    "logging": ["log", "print", "debug", "info", "warn", "error"]
  }
}
```

## Output Files

### Excel Report (api_test_coverage.xlsx)

| Column | Description |
|--------|-------------|
| API类别 | Functional category of the API |
| host还是device接口 | Platform type (host/device/client/server) |
| API Name | Name of the API function/method |
| API定义头文件 | Source file where API is defined |
| 是否有测试用例 | Test coverage status (YES/NO) |
| 测试用例所在文件 | Test file containing API tests |

### Markdown Report (api_test_coverage_report.md)

#### Sections
1. **接口统计概览** - Summary statistics
2. **完整对外接口清单** - Complete API inventory
3. **未覆盖测试用例的对外接口** - Prioritized uncovered APIs
4. **优化建议** - Recommendations for improvement

#### Metrics
- Total API count
- Covered API count
- Uncovered API count
- Coverage percentage
- Priority categorization (High/Medium/Low)

## Workflow

### 1. Repository Analysis
```python
from skills.api_test_coverage import Analyzer

analyzer = Analyzer(
    repo_path="/path/to/repo",
    language="cpp",
    include_dirs=["include"],
    test_dirs=["tests"]
)

# Analyze repository
results = analyzer.analyze()
```

### 2. API Detection
```python
# Detect public APIs
apis = analyzer.detect_apis()

# Categorize APIs
categorized_apis = analyzer.categorize_apis(apis)

# Match test cases
coverage = analyzer.match_tests(categorized_apis)
```

### 3. Report Generation
```python
from skills.api_test_coverage import Reporter

reporter = Reporter(
    coverage_results=coverage,
    output_dir="./reports"
)

# Generate Excel report
reporter.generate_excel("api_coverage.xlsx")

# Generate Markdown report
reporter.generate_markdown("api_coverage_report.md")
```

## Integration

### CI/CD Integration

```bash
# Add to CI pipeline
python -m skills.api_test_coverage analyze \
  --coverage-threshold 80 \
  --fail-on-low-coverage

# Generate coverage badge
python -m skills.api_test_coverage analyze \
  --generate-badge
```

### Pre-commit Hooks

```bash
# .git/hooks/pre-commit
#!/bin/bash
python -m skills.api_test_coverage analyze --quick-check
```

### GitHub Actions

```yaml
name: API Coverage Check
on: [push, pull_request]
jobs:
  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Analyze API Coverage
        run: |
          python -m skills.api_test_coverage analyze \
            --coverage-threshold 75 \
            --fail-on-low-coverage
```

## Best Practices

### API Documentation
- Add descriptive comments to API definitions
- Include parameter descriptions and return types
- Document error conditions and edge cases

### Test Organization
- Organize tests by API category
- Use descriptive test names
- Include both positive and negative test cases
- Add comments explaining test purpose

### Coverage Goals
- Aim for >80% coverage for critical APIs
- Prioritize initialization and configuration APIs
- Ensure error handling APIs are tested
- Cover boundary conditions and edge cases

### Regular Analysis
- Run analysis after significant API changes
- Update reports before releases
- Review uncovered APIs regularly
- Maintain coverage trends over time

## Troubleshooting

### Common Issues

#### Low API Detection
**Problem**: Few APIs detected
**Solution**: 
- Check API patterns in configuration
- Verify include directories are correct
- Ensure visibility macros are properly defined

#### Test Matching Failures
**Problem**: Tests not matching APIs
**Solution**:
- Verify test directory paths
- Check test framework compatibility
- Ensure test file naming conventions

#### Report Generation Errors
**Problem**: Report generation fails
**Solution**:
- Check output directory permissions
- Verify template files exist
- Ensure sufficient disk space

### Debug Mode

```bash
# Enable debug output
python -m skills.api_test_coverage analyze --debug

# Verbose mode
python -m skills.api_test_coverage analyze --verbose

# Save intermediate results
python -m skills.api_test_coverage analyze --save-intermediate
```

## Extensibility

### Custom Language Support

```python
from skills.api_test_coverage import LanguageDetector

class CustomLanguageDetector(LanguageDetector):
    def detect_apis(self, files):
        # Custom API detection logic
        pass
    
    def match_tests(self, apis, test_files):
        # Custom test matching logic
        pass
```

### Custom Report Templates

```markdown
# custom_template.md

# Custom API Coverage Report

## Executive Summary
- Total APIs: {{total_apis}}
- Coverage: {{coverage_percentage}}%
- Critical Issues: {{critical_issues}}

## Detailed Analysis
{{detailed_analysis}}
```

### Custom Categorization

```python
def custom_categorizer(api_name):
    # Custom categorization logic
    if "security" in api_name.lower():
        return "Security"
    elif "crypto" in api_name.lower():
        return "Cryptography"
    return "General"
```

## Performance Considerations

### Large Repositories
- Use incremental analysis for large codebases
- Cache analysis results between runs
- Parallelize file processing
- Optimize regex patterns

### Memory Management
- Process files in batches
- Clean up intermediate results
- Use generators for large datasets
- Monitor memory usage during analysis

## License and Attribution

This skill is designed for automated API test coverage analysis and reporting. It supports multiple programming languages and integrates with various development workflows.

## Version History

- **1.0.0**: Initial release
  - Multi-language support (C/C++, Python, Java)
  - Automatic API detection
  - Test case matching
  - Excel and Markdown report generation
  - CI/CD integration support

## Contributing

To extend this skill for additional languages or features:

1. Add language-specific detection logic
2. Implement test framework matching
3. Create appropriate report templates
4. Update documentation
5. Add tests for new functionality

## Support

For issues, questions, or contributions, please refer to the project documentation and issue tracking system.

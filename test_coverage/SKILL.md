---
name: test_coverage
description: Analyze code repository for API definitions and test case coverage. Use this skill when the user wants to: Analyze test coverage for a codebase; Find which APIs have corresponding test cases; Generate test coverage reports (text and Excel formats); Identify missing test cases for APIs; Review API-to-test mapping in a repository; Assess testing completeness for a library or SDK; Create documentation about what features are tested vs untested; Generate test coverage statistics and recommendations. Trigger this skill whenever the user mentions analyzing test coverage, finding test cases, checking what APIs are tested, or generating test coverage reports, even if they don't explicitly ask for a "test coverage analysis".
---

# Test Coverage Analysis Skill

This skill analyzes code repositories to identify API definitions and their corresponding test case coverage, generating comprehensive reports.

## Overview

This skill performs the following tasks:
1. Scans repository structure to find API definitions
2. Searches for corresponding test cases
3. Generates detailed coverage reports in both text and Excel formats
4. Provides statistics and recommendations for improving test coverage

## When to Use This Skill

Use this skill when you encounter requests like:
- "Analyze the test coverage for this codebase"
- "Find which APIs have test cases"
- "Generate a test coverage report"
- "Check what APIs are missing tests"
- "Review the API-to-test mapping"
- "Create a report showing tested vs untested features"
- "What's the test coverage percentage?"
- "Identify APIs that need test cases"

## Analysis Process

### Step 1: Explore Repository Structure

First, understand the codebase structure:

1. **Find API/source directories**: Look for directories containing API definitions
   - Common locations: `include/`, `src/`, `lib/`, `api/`, `public/`
   - Search for header files: `.h`, `.hpp`, `.py`, `.ts`, `.js`

2. **Find test directories**: Look for directories containing test files
   - Common locations: `tests/`, `test/`, `unittest/`, `spec/`, `__tests__/`
   - Look for test file patterns: `*_test.*`, `test_*.py`, `*.spec.*`

3. **Detect programming language**: Based on file extensions and structure
   - C/C++: `.h`, `.hpp`, `.c`, `.cpp`
   - Python: `.py`
   - JavaScript/TypeScript: `.js`, `.ts`
   - Java: `.java`
   - Go: `.go`

### Step 2: Extract API Definitions

Parse source files to extract API information:

**For C/C++:**
- Look for function declarations with API markers:
  - `PUBLIC_API`, `EXPORT_API`, `DLLEXPORT`, `extern "C"`
  - Function declarations in header files
- Extract function name, return type, parameters

**For Python:**
- Look for function definitions with decorators:
  - `@public`, `@api`, `@export`
  - Functions in `__all__` lists
- Extract function name and signature

**For JavaScript/TypeScript:**
- Look for exported functions:
  - `export function`, `export const`
  - Functions in `module.exports`
- Extract function name

**For any language:**
- Extract function/class names
- Note the file path and location
- Categorize based on directory structure

### Step 3: Find Test Cases

Search for corresponding test cases:

1. **Search test files**: Look for test files that might test each API
2. **Match patterns**:
   - API name in test file content
   - Test file name related to API
   - Directory-based matching (e.g., API in `api/` tested in `tests/api/`)

3. **Record test status**:
   - "Has test" - found matching test case
   - "No test" - no matching test case found

### Step 4: Generate Reports

Create comprehensive reports:

#### Text Report Format

Generate a detailed text report with:
- Report overview and generation time
- Detailed API listings by category
- Statistics summary
- Analysis and recommendations
- Prioritized suggestions for missing tests

#### Excel Report Format

Generate an Excel file with multiple sheets:

1. **APIs by Category** sheet:
   - Columns: Category, API Name, Source File, Test Status, Test File

2. **Statistics** sheet:
   - Total APIs count
   - Tested APIs count
   - Test coverage percentage
   - Coverage by category

3. **Missing Tests** sheet:
   - APIs without tests
   - Priority recommendations

### Step 5: Calculate Statistics

Compute coverage statistics:

1. **Overall coverage**:
   - Total APIs = count of all APIs
   - Tested APIs = count of APIs with test cases
   - Coverage = (Tested / Total) × 100%

2. **Category coverage**:
   - Coverage percentage for each category
   - Identify well-tested and poorly-tested categories

### Step 6: Provide Recommendations

Generate actionable recommendations:

1. **High priority** (core functionality):
   - Initialization/finalization APIs
   - Core data manipulation APIs
   - Main communication APIs

2. **Medium priority** (important features):
   - Configuration APIs
   - Query/information APIs
   - Utility functions

3. **Low priority** (nice to have):
   - Convenience functions
   - Deprecated APIs
   - Rarely used features

## Output Files

Generate two output files:

1. **Text report**: `[repository]_test_coverage_report.txt`
   - Human-readable detailed analysis
   - Includes recommendations and next steps

2. **Excel report**: `[repository]_api_coverage.xlsx`
   - Machine-readable structured data
   - Easy to filter, sort, and analyze

## Programming Language Support

### C/C++ (default)

- Header files: `.h`, `.hpp`
- API markers: `PUBLIC_API`, `EXPORT_API`, `extern "C"`
- Test files: `*_test.cpp`, `*_test.c`

### Python

- Source files: `.py`
- API markers: `@public`, `@api`, `@export`
- Test files: `test_*.py`, `*_test.py`

### JavaScript/TypeScript

- Source files: `.js`, `.ts`
- API markers: `export function`, `export const`
- Test files: `*.test.js`, `*.spec.ts`

### Java

- Source files: `.java`
- API markers: `public`, `@Api`
- Test files: `*Test.java`, `*Tests.java`

### Go

- Source files: `.go`
- API markers: exported functions (capitalized)
- Test files: `*_test.go`

## Customization

### API Detection Patterns

You can customize API detection by modifying patterns in the analysis script:

**C/C++ patterns:**
```python
api_patterns = [
    r'PUBLIC_API\s+(\w+)\s*\([^)]*\)',
    r'EXPORT_API\s+(\w+)\s*\([^)]*\)',
    r'DLLEXPORT\s+(\w+)\s*\([^)]*\)',
    r'extern\s+"C"\s*\{?\s*(\w+)\s*\([^)]*\)',
]
```

**Python patterns:**
```python
api_patterns = [
    r'@public\s+def\s+(\w+)\s*\(',
    r'@api\s+def\s+(\w+)\s*\(',
    r'def\s+(\w+)\s*\(',  # All functions
]
```

**JavaScript patterns:**
```python
api_patterns = [
    r'export\s+function\s+(\w+)\s*\(',
    r'export\s+const\s+(\w+)\s*=',
    r'module\.exports\.\s*(\w+)\s*=',
]
```

### Category Detection

APIs are categorized based on their file path:

```python
def get_category_from_path(file_path):
    path_str = str(file_path).lower()
    
    # Customize these mappings for your repository
    if 'init' in path_str or 'setup' in path_str:
        return 'Initialization'
    elif 'mem' in path_str or 'alloc' in path_str:
        return 'Memory'
    elif 'io' in path_str or 'file' in path_str:
        return 'I/O'
    elif 'net' in path_str or 'comm' in path_str:
        return 'Communication'
    elif 'util' in path_str or 'helper' in path_str:
        return 'Utilities'
    else:
        return 'Other'
```

### Directory Structure

Customize which directories to search:

```python
# Source directories
source_dirs = [
    repo_path / "include",
    repo_path / "src",
    repo_path / "lib",
    repo_path / "api",
    repo_path / "public",
]

# Test directories
test_dirs = [
    repo_path / "tests",
    repo_path / "test",
    repo_path / "unittest",
    repo_path / "spec",
    repo_path / "__tests__",
]
```

## Usage Examples

### As a Skill

When loaded as a skill, simply ask Claude to analyze test coverage:

```
"Analyze the test coverage for this codebase"
"Find which APIs have test cases and generate a report"
"Check what APIs are missing tests in this repository"
```

### As a Script

You can also use the bundled script directly:

```bash
python analyze_coverage.py <repo_path> [output_dir]
```

Example:
```bash
python analyze_coverage.py /path/to/repo /path/to/output
```

## Example Output

### Statistics Summary

```
===================================================================================================
Repository Test Coverage Report
===================================================================================================

【Statistics】
----------------------------------------------------------------------------------------------------
Total APIs: 583
Tested APIs: 392
Overall Coverage: 67.2%

Coverage by Category:
  Initialization: 85.0% (17/20)
  Memory: 45.0% (9/20)
  I/O: 75.0% (15/20)
  Communication: 90.0% (18/20)
  Utilities: 60.0% (12/20)
  Other: 50.0% (321/642)
===================================================================================================
```

### API Coverage Details

```
【API Coverage Details】
----------------------------------------------------------------------------------------------------
Category       API Name                  Source File          Test Status    Test File
----------------------------------------------------------------------------------------------------
Initialization  init_api                   api_init.h           Has test      api_init_test.cpp
Initialization  setup_connection           api_setup.h           No test       -
Memory         allocate_memory             memory.h             Has test      memory_test.cpp
Memory         free_memory                 memory.h             No test       -
```

## Limitations

Be aware of these limitations:

1. **Static analysis only**: Cannot determine if tests actually pass or cover all scenarios
2. **Pattern matching**: Relies on naming conventions; may miss tests with unconventional names
3. **Language-specific**: Some features are language-dependent
4. **Complex patterns**: May not fully expand complex macro-generated APIs
5. **Dynamic code**: Cannot analyze APIs generated at runtime

## Tips for Better Results

To get the most accurate coverage analysis:

1. **Provide repository context**: Mention the programming language and framework
2. **Specify source directories**: If non-standard, point to API locations
3. **Specify test directories**: If tests are in unusual locations, specify them
4. **Mention API patterns**: If APIs use special naming or markers, describe them
5. **Request specific format**: If you need a particular report format, specify it

## Troubleshooting

**No APIs found**: Check that you're looking in the right directories for source files

**No tests found**: Verify test directory location and test file naming patterns

**Incorrect test status**: Review the matching logic and adjust patterns if needed

**Statistics don't add up**: Ensure you're counting APIs and tests consistently

**Excel file errors**: Verify openpyxl library is available and file permissions are correct

## Requirements

- Python 3.6+
- openpyxl library (for Excel report generation)

Install dependencies:
```bash
pip install openpyxl
```

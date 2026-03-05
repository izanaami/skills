# Test Coverage Analysis Skill

This skill analyzes code repositories to identify API definitions and their corresponding test case coverage, generating comprehensive reports in both text and Excel formats.

## What It Does

- Extracts API definitions from header files in `include/` directories
- Searches for corresponding test cases in `tests/` directories  
- Generates detailed coverage reports in both text and Excel formats
- Provides statistics and recommendations for improving test coverage
- Identifies missing test cases for APIs

## When to Use

Use this skill when you need to:
- Analyze test coverage for a codebase
- Find which APIs have corresponding test cases
- Generate test coverage reports
- Identify missing test cases for APIs
- Review API-to-test mapping in a repository
- Assess testing completeness for a library or SDK
- Create documentation about what features are tested vs untested

## How to Use

### As a Skill

When loaded as a skill, simply ask Claude to analyze test coverage:

```
"Analyze the test coverage for this codebase"
"Find which APIs have test cases and generate a report"
"Check what APIs are missing tests in this repository"
```

The skill will automatically:
1. Explore the repository structure
2. Extract API definitions from header files
3. Search for test cases
4. Generate comprehensive reports
5. Provide statistics and recommendations

### As a Script

You can also use the bundled script directly:

```bash
python analyze_coverage.py <repo_path> [output_dir]
```

Example:
```bash
python analyze_coverage.py /path/to/repo /path/to/output
```

## Output Files

The skill generates two output files:

1. **Text Report**: `[repository]_test_coverage_report.txt`
   - Human-readable detailed analysis
   - Includes recommendations and next steps
   - Contains statistics and prioritized suggestions

2. **Excel Report**: `[repository]_api_coverage.xlsx`
   - Machine-readable structured data
   - Contains multiple sheets:
     - Host端API (Host APIs)
     - Device端API (Device APIs)  
     - 统计信息 (Statistics)
   - Easy to filter, sort, and analyze

## Example Output

### Statistics Summary

```
===================================================================================================
SHMEM Test Coverage Report
===================================================================================================

【统计信息】
----------------------------------------------------------------------------------------------------
Host端API总数: 46
Host端有测试的API数: 30
Host端测试覆盖率: 65.2%

Device端API总数: 23
Device端有测试的API数: 20
Device端测试覆盖率: 87.0%

API总数: 69
有测试的API总数: 50
整体测试覆盖率: 72.5%
===================================================================================================
```

### API Coverage Details

```
【Host端API详细列表】
----------------------------------------------------------------------------------------------------
分类           API名称                                    头文件                            测试状态       测试文件
----------------------------------------------------------------------------------------------------
初始化          aclshmemx_init_attr                      shmem_host_init.h              有测试        init_host_test
初始化          aclshmem_finalize                        shmem_host_init.h              无测试        -
内存管理         aclshmem_malloc                          shmem_host_heap.h              有测试        shmem_host_heap_test
内存管理         aclshmem_calloc                          shmem_host_heap.h              无测试        -
```

## Supported Patterns

### API Detection

The skill recognizes API declarations with these patterns:
- `ACLSHMEM_HOST_API function_name(...)`
- `ACLSHMEM_DEVICE function_name(...)`
- `PUBLIC_API function_name(...)`
- `extern "C" function_name(...)`

### Test File Patterns

The skill searches for test files matching these patterns:
- `*_test.cpp`
- `*_test.c`
- `test_*.py`
- `*.spec.js`

### Category Detection

APIs are automatically categorized based on their file path:
- **Host APIs**: init, mem/heap, rma, sync/p2p, cc, team, so
- **Device APIs**: amo, rma, sync/p2p, cc, team, mo

## Customization

The skill can be customized for specific repositories by modifying the patterns in `analyze_coverage.py`:

1. **API detection patterns**: Add regex patterns for API declarations
2. **Test file patterns**: Specify test file naming conventions
3. **Category mapping**: Define how to categorize APIs
4. **Priority rules**: Customize recommendation priorities
5. **Output format**: Adjust report structure for specific needs

## Requirements

- Python 3.6+
- openpyxl library (for Excel report generation)

Install dependencies:
```bash
pip install openpyxl
```

## Limitations

- Static analysis only - cannot determine if tests actually pass
- Relies on naming conventions - may miss tests with unconventional names
- May not fully expand complex macro-generated APIs
- Cannot analyze APIs generated at runtime

## License

See LICENSE.txt in the skill directory for details.

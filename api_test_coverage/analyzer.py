"""
API Test Coverage Analysis Skill
Core analyzer for detecting APIs and matching test cases
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum


class Language(Enum):
    """Supported programming languages"""
    CPP = "cpp"
    PYTHON = "python"
    JAVA = "java"
    GO = "go"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"


@dataclass
class APICategory:
    """API category configuration"""
    name: str
    keywords: List[str]
    priority: str = "medium"  # high, medium, low


@dataclass
class APIInfo:
    """API information"""
    name: str
    category: str
    platform: str  # host, device, client, server, etc.
    header_file: str
    line_number: int
    parameters: List[str]
    return_type: str
    is_public: bool = True


@dataclass
class TestMatch:
    """Test case match information"""
    api_name: str
    test_file: str
    line_number: int
    test_function: str


@dataclass
class CoverageResult:
    """Coverage analysis result"""
    api: APIInfo
    is_covered: bool
    test_files: List[str]
    test_functions: List[str]


class APIDetector:
    """Base class for API detection"""
    
    def __init__(self, language, config):
        self.language = language
        self.config = config
    
    def detect_apis(self, files):
        """Detect APIs from source files"""
        raise NotImplementedError


class CPPAPIDetector(APIDetector):
    """C/C++ API detector"""
    
    def __init__(self, config):
        super().__init__(Language.CPP, config)
        self.api_patterns = config.get('api_patterns', [
            r'ACLSHMEM_HOST_API',
            r'ACLSHMEM_DEVICE_API',
            r'__attribute__\(\(visibility\("default"\)\)',
            r'extern "C"',
        ])
        self.visibility_macros = config.get('visibility_macros', [
            'ACLSHMEM_HOST_API',
            'ACLSHMEM_DEVICE_API',
        ])
    
    def detect_apis(self, files):
        """Detect C/C++ APIs from header files"""
        apis = []
        
        for file_path in files:
            if not file_path.suffix in ['.h', '.hpp', '.hxx']:
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                file_apis = self._parse_header_file(file_path, lines)
                apis.extend(file_apis)
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")
        
        return apis
    
    def _parse_header_file(self, file_path, lines):
        """Parse a single header file for API declarations"""
        apis = []
        in_extern_c = False
        in_function_comment = False
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Track extern "C" blocks
            if 'extern "C"' in line or 'extern \'C\'' in line:
                in_extern_c = True
            elif line.startswith('}') and in_extern_c:
                in_extern_c = False
            
            # Skip comments and preprocessor directives
            if line.startswith('//') or line.startswith('#'):
                continue
            if line.startswith('/*') and '*/' not in line:
                in_function_comment = True
                continue
            if in_function_comment:
                if '*/' in line:
                    in_function_comment = False
                    continue
            
            # Check for API visibility macros
            is_public_api = any(macro in line for macro in self.visibility_macros)
            
            # Try to match function declarations
            function_match = self._match_function_declaration(line)
            if function_match and (is_public_api or in_extern_c):
                api_name, return_type, params = function_match
                
                # Skip if it's a macro definition
                if '#define' in line or 'typedef' in line:
                    continue
                    
                api_info = APIInfo(
                    name=api_name,
                    category=self._categorize_api(api_name),
                    platform=self._detect_platform(file_path),
                    header_file=str(file_path),
                    line_number=line_num,
                    parameters=params,
                    return_type=return_type,
                    is_public=True
                )
                apis.append(api_info)
        
        return apis
    
    def _match_function_declaration(self, line):
        """Match C/C++ function declaration"""
        # Common function patterns
        patterns = [
            r'(\w+(?:\s*\*?)?)\s+(\w+)\s*\(([^)]*)\)',  # return_type func_name(params)
            r'(\w+(?:\s*\*?)?)\s+(\w+)\s*\(([^)]*)\)\s*(?:\w+)',  # return_type func_name(params) ;
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                return_type = match.group(1).strip()
                func_name = match.group(2).strip()
                params_str = match.group(3).strip()
                
                # Clean up return type
                return_type = return_type.replace('*', '').replace('&', '').strip()
                
                # Parse parameters
                params = self._parse_parameters(params_str)
                
                return func_name, return_type, params
        
        return None
    
    def _parse_parameters(self, params_str):
        """Parse function parameters"""
        if not params_str or params_str == 'void':
            return []
        
        # Simple parameter extraction (doesn't handle complex cases)
        params = []
        for param in params_str.split(','):
            param = param.strip()
            if param and param != 'void':
                params.append(param)
        
        return params
    
    def _categorize_api(self, api_name):
        """Categorize API based on name patterns"""
        categories = self.config.get('categories', {})
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword.lower() in api_name.lower():
                    return category
        
        # Default categorization
        if any(word in api_name.lower() for word in ['init', 'setup', 'start', 'create']):
            return 'Initialization'
        elif any(word in api_name.lower() for word in ['malloc', 'free', 'alloc', 'memory', 'buffer']):
            return 'Memory Management'
        elif any(word in api_name.lower() for word in ['put', 'get', 'send', 'recv', 'copy']):
            return 'RMA'
        elif any(word in api_name.lower() for word in ['barrier', 'sync', 'wait', 'signal']):
            return 'Sync'
        elif any(word in api_name.lower() for word in ['team', 'group', 'collective']):
            return 'Team'
        elif any(word in api_name.lower() for word in ['log', 'print', 'debug', 'info']):
            return 'Logging'
        elif any(word in api_name.lower() for word in ['atomic', 'amo', 'fetch', 'add']):
            return 'AMO'
        elif any(word in api_name.lower() for word in ['connect', 'bind', 'listen', 'socket']):
            return 'Network'
        
        return 'Other'
    
    def _detect_platform(self, file_path):
        """Detect platform from file path"""
        path_str = str(file_path).lower()
        
        if '/host/' in path_str or 'host' in path_str:
            return 'host'
        elif '/device/' in path_str or 'device' in path_str:
            return 'device'
        elif '/client/' in path_str or 'client' in path_str:
            return 'client'
        elif '/server/' in path_str or 'server' in path_str:
            return 'server'
        
        return 'unknown'


class PythonAPIDetector(APIDetector):
    """Python API detector"""
    
    def __init__(self, config):
        super().__init__(Language.PYTHON, config)
    
    def detect_apis(self, files):
        """Detect Python APIs from source files"""
        apis = []
        
        for file_path in files:
            if not file_path.suffix in ['.py']:
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                file_apis = self._parse_python_file(file_path, lines)
                apis.extend(file_apis)
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")
        
        return apis
    
    def _parse_python_file(self, file_path, lines):
        """Parse a single Python file for API definitions"""
        apis = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip comments and imports
            if line.startswith('#') or line.startswith('import') or line.startswith('from'):
                continue
            
            # Match function definitions
            function_match = self._match_function_definition(line)
            if function_match:
                func_name, params, is_public = function_match
                
                if is_public:
                    api_info = APIInfo(
                        name=func_name,
                        category=self._categorize_api(func_name),
                        platform=self._detect_platform(file_path),
                        header_file=str(file_path),
                        line_number=line_num,
                        parameters=params,
                        return_type='None',
                        is_public=True
                    )
                    apis.append(api_info)
        
        return apis
    
    def _match_function_definition(self, line):
        """Match Python function definition"""
        # Function definition patterns
        patterns = [
            r'def\s+(\w+)\s*\(([^)]*)\)',  # def func_name(params)
            r'def\s+(\w+)\s*\(([^)]*)\)\s*->',  # def func_name(params) ->
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                func_name = match.group(1)
                params_str = match.group(2).strip()
                
                # Check if public (not starting with _)
                is_public = not func_name.startswith('_')
                
                # Parse parameters
                params = self._parse_parameters(params_str)
                
                return func_name, params, is_public
        
        return None
    
    def _parse_parameters(self, params_str):
        """Parse function parameters"""
        if not params_str:
            return []
        
        params = []
        for param in params_str.split(','):
            param = param.strip()
            if param and param != 'self':
                # Remove default values and type hints
                param = re.sub(r'=.*', '', param)
                param = re.sub(r':.*', '', param)
                param = param.strip()
                if param:
                    params.append(param)
        
        return params
    
    def _categorize_api(self, api_name):
        """Categorize Python API based on name patterns"""
        if any(word in api_name.lower() for word in ['init', 'setup', 'start', 'create']):
            return 'Initialization'
        elif any(word in api_name.lower() for word in ['get', 'set', 'fetch', 'update']):
            return 'Data Access'
        elif any(word in api_name.lower() for word in ['connect', 'disconnect', 'send', 'receive']):
            return 'Network'
        elif any(word in api_name.lower() for word in ['log', 'debug', 'info', 'warn', 'error']):
            return 'Logging'
        
        return 'Other'
    
    def _detect_platform(self, file_path):
        """Detect platform from file path"""
        return 'python'


class TestMatcher:
    """Test case matcher"""
    
    def __init__(self, test_frameworks=None):
        self.test_frameworks = test_frameworks or ['gtest', 'pytest', 'unittest', 'junit']
    
    def match_tests(self, apis, test_files):
        """Match test cases to APIs"""
        coverage_results = []
        
        # Build API name index for faster matching
        api_index = {api.name.lower(): api for api in apis}
        
        for test_file in test_files:
            if not test_file.suffix in ['.cpp', '.py', '.java', '.go']:
                continue
                
            try:
                with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                # Find API calls in test file
                file_matches = self._find_api_calls(test_file, lines, api_index)
                coverage_results.extend(file_matches)
            except Exception as e:
                print(f"Warning: Could not read {test_file}: {e}")
        
        # Ensure all APIs have coverage results
        covered_api_names = {result.api.name for result in coverage_results}
        for api in apis:
            if api.name not in covered_api_names:
                coverage_results.append(CoverageResult(
                    api=api,
                    is_covered=False,
                    test_files=[],
                    test_functions=[]
                ))
        
        return coverage_results
    
    def _find_api_calls(self, test_file, lines, api_index):
        """Find API calls in test file"""
        matches = []
        found_apis = set()
        
        for line_num, line in enumerate(lines, 1):
            # Check for each API name
            for api_name_lower, api in api_index.items():
                if api_name_lower in line.lower():
                    # Found API call
                    if api.name not in found_apis:
                        matches.append(CoverageResult(
                            api=api,
                            is_covered=True,
                            test_files=[str(test_file)],
                            test_functions=[self._extract_test_function(lines, line_num)]
                        ))
                        found_apis.add(api.name)
        
        return matches
    
    def _extract_test_function(self, lines, line_num):
        """Extract test function name from context"""
        # Look backwards for test function definition
        for i in range(max(0, line_num - 10), line_num):
            line = lines[i].strip()
            
            # Google Test pattern
            if line.startswith('TEST_') or line.startswith('TEST_F'):
                return line.split('(')[0].strip()
            
            # pytest pattern
            if line.startswith('def test_'):
                return line.split('(')[0].strip()
            
            # unittest pattern
            if 'def test' in line and 'self' in line:
                return line.split('(')[0].strip()
        
        return "unknown_test"


class Analyzer:
    """Main API coverage analyzer"""
    
    def __init__(self, repo_path, config=None):
        self.repo_path = Path(repo_path)
        self.config = config or self._load_default_config()
        self.language = Language(self.config.get('language', 'cpp'))
        
        # Initialize detector based on language
        if self.language == Language.CPP:
            self.api_detector = CPPAPIDetector(self.config)
        elif self.language == Language.PYTHON:
            self.api_detector = PythonAPIDetector(self.config)
        else:
            raise ValueError(f"Unsupported language: {self.language}")
        
        self.test_matcher = TestMatcher(self.config.get('test_frameworks'))
    
    def _load_default_config(self):
        """Load default configuration"""
        return {
            'language': 'cpp',
            'api_patterns': [
                r'ACLSHMEM_HOST_API',
                r'ACLSHMEM_DEVICE_API',
                r'____attribute__\(\(visibility\("default"\)\)',
            ],
            'include_dirs': ['include', 'include/public', 'src'],
            'test_dirs': ['tests', 'test', 'unittest'],
            'test_frameworks': ['gtest', 'gtest_lite'],
            'categories': {
                'Initialization': ['init', 'setup', 'configure', 'start', 'create'],
                'Memory Management': ['malloc', 'free', 'alloc', 'memory', 'buffer', 'heap'],
                'RMA': ['put', 'get', 'send', 'recv', 'copy', 'rma', 'remote'],
                'Network': ['connect', 'bind', 'listen', 'socket', 'network'],
                'Data': ['get', 'set', 'data', 'value'],
                'Sync': ['sync', 'barrier', 'wait', 'signal', 'lock', 'p2p'],
                'Team': ['team', 'group', 'collective', 'allreduce', 'split'],
                'Logging': ['log', 'print', 'debug', 'info', 'warn', 'error', 'prof'],
                'AMO': ['atomic', 'amo', 'fetch', 'add', 'atomic_add'],
                'CC': ['barrier', 'sync', 'collective', 'allreduce'],
            }
        }
    
    def analyze(self):
        """Perform complete analysis"""
        print(f"Analyzing repository: {self.repo_path}")
        print(f"Language: {self.language.value}")
        
        # Discover files
        source_files = self._discover_source_files()
        test_files = self._discover_test_files()
        
        print(f"Found {len(source_files)} source files")
        print(f"Found {len(test_files)} test files")
        
        # Detect APIs
        print("Detecting APIs...")
        apis = self.api_detector.detect_apis(source_files)
        print(f"Detected {len(apis)} public APIs")
        
        # Match test cases
        print("Matching test cases...")
        coverage_results = self.test_matcher.match_tests(apis, test_files)
        
        # Calculate statistics
        stats = self._calculate_statistics(coverage_results)
        
        return {
            'apis': apis,
            'coverage_results': coverage_results,
            'statistics': stats,
            'config': self.config
        }
    
    def _discover_source_files(self):
        """Discover source files"""
        source_files = []
        include_dirs = self.config.get('include_dirs', ['include'])
        
        for include_dir in include_dirs:
            dir_path = self.repo_path / include_dir
            if dir_path.exists():
                for ext in ['*.h', '*.hpp', '*.hxx', '*.c', '*.cpp', '*.cc', '*.py', '*.java', '*.go']:
                    source_files.extend(dir_path.rglob(ext))
        
        return source_files
    
    def _discover_test_files(self):
        """Discover test files"""
        test_files = []
        test_dirs = self.config.get('test_dirs', ['tests'])
        
        for test_dir in test_dirs:
            dir_path = self.repo_path / test_dir
            if dir_path.exists():
                for ext in ['*.cpp', '*.py', '*.java', '*.go']:
                    test_files.extend(dir_path.rglob(ext))
        
        return test_files
    
    def _calculate_statistics(self, coverage_results):
        """Calculate coverage statistics"""
        total_apis = len(coverage_results)
        covered_apis = sum(1 for result in coverage_results if result.is_covered)
        uncovered_apis = total_apis - covered_apis
        coverage_percentage = (covered_apis / total_apis * 100) if total_apis > 0 else 0
        
        # Category breakdown
        category_stats = {}
        for result in coverage_results:
            category = result.api.category
            if category not in category_stats:
                category_stats[category] = {'total': 0, 'covered': 0}
            category_stats[category]['total'] += 1
            if result.is_covered:
                category_stats[category]['covered'] += 1
        
        return {
            'total_apis': total_apis,
            'covered_apis': covered_apis,
            'uncovered_apis': uncovered_apis,
            'coverage_percentage': coverage_percentage,
            'category_breakdown': category_stats
        }


def main():
    """Main entry point for CLI usage"""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description='API Test Coverage Analysis')
    parser.add_argument('--path', type=str, default='.', help='Repository path')
    parser.add_argument('--language', type=str, default='cpp', help='Programming language')
    parser.add_argument('--include-dir', type=str, action='append', help='Include directories')
    parser.add_argument('--test-dir', type=str, action='append', help='Test directories')
    parser.add_argument('--config', type=str, help='Configuration file')
    parser.add_argument('--output-dir', type=str, default='./reports', help='Output directory')
    parser.add_argument('--output-format', type=str, default='all', help='Output format (xlsx, md, all)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Override config with CLI arguments
    if args.language:
        config['language'] = args.language
    if args.include_dir:
        config['include_dirs'] = args.include_dir
    if args.test_dir:
        config['test_dirs'] = args.test_dir
    
    # Create analyzer
    try:
        analyzer = Analyzer(args.path, config)
        results = analyzer.analyze()
        
        # Generate reports
        import reporter
        
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        reporter_instance = reporter.Reporter(results, str(output_dir))
        
        if args.output_format in ['all', 'xlsx']:
            reporter_instance.generate_excel('api_test_coverage.xlsx')
            print(f"Excel report generated: {output_dir}/api_test_coverage.xlsx")
        
        if args.output_format in ['all', 'md']:
            reporter_instance.generate_markdown('api_test_coverage_report.md')
            print(f"Markdown report generated: {output_dir}/api_test_coverage_report.md")
        
        # Print summary
        stats = results['statistics']
        print(f"\nCoverage Summary:")
        print(f"  Total APIs: {stats['total_apis']}")
        print(f"  Covered APIs: {stats['covered_apis']}")
        print(f"  Uncovered APIs: {stats['uncovered_apis']}")
        print(f"  Coverage: {stats['coverage_percentage']:.1f}%")
        
    except Exception as e:
        print(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

"""
Report generator for API test coverage analysis
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class Reporter:
    """Generate coverage reports in multiple formats"""
    
    def __init__(self, analysis_results: Dict, output_dir: str):
        self.results = analysis_results
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_excel(self, filename: str = 'api_test_coverage.xlsx'):
        """Generate Excel coverage report"""
        try:
            import pandas as pd
        except ImportError:
            print("Warning: pandas not available. Skipping Excel report generation.")
            return
        
        coverage_results = self.results['coverage_results']
        
        excel_data = []
        for result in coverage_results:
            api = result.api
            test_files_str = '; '.join(result.test_files) if result.test_files else ''
            
            excel_data.append({
                'API类别': api.category,
                'host还是device接口': api.platform,
                'API Name': api.name,
                'API定义头文件': api.header_file,
                '是否有测试用例': 'YES' if result.is_covered else 'NO',
                '测试用例所在文件': test_files_str
            })
        
        df = pd.DataFrame(excel_data)
        df = df.sort_values(by=['API类别', '是否有测试用例'], ascending=[True, False])
        
        output_path = self.output_dir / filename
        df.to_excel(output_path, index=False, engine='openpyxl')
        
        print(f"Excel report generated: {output_path}")
    
    def generate_markdown(self, filename: str = 'api_test_coverage_report.md'):
        """Generate Markdown coverage report"""
        coverage_results = self.results['coverage_results']
        stats = self.results['statistics']
        
        md_content = self._build_markdown_content(coverage_results, stats)
        
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"Markdown report generated: {output_path}")
    
    def _build_markdown_content(self, coverage_results: List, stats: Dict) -> str:
        """Build complete Markdown report"""
        content = []
        
        content.append("# API测试用例覆盖分析报告\n")
        content.append(self._get_generation_info())
        content.append("\n## 一、接口统计概览\n")
        content.append(self._build_statistics_table(stats))
        
        content.append("\n## 二、完整对外接口清单\n")
        content.append(self._build_api_inventory_table(coverage_results))
        
        content.append("\n## 三、未覆盖测试用例的对外接口（需重点补充用例）\n")
        content.append(self._build_uncovered_apis_table(coverage_results))
        
        content.append("\n## 四、优化建议\n")
        content.append(self._build_recommendations(coverage_results))
        
        return '\n'.join(content)
    
    def _get_generation_info(self) -> str:
        """Get report generation information"""
        return f"""**报告生成时间**: {datetime.now().strftime('%Y-%m-%d')}  
**分析工具**: 静态代码分析  
**分析范围**: include/ 和 tests/ 目录  
**分析语言**: {self.results['config'].get('language', 'cpp').upper()}  
**分析标准**: 基于公共API宏和extern声明识别对外接口
"""
    
    def _build_statistics_table(self, stats: Dict) -> str:
        """Build statistics table"""
        table = []
        table.append("| 统计项 | 数量 |")
        table.append("|--------|------|")
        table.append(f"| 总对外接口数 | {stats['total_apis']} |")
        table.append(f"| 已覆盖接口数 | {stats['covered_apis']} |")
        table.append(f"| 未覆盖接口数 | {stats['uncovered_apis']} |")
        table.append(f"| 测试用例覆盖率 | {stats['coverage_percentage']:.1f}% |")
        
        table.append("\n### 按类别统计")
        table.append("| 类别 | 总数 | 已覆盖 | 覆盖率 |")
        table.append("|------|------|--------|--------|")
        
        for category, cat_stats in stats['category_breakdown'].items():
            total = cat_stats['total']
            covered = cat_stats['covered']
            coverage_rate = (covered / total * 100) if total > 0 else 0
            table.append(f"| {category} | {total} | {covered} | {coverage_rate:.1f}% |")
        
        return '\n'.join(table)
    
    def _build_api_inventory_table(self, coverage_results: List) -> str:
        """Build complete API inventory table"""
        table = []
        table.append("| API类别 | host还是device接口 | API Name | API定义头文件 | 是否被测试用例覆盖 |")
        table.append("|----------|-------------------|----------|----------------|------------------|")
        
        for result in coverage_results:
            api = result.api
            status = " " if result.is_covered else " "
            table.append(f"| {api.category} | {api.platform} | {api.name} | {api.header_file} | {status} |")
        
        return '\n'.join(table)
    
    def _build_uncovered_apis_table(self, coverage_results: List) -> str:
        """Build uncovered APIs table with priorities"""
        uncovered = [r for r in coverage_results if not r.is_covered]
        
        if not uncovered:
            return "所有接口都有测试用例覆盖！ "
        
        table = []
        table.append("以下接口当前没有测试用例覆盖，建议优先补充：\n")
        table.append("| API类别 | host还是device接口 | API Name | API定义头文件 | 优先级 |")
        table.append("|----------|-------------------|----------|----------------|--------|")
        
        priority_order = {'高': 0, '中': 1, '低': 2}
        uncovered_sorted = sorted(uncovered, key=lambda x: priority_order.get(self._get_priority(x.api.category), 3))
        
        for result in uncovered_sorted:
            api = result.api
            priority = self._get_priority(api.category)
            table.append(f"| {api.category} | {api.platform} | {api.name} | {api.header_file} | {priority} |")
        
        return '\n'.join(table)
    
    def _get_priority(self, category: str) -> str:
        """Get priority level for category"""
        high_priority = ['Initialization', 'Logging', 'CC', 'Network']
        medium = ['RMA', 'Team', 'P2P Sync', 'Sync', 'Data Access']
        
        if category in high_priority:
            return '高'
        elif category in medium:
            return '中'
        else:
            return '低'
    
    def _build_recommendations(self, coverage_results: List) -> str:
        """Build detailed recommendations"""
        recommendations = []
        
        uncovered_by_category = {}
        for result in coverage_results:
            if not result.is_covered:
                category = result.api.category
                if category not in uncovered_by_category:
                    uncovered_by_category[category] = []
                uncovered_by_category[category].append(result.api)
        
        recommendations.append("### 4.1 针对未覆盖接口的测试补充建议\n")
        
        high_priority = ['Initialization', 'Logging', 'CC', 'Network']
        medium = ['RMA', 'Team', 'P2P Sync', 'Sync', 'Data Access']
        low_priority = ['Memory Management', 'AMO', 'Other']
        
        recommendations.append("#### 高优先级（建议立即补充）\n")
        recommendations.append(self._build_category_recommendations(uncovered_by_category, high_priority))
        
        recommendations.append("\n#### 中优先级（建议近期补充着）\n")
        recommendations.append(self._build_category_recommendations(uncovered_by_category, medium))
        
        recommendations.append("\n#### 低优先级（可后续补充）\n")
        recommendations.append(self._build_category_recommendations(uncovered_by_category, 
low_priority))
        
        recommendations.append("\n### 4.2 接口测试用例规范与完善方向\n")
        recommendations.append(self._build_general_recommendations())
        
        return '\n'.join(recommendations)
    
    def _build_category_recommendations(self, uncovered_by_category: Dict, priority_categories: List[str]) -> str:
        """Build recommendations for specific priority category"""
        recommendations = []
        
        for category in priority_categories:
            if category in uncovered_by_category:
                apis = uncovered_by_category[category]
                recommendations.append(f"1. **{category}相关接口**\n")
                
                for api in apis[:5]:
                    recommendations.append(f"   - `{api.name}`: 需要补充{self._get_api_description(api)}的测试用例\n")
                
                if len(apis) > 5:
                    recommendations.append(f"   - 还有{len(apis) - 5}个{category}接口需要补充测试用例\n")
                
                recommendations.append("")
        
        return '\n'.join(recommendations)
    
    def _get_api_description(self, api) -> str:
        """Get description for API based on name"""
        name_lower = api.name.lower()
        
        if 'init' in name_lower:
            return "初始化"
        elif 'malloc' in name_lower or 'alloc' in name_lower:
            return "内存分配"
        elif 'free' in name_lower:
            return "内存释放"
        elif 'put' in name_lower:
            return "数据传输（put）"
        elif 'get' in name_lower:
            return "数据获取（get）"
        elif 'barrier' in name_lower:
            return "屏障同步"
        elif 'sync' in name_lower:
            return "同步操作"
        elif 'log' in name_lower:
            return "日志记录"
        elif 'team' in name_lower:
            return "团队管理"
        elif 'signal' in name_lower:
            return "信号操作"
        elif 'atomic' in name_lower:
            return "原子操作"
        
        return "功能"
    
    def _build_general_recommendations(self) -> str:
        """Build general recommendations"""
        recommendations = []
        
        recommendations.append("#### 测试用例组织规范\n")
        recommendations.append("1. **目录结构规范**\n")
        recommendations.append("   - 按照API类别组织测试用例目录结构\n")
        recommendations.append("   - Host端测试用例放在 `tests/unittest/host/` 下\n")
        recommendations.append("   - Device端测试用例放在 `tests/unittest/device/` 下\n")
        recommendations.append("   - 每个API类别创建独立的子目录\n")
        
        recommendations.append("\n2. **测试用例命名规范**\n")
        recommendations.append("   - 使用描述性的测试用例名称，如 `test_aclshmem_init_basic_success`\n")
        recommendations.append("   - 测试失败场景的用例名称应包含失败原因，如 `test_aclshmem_init_invalid_rank_id`\n")
        recommendations.append("   - 使用统一的命名前缀，便于识别和维护\n")
        
        recommendations.append("\n3. **测试用例内容规范**\n")
        recommendations.append("   - 每个测试用例应包含初始化和清理逻辑\n")
        recommendations.append("   - 使用测试框架的断言宏（EXPECT_EQ, ASSERT_EQ等）\n")
        recommendations.append("   - 添加适当的注释说明测试目的和预期结果\n")
        recommendations.append("   - 考虑边界条件和异常情况\n")
        
        recommendations.append("\n#### 测试用例完善方向\n")
        recommendations.append("1. **增加边界条件测试**\n")
        recommendations.append("   - 测试零值、最大值、最小值等边界条件\n")
        recommendations.append("   - 测试无效参数的错误处理\n")
        recommendations.append("   - 测试内存不足等资源限制情况\n")
        
        recommendations.append("\n2. **增加并发测试**\n")
        recommendations.append("   - 测试多PE并发调用的正确性\n")
        recommendations.append("   - 测试多线程环境下的接口行为\n")
        recommendations.append("   - 测试资源竞争和死锁场景\n")
        
        recommendations.append("\n3. **增加性能测试**\n")
        recommendations.append("   - 测试大数据量传输的性能\n")
        recommendations.append("   - 测试高频调用的性能表现\n")
        recommendations.append("   - 收集性能指标用于优化参考\n")
        
        recommendations.append("\n4. **增加集成测试**\n")
        recommendations.append("   - 测试多个API组合使用的场景\n")
        recommendations.append("   - 测试复杂工作流程的端到端功能\n")
        recommendations.append("   - 测试与外部系统的集成情况\n")
        
        recommendations.append("\n#### 测试用例维护建议\n")
        recommendations.append("1. **定期更新测试用例**\n")
        recommendations.append("   - 当新增API时，同步添加测试用例\n")
        recommendations.append("   - 当API行为变更时，更新相关测试用例\n")
        recommendations.append("   - 定期review测试用例的有效性\n")
        
        recommendations.append("\n2. **测试用例文档化**\n")
        recommendations.append("   - 为复杂测试用例添加详细注释\n")
        recommendations.append("   - 维护测试用例的设计文档\n")
        recommendations.append("   - 记录已知问题和限制\n")
        
        recommendations.append("\n3. **持续集成集成**\n")
        recommendations.append("   - 将测试用例集成到CI/CD流程\n")
        recommendations.append("   - 设置自动化测试执行和报告\n")
        recommendations.append("   - 建立测试失败的告警机制\n")
        
        return '\n'.join(recommendations)
    
    def generate_json(self, filename: str = 'api_test_coverage.json'):
        """Generate JSON coverage report for programmatic access"""
        json_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'language': self.results['config'].get('language', 'cpp'),
                'total_apis': self.results['statistics']['total_apis'],
                'covered_apis': self.results['statistics']['covered_apis'],
                'coverage_percentage': self.results['statistics']['coverage_percentage']
            },
            'apis': []
        }
        
        for result in self.results['coverage_results']:
            api_data = {
                'name': result.api.name,
                'category': result.api.category,
                'platform': result.api.platform,
                'header_file': result.api.header_file,
                'line_number': result.api.line_number,
                'is_covered': result.is_covered,
                'test_files': result.test_files,
                'test_functions': result.test_functions
            }
            json_data['apis'].append(api_data)
        
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"JSON report generated: {output_path}")

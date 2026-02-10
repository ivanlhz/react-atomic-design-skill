#!/usr/bin/env python3
"""
Atomic Design Structure Analyzer

Scans a React project's components directory and detects violations
of Atomic Design principles.

Usage:
    python analyze_structure.py [path_to_src]
    
Example:
    python analyze_structure.py ./src
    python analyze_structure.py /path/to/project/src
"""

import os
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Set


@dataclass
class Violation:
    type: str
    path: str
    message: str
    severity: str = "warning"  # warning | error


@dataclass
class AnalysisReport:
    violations: List[Violation] = field(default_factory=list)
    components_found: int = 0
    components_with_tests: int = 0
    components_with_barrels: int = 0
    
    def add(self, violation: Violation):
        self.violations.append(violation)
    
    def has_errors(self) -> bool:
        return any(v.severity == "error" for v in self.violations)


class AtomicDesignAnalyzer:
    COMPONENT_EXTENSIONS = {'.tsx', '.jsx'}
    TEST_PATTERNS = {'.test.tsx', '.test.jsx', '.spec.tsx', '.spec.jsx'}
    BARREL_FILES = {'index.ts', 'index.tsx', 'index.js', 'index.jsx'}
    
    # Patterns that suggest logic in component
    LOGIC_PATTERNS = [
        r'const\s+\w+\s*=\s*\([^)]*\)\s*=>\s*\{',  # arrow functions
        r'function\s+\w+\s*\([^)]*\)\s*\{',         # regular functions
        r'async\s+function',                         # async functions
    ]
    
    STATE_HOOKS = ['useState', 'useReducer', 'useEffect', 'useMemo', 'useCallback']
    
    def __init__(self, src_path: str):
        self.src_path = Path(src_path)
        self.components_path = self.src_path / 'components'
        self.report = AnalysisReport()
        
    def analyze(self) -> AnalysisReport:
        if not self.components_path.exists():
            self.report.add(Violation(
                type="structure",
                path=str(self.components_path),
                message="components/ directory not found",
                severity="error"
            ))
            return self.report
        
        self._check_top_level_structure()
        self._analyze_components()
        
        return self.report
    
    def _check_top_level_structure(self):
        """Check that atoms/, molecules/, organisms/ exist"""
        expected_dirs = ['atoms', 'molecules', 'organisms']
        
        for dir_name in expected_dirs:
            dir_path = self.components_path / dir_name
            if not dir_path.exists():
                self.report.add(Violation(
                    type="structure",
                    path=str(dir_path),
                    message=f"Missing {dir_name}/ directory",
                    severity="warning"
                ))
    
    def _analyze_components(self):
        """Walk through all component directories"""
        for level in ['atoms', 'molecules', 'organisms']:
            level_path = self.components_path / level
            if not level_path.exists():
                continue
                
            for component_dir in self._find_component_dirs(level_path):
                self._analyze_component(component_dir, level)
    
    def _find_component_dirs(self, base_path: Path) -> List[Path]:
        """Find all component directories (directories containing .tsx files)"""
        component_dirs = []
        
        for root, dirs, files in os.walk(base_path):
            root_path = Path(root)
            has_component = any(
                f.endswith(tuple(self.COMPONENT_EXTENSIONS)) 
                and not any(f.endswith(p) for p in self.TEST_PATTERNS)
                for f in files
            )
            if has_component:
                component_dirs.append(root_path)
        
        return component_dirs
    
    def _analyze_component(self, component_path: Path, level: str):
        """Analyze a single component directory"""
        self.report.components_found += 1
        
        files = list(component_path.iterdir())
        file_names = {f.name for f in files if f.is_file()}
        
        # Check for barrel
        has_barrel = bool(file_names & self.BARREL_FILES)
        if has_barrel:
            self.report.components_with_barrels += 1
        else:
            self.report.add(Violation(
                type="barrel",
                path=str(component_path),
                message="Missing barrel file (index.ts)",
                severity="warning"
            ))
        
        # Check for tests
        has_test = any(
            any(f.endswith(pattern) for pattern in self.TEST_PATTERNS)
            for f in file_names
        )
        if has_test:
            self.report.components_with_tests += 1
        else:
            self.report.add(Violation(
                type="test",
                path=str(component_path),
                message="Missing test file",
                severity="warning"
            ))
        
        # Analyze component files for logic
        for file in files:
            if file.suffix in self.COMPONENT_EXTENSIONS:
                if not any(file.name.endswith(p) for p in self.TEST_PATTERNS):
                    self._check_component_logic(file, level)
                    self._check_imports(file, level)
    
    def _check_component_logic(self, file_path: Path, level: str):
        """Check if component has too much logic that should be in a hook"""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            return
        
        # Count state hooks
        hook_count = sum(content.count(hook) for hook in self.STATE_HOOKS)
        
        # Count function definitions (excluding the component itself)
        function_matches = []
        for pattern in self.LOGIC_PATTERNS:
            function_matches.extend(re.findall(pattern, content))
        
        # Heuristic: if more than 2 hooks AND more than 2 functions, suggest extraction
        if hook_count > 2 and len(function_matches) > 2:
            self.report.add(Violation(
                type="logic",
                path=str(file_path),
                message=f"Component has {hook_count} hooks and {len(function_matches)} functions. Consider extracting logic to a custom hook.",
                severity="warning"
            ))
    
    def _check_imports(self, file_path: Path, level: str):
        """Check for inverted dependencies"""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            return
        
        # atoms should not import from molecules or organisms
        # molecules should not import from organisms
        
        forbidden_imports = {
            'atoms': ['molecules', 'organisms'],
            'molecules': ['organisms'],
            'organisms': []
        }
        
        for forbidden in forbidden_imports.get(level, []):
            # Look for imports from forbidden level
            pattern = rf"from\s+['\"].*/{forbidden}/|from\s+['\"]@/components/{forbidden}/"
            if re.search(pattern, content):
                self.report.add(Violation(
                    type="dependency",
                    path=str(file_path),
                    message=f"{level.capitalize()} should not import from {forbidden}",
                    severity="error"
                ))


def print_report(report: AnalysisReport):
    """Print analysis report to console"""
    
    print("\n" + "=" * 60)
    print("  ATOMIC DESIGN ANALYSIS REPORT")
    print("=" * 60 + "\n")
    
    # Summary
    print(f"📦 Components found: {report.components_found}")
    print(f"✅ With tests: {report.components_with_tests}/{report.components_found}")
    print(f"📄 With barrels: {report.components_with_barrels}/{report.components_found}")
    print()
    
    if not report.violations:
        print("🎉 No violations found! Your structure looks good.\n")
        return
    
    # Group violations by type
    by_type = {}
    for v in report.violations:
        by_type.setdefault(v.type, []).append(v)
    
    type_icons = {
        'structure': '🏗️ ',
        'barrel': '📄',
        'test': '🧪',
        'logic': '⚙️ ',
        'dependency': '🔗'
    }
    
    type_titles = {
        'structure': 'Structure Issues',
        'barrel': 'Missing Barrels',
        'test': 'Missing Tests',
        'logic': 'Logic in Components',
        'dependency': 'Dependency Violations'
    }
    
    for vtype, violations in by_type.items():
        icon = type_icons.get(vtype, '⚠️')
        title = type_titles.get(vtype, vtype)
        
        print(f"{icon} {title} ({len(violations)})")
        print("-" * 40)
        
        for v in violations:
            severity_icon = "❌" if v.severity == "error" else "⚠️"
            # Show relative path
            rel_path = v.path.split('/components/')[-1] if '/components/' in v.path else v.path
            print(f"  {severity_icon} {rel_path}")
            print(f"     {v.message}")
        print()
    
    # Final summary
    errors = sum(1 for v in report.violations if v.severity == "error")
    warnings = sum(1 for v in report.violations if v.severity == "warning")
    
    print("-" * 60)
    if errors:
        print(f"❌ {errors} error(s), {warnings} warning(s)")
    else:
        print(f"⚠️  {warnings} warning(s), no errors")
    print()


def main():
    # Default to current directory's src/
    src_path = sys.argv[1] if len(sys.argv) > 1 else './src'
    
    if not os.path.exists(src_path):
        print(f"Error: Path '{src_path}' does not exist")
        print(f"Usage: python {sys.argv[0]} [path_to_src]")
        sys.exit(1)
    
    analyzer = AtomicDesignAnalyzer(src_path)
    report = analyzer.analyze()
    print_report(report)
    
    # Exit with error code if there are errors
    sys.exit(1 if report.has_errors() else 0)


if __name__ == '__main__':
    main()

"""Simple test for the Pylint analyzer."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzer import PylintAnalyzer


def test_pylint_analyzer():
    """Test basic Pylint analysis."""
    code = """
def foo():
    x = 1
    return 2
"""
    
    analyzer = PylintAnalyzer()
    issues = analyzer.analyze(code)
    
    print(f"Found {len(issues)} issues:")
    for issue in issues:
        print(f"  Line {issue['line']}: {issue['message']} ({issue['rule_id']})")
    
    # Should find unused variable 'x'
    assert len(issues) > 0
    assert any('x' in issue['message'] for issue in issues)
    print("✅ Test passed!")


if __name__ == "__main__":
    test_pylint_analyzer()

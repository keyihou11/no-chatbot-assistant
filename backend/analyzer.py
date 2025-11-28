"""Pylint analyzer wrapper for No-Chatbot."""
import json
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class PylintAnalyzer:
    """Wrapper for running Pylint and parsing results."""
    
    def __init__(self):
        """Initialize the Pylint analyzer."""
        self.severity_map = {
            "error": "error",
            "warning": "warning",
            "refactor": "info",
            "convention": "info",
            "info": "info"
        }
    
    def analyze(self, code_content: str, file_path: str = "temp.py") -> List[Dict[str, Any]]:
        """
        Run Pylint on the provided code content.
        
        Args:
            code_content: Python code to analyze
            file_path: Virtual file path for context (not used for actual I/O)
            
        Returns:
            List of issues found by Pylint
        """
        issues = []
        
        try:
            # Write code to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
                tmp.write(code_content)
                tmp_path = tmp.name
            
            # Run Pylint with JSON output
            # Disable some less important checks, focusing on code logic issues
            result = subprocess.run(
                [
                    'pylint',
                    '--output-format=json',
                    '--score=n',
                    '--disable=C0303,C0304,C0114,C0115,C0116,R0903',  # Disable formatting and design-related checks
                    tmp_path
                ],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Parse JSON output
            if result.stdout:
                pylint_results = json.loads(result.stdout)
                
                for item in pylint_results:
                    issues.append({
                        'line': item.get('line', 1),
                        'column': item.get('column', 0),
                        'severity': self.severity_map.get(item.get('type', 'info'), 'info'),
                        'message': item.get('message', ''),
                        'rule_id': item.get('message-id', item.get('symbol', 'unknown'))
                    })
            
            # Clean up temporary file
            Path(tmp_path).unlink(missing_ok=True)
            
            logger.info(f"Pylint found {len(issues)} issues")
            
        except subprocess.TimeoutExpired:
            logger.error("Pylint analysis timed out")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Pylint output: {e}")
        except Exception as e:
            logger.error(f"Pylint analysis failed: {e}")
        
        return issues

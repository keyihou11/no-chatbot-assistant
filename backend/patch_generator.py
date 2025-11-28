"""Patch generator for applying code fixes."""
import difflib
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PatchGenerator:
    """Generate and apply unified diff patches."""
    
    @staticmethod
    def create_patch(original: str, fixed: str, filename: str = "file.py") -> str:
        """
        Create a unified diff patch from original and fixed code.
        
        Args:
            original: Original code content
            fixed: Fixed code content
            filename: Name of the file (for diff header)
            
        Returns:
            Unified diff string
        """
        original_lines = original.splitlines(keepends=True)
        fixed_lines = fixed.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            original_lines,
            fixed_lines,
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
            lineterm=''
        )
        
        return ''.join(diff)
    
    @staticmethod
    def apply_patch(original: str, patch: str) -> Optional[str]:
        """
        Apply a unified diff patch to original code.
        
        Args:
            original: Original code content
            patch: Unified diff patch string
            
        Returns:
            Patched code, or None if patch application failed
        """
        try:
            # Simple patch application for MVP
            # For a production system, use a proper patch library
            
            # Extract the fixed content from the patch
            # This is a simplified implementation
            patch_lines = patch.split('\n')
            result_lines = original.split('\n')
            
            # Track which line we're modifying
            current_line = 0
            
            for line in patch_lines:
                if line.startswith('@@'):
                    # Parse the line range
                    # Format: @@ -start,count +start,count @@
                    parts = line.split()
                    if len(parts) >= 3:
                        # Extract the starting line for the new version
                        new_start = parts[2].split(',')[0]
                        current_line = int(new_start.lstrip('+')) - 1
                elif line.startswith('+') and not line.startswith('+++'):
                    # Add line
                    result_lines.insert(current_line, line[1:])
                    current_line += 1
                elif line.startswith('-') and not line.startswith('---'):
                    # Remove line
                    if current_line < len(result_lines):
                        result_lines.pop(current_line)
                elif line.startswith(' '):
                    # Context line, move forward
                    current_line += 1
            
            return '\n'.join(result_lines)
            
        except Exception as e:
            logger.error(f"Failed to apply patch: {e}")
            return None
    
    @staticmethod
    def extract_code_from_llm_patch(llm_patch: str) -> Optional[str]:
        """
        Extract the fixed code from an LLM-generated patch.
        
        Args:
            llm_patch: Patch string from LLM (may contain markdown)
            
        Returns:
            Clean unified diff, or None if extraction failed
        """
        # Remove markdown code fences if present
        lines = llm_patch.strip().split('\n')
        clean_lines = []
        in_code_block = False
        
        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block or line.startswith(('---', '+++', '@@', '+', '-', ' ')):
                clean_lines.append(line)
        
        return '\n'.join(clean_lines) if clean_lines else llm_patch

#!/usr/bin/env python3
"""
Stardeus Translation Validator

This script validates CSV translation files for the Stardeus game.

USAGE:
    python validate_translations.py [--verbose] [--strict]

OPTIONS:
    --verbose    Show detailed information for each file
    --strict     Treat warnings as errors (return exit code 1)

CHECKS PERFORMED:
    1. Proper CSV format (4 columns: Key, Translation, Version, Comment)
    2. UTF-8 encoding without BOM
    3. Variables consistency (check for malformed placeholders like unmatched braces)
    4. HTML tag integrity (balanced opening/closing tags within translation)
    5. Empty translations (warnings)
    6. Duplicate keys

NOTE:
    Without an English reference file, variable and HTML tag checks are limited to
    validating proper formatting within each translation, not comparing against source.

EXIT CODES:
    0 - Success (no critical errors)
    1 - Critical errors found (or warnings with --strict)
"""

import csv
import re
import argparse
import sys
from pathlib import Path
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Set


class ValidationIssue:
    """Represents a validation issue found in a translation file."""
    
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"
    
    def __init__(self, severity: str, line_num: int, key: str, message: str):
        self.severity = severity
        self.line_num = line_num
        self.key = key
        self.message = message
    
    def __str__(self):
        return f"  [{self.severity}] Line {self.line_num} (Key: {self.key}): {self.message}"


class TranslationValidator:
    """Validates translation CSV files."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.issues: Dict[str, List[ValidationIssue]] = defaultdict(list)
        self.stats = {
            'files_validated': 0,
            'total_keys': 0,
            'critical_errors': 0,
            'warnings': 0,
            'infos': 0
        }
    
    def validate_file(self, file_path: Path) -> List[ValidationIssue]:
        """
        Validate a single translation CSV file.
        
        Args:
            file_path: Path to the CSV file to validate
            
        Returns:
            List of ValidationIssue objects found
        """
        issues = []
        
        # Check file encoding
        encoding_issue = self._check_encoding(file_path)
        if encoding_issue:
            issues.append(encoding_issue)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse CSV
            lines = content.splitlines()
            reader = csv.reader(lines)
            
            # Check header
            try:
                header = next(reader)
                num_columns = len(header)
                
                # Support both 4 and 5 column formats
                # 4 columns: Key, Translation, Version, Comment
                # 5 columns: Key (notes), Translation, Version, Comment (notes), [empty]
                if num_columns not in [4, 5]:
                    issues.append(ValidationIssue(
                        ValidationIssue.CRITICAL, 1, "N/A",
                        f"Header should have 4 or 5 columns, found {num_columns}"
                    ))
                    return issues
                    
                # Check for common variations in first column name
                if header[0] not in ['Key', 'key'] and not header[0].startswith('Key'):
                    issues.append(ValidationIssue(
                        ValidationIssue.WARNING, 1, "N/A",
                        f"First column should be 'Key', found '{header[0]}'"
                    ))
            except StopIteration:
                issues.append(ValidationIssue(
                    ValidationIssue.CRITICAL, 0, "N/A",
                    "File is empty"
                ))
                return issues
            
            # Track keys for duplicate detection
            key_tracker = Counter()
            line_num = 2  # Start at 2 (1 is header)
            
            for row in reader:
                # Skip completely empty lines
                if not row or all(not cell.strip() for cell in row):
                    line_num += 1
                    continue
                
                # Check column count (allow both 4 and 5 column formats)
                if len(row) not in [num_columns, 4, 5]:
                    issues.append(ValidationIssue(
                        ValidationIssue.CRITICAL, line_num, row[0] if row else "N/A",
                        f"Expected {num_columns} columns (like header), found {len(row)}"
                    ))
                    line_num += 1
                    continue
                
                # Extract key and translation (same position in both 4 and 5 column formats)
                key = row[0]
                translation = row[1] if len(row) > 1 else ""
                version = row[2] if len(row) > 2 else ""
                comment = row[3] if len(row) > 3 else ""
                
                # Track duplicate keys
                key_tracker[key] += 1
                
                # Validate key is not empty
                if not key.strip():
                    issues.append(ValidationIssue(
                        ValidationIssue.CRITICAL, line_num, "EMPTY",
                        "Key field is empty"
                    ))
                
                # Check for empty translation
                if not translation.strip():
                    issues.append(ValidationIssue(
                        ValidationIssue.WARNING, line_num, key,
                        "Translation is empty"
                    ))
                else:
                    # Validate variables consistency
                    var_issues = self._check_variables(key, translation, line_num)
                    issues.extend(var_issues)
                    
                    # Validate HTML tags
                    tag_issues = self._check_html_tags(key, translation, line_num)
                    issues.extend(tag_issues)
                
                line_num += 1
            
            # Check for duplicate keys
            for key, count in key_tracker.items():
                if count > 1:
                    issues.append(ValidationIssue(
                        ValidationIssue.CRITICAL, 0, key,
                        f"Duplicate key found {count} times"
                    ))
            
            self.stats['total_keys'] += len(key_tracker)
            
        except UnicodeDecodeError as e:
            issues.append(ValidationIssue(
                ValidationIssue.CRITICAL, 0, "N/A",
                f"Unable to read file with UTF-8 encoding: {e}"
            ))
        except csv.Error as e:
            issues.append(ValidationIssue(
                ValidationIssue.CRITICAL, 0, "N/A",
                f"CSV parsing error: {e}"
            ))
        except Exception as e:
            issues.append(ValidationIssue(
                ValidationIssue.CRITICAL, 0, "N/A",
                f"Unexpected error: {e}"
            ))
        
        return issues
    
    def _check_encoding(self, file_path: Path) -> ValidationIssue | None:
        """Check if file has UTF-8 BOM (which should be avoided)."""
        try:
            with open(file_path, 'rb') as f:
                start = f.read(3)
                if start == b'\xef\xbb\xbf':
                    return ValidationIssue(
                        ValidationIssue.WARNING, 0, "N/A",
                        "File has UTF-8 BOM marker (should be UTF-8 without BOM)"
                    )
        except Exception:
            pass
        return None
    
    def _check_variables(self, key: str, translation: str, line_num: int) -> List[ValidationIssue]:
        """
        Check for malformed placeholder variables in translation.
        Supports formats: {0}, {1}, {variable}, etc.
        Without an English reference file, we can only check for basic issues.
        """
        issues = []
        
        # Check for unmatched braces (malformed placeholders)
        open_braces = translation.count('{')
        close_braces = translation.count('}')
        
        if open_braces != close_braces:
            issues.append(ValidationIssue(
                ValidationIssue.CRITICAL, line_num, key,
                f"Unmatched braces in translation: {open_braces} '{{' vs {close_braces} '}}'"
            ))
        
        # Check for potentially malformed placeholders (e.g., { 0}, {0 }, etc.)
        malformed_pattern = r'\{\s+\w+\s*\}|\{\s*\w+\s+\}'
        malformed = re.findall(malformed_pattern, translation)
        if malformed:
            issues.append(ValidationIssue(
                ValidationIssue.WARNING, line_num, key,
                f"Potentially malformed placeholders (extra spaces): {', '.join(malformed)}"
            ))
        
        return issues
    
    def _check_html_tags(self, key: str, translation: str, line_num: int) -> List[ValidationIssue]:
        """Check that HTML tags are properly balanced in translation."""
        issues = []
        
        # List of self-closing HTML/Unity TextMesh Pro tags that don't need closing tags
        self_closing_tags = {'br', 'hr', 'img', 'input', 'link', 'meta', 'area', 
                            'base', 'col', 'embed', 'param', 'source', 'track', 'wbr',
                            'sprite'}  # Unity TextMesh Pro
        
        # Extract HTML-like tags from translation only: <tag>, <tag=value>, and </tag>
        # This handles both regular HTML and Unity TextMesh Pro tags like <color=#FF0000>
        tag_pattern = r'<(/?)(\w+)(?:[=\s][^>]*)?>'
        trans_tags = re.findall(tag_pattern, translation)
        
        # Build tag balance for translation
        trans_balance = defaultdict(int)
        for is_closing, tag_name in trans_tags:
            tag_lower = tag_name.lower()
            
            # Skip self-closing tags
            if tag_lower in self_closing_tags:
                continue
            
            if is_closing:
                trans_balance[tag_lower] -= 1
            else:
                trans_balance[tag_lower] += 1
        
        # Check if tags are balanced within the translation
        for tag, balance in trans_balance.items():
            if balance != 0:
                issues.append(ValidationIssue(
                    ValidationIssue.CRITICAL, line_num, key,
                    f"Unbalanced HTML tag <{tag}> in translation (net balance: {balance})"
                ))
        
        return issues
    
    def validate_directory(self, translations_dir: Path) -> Dict[str, List[ValidationIssue]]:
        """
        Validate all CSV files in the translations directory (excluding Abandoned folder).
        
        Args:
            translations_dir: Path to the Translations directory
            
        Returns:
            Dictionary mapping file paths to lists of issues
        """
        if not translations_dir.exists():
            print(f"ERROR: Directory not found: {translations_dir}")
            sys.exit(1)
        
        # Find all CSV files, excluding Abandoned folder
        csv_files = []
        for csv_file in translations_dir.glob("*.csv"):
            csv_files.append(csv_file)
        
        if not csv_files:
            print(f"WARNING: No CSV files found in {translations_dir}")
            return {}
        
        # Validate each file
        for csv_file in sorted(csv_files):
            print(f"Validating: {csv_file.name}...", end=" ")
            issues = self.validate_file(csv_file)
            self.issues[str(csv_file)] = issues
            self.stats['files_validated'] += 1
            
            # Count issues by severity
            for issue in issues:
                if issue.severity == ValidationIssue.CRITICAL:
                    self.stats['critical_errors'] += 1
                elif issue.severity == ValidationIssue.WARNING:
                    self.stats['warnings'] += 1
                else:
                    self.stats['infos'] += 1
            
            if issues:
                print(f"⚠️  {len(issues)} issue(s)")
            else:
                print("✓ OK")
        
        return self.issues
    
    def print_report(self, show_details: bool = True):
        """Print a detailed validation report."""
        print("\n" + "=" * 80)
        print("VALIDATION REPORT")
        print("=" * 80)
        
        if show_details:
            for file_path, issues in self.issues.items():
                if not issues:
                    continue
                
                file_name = Path(file_path).name
                print(f"\n{file_name}:")
                print("-" * len(file_name))
                
                # Sort issues by severity and line number
                sorted_issues = sorted(issues, key=lambda x: (
                    0 if x.severity == ValidationIssue.CRITICAL else 
                    1 if x.severity == ValidationIssue.WARNING else 2,
                    x.line_num
                ))
                
                for issue in sorted_issues:
                    print(issue)
        
        # Print summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Files validated:   {self.stats['files_validated']}")
        print(f"Total keys:        {self.stats['total_keys']}")
        print(f"Critical errors:   {self.stats['critical_errors']}")
        print(f"Warnings:          {self.stats['warnings']}")
        print(f"Info messages:     {self.stats['infos']}")
        print("=" * 80)
        
        if self.stats['critical_errors'] == 0 and self.stats['warnings'] == 0:
            print("\n✓ All validations passed!")
        elif self.stats['critical_errors'] == 0:
            print(f"\n⚠️  Validation completed with {self.stats['warnings']} warning(s)")
        else:
            print(f"\n❌ Validation failed with {self.stats['critical_errors']} critical error(s)")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Validate Stardeus translation CSV files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed information for each file'
    )
    parser.add_argument(
        '--strict', '-s',
        action='store_true',
        help='Treat warnings as errors (exit code 1)'
    )
    parser.add_argument(
        '--dir', '-d',
        type=str,
        default='Translations',
        help='Path to translations directory (default: Translations)'
    )
    
    args = parser.parse_args()
    
    # Get the translations directory
    script_dir = Path(__file__).parent
    translations_dir = script_dir / args.dir
    
    print("Stardeus Translation Validator")
    print("=" * 80)
    print(f"Validating files in: {translations_dir}")
    print(f"Verbose mode: {'ON' if args.verbose else 'OFF'}")
    print(f"Strict mode: {'ON' if args.strict else 'OFF'}")
    print("=" * 80 + "\n")
    
    # Create validator and run
    validator = TranslationValidator(verbose=args.verbose)
    validator.validate_directory(translations_dir)
    
    # Print report
    validator.print_report(show_details=True)
    
    # Determine exit code
    has_errors = validator.stats['critical_errors'] > 0
    has_warnings = validator.stats['warnings'] > 0
    
    if has_errors:
        sys.exit(1)
    elif args.strict and has_warnings:
        print("\n⚠️  Exiting with error code due to --strict mode")
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

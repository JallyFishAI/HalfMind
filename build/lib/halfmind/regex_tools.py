import re
import json
from collections import Counter


class RegexTools:
    """Tools for pattern matching, text extraction, and regex operations"""
    
    COMMON_PATTERNS = {
        'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'url': r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)',
        'ipv4': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        'ipv6': r'(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}',
        'phone_us': r'(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
        'phone_international': r'\+?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,9}',
        'date_us': r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
        'date_iso': r'\d{4}-\d{2}-\d{2}',
        'time_24h': r'(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d)?',
        'time_12h': r'(?:1[0-2]|0?[1-9]):[0-5]\d\s?(?:AM|PM|am|pm)',
        'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'zip_code_us': r'\b\d{5}(?:-\d{4})?\b',
        'hashtag': r'#[a-zA-Z0-9_]+',
        'mention': r'@[a-zA-Z0-9_]+',
        'html_tag': r'<([a-zA-Z][a-zA-Z0-9]*)\b[^>]*>.*?</\1>',
        'hex_color': r'#(?:[0-9a-fA-F]{3}){1,2}\b',
        'mac_address': r'(?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}',
        'uuid': r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
        'integer': r'-?\b\d+\b',
        'float': r'-?\b\d+\.?\d*\b',
        'word': r'\b[a-zA-Z]+\b',
        'whitespace': r'\s+'
    }
    
    def __init__(self):
        self.compiled_patterns = {}
    
    def compile_pattern(self, pattern, flags=0):
        """Compiles and caches a regex pattern"""
        key = (pattern, flags)
        if key not in self.compiled_patterns:
            self.compiled_patterns[key] = re.compile(pattern, flags)
        return self.compiled_patterns[key]
    
    def match(self, text, pattern, flags=0):
        """Checks if pattern matches at the beginning of text"""
        compiled = self.compile_pattern(pattern, flags)
        match = compiled.match(text)
        if match:
            return {
                'matched': True,
                'groups': match.groups(),
                'groupdict': match.groupdict(),
                'span': match.span(),
                'matched_text': match.group()
            }
        return {'matched': False}
    
    def search(self, text, pattern, flags=0):
        """Searches for pattern anywhere in text"""
        compiled = self.compile_pattern(pattern, flags)
        match = compiled.search(text)
        if match:
            return {
                'matched': True,
                'groups': match.groups(),
                'groupdict': match.groupdict(),
                'span': match.span(),
                'matched_text': match.group()
            }
        return {'matched': False}
    
    def find_all(self, text, pattern, flags=0):
        """Finds all occurrences of pattern in text"""
        compiled = self.compile_pattern(pattern, flags)
        matches = []
        for match in compiled.finditer(text):
            matches.append({
                'matched_text': match.group(),
                'groups': match.groups(),
                'groupdict': match.groupdict(),
                'span': match.span()
            })
        return matches
    
    def find_first(self, text, pattern, flags=0):
        """Finds first occurrence of pattern in text"""
        compiled = self.compile_pattern(pattern, flags)
        match = compiled.search(text)
        if match:
            return match.group()
        return None
    
    def split(self, text, pattern, flags=0):
        """Splits text by pattern"""
        compiled = self.compile_pattern(pattern, flags)
        return compiled.split(text)
    
    def replace(self, text, pattern, replacement, flags=0, count=0):
        """Replaces pattern matches with replacement"""
        compiled = self.compile_pattern(pattern, flags)
        return compiled.sub(replacement, text, count=count)
    
    def replace_callback(self, text, pattern, callback, flags=0):
        """Replaces pattern matches using a callback function"""
        compiled = self.compile_pattern(pattern, flags)
        return compiled.sub(callback, text)
    
    def validate(self, text, pattern, flags=0):
        """Validates if entire text matches pattern"""
        compiled = self.compile_pattern(f'^{pattern}$', flags)
        return bool(compiled.match(text))
    
    def extract_with_pattern(self, text, pattern_name):
        """Extracts data using a predefined common pattern"""
        if pattern_name not in self.COMMON_PATTERNS:
            raise ValueError(f"Unknown pattern: {pattern_name}")
        pattern = self.COMMON_PATTERNS[pattern_name]
        return self.find_all(text, pattern)
    
    def extract_emails(self, text):
        """Extracts all email addresses from text"""
        return self.extract_with_pattern(text, 'email')
    
    def extract_urls(self, text):
        """Extracts all URLs from text"""
        return self.extract_with_pattern(text, 'url')
    
    def extract_phones(self, text):
        """Extracts all phone numbers from text"""
        us_phones = self.find_all(text, self.COMMON_PATTERNS['phone_us'])
        intl_phones = self.find_all(text, self.COMMON_PATTERNS['phone_international'])
        return {'us': us_phones, 'international': intl_phones}
    
    def extract_dates(self, text):
        """Extracts all dates from text"""
        us_dates = self.find_all(text, self.COMMON_PATTERNS['date_us'])
        iso_dates = self.find_all(text, self.COMMON_PATTERNS['date_iso'])
        return {'us_format': us_dates, 'iso_format': iso_dates}
    
    def extract_ip_addresses(self, text):
        """Extracts IP addresses from text"""
        ipv4 = self.find_all(text, self.COMMON_PATTERNS['ipv4'])
        ipv6 = self.find_all(text, self.COMMON_PATTERNS['ipv6'])
        return {'ipv4': ipv4, 'ipv6': ipv6}
    
    def extract_hashtags(self, text):
        """Extracts hashtags from text"""
        return self.extract_with_pattern(text, 'hashtag')
    
    def extract_mentions(self, text):
        """Extracts mentions from text"""
        return self.extract_with_pattern(text, 'mention')
    
    def extract_numbers(self, text):
        """Extracts all numbers from text"""
        integers = self.find_all(text, self.COMMON_PATTERNS['integer'])
        floats = self.find_all(text, self.COMMON_PATTERNS['float'])
        return {'integers': integers, 'floats': floats}
    
    def extract_hex_colors(self, text):
        """Extracts hex color codes from text"""
        return self.extract_with_pattern(text, 'hex_color')
    
    def count_matches(self, text, pattern, flags=0):
        """Counts occurrences of pattern in text"""
        matches = self.find_all(text, pattern, flags)
        return len(matches)
    
    def count_by_pattern(self, text, pattern_name):
        """Counts matches for a predefined pattern"""
        if pattern_name not in self.COMMON_PATTERNS:
            raise ValueError(f"Unknown pattern: {pattern_name}")
        return self.count_matches(text, self.COMMON_PATTERNS[pattern_name])
    
    def get_unique_matches(self, text, pattern, flags=0):
        """Returns unique matches from text"""
        matches = self.find_all(text, pattern, flags)
        unique = list(set(m['matched_text'] for m in matches))
        return sorted(unique)
    
    def match_frequency(self, text, pattern, flags=0):
        """Returns frequency of each match"""
        matches = self.find_all(text, pattern, flags)
        counter = Counter(m['matched_text'] for m in matches)
        return dict(counter.most_common())
    
    def test_patterns(self, text, patterns):
        """Tests multiple patterns against text"""
        results = {}
        for name, pattern in patterns.items():
            matches = self.find_all(text, pattern)
            results[name] = {
                'count': len(matches),
                'matches': [m['matched_text'] for m in matches]
            }
        return results
    
    def create_capture_groups(self, pattern, group_names):
        """Adds named capture groups to a pattern"""
        for name in group_names:
            pattern = pattern.replace(f'(?P<{name}>', f'(?P<{name}>', 1)
        return pattern
    
    def escape_special_chars(self, text):
        """Escapes special regex characters"""
        return re.escape(text)
    
    def unescape_pattern(self, pattern):
        """Removes escaping from a pattern"""
        return pattern.replace('\\', '')
    
    def pattern_to_wildcard(self, pattern):
        """Converts regex pattern to wildcard format"""
        wildcard = pattern
        wildcard = wildcard.replace('.*', '*')
        wildcard = wildcard.replace('.+', '*')
        wildcard = wildcard.replace('.', '?')
        wildcard = re.sub(r'\[[^\]]+\]', '?', wildcard)
        wildcard = re.sub(r'[(){}|]', '', wildcard)
        return wildcard
    
    def wildcard_to_pattern(self, wildcard):
        """Converts wildcard format to regex pattern"""
        pattern = re.escape(wildcard)
        pattern = pattern.replace(r'\*', '.*')
        pattern = pattern.replace(r'\?', '.')
        return f'^{pattern}$'
    
    def fuzzy_match(self, text, pattern, threshold=0.8):
        """Performs fuzzy matching with similarity score"""
        from difflib import SequenceMatcher
        words = text.split()
        results = []
        for word in words:
            similarity = SequenceMatcher(None, word, pattern).ratio()
            if similarity >= threshold:
                results.append({
                    'word': word,
                    'similarity': round(similarity, 4)
                })
        return sorted(results, key=lambda x: x['similarity'], reverse=True)
    
    def find_between(self, text, start_pattern, end_pattern):
        """Finds text between two patterns"""
        pattern = f'{start_pattern}(.*?){end_pattern}'
        matches = self.find_all(text, pattern, re.DOTALL)
        return [m['groups'][0] if m['groups'] else '' for m in matches]
    
    def find_balanced(self, text, open_char, close_char):
        """Finds balanced pairs of characters"""
        results = []
        stack = []
        for i, char in enumerate(text):
            if char == open_char:
                stack.append(i)
            elif char == close_char and stack:
                start = stack.pop()
                results.append(text[start:i+1])
        return results
    
    def tokenize(self, text, pattern=None):
        """Tokenizes text using a pattern"""
        if pattern is None:
            pattern = r'\b\w+\b'
        matches = self.find_all(text, pattern)
        return [m['matched_text'] for m in matches]
    
    def is_valid_pattern(self, pattern):
        """Validates if a regex pattern is valid"""
        try:
            re.compile(pattern)
            return {'valid': True}
        except re.error as e:
            return {'valid': False, 'error': str(e)}
    
    def get_pattern_info(self, pattern):
        """Returns information about a regex pattern"""
        try:
            compiled = re.compile(pattern)
            return {
                'valid': True,
                'groups': compiled.groups,
                'groupindex': compiled.groupindex,
                'flags': compiled.flags,
                'pattern': compiled.pattern
            }
        except re.error as e:
            return {'valid': False, 'error': str(e)}
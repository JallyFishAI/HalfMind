import os
import json
import csv
import hashlib
from pathlib import Path
from collections import Counter, defaultdict


class DataTools:
    """Tools for data processing, CSV, JSON, and statistical operations"""
    
    MAX_FILE_SIZE = 100 * 1024 * 1024
    
    def __init__(self):
        self.data_cache = {}
    
    def _validate_path(self, path, must_exist=True):
        """Validates file path for security"""
        resolved = Path(path).resolve()
        if must_exist:
            if not resolved.exists():
                raise FileNotFoundError(f"File not found: {path}")
            if resolved.stat().st_size > self.MAX_FILE_SIZE:
                raise ValueError("File size exceeds maximum allowed")
        return str(resolved)
    
    def read_csv(self, file_path, delimiter=',', encoding='utf-8'):
        """Reads a CSV file and returns data as list of dictionaries"""
        validated_path = self._validate_path(file_path)
        data = []
        with open(validated_path, 'r', encoding=encoding) as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                data.append(dict(row))
        return data
    
    def write_csv(self, file_path, data, fieldnames=None, delimiter=',', encoding='utf-8'):
        """Writes data to a CSV file"""
        validated_path = self._validate_path(file_path, must_exist=False)
        if not fieldnames and data:
            fieldnames = list(data[0].keys())
        with open(validated_path, 'w', encoding=encoding, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
            writer.writeheader()
            writer.writerows(data)
        return True
    
    def read_json(self, file_path, encoding='utf-8'):
        """Reads a JSON file"""
        validated_path = self._validate_path(file_path)
        with open(validated_path, 'r', encoding=encoding) as f:
            return json.load(f)
    
    def write_json(self, file_path, data, indent=4, encoding='utf-8'):
        """Writes data to a JSON file"""
        validated_path = self._validate_path(file_path, must_exist=False)
        with open(validated_path, 'w', encoding=encoding) as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    
    def json_to_csv(self, json_path, csv_path, encoding='utf-8'):
        """Converts a JSON file to CSV"""
        data = self.read_json(json_path, encoding)
        if isinstance(data, list) and data:
            self.write_csv(csv_path, data, encoding=encoding)
            return True
        raise ValueError("JSON must contain a list of objects")
    
    def csv_to_json(self, csv_path, json_path, delimiter=',', encoding='utf-8'):
        """Converts a CSV file to JSON"""
        data = self.read_csv(csv_path, delimiter, encoding)
        self.write_json(json_path, data, encoding=encoding)
        return True
    
    def filter_data(self, data, conditions):
        """Filters data based on conditions dictionary"""
        filtered = []
        for row in data:
            match = True
            for key, value in conditions.items():
                if key not in row or row[key] != value:
                    match = False
                    break
            if match:
                filtered.append(row)
        return filtered
    
    def sort_data(self, data, key, reverse=False):
        """Sorts data by a specific key"""
        return sorted(data, key=lambda x: x.get(key, ''), reverse=reverse)
    
    def group_by(self, data, key):
        """Groups data by a specific key"""
        groups = defaultdict(list)
        for row in data:
            group_key = row.get(key, 'unknown')
            groups[group_key].append(row)
        return dict(groups)
    
    def aggregate(self, data, group_key, agg_key, operation='sum'):
        """Aggregates data by group"""
        groups = self.group_by(data, group_key)
        results = {}
        for group, rows in groups.items():
            values = [float(row.get(agg_key, 0)) for row in rows]
            if operation == 'sum':
                results[group] = sum(values)
            elif operation == 'avg':
                results[group] = sum(values) / len(values) if values else 0
            elif operation == 'min':
                results[group] = min(values) if values else 0
            elif operation == 'max':
                results[group] = max(values) if values else 0
            elif operation == 'count':
                results[group] = len(values)
        return results
    
    def pivot_table(self, data, index, columns, values, aggfunc='sum'):
        """Creates a pivot table from data"""
        pivot = defaultdict(lambda: defaultdict(list))
        for row in data:
            row_key = row.get(index, 'unknown')
            col_key = row.get(columns, 'unknown')
            value = float(row.get(values, 0))
            pivot[row_key][col_key].append(value)
        result = {}
        for row_key, cols in pivot.items():
            result[row_key] = {}
            for col_key, vals in cols.items():
                if aggfunc == 'sum':
                    result[row_key][col_key] = sum(vals)
                elif aggfunc == 'avg':
                    result[row_key][col_key] = sum(vals) / len(vals) if vals else 0
                elif aggfunc == 'count':
                    result[row_key][col_key] = len(vals)
        return result
    
    def calculate_statistics(self, data, key):
        """Calculates statistical measures for a numeric field"""
        values = [float(row.get(key, 0)) for row in data if key in row]
        if not values:
            return None
        n = len(values)
        sorted_values = sorted(values)
        return {
            'count': n,
            'sum': sum(values),
            'mean': sum(values) / n,
            'median': sorted_values[n // 2] if n % 2 == 1 else (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2,
            'min': min(values),
            'max': max(values),
            'range': max(values) - min(values),
            'variance': sum((x - sum(values) / n) ** 2 for x in values) / n,
            'std_dev': (sum((x - sum(values) / n) ** 2 for x in values) / n) ** 0.5
        }
    
    def frequency_distribution(self, data, key):
        """Calculates frequency distribution for a field"""
        counter = Counter(row.get(key, 'unknown') for row in data)
        total = sum(counter.values())
        return {
            'counts': dict(counter),
            'percentages': {k: round(v / total * 100, 2) for k, v in counter.items()},
            'total': total
        }
    
    def find_duplicates(self, data, keys=None):
        """Finds duplicate records based on specified keys"""
        if keys is None:
            keys = list(data[0].keys()) if data else []
        seen = set()
        duplicates = []
        for row in data:
            key_values = tuple(row.get(k) for k in keys)
            if key_values in seen:
                duplicates.append(row)
            else:
                seen.add(key_values)
        return duplicates
    
    def remove_duplicates(self, data, keys=None):
        """Removes duplicate records"""
        if keys is None:
            keys = list(data[0].keys()) if data else []
        seen = set()
        unique = []
        for row in data:
            key_values = tuple(row.get(k) for k in keys)
            if key_values not in seen:
                seen.add(key_values)
                unique.append(row)
        return unique
    
    def merge_datasets(self, data1, data2, key, how='inner'):
        """Merges two datasets on a common key"""
        if how == 'inner':
            keys2 = {row[key]: row for row in data2}
            return [{**row, **keys2[row[key]]} for row in data1 if row[key] in keys2]
        elif how == 'left':
            keys2 = {row[key]: row for row in data2}
            return [{**row, **keys2.get(row[key], {})} for row in data1]
        elif how == 'right':
            keys1 = {row[key]: row for row in data1}
            return [{**row, **keys1.get(row[key], {})} for row in data2]
        elif how == 'outer':
            keys1 = {row[key]: row for row in data1}
            keys2 = {row[key]: row for row in data2}
            all_keys = set(keys1.keys()) | set(keys2.keys())
            return [{**keys1.get(k, {}), **keys2.get(k, {})} for k in all_keys]
    
    def transform_data(self, data, transformations):
        """Applies transformations to data"""
        result = []
        for row in data:
            new_row = {}
            for key, value in row.items():
                if key in transformations:
                    func = transformations[key]
                    new_row[key] = func(value)
                else:
                    new_row[key] = value
            result.append(new_row)
        return result
    
    def sample_data(self, data, n, random_seed=None):
        """Returns a random sample of data"""
        import random
        if random_seed is not None:
            random.seed(random_seed)
        return random.sample(data, min(n, len(data)))
    
    def split_data(self, data, ratio=0.8, random_seed=None):
        """Splits data into training and testing sets"""
        import random
        if random_seed is not None:
            random.seed(random_seed)
        shuffled = data.copy()
        random.shuffle(shuffled)
        split_idx = int(len(shuffled) * ratio)
        return {
            'train': shuffled[:split_idx],
            'test': shuffled[split_idx:]
        }
    
    def normalize_values(self, data, key):
        """Normalizes numeric values to 0-1 range"""
        values = [float(row.get(key, 0)) for row in data]
        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val
        if range_val == 0:
            return [0.5] * len(values)
        return [(v - min_val) / range_val for v in values]
    
    def encode_categorical(self, data, key):
        """Encodes categorical values as integers"""
        categories = list(set(row.get(key, '') for row in data))
        encoding = {cat: idx for idx, cat in enumerate(categories)}
        return {
            'encoding': encoding,
            'decoding': {idx: cat for cat, idx in encoding.items()},
            'encoded': [{**row, key: encoding.get(row.get(key, ''), -1)} for row in data]
        }
    
    def detect_outliers(self, data, key, threshold=2):
        """Detects outliers using z-score method"""
        values = [float(row.get(key, 0)) for row in data]
        mean = sum(values) / len(values)
        std_dev = (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5
        if std_dev == 0:
            return []
        outliers = []
        for i, row in enumerate(data):
            z_score = abs(values[i] - mean) / std_dev
            if z_score > threshold:
                outliers.append({'index': i, 'row': row, 'z_score': z_score})
        return outliers
    
    def interpolate_missing(self, data, key, method='linear'):
        """Interpolates missing values in a numeric field"""
        values = [float(row.get(key)) if row.get(key) else None for row in data]
        for i in range(len(values)):
            if values[i] is None:
                prev_idx = next((j for j in range(i - 1, -1, -1) if values[j] is not None), None)
                next_idx = next((j for j in range(i + 1, len(values)) if values[j] is not None), None)
                if prev_idx is not None and next_idx is not None:
                    if method == 'linear':
                        ratio = (i - prev_idx) / (next_idx - prev_idx)
                        values[i] = values[prev_idx] + ratio * (values[next_idx] - values[prev_idx])
                    elif method == 'nearest':
                        values[i] = values[prev_idx] if i - prev_idx <= next_idx - i else values[next_idx]
                elif prev_idx is not None:
                    values[i] = values[prev_idx]
                elif next_idx is not None:
                    values[i] = values[next_idx]
        for i, row in enumerate(data):
            if values[i] is not None:
                row[key] = values[i]
        return data
    
    def export_summary(self, data, output_path):
        """Exports a summary report of the dataset"""
        summary = {
            'total_records': len(data),
            'columns': list(data[0].keys()) if data else [],
            'column_stats': {}
        }
        if data:
            for col in summary['columns']:
                values = [row.get(col) for row in data]
                unique_values = set(str(v) for v in values if v is not None)
                summary['column_stats'][col] = {
                    'unique_count': len(unique_values),
                    'null_count': sum(1 for v in values if v is None),
                    'sample_values': list(unique_values)[:5]
                }
                numeric_values = [float(v) for v in values if v is not None and str(v).replace('.', '').replace('-', '').isdigit()]
                if numeric_values:
                    summary['column_stats'][col]['numeric'] = {
                        'min': min(numeric_values),
                        'max': max(numeric_values),
                        'mean': sum(numeric_values) / len(numeric_values)
                    }
        self.write_json(output_path, summary)
        return summary
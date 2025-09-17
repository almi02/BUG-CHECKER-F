import json
import csv
import os
from datetime import datetime
from typing import List, Dict, Optional

class DataExporter:
    """
    Handle data export in various formats suitable for LLM training
    """
    
    def __init__(self, output_dir: str = "scraped_data"):
        self.output_dir = output_dir
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def export_to_json(self, data: List[Dict], filename: Optional[str] = None) -> str:
        """Export scraped data to JSON format"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"scraped_data_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Format data for LLM training
        formatted_data = {
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "total_records": len(data),
                "format": "json"
            },
            "data": data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(formatted_data, f, indent=2, ensure_ascii=False)
        
        print(f"Data exported to: {filepath}")
        return filepath
    
    def export_to_csv(self, data: List[Dict], filename: Optional[str] = None) -> str:
        """Export scraped data to CSV format"""
        if not data:
            print("No data to export")
            return ""
            
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"scraped_data_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Get all unique keys from all dictionaries
        fieldnames = set()
        for item in data:
            fieldnames.update(item.keys())
        fieldnames = list(fieldnames)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"Data exported to: {filepath}")
        return filepath
    
    def export_for_llm_training(self, data: List[Dict], format_type: str = "jsonl") -> str:
        """Export data in format optimized for LLM training"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        filepath = ""
        
        if format_type == "jsonl":
            filename = f"llm_training_data_{timestamp}.jsonl"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                for item in data:
                    # Format each record as a single JSON line
                    training_record = {
                        "input": f"Business information from {item.get('search_query', 'web scraping')}",
                        "output": json.dumps(item, ensure_ascii=False),
                        "source": "web_scraper",
                        "timestamp": item.get('scraped_at', datetime.now().isoformat())
                    }
                    f.write(json.dumps(training_record, ensure_ascii=False) + '\n')
        
        elif format_type == "text":
            filename = f"llm_training_data_{timestamp}.txt"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                for item in data:
                    # Format as readable text
                    text_content = f"Business: {item.get('name', 'Unknown')}\n"
                    text_content += f"Rating: {item.get('rating', 'No rating')}\n"
                    text_content += f"Address: {item.get('address', 'No address')}\n"
                    text_content += f"Query: {item.get('search_query', 'Unknown')}\n"
                    text_content += "---\n"
                    f.write(text_content)
        
        print(f"LLM training data exported to: {filepath}")
        return filepath
    
    def list_exported_files(self) -> List[str]:
        """List all exported files"""
        files = []
        if os.path.exists(self.output_dir):
            for filename in os.listdir(self.output_dir):
                if filename.endswith(('.json', '.csv', '.jsonl', '.txt')):
                    files.append(os.path.join(self.output_dir, filename))
        return files
from flask import Flask, render_template, request, jsonify, send_file
import json
import os
from scraper_engine import AntiDetectionScraper, GoogleMapsScraper
from data_exporter import DataExporter
from bug_checker import WebBugChecker

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-key-change-in-production')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for development

# Initialize components
scraper = AntiDetectionScraper()
maps_scraper = GoogleMapsScraper()
exporter = DataExporter()
bug_checker = WebBugChecker()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape_data():
    try:
        data = request.get_json()
        scrape_type = data.get('type', 'url')
        
        if scrape_type == 'url':
            url = data.get('url', '')
            use_trafilatura = data.get('use_trafilatura', False)
            
            if not url:
                return jsonify({'error': 'URL is required'}), 400
            
            result = scraper.scrape_url(url, use_trafilatura)
            return jsonify({'status': 'success', 'data': result})
            
        elif scrape_type == 'google_maps':
            query = data.get('query', '')
            location = data.get('location', '')
            
            if not query:
                return jsonify({'error': 'Search query is required'}), 400
            
            businesses = maps_scraper.extract_business_info(query, location)
            return jsonify({'status': 'success', 'data': businesses, 'count': len(businesses)})
            
        else:
            return jsonify({'error': 'Invalid scrape type'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/check-bugs', methods=['POST'])
def check_bugs():
    try:
        data = request.get_json()
        url = data.get('url', '')
        check_types = data.get('check_types', {})
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Ensure at least one check type is selected
        if not any(check_types.values()):
            return jsonify({'error': 'At least one check type must be selected'}), 400
        
        # Run the bug analysis
        report = bug_checker.check_website(url, check_types)
        
        return jsonify({'status': 'success', 'data': report})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/export-report', methods=['POST'])
def export_report():
    try:
        data = request.get_json()
        report = data.get('report', {})
        export_format = data.get('format', 'json')
        
        if not report:
            return jsonify({'error': 'No report data to export'}), 400
        
        # Create a bug reports directory
        os.makedirs('bug_reports', exist_ok=True)
        
        # Generate filename with timestamp
        import time
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        if export_format == 'json':
            filename = f'bug_report_{timestamp}.json'
            filepath = os.path.join('bug_reports', filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        elif export_format == 'pdf':
            # For now, we'll export as JSON since PDF generation requires additional dependencies
            filename = f'bug_report_{timestamp}.json'
            filepath = os.path.join('bug_reports', filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        else:
            return jsonify({'error': 'Invalid export format'}), 400
        
        return jsonify({'status': 'success', 'filepath': filepath})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/export', methods=['POST'])
def export_data():
    try:
        data = request.get_json()
        export_data = data.get('data', [])
        export_format = data.get('format', 'json')
        
        if not export_data:
            return jsonify({'error': 'No data to export'}), 400
        
        if export_format == 'json':
            filepath = exporter.export_to_json(export_data)
        elif export_format == 'csv':
            filepath = exporter.export_to_csv(export_data)
        elif export_format == 'llm_jsonl':
            filepath = exporter.export_for_llm_training(export_data, 'jsonl')
        elif export_format == 'llm_text':
            filepath = exporter.export_for_llm_training(export_data, 'text')
        else:
            return jsonify({'error': 'Invalid export format'}), 400
        
        return jsonify({'status': 'success', 'filepath': filepath})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/files')
def list_files():
    try:
        files = exporter.list_exported_files()
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Web App Bug Checker is running'})

if __name__ == '__main__':
    # Ensure scraped_data directory exists
    os.makedirs('scraped_data', exist_ok=True)
    
    # Run with all hosts allowed for Replit
    app.run(host='0.0.0.0', port=5000, debug=True)
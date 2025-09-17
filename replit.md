# Web App Bug Checker

## Overview

This is a Flask-based web application bug detection tool designed to analyze websites for various issues including HTML validation errors, broken links, performance problems, accessibility issues, SEO problems, and JavaScript errors. The tool provides a comprehensive web interface for performing different types of bug analysis with detailed reporting and export capabilities. The application is built with a modular bug checking engine that provides structured analysis results categorized by issue type and severity.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Web Interface**: Simple HTML/Bootstrap-based single-page application served via Flask templates
- **User Interaction**: Form-based input for URLs and search queries with real-time feedback
- **AJAX Communication**: Asynchronous requests to backend API endpoints for non-blocking user experience

### Backend Architecture
- **Framework**: Flask web framework with modular component design
- **Core Components**:
  - `AntiDetectionScraper`: Handles general website scraping with bot evasion
  - `GoogleMapsScraper`: Specialized scraper for Google Maps business data
  - `DataExporter`: Manages data export in multiple formats (JSON, CSV)
- **API Design**: RESTful endpoints with JSON request/response format
- **Error Handling**: Comprehensive exception handling with structured error responses

### Scraping Engine Design
- **Anti-Detection Features**: 
  - Random user agent rotation using fake-useragent library
  - Random header generation to mimic real browser requests
  - Rate limiting and request delays to avoid detection
  - Proxy rotation capability (infrastructure prepared)
  - Session management for persistent connections
- **Content Extraction**: 
  - BeautifulSoup for HTML parsing
  - Trafilatura integration for clean text extraction
  - Dual extraction modes (HTML + clean text)

### Data Processing Pipeline
- **Extraction**: Multi-threaded scraping capability with retry mechanisms
- **Processing**: Content cleaning and structuring for downstream use
- **Export**: Multiple format support optimized for LLM training data
- **Storage**: File-based export system with timestamped outputs

## External Dependencies

### Python Libraries
- **Flask**: Web framework for API and template serving
- **requests**: HTTP client for web scraping operations
- **BeautifulSoup4**: HTML parsing and content extraction
- **trafilatura**: Clean text extraction from web pages
- **fake-useragent**: User agent rotation for anti-detection
- **json**: Data serialization and export
- **csv**: Structured data export functionality

### Frontend Dependencies
- **Bootstrap 5.1.3**: CSS framework for responsive UI design
- **JavaScript (Vanilla)**: Client-side interactivity and AJAX requests

### Infrastructure Requirements
- **File System**: Local storage for scraped data exports
- **Network Access**: HTTP/HTTPS requests to target websites
- **Session Management**: Flask session handling with configurable secret key

### Optional Integrations
- **Proxy Services**: Infrastructure prepared for proxy rotation
- **Google Maps API**: Potential integration for enhanced location data
- **Database Storage**: Currently file-based but architected for database expansion
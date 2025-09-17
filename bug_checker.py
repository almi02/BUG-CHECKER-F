import requests
import time
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import json

class WebBugChecker:
    """
    Comprehensive web application bug checker for finding various issues
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 30
        
    def check_website(self, url: str, check_types: Dict[str, bool]) -> Dict:
        """
        Main method to check a website for various bugs and issues
        """
        start_time = time.time()
        report = {
            'url': url,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {'total': 0, 'critical': 0, 'warnings': 0, 'info': 0},
            'categories': {
                'html': [],
                'links': [],
                'performance': [],
                'accessibility': [],
                'seo': [],
                'javascript': []
            }
        }
        
        try:
            # Fetch the webpage
            response = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Run selected checks
            if check_types.get('html', False):
                html_issues = self.check_html_validation(soup, response)
                report['categories']['html'] = html_issues
                
            if check_types.get('links', False):
                link_issues = self.check_broken_links(soup, url)
                report['categories']['links'] = link_issues
                
            if check_types.get('performance', False):
                perf_issues = self.check_performance(response, soup, time.time() - start_time)
                report['categories']['performance'] = perf_issues
                
            if check_types.get('accessibility', False):
                a11y_issues = self.check_accessibility(soup)
                report['categories']['accessibility'] = a11y_issues
                
            if check_types.get('seo', False):
                seo_issues = self.check_seo_metadata(soup, response)
                report['categories']['seo'] = seo_issues
                
            if check_types.get('javascript', False):
                js_issues = self.check_javascript_issues(soup, response.text)
                report['categories']['javascript'] = js_issues
            
            # Calculate summary
            self._calculate_summary(report)
            
        except requests.exceptions.RequestException as e:
            report['categories']['performance'].append({
                'title': 'Connection Error',
                'description': f'Unable to connect to website: {str(e)}',
                'severity': 'critical',
                'location': url,
                'suggestion': 'Check if the URL is correct and the website is accessible'
            })
            
        except Exception as e:
            report['categories']['html'].append({
                'title': 'Analysis Error',
                'description': f'Error during analysis: {str(e)}',
                'severity': 'warning',
                'location': 'General',
                'suggestion': 'The website might have unusual content that caused analysis issues'
            })
            
        self._calculate_summary(report)
        return report
    
    def check_html_validation(self, soup: BeautifulSoup, response) -> List[Dict]:
        """Check for HTML validation issues"""
        issues = []
        
        # Check for missing DOCTYPE
        if not response.text.strip().startswith('<!DOCTYPE'):
            issues.append({
                'title': 'Missing DOCTYPE Declaration',
                'description': 'The HTML document is missing a DOCTYPE declaration',
                'severity': 'warning',
                'location': 'Document start',
                'suggestion': 'Add <!DOCTYPE html> at the beginning of your HTML document'
            })
        
        # Check for missing title
        title = soup.find('title')
        if not title or not title.get_text().strip():
            issues.append({
                'title': 'Missing or Empty Title',
                'description': 'The page is missing a title tag or it\'s empty',
                'severity': 'critical',
                'location': '<head> section',
                'suggestion': 'Add a descriptive <title> tag in the <head> section'
            })
        
        # Check for missing meta charset
        charset = soup.find('meta', attrs={'charset': True})
        if not charset:
            issues.append({
                'title': 'Missing Character Set Declaration',
                'description': 'No charset meta tag found',
                'severity': 'warning',
                'location': '<head> section',
                'suggestion': 'Add <meta charset="UTF-8"> in the <head> section'
            })
        
        # Check for missing viewport meta tag (important for mobile)
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if not viewport:
            issues.append({
                'title': 'Missing Viewport Meta Tag',
                'description': 'No viewport meta tag found for mobile responsiveness',
                'severity': 'warning',
                'location': '<head> section',
                'suggestion': 'Add <meta name="viewport" content="width=device-width, initial-scale=1.0">'
            })
        
        # Check for duplicate IDs
        ids = []
        for element in soup.find_all(attrs={'id': True}):
            if hasattr(element, 'get'):
                element_id = element.get('id')
                if element_id and element_id in ids:
                    issues.append({
                        'title': 'Duplicate ID Attribute',
                        'description': f'ID "{element_id}" is used more than once',
                        'severity': 'critical',
                        'location': f'ID: {element_id}',
                        'suggestion': 'Ensure all ID attributes are unique on the page'
                    })
                elif element_id:
                    ids.append(element_id)
        
        return issues
    
    def check_broken_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Check for broken links"""
        issues = []
        checked_urls = set()
        
        # Find all links
        links = soup.find_all('a', href=True)
        
        for link in links[:10]:  # Limit to first 10 links to avoid too many requests
            if not hasattr(link, 'get'):
                continue
            href = link.get('href')
            if not href or not isinstance(href, str):
                continue
            if href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
                continue
                
            # Convert relative URLs to absolute
            full_url = urljoin(base_url, href)
            
            if full_url in checked_urls:
                continue
            checked_urls.add(full_url)
            
            try:
                response = self.session.head(full_url, timeout=10, allow_redirects=True)
                if response.status_code >= 400:
                    issues.append({
                        'title': f'Broken Link (HTTP {response.status_code})',
                        'description': f'Link returns error status code: {response.status_code}',
                        'severity': 'critical' if response.status_code >= 500 else 'warning',
                        'location': f'Link: {href}',
                        'suggestion': 'Check if the linked resource exists and is accessible'
                    })
            except requests.exceptions.RequestException:
                issues.append({
                    'title': 'Unreachable Link',
                    'description': f'Unable to reach the linked resource',
                    'severity': 'warning',
                    'location': f'Link: {href}',
                    'suggestion': 'Verify the link URL and ensure the target server is accessible'
                })
        
        return issues
    
    def check_performance(self, response, soup: BeautifulSoup, load_time: float) -> List[Dict]:
        """Check for performance issues"""
        issues = []
        
        # Check page load time
        if load_time > 5:
            issues.append({
                'title': 'Slow Page Load Time',
                'description': f'Page took {load_time:.2f} seconds to load',
                'severity': 'critical' if load_time > 10 else 'warning',
                'location': 'Page load',
                'suggestion': 'Optimize images, reduce HTTP requests, and consider using a CDN'
            })
        
        # Check page size
        page_size = len(response.content) / 1024  # KB
        if page_size > 500:
            issues.append({
                'title': 'Large Page Size',
                'description': f'Page size is {page_size:.1f} KB',
                'severity': 'warning' if page_size < 1000 else 'critical',
                'location': 'Page content',
                'suggestion': 'Compress images, minify CSS/JS, and remove unnecessary content'
            })
        
        # Check for unoptimized images
        images = soup.find_all('img')
        large_images = 0
        for img in images:
            src = img.get('src')
            if src and not src.startswith('data:'):
                # Check if image has alt attribute
                if not img.get('alt'):
                    issues.append({
                        'title': 'Image Missing Alt Text',
                        'description': 'Image without alt attribute found',
                        'severity': 'warning',
                        'location': f'Image: {src}',
                        'suggestion': 'Add descriptive alt text for accessibility and SEO'
                    })
        
        # Check for inline CSS/JS
        style_tags = soup.find_all('style')
        if len(style_tags) > 2:
            issues.append({
                'title': 'Excessive Inline CSS',
                'description': f'Found {len(style_tags)} inline style tags',
                'severity': 'info',
                'location': 'Page head/body',
                'suggestion': 'Move styles to external CSS files for better caching'
            })
        
        return issues
    
    def check_accessibility(self, soup: BeautifulSoup) -> List[Dict]:
        """Check for accessibility issues"""
        issues = []
        
        # Check for images without alt text
        images = soup.find_all('img')
        for img in images:
            if hasattr(img, 'get'):
                alt_attr = img.get('alt')
                if not alt_attr:
                    src = img.get('src') or 'unknown'
                    issues.append({
                        'title': 'Image Missing Alt Text',
                        'description': 'Image without alt attribute affects screen readers',
                        'severity': 'warning',
                        'location': f'Image: {src}',
                        'suggestion': 'Add descriptive alt text: <img alt="description of image">'
                    })
        
        # Check for form inputs without labels
        inputs = soup.find_all(['input', 'textarea', 'select'])
        for input_elem in inputs:
            if hasattr(input_elem, 'get'):
                input_type = input_elem.get('type') or 'text'
                if input_type not in ['hidden', 'submit', 'button']:
                    input_id = input_elem.get('id')
                    if input_id:
                        label = soup.find('label', attrs={'for': input_id})
                        if not label:
                            issues.append({
                                'title': 'Form Input Without Label',
                                'description': 'Form input missing associated label',
                                'severity': 'warning',
                                'location': f'Input ID: {input_id}',
                                'suggestion': 'Add a <label for="input-id"> element or aria-label attribute'
                            })
        
        # Check for missing heading structure
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if not soup.find('h1'):
            issues.append({
                'title': 'Missing Main Heading (H1)',
                'description': 'Page should have exactly one H1 heading',
                'severity': 'warning',
                'location': 'Page structure',
                'suggestion': 'Add one H1 tag that describes the main content of the page'
            })
        
        # Check for sufficient color contrast (basic check)
        # This is a simplified check - real contrast checking requires more complex analysis
        elements_with_style = soup.find_all(attrs={'style': True})
        for elem in elements_with_style:
            if hasattr(elem, 'get') and hasattr(elem, 'name'):
                style = elem.get('style')
                if style and isinstance(style, str):
                    if 'color:' in style and 'background' in style:
                        elem_name = getattr(elem, 'name', 'unknown')
                        issues.append({
                            'title': 'Potential Color Contrast Issue',
                            'description': 'Element has both color and background defined - check contrast ratio',
                            'severity': 'info',
                            'location': f'Element: {elem_name}',
                            'suggestion': 'Ensure color contrast ratio meets WCAG guidelines (4.5:1 for normal text)'
                        })
        
        return issues
    
    def check_seo_metadata(self, soup: BeautifulSoup, response) -> List[Dict]:
        """Check for SEO and metadata issues"""
        issues = []
        
        # Check title length
        title = soup.find('title')
        if title:
            title_text = title.get_text().strip()
            if len(title_text) < 10:
                issues.append({
                    'title': 'Title Too Short',
                    'description': f'Title is only {len(title_text)} characters',
                    'severity': 'warning',
                    'location': '<title> tag',
                    'suggestion': 'Make title 50-60 characters for optimal SEO'
                })
            elif len(title_text) > 70:
                issues.append({
                    'title': 'Title Too Long',
                    'description': f'Title is {len(title_text)} characters',
                    'severity': 'warning',
                    'location': '<title> tag',
                    'suggestion': 'Keep title under 60 characters to prevent truncation in search results'
                })
        
        # Check meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc:
            issues.append({
                'title': 'Missing Meta Description',
                'description': 'No meta description found',
                'severity': 'warning',
                'location': '<head> section',
                'suggestion': 'Add <meta name="description" content="page description"> for better SEO'
            })
        elif hasattr(meta_desc, 'get'):
            content = meta_desc.get('content')
            if content and isinstance(content, str):
                desc_length = len(content)
                if desc_length > 160:
                    issues.append({
                        'title': 'Meta Description Too Long',
                        'description': f'Meta description is {desc_length} characters',
                        'severity': 'info',
                        'location': 'Meta description',
                        'suggestion': 'Keep meta description under 160 characters'
                    })
        
        # Check for meta keywords (outdated)
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            issues.append({
                'title': 'Outdated Meta Keywords',
                'description': 'Meta keywords tag is no longer used by search engines',
                'severity': 'info',
                'location': 'Meta keywords',
                'suggestion': 'Remove meta keywords tag as it\'s no longer relevant for SEO'
            })
        
        # Check for Open Graph tags
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if not og_title or not og_desc:
            issues.append({
                'title': 'Missing Open Graph Tags',
                'description': 'Missing og:title or og:description for social media sharing',
                'severity': 'info',
                'location': '<head> section',
                'suggestion': 'Add Open Graph meta tags for better social media preview'
            })
        
        return issues
    
    def check_javascript_issues(self, soup: BeautifulSoup, html_content: str) -> List[Dict]:
        """Check for potential JavaScript issues"""
        issues = []
        
        # Check for inline JavaScript
        script_tags = soup.find_all('script')
        inline_scripts = []
        for script in script_tags:
            if hasattr(script, 'string') and script.string and script.string.strip():
                inline_scripts.append(script)
        
        if len(inline_scripts) > 3:
            issues.append({
                'title': 'Excessive Inline JavaScript',
                'description': f'Found {len(inline_scripts)} inline script blocks',
                'severity': 'info',
                'location': 'Page scripts',
                'suggestion': 'Move JavaScript to external files for better organization and caching'
            })
        
        # Check for common JavaScript errors in inline scripts
        for script in inline_scripts:
            if hasattr(script, 'string'):
                script_content = script.string or ''
                
                # Check for console.log statements (debugging code left in production)
                if 'console.log' in script_content:
                    issues.append({
                        'title': 'Debug Code in Production',
                        'description': 'console.log statements found in JavaScript',
                        'severity': 'info',
                        'location': 'Inline JavaScript',
                        'suggestion': 'Remove console.log statements from production code'
                    })
                
                # Check for eval() usage (security risk)
                if 'eval(' in script_content:
                    issues.append({
                        'title': 'Unsafe eval() Usage',
                        'description': 'eval() function usage detected',
                        'severity': 'critical',
                        'location': 'JavaScript code',
                        'suggestion': 'Avoid using eval() as it poses security risks'
                    })
        
        # Check for missing error handling
        script_tags_with_src = soup.find_all('script', src=True)
        if len(script_tags_with_src) > 0:
            # This is a basic check - in a real scenario, we'd need to fetch and analyze external scripts
            issues.append({
                'title': 'External JavaScript Files',
                'description': f'Found {len(script_tags_with_src)} external JavaScript files',
                'severity': 'info',
                'location': 'External scripts',
                'suggestion': 'Ensure external scripts have proper error handling and loading strategies'
            })
        
        return issues
    
    def _calculate_summary(self, report: Dict):
        """Calculate the summary statistics for the report"""
        total = 0
        critical = 0
        warnings = 0
        info = 0
        
        for category_issues in report['categories'].values():
            for issue in category_issues:
                total += 1
                severity = issue.get('severity', 'info')
                if severity == 'critical':
                    critical += 1
                elif severity == 'warning':
                    warnings += 1
                elif severity == 'info':
                    info += 1
        
        report['summary'] = {
            'total': total,
            'critical': critical,
            'warnings': warnings,
            'info': info
        }
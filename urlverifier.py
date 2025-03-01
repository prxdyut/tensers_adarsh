import re
import requests
import time
from typing import List, Dict
from urllib.parse import urlparse
import json

class URLAnalyzer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.vt_base_url = "https://www.virustotal.com/api/v3"
        self.headers = {
            "accept": "application/json",
            "x-apikey": self.api_key
        }

    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text using regex pattern."""
        # URL pattern that matches most common URL formats
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        return list(set(urls))  # Remove duplicates

    def validate_url(self, url: str) -> Dict:
        """
        Check URL safety using VirusTotal API.
        Returns a dictionary with safety analysis.
        """
        try:
            # URL ID is based on base64 of URL
            import base64
            url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
            
            # First check if we have existing analysis
            analysis_url = f"{self.vt_base_url}/urls/{url_id}"
            response = requests.get(analysis_url, headers=self.headers)
            
            if response.status_code == 404:
                # If no existing analysis, submit URL for scanning
                scan_url = f"{self.vt_base_url}/urls"
                data = {"url": url}
                response = requests.post(scan_url, headers=self.headers, data=data)
                
                if response.status_code == 200:
                    # Wait for analysis to complete (with timeout)
                    max_attempts = 10
                    for _ in range(max_attempts):
                        time.sleep(3)  # Wait between checks
                        response = requests.get(analysis_url, headers=self.headers)
                        if response.status_code == 200:
                            break

            if response.status_code != 200:
                return {
                    "url": url,
                    "error": f"API Error: {response.status_code}",
                    "is_safe": False
                }

            results = response.json()
            last_analysis_stats = results.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            
            # Calculate risk score
            malicious = last_analysis_stats.get("malicious", 0)
            suspicious = last_analysis_stats.get("suspicious", 0)
            total_detections = malicious + suspicious
            
            return {
                "url": url,
                "is_safe": total_detections == 0,
                "malicious_detections": malicious,
                "suspicious_detections": suspicious,
                "last_analysis_date": results.get("data", {}).get("attributes", {}).get("last_analysis_date"),
                "reputation_score": results.get("data", {}).get("attributes", {}).get("reputation", 0)
            }

        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "is_safe": False
            }

def analyze_text(text: str, api_key: str) -> List[Dict]:
    """
    Analyze text for URLs and check their safety.
    Returns list of analysis results.
    """
    analyzer = URLAnalyzer(api_key)
    
    # Extract URLs
    print("Extracting URLs from text...")
    urls = analyzer.extract_urls(text)
    
    if not urls:
        print("No URLs found in the text.")
        return []
    
    # Analyze each URL
    results = []
    print(f"\nAnalyzing {len(urls)} URLs with VirusTotal...")
    for url in urls:
        print(f"\nChecking URL: {url}")
        result = analyzer.validate_url(url)
        results.append(result)
        
        # Print result
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            status = "✅ Safe" if result["is_safe"] else "🚨 Potentially Dangerous"
            print(f"Status: {status}")
            print(f"Malicious Detections: {result['malicious_detections']}")
            print(f"Suspicious Detections: {result['suspicious_detections']}")
            
        # Respect VirusTotal API rate limits (4 requests/minute for free API)
        time.sleep(15)
    
    return results

if __name__ == "__main__":
    # Load API key from config file
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
            VIRUSTOTAL_API_KEY = config.get("VIRUSTOTAL_API_KEY")
    except FileNotFoundError:
        print("Error: config.json file not found.")
        print("Please create a config.json file with your VirusTotal API key:")
        print("""
{
    "VIRUSTOTAL_API_KEY": "your_api_key_here"
}
        """)
        exit(1)

    # Example usage
    test_text = """
    Check out these links:
    https://www.google.com
    https://example.com/login
    http://suspicious-site.com/verify
    """
    
    results = analyze_text(test_text, VIRUSTOTAL_API_KEY)
    
    # Save results to file
    with open("url_analysis_results.json", "w") as f:
        json.dump(results, f, indent=4)
    print("\nResults saved to url_analysis_results.json")
import re
import requests
from urllib.parse import urlparse
from typing import Dict, List
import tldextract
import socket
import ssl
import whois
from datetime import datetime
email_content = """
Delivered-To: dyavanapellisujal7@gmail.com
Received: by 2002:a05:6214:27ef:b0:6e8:8e91:fc1 with SMTP id jt15csp196933qvb;
        Thu, 27 Feb 2025 05:52:32 -0800 (PST)
X-Google-Smtp-Source: AGHT+IEfoW7Y5dSw8Pz3meMnMYkXaHWL7UV3V5P/s4SgiqBh81EGb0j0JyH0sKHPAzjcXNsHPTar
X-Received: by 2002:a05:6a00:4fc4:b0:730:f1b7:9bd2 with SMTP id d2e1a72fcca58-73426ca50f7mr39103878b3a.6.1740664352405;
        Thu, 27 Feb 2025 05:52:32 -0800 (PST)
ARC-Seal: i=1; a=rsa-sha256; t=1740664352; cv=none;
        d=google.com; s=arc-20240605;
        b=Zc1u7haMhYu2pXNsQfVrxsM3Yg0Wq+jYbqtLwbBDtoZ/+K6XHjToZntE+s5n4yVgyY
         itIn91FnFLltgmGJCR7tFBsfplOoZY5nCO0m6TIw6Q9uPX7IoxZEWJxdYcqUiu9yiYrO
         h23wNR5/uHnP4TQ8oWUMcNykswY3Oyo1EVuCPSo13GqSFEoSKC+1LzsMLumDCFLsAmWB
         Xa8tDI8GJAFfw0/33PLZ6k16v3FhT/vJfn+fE1yOmsjFk/1Sf7ztZzRubvrvodSRae54
         Qp+VeepVeWGPy8NuoUwR7l9hkWAqxnte8OWd60EAWMwKNQHIQYtB8aE4swJ5C5H1Ozz9
         1cUg==
ARC-Message-Signature: i=1; a=rsa-sha256; c=relaxed/relaxed; d=google.com; s=arc-20240605;
        h=feedback-id:mime-version:subject:message-id:to:from:date
         :dkim-signature:dkim-signature;
        bh=BsCdIZcSEL5pMSUtbq3xoWAFare0mR7uhG9w9r4cC6s=;
        fh=GIvVn7JuYe/LkBQAqRptnFkHzf9sxzU5xgqKQHj5VOA=;
        b=QQKnCDEbDoro7QUaYGKGvVmzr97ASlB3D/87gKX/2aFUZogSc71uHa2V2UeImVEJEc
         GqKvoYnvWkqHR7BQ5IFAOLqcI3bGBEN6p8Q1rj0wGP0shfqEMlQE3EkRMS4QYd0jSfyA
         wovEZJGIcvSfaV5x/7SRUcIgv3sIHEAfbNTfnvd6fgM79WXMOtJOrpUGUybgKpZwDbts
         TFU7U3Ol0Y7OEFiC4Gg79idD454VWhsId3CpIDRCkYGkRjOPkDcNh0ATNYsgDJwQcuhU
         v8LyUaCil7ffxLF1dWTCIzdCRFr361G6VFhAMYfhX+M9IQWdAb8gvu3e9gucB/vKmjPU
         +jlA==;
        dara=google.com
ARC-Authentication-Results: i=1; mx.google.com;
       dkim=pass header.i=@indmoney.com header.s=4miarn56u6qixaa46t5m3fe2h7xa4xvw header.b=mVNM1a63;
       dkim=pass header.i=@amazonses.com header.s=zpkik46mrueu52d3326ufxxchortqmoc header.b=COtwBb+l;
       spf=pass (google.com: domain of 0109019547ae2991-63e9864b-2b1e-4f66-a19f-9b3936896b7c-000000@ap-south-1.amazonses.com designates 76.223.180.116 as permitted sender) smtp.mailfrom=0109019547ae2991-63e9864b-2b1e-4f66-a19f-9b3936896b7c-000000@ap-south-1.amazonses.com;
       dmarc=pass (p=QUARANTINE sp=QUARANTINE dis=NONE) header.from=indmoney.com
Return-Path: <0109019547ae2991-63e9864b-2b1e-4f66-a19f-9b3936896b7c-000000@ap-south-1.amazonses.com>
Received: from c180-116.smtp-out.ap-south-1.amazonses.com (c180-116.smtp-out.ap-south-1.amazonses.com. [76.223.180.116])
        by mx.google.com with ESMTPS id d2e1a72fcca58-734a0061ffcsi2350155b3a.306.2025.02.27.05.52.31
        for <dyavanapellisujal7@gmail.com>
        (version=TLS1_3 cipher=TLS_AES_128_GCM_SHA256 bits=128/128);
        Thu, 27 Feb 2025 05:52:32 -0800 (PST)
Received-SPF: pass (google.com: domain of 0109019547ae2991-63e9864b-2b1e-4f66-a19f-9b3936896b7c-000000@ap-south-1.amazonses.com designates 76.223.180.116 as permitted sender) client-ip=76.223.180.116;
Authentication-Results: mx.google.com;
       dkim=pass header.i=@indmoney.com header.s=4miarn56u6qixaa46t5m3fe2h7xa4xvw header.b=mVNM1a63;
       dkim=pass header.i=@amazonses.com header.s=zpkik46mrueu52d3326ufxxchortqmoc header.b=COtwBb+l;
       spf=pass (google.com: domain of 0109019547ae2991-63e9864b-2b1e-4f66-a19f-9b3936896b7c-000000@ap-south-1.amazonses.com designates 76.223.180.116 as permitted sender) smtp.mailfrom=0109019547ae2991-63e9864b-2b1e-4f66-a19f-9b3936896b7c-000000@ap-south-1.amazonses.com;
       dmarc=pass (p=QUARANTINE sp=QUARANTINE dis=NONE) header.from=indmoney.com
DKIM-Signature: v=1; a=rsa-sha256; q=dns/txt; c=relaxed/simple; s=4miarn56u6qixaa46t5m3fe2h7xa4xvw; d=indmoney.com; t=1740664351; i=@transactions.indmoney.com; h=Date:From:To:Message-ID:Subject:MIME-Version:Content-Type; bh=YuFspKnp3x9oRydDNtD4ptCIXT5pUd2aK+gSa6JYo8c=; b=mVNM1a63vTNl6AsS9EF7rh0/+5+9kQf/SEpbbmwyE4iXV6Ta/dzR+Sc3ZK+mfDXg k5AqstpP2CmXcXrbM2UpeHH5sBQOybkOZ2z/zHTmp6rmARYcfMQQHarUf1Qfb2BIBR1 Dz3XmgCZ6TJKCegKvl/b62ILifqucblrPt2qQElCirHYn5k5M5ZwE8rC/6DWJqr1HVt C/64A/MarCxb3Ft5ICuKB8pHa7G/8C99hN3z5EQftw+q+QQy4I7G3dOXlHAULCdkxNa AsvJYruBmQOqxfbhX2kxPaz3O/T8RmCB/0vWTRO9YJ+tvtw+qfdhN8slatBkQ7OKRuB ntjzU4j9ng==
DKIM-Signature: v=1; a=rsa-sha256; q=dns/txt; c=relaxed/simple; s=zpkik46mrueu52d3326ufxxchortqmoc; d=amazonses.com; t=1740664351; h=Date:From:To:Message-ID:Subject:MIME-Version:Content-Type:Feedback-ID; bh=YuFspKnp3x9oRydDNtD4ptCIXT5pUd2aK+gSa6JYo8c=; b=COtwBb+lB8rHlytqmMnFs9T2ksQ9Lp+mxQ+Th5B92pGc1ZMzmF9+ET6ujt465E7T VBR5hxwLY5cj2ePLyt6S9CC37K77tOykXMqDM3pyI307BnZGoESaVbazx385iJi+XrU 6xyLA90Gn9iXSEscj6+R2YG6FJdN5KSzPYxgUnxg=
Date: Thu, 27 Feb 2025 13:52:31 +0000
From: INDmoney Statements <statements@transactions.indmoney.com>
To: dyavanapellisujal7@gmail.com
Message-ID: <0109019547ae2991-63e9864b-2b1e-4f66-a19f-9b3936896b7c-000000@ap-south-1.amazonses.com>
Subject: Weekly Statement of Funds & Securities | INDmoney
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="----=_Part_627332_242718736.1740664351092"
X-Mailer: SenderID:SignMail27022025152221_JLGJ2MX53L_Grp1_17022025LDWK#)<br>
Feedback-ID: ::1.ap-south-1.wVrw0+2xjBkJR9/X/DhIs4+F/brlUsZfXeBKqZZI+PY=:AmazonSES
X-SES-Outgoing: 2025.02.27-76.223.180.116

------=_Part_627332_242718736.1740664351092
Content-Type: multipart/alternative; boundary="----=_Part_627331_11564662.1740664351091"

------=_Part_627331_11564662.1740664351091
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 7bit


									
									
												
													
																
																	
																
																
																
													
												
									
									
									
									
								

------=_Part_627331_11564662.1740664351091
Content-Type: text/html; charset=UTF-8
Content-Transfer-Encoding: 7bit

 <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html data-editor-version="2" class="sg-campaigns" xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1, maximum-scale=1">

	
<meta name="supported-color-schemes" content="light">

<meta name="supported-color-schemes" content="light dark">	
	
<!--[if !mso]><!-->
<meta http-equiv="X-UA-Compatible" content="IE=Edge">
<!--<![endif]--> 

<!--user entered Head Start--><!--End Head user entered-->
<meta name="x-apple-disable-message-reformatting">
<title>Weekly Statement  </title>
<!--[if mso]>
    <style>
        table {border-collapse:collapse;border-spacing:0;border:none;margin:0;}
        div, td {padding:0;}
        div {margin:0 !important;}
    </style>
    <noscript>
        <xml>
            <o:OfficeDocumentSettings>
            <o:PixelsPerInch>96</o:PixelsPerInch>
            </o:OfficeDocumentSettings>
        </xml>
    </noscript>
    <![endif]-->
<style>
	
	
	
body{
    background: #F2F5F8;
}	
table, td, div, h1, p {
    font-family: 'Arial', sans-serif;
}
p {
    margin: 0;
    padding: 0;
}
.cta-wrap {
    margin: 25px 0 20px 0;
    text-align: center;
}
.cta-btn {
    background: #FFC40D;
    border: 0 none;
    color: #000 !important;
    font-size: 22px;
    font-weight: 600;
    padding: 16px 70px;
    border-radius: 40px;
    text-decoration: none;
    cursor: pointer;
    display: inline-block;
   
}
.header {
    background-color: #1366E8;
    padding: 21px 0 0 0;
}
.grad-bg {
    background: #017AFF;
    padding: 0 10px;
}
.footer-nav {
    padding: 45px 0 10px 0;
}
.footer-help-text {
    font-size: 13px;
    font-weight: 500;
    color: #000000;
    padding: 0;
    max-width: 480px;
}
	

	
	
	
@media only screen and (min-width: 320px) and (max-width:530px)
    {
		.responsiveimg{max-width:100%;}		
		.padLR10{padding:0 10px!important;}
		.padLR20{padding:0 20px!important;}
		.padLR40{padding:0 40px!important;}
		.linewidth{width:20px!important;}
		.width100{width:100%;}
		.mbtn{    padding: 10px 22px!important; font-size:14px!important;}
.table-2colum {
    display: inline-block !important;
    width: 100% !important;
    max-width: 100% !important;
    direction: ltr !important;
}		
	
		.appendBottom15{margin-bottom:15px!important;}
		.mobile-left{text-align: left;}
		.mheading{line-height: 28px!important; font-size: 22px!important; }	
		
		.sub-heading{line-height: 28px!important; font-size: 24px!important;}
		
		
		
		
		
	}

@media (prefers-color-scheme: dark) {
body, .mainBg {
    background: #F2F5F8;
}

	
.grad-bg {
    background: #3578f7;
}
	
	
	
	
	
}
</style>
</head>

<body style="background-color: #F2F5F8; margin: 0; padding: 0;font-family: 'Arial', sans-serif; word-spacing:normal;">
<table width="100%" class="mainBg" cellspacing="0" cellpadding="0" border="0" align="center" style="background-color: #F2F5F8; background: url(http://cdn.mcauto-images-production.sendgrid.net/61d70335c7e70d7c/39213c91-95e9-409a-a424-0166bf67c400/5x5.png); font-family: 'Arial', sans-serif; word-spacing:normal">
  <tr>
    <td><div style="max-width: 600px; margin: 0px auto; background-color: #F2F5F8;"> 
        <!-- Logo -->
       
        <!-- Head -->
	

		
		
		
        <table width="100%" cellspacing="0" cellpadding="0" style="background:#fff;background-color:#fff;">
          <tr>
            <td  align="center"  style="padding:20px 0; background: url(http://cdn.mcauto-images-production.sendgrid.net/61d70335c7e70d7c/39213c91-95e9-409a-a424-0166bf67c400/5x5.png)"><a href="https://www.indmoney.com/" target="_blank"><img src="https://cdn.indiawealth.in/public/ind-marketing/indstocklogo.png" style=" text-align: center; max-width:140px;" alt=" INDstocks" vspace="0" hspace="0" align="absmiddle"></a></td>
          </tr>
          <tr>
            <td class="padLR20" style="background-color:#fff; padding:20px 40px; background: url(https://cdn.indiawealth.in/public/ind-marketing/white-bg.png)">
				
			<div>	
				
		<table width="100%" cellpadding="0" cellspacing="0" style="max-width: 530px; margin: 0 auto; text-align: center;">
				
			<tr>
		          <td align="center" style="padding:0;">
				<p class="mheading" style="font-family:'Avenir Next', 'Arial', sans-serif; line-height: 36px; font-size: 32px; text-align: left; margin:30px 0 50px; font-weight: 600; color:#535353;"> Weekly Statement </p>	
					
	<p style="font-family:'Avenir Next', 'Arial', sans-serif; line-height: 24px; font-size: 16px; color: #757779; text-align: left; margin: 0; padding:0;">Hi Sujal prabhakar dyavanpelli,
</p>						
					
	<p style="font-family:'Avenir Next', 'Arial', sans-serif; line-height: 24px; font-size: 16px; color: #757779; text-align: left; margin: 0 0 40px; padding:0;">Client Code: JLGJ2MX53L
</p>
					  
<p style="font-family:'Avenir Next', 'Arial', sans-serif; line-height: 24px; font-size: 16px; color: #757779; text-align: left; margin: 0 0 6px ; padding:0;">We have attached the weekly statement of accounts for funds & securities.

</p>
					  
<p style="font-family:'Avenir Next', 'Arial', sans-serif; line-height: 24px; font-size: 16px; color: #757779; text-align: left; margin: 0 0 20px; padding:0;">The document is password protected. Please use your PAN in capital letters to access the document.
</p>
					  
					  
<p style="font-family:'Avenir Next', 'Arial', sans-serif; line-height: 24px; font-size: 16px; color: #757779; text-align: left; margin: 0 0 6px; padding:0;">For any queries, you can contact us at <a href="mailto:instockssupport@indmoney.com" target="_blank" style="color:#3478f6; text-decoration:none;">instockssupport@indmoney.com</a>
</p>
<p style="font-family:'Avenir Next', 'Arial', sans-serif; line-height: 24px; font-size: 16px; color: #757779; text-align: left; margin: 0 0 6px; padding:0;">Team INDmoney
</p>	
<p style="font-family:'Avenir Next', 'Arial', sans-serif; line-height: 24px; font-size: 16px; color: #757779; text-align: left; margin: 0 0 6px; padding:0; display:none;">MailID:(SignMail27022025152221_JLGJ2MX53L_Grp1_17022025LDWK#)
</p>					  
					</td>
	            </tr>
		
		
		
</table>
			  
			</div>  
			  
			  
			  </td>
          </tr>
          <tr>
            <td  style="background-color:#F7F9FC; padding:20px 20px;">
			  
	<table width="100%"  align="center" cellpadding="0" cellspacing="0">
                    <tr>
                      <td align="center">
						
	<p style=" line-height: 20px; font-size: 15px; color:#757779; text-align: center; padding:0; margin:0 0 8px; font-weight: 600;">Get the INDmoney app!</p>	
						  
	<p style=" line-height: 20px; font-size: 13px; color: #757779; text-align: center; padding:0; margin:0 0 10px;">Available in the App Store or Google Play</p>						  
						</td>
                    </tr>
                    <tr> 
	   
	   <td style="vertical-align:top"> <table cellspacing="0" cellpadding="0" border="0" align="center"> <tbody><tr> <td style="vertical-align:top;padding-right:5px"> <a href="https://play.google.com/store/apps/details?id=in.indwealth&referrer=af_tranid%3D_fSsAqrepT64E4us6LhYyw%26shortlink%3D41d5a150%26….
"""

class URLValidator:
    def __init__(self):
        # Common legitimate domains that shouldn't trigger false positives
        self.whitelist_domains = {
            'google.com', 'apple.com', 'microsoft.com', 'amazon.com',
            'play.google.com', 'indmoney.com', 'amazonses.com'
        }
        
        # Common phishing indicators in URLs
        self.suspicious_keywords = [
            'login', 'signin', 'verify', 'verification', 'account',
            'password', 'secure', 'update', 'banking', 'confirm'
        ]

    def check_url_safety(self, url: str) -> Dict:
        """
        Check if a URL is potentially phishing using multiple validation methods.
        """
        result = {
            'url': url,
            'is_suspicious': False,
            'risk_factors': [],
            'safety_score': 100,  # Start with perfect score and deduct points
            'checks': {}
        }

        # Extract domain information
        extracted = tldextract.extract(url)
        domain = f"{extracted.domain}.{extracted.suffix}"

        # 1. Check if domain is whitelisted
        if domain in self.whitelist_domains:
            result['checks']['whitelist'] = "Domain is whitelisted"
            return result

        # 2. Check for suspicious keywords
        if any(keyword in url.lower() for keyword in self.suspicious_keywords):
            result['risk_factors'].append("Contains suspicious keywords")
            result['safety_score'] -= 20

        # 3. Check for URL length (extremely long URLs are suspicious)
        if len(url) > 100:
            result['risk_factors'].append("Unusually long URL")
            result['safety_score'] -= 10

        # 4. Check for SSL/TLS certificate
        try:
            hostname = urlparse(url).netloc
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    result['checks']['ssl'] = "Valid SSL certificate"
        except:
            result['risk_factors'].append("Invalid or missing SSL certificate")
            result['safety_score'] -= 30

        # 5. Check domain age using WHOIS
        try:
            domain_info = whois.whois(domain)
            if domain_info.creation_date:
                creation_date = domain_info.creation_date
                if isinstance(creation_date, list):
                    creation_date = creation_date[0]
                domain_age = (datetime.now() - creation_date).days
                if domain_age < 30:
                    result['risk_factors'].append("Domain is less than 30 days old")
                    result['safety_score'] -= 30
        except:
            result['risk_factors'].append("Cannot verify domain age")
            result['safety_score'] -= 10

        # Determine if URL is suspicious based on safety score
        result['is_suspicious'] = result['safety_score'] < 70
        
        return result

def validate_urls(urls: List[str]) -> List[Dict]:
    """
    Validate a list of URLs and return their safety analysis.
    """
    validator = URLValidator()
    results = []
    
    for url in urls:
        try:
            result = validator.check_url_safety(url)
            results.append(result)
        except Exception as e:
            results.append({
                'url': url,
                'error': str(e),
                'is_suspicious': True,
                'risk_factors': ['Error during validation'],
                'safety_score': 0
            })
    
    return results

def main():
    """Main function to demonstrate URL validation"""
    try:
        # Import URL extractor
        from urlextractor import extract_urls_from_email
        
        print("Starting URL validation process...")
        
        # Example URLs for testing
        test_urls = [
            "https://www.indmoney.com/",
            "https://play.google.com/store/apps/details?id=in.indwealth",
            "mailto:instockssupport@indmoney.com"
        ]
        
        print("\nAnalyzing URLs...")
        validation_results = validate_urls(test_urls)
        
        # Print results in a formatted way
        for result in validation_results:
            print("\n" + "="*50)
            print(f"URL: {result['url']}")
            print(f"Safety Score: {result['safety_score']}/100")
            print(f"Status: {'🚨 SUSPICIOUS' if result['is_suspicious'] else '✅ SAFE'}")
            
            if result['risk_factors']:
                print("\nRisk Factors:")
                for factor in result['risk_factors']:
                    print(f"❌ {factor}")
            
            if 'checks' in result and result['checks']:
                print("\nPassed Checks:")
                for check in result['checks'].values():
                    print(f"✓ {check}")
            print("="*50)
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main()
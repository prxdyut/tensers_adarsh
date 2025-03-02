import dotenv from 'dotenv';
import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import bodyParser from 'body-parser';
import jwt from 'jsonwebtoken';
import cookieParser from 'cookie-parser';
import fetch from 'node-fetch';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Get __dirname equivalent in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const users = [];

// Incidents data
const incidents = [
  {
    id: 1,
    date: "2023-06-15", 
    subject: "PayPal Transaction Confirmation",
    sender: "support@paypal.com",
    verdict: "Legitimate",
    email_headers: "From: support@paypal.com\nReply-To: support@paypal.com\nARC-Authentication-Results: i=1; mx.google.com;\n   dkim=pass header.i=@paypal.com header.s=Outgoing01 header.b=jbnHPD4n;\n   spf=pass (google.com: domain of support@paypal.com designates 121.241.26.42 as permitted sender) smtp.mailfrom=support@paypal.com;\n   dmarc=pass (p=REJECT sp=REJECT dis=NONE) header.from=paypal.com",
    email_content: "Dear Customer, your recent transaction of $50.00 has been processed successfully. If you did not authorize this transaction, please contact us immediately.",
    vt_results: {
      IP: "192.168.1.1: Not Malicious",
      Domain: "paypal.com: Not Malicious", 
      URLs: [
        "https://paypal.com: Not Malicious"
      ]
    }
  },
  {
    id: 2,
    date: "2023-06-14",
    subject: "Bank of America Security Alert",
    sender: "security@bankofamerica.com",
    verdict: "Phishing",
    email_headers: "From: security@bankofamerica.com\nReply-To: security@bankofamerica.com\nARC-Authentication-Results: i=1; mx.google.com;\n   dkim=fail header.i=@bankofamerica.com header.s=Outgoing01 header.b=jbnHPD4n;\n   spf=fail (google.com: domain of security@bankofamerica.com does not designate 121.241.26.42 as permitted sender) smtp.mailfrom=security@bankofamerica.com;\n   dmarc=fail (p=REJECT sp=REJECT dis=NONE) header.from=bankofamerica.com",
    email_content: "Your Bank of America account has been compromised. Click here to secure your account: http://bit.ly/fake-bank-link.",
    vt_results: {
      IP: "192.168.1.2: Malicious",
      Domain: "bankofamerica.com: Malicious (Detected)",
      URLs: [
        "http://bit.ly/fake-bank-link: Malicious (Detected by 5 engines)"
      ]
    }
  },
  {
    id: 3,
    date: "2023-06-13",
    subject: "Amazon Account Alert",
    sender: "noreply@amazon.com",
    verdict: "Phishing",
    email_headers: "From: noreply@amazon.com\nReply-To: noreply@amazon.com\nARC-Authentication-Results: i=1; mx.google.com;\n   dkim=pass header.i=@amazon.com header.s=Outgoing01 header.b=jbnHPD4n;\n   spf=pass (google.com: domain of noreply@amazon.com designates 121.241.26.42 as permitted sender) smtp.mailfrom=noreply@amazon.com;\n   dmarc=pass (p=REJECT sp=REJECT dis=NONE) header.from=amazon.com",
    email_content: "URGENT: Your Amazon account has been locked. Click here to verify your identity: http://bit.ly/fake-amazon-link.",
    vt_results: {
      IP: "192.168.1.3: Not Malicious",
      Domain: "amazon.com: Not Malicious",
      URLs: [
        "http://bit.ly/fake-amazon-link: Malicious (Detected by 3 engines)"
      ]
    }
  },
  {
    id: 4,
    date: "2023-06-12",
    subject: "PayPal Account Restricted",
    sender: "support@paypa1.com",
    verdict: "Phishing",
    email_headers: "From: support@paypa1.com\nReply-To: support@paypa1.com\nARC-Authentication-Results: i=1; mx.google.com;\n   dkim=fail header.i=@paypa1.com header.s=Outgoing01 header.b=jbnHPD4n;\n   spf=fail (google.com: domain of support@paypa1.com does not designate 121.241.26.42 as permitted sender) smtp.mailfrom=support@paypa1.com;\n   dmarc=fail (p=REJECT sp=REJECT dis=NONE) header.from=paypa1.com",
    email_content: "Your PayPal account has been restricted. Click here to unlock it: http://bit.ly/fake-paypal-link.",
    vt_results: {
      IP: "192.168.1.4: Malicious",
      Domain: "paypa1.com: Malicious (Detected)",
      URLs: [
        "http://bit.ly/fake-paypal-link: Malicious (Detected by 7 engines)"
      ]
    }
  },
  {
    id: 5,
    date: "2023-06-03",
    subject: "Walmart Gift Card Winner",
    sender: "bankalerts@kotak.com",
    verdict: "Phishing",
    email_headers: "From: bankalerts@kotak.com\nReply-To: bankalerts@kotak.com\nARC-Authentication-Results: i=1; mx.google.com;\n   dkim=pass header.i=@kotak.com header.s=Outgoing01 header.b=jbnHPD4n;\n   spf=pass (google.com: domain of bankalerts@kotak.com designates 121.241.26.42 as permitted sender) smtp.mailfrom=bankalerts@kotak.com;\n   dmarc=pass (p=REJECT sp=REJECT dis=NONE) header.from=kotak.com",
    email_content: "Congratulations! You've won a $1000 Walmart gift card. Go to http://bit.ly/fake-link to claim now.\nThis is a limited-time offer, so act fast!",
    vt_results: {
      IP: "192.168.1.1: Not Malicious",
      Domain: "example.com: Malicious (Detected)",
      URLs: [
        "https://malicious-site.com: Malicious (Detected by 5 engines)",
        "https://safe-site.com: Not Malicious"
      ]
    }
  },
  {
    id: 6,
    date: "2023-06-10",
    subject: "Apple ID Locked",
    sender: "security@apple.com",
    verdict: "Phishing",
    email_headers: "From: security@apple.com\nReply-To: security@apple.com\nARC-Authentication-Results: i=1; mx.google.com;\n   dkim=fail header.i=@apple.com header.s=Outgoing01 header.b=jbnHPD4n;\n   spf=fail (google.com: domain of security@apple.com does not designate 121.241.26.42 as permitted sender) smtp.mailfrom=security@apple.com;\n   dmarc=fail (p=REJECT sp=REJECT dis=NONE) header.from=apple.com",
    email_content: "Your Apple ID has been locked. Click here to unlock it: http://bit.ly/fake-apple-link.",
    vt_results: {
      IP: "192.168.1.6: Malicious",
      Domain: "apple.com: Malicious (Detected)",
      URLs: [
        "http://bit.ly/fake-apple-link: Malicious (Detected by 6 engines)"
      ]
    }
  },
  // Adding 10 more incidents with a mix of phishing and legitimate emails
  {
    id: 7,
    date: "2023-06-09",
    subject: "Google Drive Shared Document",
    sender: "drive-shares-noreply@google.com",
    verdict: "Legitimate",
    email_headers: "From: drive-shares-noreply@google.com\nReply-To: drive-shares-noreply@google.com\nARC-Authentication-Results: i=1; mx.google.com;\n   dkim=pass header.i=@google.com header.s=Outgoing01 header.b=jbnHPD4n;\n   spf=pass (google.com: domain of drive-shares-noreply@google.com designates 121.241.26.42 as permitted sender) smtp.mailfrom=drive-shares-noreply@google.com;\n   dmarc=pass (p=REJECT sp=REJECT dis=NONE) header.from=google.com",
    email_content: "John Doe has shared a document with you: 'Q2 Financial Report'. Click here to view: https://drive.google.com/file/d/1234567890",
    vt_results: {
      IP: "192.168.1.7: Not Malicious",
      Domain: "google.com: Not Malicious",
      URLs: [
        "https://drive.google.com/file/d/1234567890: Not Malicious"
      ]
    }
  },
  {
    id: 8,
    date: "2023-06-08",
    subject: "Netflix: Update Your Payment Information",
    sender: "info@netflix-mail.com",
    verdict: "Phishing",
    email_headers: "From: info@netflix-mail.com\nReply-To: info@netflix-mail.com\nARC-Authentication-Results: i=1; mx.google.com;\n   dkim=fail header.i=@netflix-mail.com header.s=Outgoing01 header.b=jbnHPD4n;\n   spf=fail (google.com: domain of info@netflix-mail.com does not designate 121.241.26.42 as permitted sender) smtp.mailfrom=info@netflix-mail.com;\n   dmarc=fail (p=REJECT sp=REJECT dis=NONE) header.from=netflix-mail.com",
    email_content: "Dear Customer, your Netflix payment method has expired. Update your payment information now to avoid service interruption: http://bit.ly/fake-netflix-link",
    vt_results: {
      IP: "192.168.1.8: Malicious",
      Domain: "netflix-mail.com: Malicious (Detected)",
      URLs: [
        "http://bit.ly/fake-netflix-link: Malicious (Detected by 8 engines)"
      ]
    }
  },
  {
    id: 9,
    date: "2023-06-07",
    subject: "Your Amazon Order #123-4567890-1234567",
    sender: "auto-confirm@amazon.com",
    verdict: "Legitimate",
    email_headers: "From: auto-confirm@amazon.com\nReply-To: auto-confirm@amazon.com\nARC-Authentication-Results: i=1; mx.google.com;\n   dkim=pass header.i=@amazon.com header.s=Outgoing01 header.b=jbnHPD4n;\n   spf=pass (google.com: domain of auto-confirm@amazon.com designates 121.241.26.42 as permitted sender) smtp.mailfrom=auto-confirm@amazon.com;\n   dmarc=pass (p=REJECT sp=REJECT dis=NONE) header.from=amazon.com",
    email_content: "Hello, Thank you for your order. Your Amazon.com order #123-4567890-1234567 has been shipped. Your package is expected to be delivered on June 10, 2023.",
    vt_results: {
      IP: "192.168.1.9: Not Malicious",
      Domain: "amazon.com: Not Malicious",
      URLs: [
        "https://amazon.com/orders/123-4567890-1234567: Not Malicious"
      ]
    }
  },
  {
    id: 10,
    date: "2023-06-06",
    subject: "Urgent: Your Microsoft Account Has Been Compromised",
    sender: "security@microsoft365.net",
    verdict: "Phishing",
    email_headers: "From: security@microsoft365.net\nReply-To: security@microsoft365.net\nARC-Authentication-Results: i=1; mx.google.com;\n   dkim=fail header.i=@microsoft365.net header.s=Outgoing01 header.b=jbnHPD4n;\n   spf=fail (google.com: domain of security@microsoft365.net does not designate 121.241.26.42 as permitted sender) smtp.mailfrom=security@microsoft365.net;\n   dmarc=fail (p=REJECT sp=REJECT dis=NONE) header.from=microsoft365.net",
    email_content: "URGENT: We have detected suspicious login attempts to your Microsoft account. Please verify your identity immediately: http://bit.ly/fake-microsoft-link",
    vt_results: {
      IP: "192.168.1.10: Malicious",
      Domain: "microsoft365.net: Malicious (Detected)",
      URLs: [
        "http://bit.ly/fake-microsoft-link: Malicious (Detected by 9 engines)"
      ]
    }
  },
  {
    id: 11,
    date: "2023-06-05",
    subject: "Your Monthly Bank Statement",
    sender: "statements@chase.com",
    verdict: "Legitimate",
    email_headers: "From: statements@chase.com\nReply-To: statements@chase.com\nARC-Authentication-Results: i=1; mx.google.com;\n   dkim=pass header.i=@chase.com header.s=Outgoing01 header.b=jbnHPD4n;\n   spf=pass (google.com: domain of statements@chase.com designates 121.241.26.42 as permitted sender) smtp.mailfrom=statements@chase.com;\n   dmarc=pass (p=REJECT sp=REJECT dis=NONE) header.from=chase.com",
    email_content: "Your Chase bank statement for May 2023 is now available. Please log in to your account to view it: https://secure.chase.com/login",
    vt_results: {
      IP: "192.168.1.11: Not Malicious",
      Domain: "chase.com: Not Malicious",
      URLs: [
        "https://secure.chase.com/login: Not Malicious"
      ]
    }
  },
  {
    id: 12,
    date: "2023-06-04",
    subject: "LinkedIn: New Connection Request",
    sender: "connections@linkedin.com",
    verdict: "Legitimate",
    email_headers: "From: connections@linkedin.com\nReply-To: connections@linkedin.com\nARC-Authentication-Results: i=1; mx.google.com;\n   dkim=pass header.i=@linkedin.com header.s=Outgoing01 header.b=jbnHPD4n;\n   spf=pass (google.com: domain of connections@linkedin.com designates 121.241.26.42 as permitted sender) smtp.mailfrom=connections@linkedin.com;\n   dmarc=pass (p=REJECT sp=REJECT dis=NONE) header.from=linkedin.com",
    email_content: "Jane Smith wants to connect with you on LinkedIn. View profile: https://www.linkedin.com/in/jane-smith-12345",
    vt_results: {
      IP: "192.168.1.12: Not Malicious",
      Domain: "linkedin.com: Not Malicious",
      URLs: [
        "https://www.linkedin.com/in/jane-smith-12345: Not Malicious"
      ]
    }
  },
  {
    id: 13,
    date: "2023-06-03",
    subject: "Dropbox: Suspicious Login Attempt",
    sender: "no-reply@dropboxmail.com",
    verdict: "Phishing",
    email_headers: "From: no-reply@dropboxmail.com\nReply-To: no-reply@dropboxmail.com\nARC-Authentication-Results: i=1; mx.google.com;\n   dkim=fail header.i=@dropboxmail.com header.s=Outgoing01 header.b=jbnHPD4n;\n   spf=fail (google.com: domain of no-reply@dropboxmail.com does not designate 121.241.26.42 as permitted sender) smtp.mailfrom=no-reply@dropboxmail.com;\n   dmarc=fail (p=REJECT sp=REJECT dis=NONE) header.from=dropboxmail.com",
    email_content: "We detected a login attempt from an unrecognized device. If this wasn't you, secure your account immediately: http://bit.ly/fake-dropbox-link",
    vt_results: {
      IP: "192.168.1.13: Malicious",
      Domain: "dropboxmail.com: Malicious (Detected)",
      URLs: [
        "http://bit.ly/fake-dropbox-link: Malicious (Detected by 6 engines)"
      ]
    }
  },
  {
    id: 14,
    date: "2023-06-02",
    subject: "Your Flight Confirmation - AA1234",
    sender: "reservations@aa.com",
    verdict: "Legitimate",
    email_headers: "From: reservations@aa.com\nReply-To: reservations@aa.com\nARC-Authentication-Results: i=1; mx.google.com;\n   dkim=pass header.i=@aa.com header.s=Outgoing01 header.b=jbnHPD4n;\n   spf=pass (google.com: domain of reservations@aa.com designates 121.241.26.42 as permitted sender) smtp.mailfrom=reservations@aa.com;\n   dmarc=pass (p=REJECT sp=REJECT dis=NONE) header.from=aa.com",
    email_content: "Thank you for your booking. Your flight AA1234 from New York (JFK) to Los Angeles (LAX) is confirmed for June 15, 2023 at 10:30 AM.",
    vt_results: {
      IP: "192.168.1.14: Not Malicious",
      Domain: "aa.com: Not Malicious",
      URLs: [
        "https://www.aa.com/reservation/view?id=ABCDEF: Not Malicious"
      ]
    }
  },
  {
    id: 15,
    date: "2023-06-01",
    subject: "Urgent: Tax Refund Notification",
    sender: "refunds@irs-gov.org",
    verdict: "Phishing",
    email_headers: "From: refunds@irs-gov.org\nReply-To: refunds@irs-gov.org\nARC-Authentication-Results: i=1; mx.google.com;\n   dkim=fail header.i=@irs-gov.org header.s=Outgoing01 header.b=jbnHPD4n;\n   spf=fail (google.com: domain of refunds@irs-gov.org does not designate 121.241.26.42 as permitted sender) smtp.mailfrom=refunds@irs-gov.org;\n   dmarc=fail (p=REJECT sp=REJECT dis=NONE) header.from=irs-gov.org",
    email_content: "You have a pending tax refund of $1,247.38. Please complete the verification process to receive your refund: http://bit.ly/fake-irs-link",
    vt_results: {
      IP: "192.168.1.15: Malicious",
      Domain: "irs-gov.org: Malicious (Detected)",
      URLs: [
        "http://bit.ly/fake-irs-link: Malicious (Detected by 10 engines)"
      ]
    }
  },
  {
    id: 16,
    date: "2023-05-31",
    subject: "Zoom Meeting Invitation: Project Review",
    sender: "no-reply@zoom.us",
    verdict: "Legitimate",
    email_headers: "From: no-reply@zoom.us\nReply-To: no-reply@zoom.us\nARC-Authentication-Results: i=1; mx.google.com;\n   dkim=pass header.i=@zoom.us header.s=Outgoing01 header.b=jbnHPD4n;\n   spf=pass (google.com: domain of no-reply@zoom.us designates 121.241.26.42 as permitted sender) smtp.mailfrom=no-reply@zoom.us;\n   dmarc=pass (p=REJECT sp=REJECT dis=NONE) header.from=zoom.us",
    email_content: "John Doe is inviting you to a scheduled Zoom meeting. Topic: Project Review Meeting. Time: June 5, 2023 02:00 PM Eastern Time (US and Canada)",
    vt_results: {
      IP: "192.168.1.16: Not Malicious",
      Domain: "zoom.us: Not Malicious",
      URLs: [
        "https://zoom.us/j/1234567890?pwd=abcdefghijklmnop: Not Malicious"
      ]
    }
  }
];

app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));
app.use("/assets", express.static("assets"));

app.use(bodyParser.urlencoded({ extended: true })); // Middleware to parse form data
app.use(bodyParser.json()); // Add JSON parser for API requests
app.use(cookieParser()); // Use cookie-parser middleware

// Routes
app.get("/login", (req, res) => {
  res.render("login");
});

app.get("/register", (req, res) => {
  res.render("register");
});

app.post("/api/auth/sign-in", async (req, res) => {
  res.redirect("/dashboard"); // Return success message
});

app.post("/api/auth/sign-up", async (req, res) => {
  res.redirect("/dashboard");
});

app.get("/dashboard", (req, res) => {
  
  res.render("dashboard", { incidents });
});

app.get("/incidents", (req, res) => {
  res.render("incidents", { incidents });
});

app.get("/report/:id?", async (req, res) => {
  try {
    const incidentId = req.params.id;
    let emailData;
    
    // If an incident ID is provided, use that incident's data
    if (incidentId) {
      const incident = incidents.find(inc => inc.id === parseInt(incidentId));
      if (!incident) {
        throw new Error("Incident not found");
      }
      emailData = {
        email_headers: incident.email_headers,
        email_content: incident.email_content,
        vt_results: incident.vt_results
      };
    } else {
      // Default email data if no incident ID is provided
      emailData = {
        email_headers: "From: bankalerts@kotak.com\nReply-To: bankalerts@kotak.com\nARC-Authentication-Results: i=1; mx.google.com;\n   dkim=pass header.i=@kotak.com header.s=Outgoing01 header.b=jbnHPD4n;\n   spf=pass (google.com: domain of bankalerts@kotak.com designates 121.241.26.42 as permitted sender) smtp.mailfrom=bankalerts@kotak.com;\n   dmarc=pass (p=REJECT sp=REJECT dis=NONE) header.from=kotak.com",
        email_content: "Hi am owner of this comapny, we are offering a free trial for our product, please click the link to claim your free trial",
        vt_results: {
          IP: "192.168.1.1: Not Malicious",
          Domain: "example.com: Malicious (Detected)",
        },
      };
    }

    const fetchUrl = "https://ad7d-14-139-125-227.ngrok-free.app/detect-phishing";
    
    const response = await fetch(fetchUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(emailData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    // Parse the report for detailed sections
    const parseReport = (reportStr) => {
      const sections = {};
      const lines = reportStr.split('\n').map(line => line.trim());
      
      let currentSection = '';
      lines.forEach(line => {
        if (line.startsWith('==')) return;
        
        if (line.match(/^\d+\./)) {
          currentSection = line.split(':')[0].substring(3).trim();
          sections[currentSection] = [];
        } else if (line.startsWith('-') && currentSection) {
          sections[currentSection].push(line.substring(2).trim());
        }
      });
      return sections;
    };

    const parsedReport = parseReport(data.report);
    
    // Prepare analysis data
    const analysisData = {
      emailData: emailData,
      verdict: data.verdict,
      confidence: (data.confidence * 100).toFixed(2),
      report: data.report,
      enhanced_report: data.enhanced_report,
      parsedReport: parsedReport,
      isPhishing: !data.verdict.toLowerCase().includes("not phishing")
    };

    res.render("report", { analysisData });
  } catch (error) {
    console.error('Error:', error);
    res.render("report", { 
      analysisData: {
        emailData: {
          email_headers: "Error fetching data",
          email_content: "Error fetching data",
          vt_results: { IP: "N/A", Domain: "N/A" }
        },
        verdict: "Error analyzing email",
        confidence: "N/A",
        report: "Analysis failed",
        enhanced_report: "Analysis failed",
        parsedReport: {},
        isPhishing: false
      }
    });
  }
});

app.get("/chatbot", (req, res) => {
  res.render("chatbot", { messages: [] });
});

app.post("/api/chat", async (req, res) => {
  try {
    const { message } = req.body;
    
    if (!message) {
      return res.status(400).json({ error: "Message is required" });
    }
    
    const response = await fetch("https://ad7d-14-139-125-227.ngrok-free.app/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    res.json(data);
  } catch (error) {
    console.error('Error in chat API:', error);
    res.status(500).json({ error: "Failed to get response from chat API" });
  }
});

app.get("/blogs", async (req, res) => {
  try {
    const response = await fetch("https://ad7d-14-139-125-227.ngrok-free.app/news");
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const blogs = await response.json();
    console.log(blogs);
    res.render("blogs", { blogs });
  } catch (error) {
    console.error('Error fetching blogs:', error);
    // Provide empty array as fallback if API call fails
    
    res.render("blogs", { blogs: [
      {
        "confidence": "0.7",
        "link": "https://cyberscoop.com/tim-brown-solarwinds-liability-cyberlawcon/",
        "sentiment": "negative",
        "summary": "SolarWinds' CISO, Tim Brown, stated that security executives are \"nervous\" about individual liability for data breaches. Brown, who faced legal action after a major hack at SolarWinds, said that holding individuals liable can distract from their core work and create uncertainty. He suggested that CISOs need clarity on how to operate effectively without undue risk of penalties. A survey found that 7 out of 10 CISOs said reports of executives being held liable for breaches has negatively affected their opinion of the job, while nearly half agreed that individual liability would improve accountability.",
        "title": "SolarWinds CISO says security execs are ‘nervous’ about individual liability for data breaches"
      },
      {
        "confidence": "0.95",
        "link": "https://cyberscoop.com/army-soldier-alleged-cybercriminal-foreign-spies/",
        "sentiment": "negative",
        "summary": "A 21-year-old US Army soldier, Cameron Wagenius, is accused of attempting to sell stolen sensitive information to a foreign intelligence service. Wagenius allegedly tried to extort $500,000 from a major telecommunications company, later identified as AT&T, by threatening to leak phone records of high-ranking public officials. He also searched for ways to defect to Russia and queried \"can hacking be treason.\" Wagenius' actions are believed to be part of a broader effort to extort victims and leak sensitive information, and he has been linked to a previous attack spree targeting organizations that stored data on Snowflake.",
        "title": "Army soldier linked to Snowflake attack spree allegedly tried to sell data to foreign spies"
      },
      {
        "confidence": "0.8",
        "link": "https://cyberscoop.com/google-sms-verification-change-passkey-multifactor-authentication/",
        "sentiment": "neutral",
        "summary": "Google is phasing out SMS-based verification for its two-step verification process, citing security vulnerabilities such as phishing attacks and dependence on phone carriers' security practices. Instead, the company is introducing a QR code-based system that users will scan with their phone's camera. The change will affect all Google services, including Gmail and YouTube, and is part of a broader industry trend towards more secure verification methods. Google will still use phone number-based verification, but not via SMS, and recommends passkeys as a preferred method. The transition will be gradual, with no specific timeline for completion.",
        "title": "Here’s what Google is (and isn’t) planning with SMS account verification"
      },
      {
        "confidence": "0.8",
        "link": "https://cyberscoop.com/cfpb-nominee-jonathan-mckernan-data-brokers/",
        "sentiment": "neutral",
        "summary": "Here is a summary of the text in 150 words or less:\n\nJonathan McKernan, nominee for director of the Consumer Financial Protection Bureau (CFPB), expressed openness to continuing the agency's work on data brokers, which was started by his predecessor Rohit Chopra. During a Senate Banking Committee hearing, McKernan stated that Chopra \"was onto something\" with his policies targeting data brokers and data aggregators, citing privacy and national security concerns. McKernan also committed to implementing a policy to protect the security of confidential information obtained by the CFPB and to reviewing the agency's data storage practices. His comments suggest that he may continue some of the CFPB's data-focused work, despite potential pushback from industry groups and",
        "title": "CFPB nominee signals openness to continuing data-broker work"
      },
      {
        "confidence": "0.8",
        "link": "https://cyberscoop.com/microsoft-generative-ai-azure-hacking-for-hire-amended-complaint/",
        "sentiment": "negative",
        "summary": "Microsoft has identified several individuals from Iran, China, Vietnam, and the UK as key players in a global cybercrime network that sold access to hacked generative AI tools. The network, known as Storm-2139, used stolen Microsoft API keys to sell access to accounts with Azure OpenAI, which were then used to generate harmful content, including images that violate safety guidelines. Microsoft has filed an amended complaint naming four individuals, including Arian Yadegarnia, Ricky Yuen, Phát Phùng Tấn, and Alan Krysiak, as key players in the scheme. The company is preparing criminal referrals to US and foreign law enforcement representatives.",
        "title": "Microsoft IDs developers behind alleged generative AI hacking-for-hire scheme"
      }
    ] });
  }
});

app.get("/scan", (req, res) => {
  res.render("scan");
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});

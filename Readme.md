# Tenser Satark

## Cybersecurity Email Analysis & Phishing Detection Platform

Tenser Satark is an advanced cybersecurity platform designed to protect organizations and individuals from phishing attacks through intelligent email analysis, machine learning-based threat detection, and comprehensive educational resources.

## 🛡️ Features

- **Advanced Email Analysis**: Analyze emails for phishing attempts using machine learning and header validation
- **Dashboard**: Visual representation of security incidents and threat analytics
- **Incident Management**: Track and manage detected phishing attempts and security incidents
- **Detailed Reports**: Comprehensive analysis reports with DKIM, SPF, and DMARC validation
- **AI-Powered Chatbot**: Get immediate security assistance and guidance
- **Security News**: Stay updated with the latest cybersecurity news and trends
- **URL & Domain Scanning**: Validate URLs and domains against known threats

## 🔧 Technology Stack

### Frontend
- **Framework**: Express.js with EJS templating
- **Authentication**: JWT (JSON Web Tokens)
- **UI**: Modern responsive design with interactive dashboards

### Backend
- **Python**: Core analysis and ML components
- **TensorFlow**: Machine learning for phishing detection
- **Groq API**: Enhanced AI-powered security analysis
- **Flask**: API endpoints (implied by the requirements)

## 📋 Project Structure

```
tenser_satark/
├── frontend/
│   ├── index.js            # Express server and route definitions
│   ├── package.json        # Frontend dependencies
│   └── views/              # EJS templates for UI
│       ├── dashboard.ejs   # Main dashboard view
│       ├── login.ejs       # Authentication view
│       ├── report.ejs      # Detailed report view
│       ├── chatbot.ejs     # Security chatbot interface
│       ├── blogs.ejs       # Security news and articles
│       ├── incidents.ejs   # Security incidents list
│       └── scan.ejs        # Email/URL scanning interface
│
├── backend/
│   ├── report_gen.py       # Email analysis and report generation
│   └── requirements.txt    # Python dependencies
```

## 🔍 Features in Detail

### Email Phishing Detection
- **Header Analysis**: Validates SPF, DKIM, and DMARC records
- **Content Analysis**: Uses LSTM model to detect phishing patterns
- **URL Validation**: Checks embedded URLs against known threats
- **AI Enhancement**: Uses Groq API for comprehensive threat analysis

### Incident Management
- Track all detected phishing attempts
- View detailed analysis of each incident
- Monitor trends and patterns in attacks

### Security Chatbot
- Get instant answers to security questions
- Learn about best practices
- Receive guidance on handling suspicious emails

### Security News Feed
- Stay updated with the latest cybersecurity threats
- Read articles on emerging attack vectors
- Learn about new defense strategies

## 📊 Machine Learning Models

Tenser Satark uses a sophisticated LSTM (Long Short-Term Memory) neural network model to detect phishing attempts in email content. The model analyzes:

- Linguistic patterns common in phishing emails
- Presence of urgency indicators
- Suspicious requests and formatting
- Hyperlink patterns and quantity

## 🔒 Security Considerations

- All API keys should be stored securely and never committed to version control
- The JWT secret should be strong and regularly rotated
- Enable HTTPS for production deployments
- Regularly update dependencies to patch security vulnerabilities

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Contributors


## 🙏 Acknowledgments

- TensorFlow team for the machine learning framework
- Groq for providing enhanced AI capabilities
- All open-source contributors whose libraries made this project possible
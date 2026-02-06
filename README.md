# 🔐 SAP SoD Risk Analysis - Web Application

## What is this?

A **web-based tool** for analyzing SAP Segregation of Duties violations. Works on **phones, tablets, and computers** - just open in your browser!

---

## ✨ Features

✅ **Drag & Drop File Upload** - No typing file paths  
✅ **Mobile Friendly** - Use on your phone  
✅ **Real-time Progress** - See analysis happening  
✅ **Interactive Charts** - Visual risk dashboards  
✅ **Instant Downloads** - Get Excel reports with one click  
✅ **No Installation Required** - Just a web browser  

---

## 🚀 Quick Start (2 minutes)

### Step 1: Install
```bash
pip install -r requirements.txt
```

### Step 2: Run
```bash
streamlit run app.py
```

### Step 3: Use
- Browser opens automatically at http://localhost:8501
- Upload rule book Excel file
- Upload user access Excel file
- Click "Run SoD Analysis"
- Download your reports!

---

## 📱 Use on Phone/Tablet

### Same WiFi Network:

1. On your computer, run:
   ```bash
   streamlit run app.py --server.address 0.0.0.0
   ```

2. Find your computer's IP address:
   - **Windows:** `ipconfig` in PowerShell
   - **Mac:** System Preferences → Network

3. On your phone browser, go to:
   ```
   http://YOUR_COMPUTER_IP:8501
   ```
   Example: http://192.168.1.100:8501

---

## 📊 What You Get

### Two Excel Reports:

1. **User-Level Violations**
   - Columns: USER_NAME, ROLE, TCODE_1, TCODE_2, RISK_FACTOR
   - Shows which users have conflicts

2. **Role-Level Violations**
   - Columns: ROLE, TCODE_1, TCODE_2, RISK_FACTOR
   - Shows which roles have conflicts

### Interactive Dashboards:
- Risk distribution pie charts
- Top 10 high-risk users
- Top 10 high-risk roles
- Risk level breakdowns

---

## 🌐 Deployment Options

### Option 1: Local (Easiest)
- Run on your laptop
- Access at http://localhost:8501
- **Best for:** Quick testing

### Option 2: Company Server (Recommended)
- Install on Windows/Linux server
- Everyone accesses via http://server-ip:8501
- **Best for:** Production use

### Option 3: Cloud (Azure/AWS)
- Host on cloud server
- Access from anywhere
- **Best for:** Remote teams

📖 See `DEPLOYMENT_GUIDE.md` for detailed instructions

---

## 🔧 Files Included

```
├── app.py                    # Main web application
├── requirements.txt          # Dependencies
├── DEPLOYMENT_GUIDE.md       # Deployment instructions
└── README.md                 # This file
```

---

## ❓ FAQ

**Q: Do I need to install SAP?**  
A: No! This is standalone.

**Q: Can I use this on my phone?**  
A: Yes! Works on any browser.

**Q: Is my data secure?**  
A: Data never leaves your server. Everything is processed locally.

**Q: What if the file is too large?**  
A: The app handles files with 500k+ rows efficiently.

**Q: Can multiple people use it at once?**  
A: Yes, when deployed on a server.

---

## 📞 Support

For deployment help, see `DEPLOYMENT_GUIDE.md`

For technical issues:
1. Check Python version (3.9+)
2. Reinstall dependencies: `pip install -r requirements.txt --upgrade`
3. Check firewall settings

---

## 🎯 Next Steps

1. ✅ Test locally on your computer
2. ✅ Test on your phone (same WiFi)
3. ✅ Deploy to company server
4. ✅ Train your team
5. ✅ Set up regular analysis schedule

---

**Made for SAP GRC Compliance Teams** 🔐

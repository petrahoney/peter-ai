\# PETER AI v4.0 - DEPLOYMENT CHECKLIST



\## PRE-DEPLOYMENT (Today - Phase 6 LIGHT)



\### 1. Environment Variables for Production

\- \[ ] Create `.env.production` with:

&#x20; - MONGO\_URL (Atlas production cluster)

&#x20; - SMTP\_SERVER, SMTP\_PORT, SENDER\_EMAIL, SENDER\_PASSWORD

&#x20; - ANTHROPIC\_API\_KEY (valid key)

&#x20; - JWT\_SECRET (strong, 32+ chars)

&#x20; - EMERGENT\_LLM\_KEY (if using)

&#x20; - SSL\_CERT\_PATH, SSL\_KEY\_PATH (after cert setup)



\### 2. Database Backup

\- \[ ] Backup current MongoDB data

\- \[ ] Test restoration procedure

\- \[ ] Create production indexes



\### 3. SSL/TLS Certificate (Let's Encrypt)

Status: ⏳ PENDING (tomorrow)


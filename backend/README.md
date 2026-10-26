# IIIT Ranchi - UP Scholarship Facilitation Portal

Portal designed by the **Scholarship Coordinator of IIIT Ranchi** to assist peers and juniors in form fill-up, managing academic records, and uploading the 9 mandatory UP Scholarship documents.

---

## 🚀 Completed Modules & Capabilities

### 1. User Authentication (`/login`, `/register`, `/me`)
- Student registration with full name, email validation, and secure password hashing (`argon2`).
- JWT-based authentication supporting both JSON and OAuth2 Form data.
- Session verification with `/me`.

### 2. Student Profile Management (`/profiles`)
- Academic and institutional record management:
  - College Registration / Roll Number
  - Department / Branch (CSE, ECE, DS & AI, Embedded Systems)
  - Current Semester
  - Aadhaar-linked Mobile Number
  - 10th & 12th Board Percentages
  - Annual Family Income (with instant UP Govt ceiling rule validation: ₹2.0 Lakhs for Gen/OBC/Minority, ₹2.5 Lakhs for SC/ST)
  - Semester Result / CGPA (Renewal applications)
- Upsert support (`POST /profiles` & `GET /profiles/me` & `PUT /profiles/me`).

### 3. Document Repository & Vault (`/documents`)
- Complete management for all 9 UP Scholarship document categories:
  1. `aadhaar_card` - 12-digit Aadhaar Card
  2. `tenth_marksheet` - High School Marksheet (Roll, Board, Year, Percentage)
  3. `twelfth_marksheet` - Intermediate Marksheet (Roll, Board, Year, Percentage)
  4. `income_certificate` - Income Certificate (Cert No, Issue Date, Income)
  5. `category_certificate` - Caste Certificate (for OBC, SC, ST)
  6. `domicile_certificate` - UP Domicile Certificate (Cert No, Issue Date, State)
  7. `bank_passbook` - Bank Passbook with NPCI Aadhaar DBT mapping
  8. `ration_card` - Ration Card / Family ID
  9. `profile_photo` - Passport Photo
- Private file storage backed by **Supabase Object Storage**.
- Secure signed download links (`GET /documents/{category}/file`).
- Document replacement and deletion.

### 4. Form Guidelines & Coordinator Notes
- 8-phase step-by-step form filling roadmap for `scholarship.up.gov.in`.
- IIIT Ranchi Institute Master info (Outside State Dashmottar Scheme).
- Common rejection causes (Aadhaar mismatch, unseeded bank account, expired income certificate).

---

## 🛠️ How to Run the Project

### Local setup from the repository root

Use the project virtual environment explicitly so `uvicorn` runs with the backend dependencies:

```powershell
py -3.12 -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
if (!(Test-Path backend\.env)) { Copy-Item backend\.env.example backend\.env }
backend\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
```

Set `DATABASE_URL` in `backend\.env` to a PostgreSQL database you intend to use. Supabase storage variables are optional locally; without them (or the Supabase package), files are stored under `backend\uploads`. See [CHATBOT_SETUP.md](./CHATBOT_SETUP.md) for local frontend setup and Render deployment configuration.

### Option A: Run Backend + Built Frontend on Port 8000 (Fastest)

#### From the repository root:

Use the virtual-environment command from the local setup section above.

#### Or From `backend` Directory:
1. From the backend folder, install the dependencies and activate its virtual environment:
   ```bash
   python -m pip install -r requirements.txt
   .\.venv\Scripts\activate
   ```
2. Start the FastAPI server with the same Python environment:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

3. Open your browser:
   - **Frontend App:** [http://localhost:8000](http://localhost:8000)
   - **Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Option B: Run React Frontend in Development Mode (Live Reload)

1. In Terminal 1 (Backend):
   ```bash
   .\backend\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
   ```
2. In Terminal 2 (Frontend):
   ```bash
   npm --prefix frontend run dev
   ```
3. Open [http://localhost:5173](http://localhost:5173).

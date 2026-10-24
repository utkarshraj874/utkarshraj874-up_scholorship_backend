<<<<<<< HEAD
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

### Option A: Run Backend + Built Frontend on Port 8000 (Fastest)

#### From Root Directory (`scholorship_ai`):
1. Activate virtual environment:
   ```bash
   .\myvenv\Scripts\activate
   ```
2. Start the FastAPI server:
   ```bash
   uvicorn backend.app.main:app --reload
   ```

#### Or From `backend` Directory:
1. Activate virtual environment:
   ```bash
   .\.venv\Scripts\activate
   # (or: ..\myvenv\Scripts\activate)
   ```
2. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

3. Open your browser:
   - **Frontend App:** [http://localhost:8000](http://localhost:8000)
   - **Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Option B: Run React Frontend in Development Mode (Live Reload)

1. In Terminal 1 (Backend):
   ```bash
   cd backend
   .\.venv\Scripts\activate
   uvicorn app.main:app --reload
   ```
2. In Terminal 2 (Frontend):
   ```bash
   cd frontend
   npm run dev
   ```
3. Open [http://localhost:5173](http://localhost:5173).

=======
# up_scholorship_backend
>>>>>>> 8689cbb8972bd2034b6cb052001baa33a1166233

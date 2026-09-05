"""Educational service providing the 25 Job Scam Red Flags matrix and Interactive Scam Hunter Simulator."""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class RedFlagItem(BaseModel):
    id: str
    number: int
    category: str
    title: str
    severity: str  # CRITICAL, HIGH, MEDIUM
    summary: str
    indicators: List[str]
    real_scam_snippet: str
    safety_protocol: str
    ftc_reference: Optional[str] = None


class SimulatorScenario(BaseModel):
    id: str
    title: str
    channel: str  # Email, SMS, Telegram, Job Board, LinkedIn
    sender: str
    difficulty: str  # Beginner, Intermediate, Expert
    body: str
    is_scam: bool
    verdict: str  # 'SCAM' or 'LEGITIMATE'
    red_flags: List[str]
    clue_phrases: List[str]
    forensic_explanation: str
    xp_reward: int = 100


# The Official 25 Job Scam Red Flags
RED_FLAGS_25: List[Dict[str, Any]] = [
    # Category 1: Financial & Payment Traps
    {
        "id": "rf-01",
        "number": 1,
        "category": "Financial & Payment Traps",
        "title": "Counterfeit Check / Home Office Equipment Scam",
        "severity": "CRITICAL",
        "summary": "Employer sends a fake cashier check to deposit into your personal account to 'purchase home office equipment' from their specific vendor.",
        "indicators": [
            "Employer mails/emails a check for $2,000–$5,000 before you start work",
            "Instructs you to wire or Zelle the balance to an 'approved vendor'",
            "Check bounces days later, leaving you liable for the entire amount"
        ],
        "real_scam_snippet": "We are mailing a cashier check of $3,800. Deposit it via mobile app and send $3,200 via Zelle to our certified IT hardware supplier for your MacBook setup.",
        "safety_protocol": "Never deposit checks from an employer to buy equipment. Legitimate organizations ship company-provisioned devices directly.",
        "ftc_reference": "FTC Consumer Advice: Fake Checks and Job Scams"
    },
    {
        "id": "rf-02",
        "number": 2,
        "category": "Financial & Payment Traps",
        "title": "Mandatory Upfront Payment for Training or Software",
        "severity": "CRITICAL",
        "summary": "Candidate is accepted for employment but required to pay upfront for background checks, onboarding modules, or proprietary software licenses.",
        "indicators": [
            "Requirement to pay an onboarding fee ($50–$300) before signing contract",
            "Claims fee will be reimbursed on your first paycheck",
            "Payment requested via crypto, gift cards, Cash App, or Venmo"
        ],
        "real_scam_snippet": "Your profile is accepted. To finalize onboarding, pay the $120 background check fee to our credential partner. You will receive 100% refund in your first pay period.",
        "safety_protocol": "Legitimate employers cover all pre-employment background check costs and software licensing. Never pay to get hired.",
        "ftc_reference": "FTC Advice: Job Scams & Upfront Fees"
    },
    {
        "id": "rf-03",
        "number": 3,
        "category": "Financial & Payment Traps",
        "title": "Cryptocurrency / Task Optimization Payout Schemes",
        "severity": "CRITICAL",
        "summary": "Promised high daily pay ($200-$600/day) for clicking app reviews, liking products, or placing crypto arbitrage orders on a fake portal.",
        "indicators": [
            "Daily commissions promised for clicking buttons for 30-45 minutes",
            "Initial micro-payout given, followed by demands to deposit USDT to unlock higher tier tasks",
            "Virtual balance shown on scam portal cannot be withdrawn"
        ],
        "real_scam_snippet": "Earn $300-$500 daily helping boost merchant store rankings on our cloud platform. Deposit 100 USDT to reset your commission pipeline.",
        "safety_protocol": "No legitimate job requires depositing crypto or personal funds to earn wages or unlock commissions. Disconnect immediately.",
        "ftc_reference": "FBI IC3 Alert: Task Scams and Fake Job Platforms"
    },
    {
        "id": "rf-04",
        "number": 4,
        "category": "Financial & Payment Traps",
        "title": "Package Reshipping & Money Mule Operations",
        "severity": "CRITICAL",
        "summary": "Hired as a 'Quality Inspector' or 'Package Logistics Manager' to receive stolen goods or funds and forward them overseas.",
        "indicators": [
            "Job requires receiving packages at home, repacking, and shipping them",
            "Recruiter asks you to receive wire transfers and buy crypto/gift cards",
            "Candidate unwittingly participates in interstate criminal laundering"
        ],
        "real_scam_snippet": "As our Remote Logistics Assistant, receive merchant test parcels at your residence, inspect packaging, and apply provided prepaid labels to forward internationally.",
        "safety_protocol": "Never accept or forward packages from unknown individuals or forward funds through your personal bank.",
        "ftc_reference": "US Postal Inspection Service: Reshipping Fraud"
    },
    {
        "id": "rf-05",
        "number": 5,
        "category": "Financial & Payment Traps",
        "title": "Unusual Payment Methods (Crypto, Wire, Gift Cards)",
        "severity": "HIGH",
        "summary": "Recruiter insists on paying sign-on bonuses or receiving fees through irreversible channels.",
        "indicators": [
            "Salaries offered via Bitcoin, USDT, or reloadable gift cards",
            "Refusal to use standard payroll (ADP, Gusto, Direct Deposit ACH)",
            "Requests for candidate's crypto wallet address as primary payroll"
        ],
        "real_scam_snippet": "We disburse sign-on bonuses via USDT (TRC-20) or Apple Gift Cards for instant tax-free processing. Provide your wallet address.",
        "safety_protocol": "Authentic corporate payroll utilizes standard W-2 / 1099 direct deposit with standard tax withholdings.",
        "ftc_reference": "FTC Guide: Scammers Demand Gift Cards and Crypto"
    },

    # Category 2: Communication & Contact Channels
    {
        "id": "rf-06",
        "number": 6,
        "category": "Communication & Contact Channels",
        "title": "Strictly Telegram, WhatsApp, or Signal Recruitment",
        "severity": "CRITICAL",
        "summary": "Recruiter insists on conducting all communications and interviews over encrypted chat apps without corporate video or phone calls.",
        "indicators": [
            "Recruiter directs you to download Telegram/WhatsApp to message the 'Hiring Manager'",
            "Refusal to provide a company phone number or conduct a Zoom/Teams interview",
            "Recruiter username contains random alphanumeric strings"
        ],
        "real_scam_snippet": "Your resume was reviewed. Please download Telegram and add our HR Director @HR_Recruitment_Lead_US to conduct your text interview.",
        "safety_protocol": "Legitimate enterprise hiring managers schedule formal video or phone interviews through verified corporate calendar links.",
        "ftc_reference": "BBB Scam Alert: Telegram Recruitment Traps"
    },
    {
        "id": "rf-07",
        "number": 7,
        "category": "Communication & Contact Channels",
        "title": "Free Webmail Addresses Claiming Corporate Affiliation",
        "severity": "HIGH",
        "summary": "Recruiter claims to represent a Fortune 500 company but emails from @gmail.com, @yahoo.com, @outlook.com, or @hotmail.com.",
        "indicators": [
            "Email sender address ends in @gmail.com (e.g. google.hiringteam2026@gmail.com)",
            "Explanation that corporate email server is 'under maintenance'",
            "Display name mimics the executive name while actual address is public webmail"
        ],
        "real_scam_snippet": "Hello, I am Sarah Davis, VP of Talent at Microsoft. Our server is migrating so please reply to microsoft.talentacquisition.team@gmail.com.",
        "safety_protocol": "Enterprise recruiters always email from authenticated corporate domain names matching the company's primary website.",
        "ftc_reference": "CISA Phishing Guidance: Free Webmail Impersonation"
    },
    {
        "id": "rf-08",
        "number": 8,
        "category": "Communication & Contact Channels",
        "title": "Lookalike / Typo-Squatted Domains",
        "severity": "HIGH",
        "summary": "Sender uses slight variations of real company domains (e.g. @deloitte-careers-portal.com or @apple-jobs-usa.org).",
        "indicators": [
            "Domain has extra words like '-jobs', '-careers', '-hr', or '-us'",
            "Domain registration WHOIS shows creation date less than 30–90 days ago",
            "Website replicates official branding with slight URL discrepancies"
        ],
        "real_scam_snippet": "Please submit your verification via our official employee portal at https://careers-amazon-global-onboarding.com/verify",
        "safety_protocol": "Inspect the root domain carefully before clicking. Check domain age on WHOIS and apply exclusively through the primary domain.",
        "ftc_reference": "FBI IC3 Alert: Spoofed Domain Names Used in Cybercrime"
    },
    {
        "id": "rf-09",
        "number": 9,
        "category": "Communication & Contact Channels",
        "title": "Unsolicited Job Offer via SMS or iMessage",
        "severity": "HIGH",
        "summary": "Receiving an unexpected text message offering employment for a job you never applied to, from an unknown phone number.",
        "indicators": [
            "Text claims 'We saw your profile on Indeed/LinkedIn' with no job reference ID",
            "Urgent call-to-action asking you to reply 'YES' or click a shortlink",
            "Phone line originates from a temporary VoIP carrier (e.g. TextNow, Bandwidth)"
        ],
        "real_scam_snippet": "Hi! We found your resume on Indeed. You are selected for our Remote Data Specialist position ($45/hr). Reply YES to connect with HR.",
        "safety_protocol": "Do not reply to unsolicited hiring SMS. Verified recruiters reach out through InMail on LinkedIn or official corporate email.",
        "ftc_reference": "FCC Guide: Robotexts and Job Offer SMS Phishing"
    },
    {
        "id": "rf-10",
        "number": 10,
        "category": "Communication & Contact Channels",
        "title": "Extreme Urgency & 24-Hour Expiration Pressure",
        "severity": "MEDIUM",
        "summary": "Recruiter exerts aggressive psychological pressure, giving 12–24 hours to sign or pay before the offer is 'permanently revoked'.",
        "indicators": [
            "Offer expires in 12–24 hours with no time allowed for review",
            "Aggressive follow-up messages demanding immediate execution",
            "Attempts to rush candidate past standard diligence checks"
        ],
        "real_scam_snippet": "Congratulations! You must sign this contract and transfer the onboarding fee within 12 hours or your candidate slot will be given away.",
        "safety_protocol": "Legitimate companies provide 3–7 business days to review employment contracts and discuss terms.",
        "ftc_reference": "FTC: Spotting Urgency Red Flags in Phishing"
    },

    # Category 3: Interview & Hiring Process
    {
        "id": "rf-11",
        "number": 11,
        "category": "Interview & Hiring Process",
        "title": "Instant Job Offer Without an Interview",
        "severity": "CRITICAL",
        "summary": "Candidate receives a formal job offer letter within hours of submitting a resume, without any phone or live video evaluation.",
        "indicators": [
            "Offer extended without any live conversation with a manager",
            "High salary offered for entry-level work immediately upon application",
            "No technical assessment, reference check, or portfolio review"
        ],
        "real_scam_snippet": "After reviewing your resume on LinkedIn, our board has decided to offer you the position of Senior Data Entry Analyst at $52/hr. Please sign the attached contract.",
        "safety_protocol": "Real companies always conduct multiple rounds of live interviews (technical, behavioral, hiring manager) before extending offers.",
        "ftc_reference": "BBB Scam Tracker: Instant Job Offer Warnings"
    },
    {
        "id": "rf-12",
        "number": 12,
        "category": "Interview & Hiring Process",
        "title": "Text-Only / Questionnaire 'Interviews'",
        "severity": "HIGH",
        "summary": "The entire 'interview' consists of filling out a Google Doc, Microsoft Form, or answering questions in a Telegram chat.",
        "indicators": [
            "No voice or video interaction throughout the hiring pipeline",
            "10 generic interview questions answered via text or document upload",
            "Immediate acceptance notification minutes after submitting the form"
        ],
        "real_scam_snippet": "Please answer these 8 screening questions via Microsoft Word and send them back. Our board will evaluate your responses and issue your offer letter.",
        "safety_protocol": "Legitimate corporate hiring requires interactive video (Zoom, Google Meet, Teams) or in-person technical interviews.",
        "ftc_reference": "FTC: How Scammers Fake the Job Interview Process"
    },
    {
        "id": "rf-13",
        "number": 13,
        "category": "Interview & Hiring Process",
        "title": "Camera-Off or Pre-Recorded Video 'Interviews'",
        "severity": "HIGH",
        "summary": "Recruiter refuses to turn on their camera during a video call or uses AI deepfake voice/avatars.",
        "indicators": [
            "Interviewer claims their camera is broken during the interview",
            "Voice sounds robotic or has noticeable synthetic latency",
            "Interview conducted on non-standard obscure video platforms"
        ],
        "real_scam_snippet": "I cannot turn on my webcam due to company security protocols. Please keep your camera on and follow my instructions.",
        "safety_protocol": "Authentic hiring managers appear on live video with verified corporate credentials. Never proceed with suspicious camera-off requests.",
        "ftc_reference": "FBI IC3 Alert: Deepfakes in Remote Worker Recruitment"
    },
    {
        "id": "rf-14",
        "number": 14,
        "category": "Interview & Hiring Process",
        "title": "No Job Listing on the Official Careers Page",
        "severity": "HIGH",
        "summary": "Recruiter contacts you about a specific requisition ID that does not exist anywhere on the company's official careers portal.",
        "indicators": [
            "Job requisition ID is missing from the company's Workday/Greenhouse ATS",
            "Company HR confirms no such position is currently open",
            "Job details contradict the company's actual business domain"
        ],
        "real_scam_snippet": "This is an unlisted stealth position for our executive data analytics division. Do not apply through the public careers website.",
        "safety_protocol": "Always search the company's official domain (`/careers` or `/jobs`) or contact official HR directly before engaging.",
        "ftc_reference": "CISA Cybersecurity: Recruitment Impersonation Verifications"
    },
    {
        "id": "rf-15",
        "number": 15,
        "category": "Interview & Hiring Process",
        "title": "Generic, Vague, or Missing Job Responsibilities",
        "severity": "MEDIUM",
        "summary": "Job description contains vague buzzwords without detailing daily deliverables, tools, team structure, or required technical background.",
        "indicators": [
            "Vague duties such as 'Assist in general clerical duties' or 'Manage digital files'",
            "Claims 'No experience needed' while offering six-figure executive pay",
            "Copy-pasted text from multiple unrelated online postings"
        ],
        "real_scam_snippet": "We need enthusiastic remote workers to perform daily administrative duties, process documents, and support our team. No experience needed.",
        "safety_protocol": "Authentic job descriptions detail clear day-to-day responsibilities, required qualifications, key metrics, and reporting hierarchy.",
        "ftc_reference": "FTC: Identifying Vague Deceptive Job Postings"
    },

    # Category 4: Identity Theft & Privacy Extraction
    {
        "id": "rf-16",
        "number": 16,
        "category": "Identity Theft & Privacy Extraction",
        "title": "Premature Social Security Number (SSN) Demands",
        "severity": "CRITICAL",
        "summary": "Application form or recruiter demands your full SSN, Tax ID, or National ID before any formal interview or signed contract.",
        "indicators": [
            "SSN required on an initial screening Google Form or preliminary questionnaire",
            "Threats to reject your application if SSN is omitted",
            "Forms hosted on third-party non-enterprise websites (e.g. formspree, docs.google.com)"
        ],
        "real_scam_snippet": "To proceed with scheduling your interview, please complete this Google Form with your full legal name, SSN, and date of birth.",
        "safety_protocol": "Never provide your SSN on preliminary application forms. SSN is only submitted during official post-hire W-4 onboarding on secure ATS.",
        "ftc_reference": "FTC Guide: Protecting Your SSN from Job Scams"
    },
    {
        "id": "rf-17",
        "number": 17,
        "category": "Identity Theft & Privacy Extraction",
        "title": "Demanding Direct Deposit Banking Details Before Offer",
        "severity": "CRITICAL",
        "summary": "Scammer asks for your voided check, bank routing number, and account number during the initial interview phase.",
        "indicators": [
            "Bank details requested before formal offer letter is signed",
            "Claims bank info is required to 'verify creditworthiness' or 'setup direct payroll'",
            "Used to execute unauthorized ACH withdrawals or open credit lines"
        ],
        "real_scam_snippet": "Please upload a photo of your voided check and bank statement so our finance team can verify your payroll eligibility before the interview.",
        "safety_protocol": "Direct deposit information is only shared after you sign a verified offer letter and access an enterprise HR portal (e.g. ADP, Workday).",
        "ftc_reference": "Consumer Financial Protection Bureau: ACH Fraud in Job Scams"
    },
    {
        "id": "rf-18",
        "number": 18,
        "category": "Identity Theft & Privacy Extraction",
        "title": "Passport & Driver's License Photos on Unsecured Channels",
        "severity": "HIGH",
        "summary": "Recruiter requests high-resolution front/back scans of your government ID sent via email, WhatsApp, or Telegram.",
        "indicators": [
            "Demands driver's license or passport scan before formal onboarding",
            "Requests selfies holding your ID card (KYC identity theft vector)",
            "Stolen IDs are reused by scammers to impersonate other victims"
        ],
        "real_scam_snippet": "Please send a clear photo of your driver's license and a selfie holding your ID to our Telegram handle for ID verification.",
        "safety_protocol": "Only upload identity verification documents to encrypted enterprise I-9 compliance platforms (e.g. Workday, Checkr).",
        "ftc_reference": "FTC Alert: Identity Theft via Stolen KYC Documents"
    },
    {
        "id": "rf-19",
        "number": 19,
        "category": "Identity Theft & Privacy Extraction",
        "title": "Credit Score Check Links via Unknown Affiliate Sites",
        "severity": "HIGH",
        "summary": "Candidate is directed to click a link to run a 'mandatory free credit check' that steals credentials or signs you up for recurring subscription charges.",
        "indicators": [
            "Requirement to run a credit score check on a specific unknown URL",
            "Link redirects to high-risk affiliate subscription billing portals",
            "Recruiter earns affiliate commission or steals credit card numbers"
        ],
        "real_scam_snippet": "Our hiring policy requires a minimum 650 credit score. Please verify your score at http://free-credit-score-applicant.com and send the report.",
        "safety_protocol": "Legitimate employers run background/credit checks through accredited FCRA-compliant screening partners at zero cost to the candidate.",
        "ftc_reference": "FTC: Free Credit Report Job Scams"
    },
    {
        "id": "rf-20",
        "number": 20,
        "category": "Identity Theft & Privacy Extraction",
        "title": "2FA Code Interception / Account Takeover Requests",
        "severity": "CRITICAL",
        "summary": "Scammer triggers a password reset on your Google, Apple, or Bank account and asks you to send them the 6-digit verification code.",
        "indicators": [
            "Recruiter asks: 'I just sent a verification code to your phone to confirm your identity, what is the 6-digit number?'",
            "Received SMS code is actually a 2-factor authentication login code",
            "Immediate account takeover upon sharing the code"
        ],
        "real_scam_snippet": "We sent a 6-digit Google code to verify your phone number on our candidate registry. Please text it back to me immediately.",
        "safety_protocol": "Never share 2FA/OTP verification codes with anyone under any circumstances. Codes are strictly private.",
        "ftc_reference": "FTC Advice: Never Share Your Verification Code"
    },

    # Category 5: Role & Company Credibility
    {
        "id": "rf-21",
        "number": 21,
        "category": "Role & Company Credibility",
        "title": "Unrealistically High Compensation for Low-Skill Work",
        "severity": "HIGH",
        "summary": "Entry-level roles like simple data entry, typing, or customer support offering $45–$90/hour with zero prerequisites.",
        "indicators": [
            "Data entry / typing jobs paying $45–$80 per hour",
            "Guaranteed 40 hours/week remote with complete schedule flexibility",
            "Pay rate is 3x–5x the national median for the role"
        ],
        "real_scam_snippet": "Urgent need for Remote Data Entry Clerks. Earn $55.00/hr, flexible 20-40 hours weekly, complete benefits package from day one.",
        "safety_protocol": "Compare offered wages against salary benchmark platforms like Levels.fyi, Glassdoor, and Bureau of Labor Statistics data.",
        "ftc_reference": "BLS & FTC: Realistic Wage Benchmarks in Fraud Detection"
    },
    {
        "id": "rf-22",
        "number": 22,
        "category": "Role & Company Credibility",
        "title": "Zero Recruiter Footprint on LinkedIn",
        "severity": "MEDIUM",
        "summary": "The person claiming to be the HR Director or Recruiter has no LinkedIn profile, or a profile created within the last 30 days with < 10 connections.",
        "indicators": [
            "Recruiter profile has an AI-generated stock portrait (ThisPersonDoesNotExist)",
            "Account has less than 10 connections and zero work endorsements",
            "Recruiter is not listed as an employee under the company's verified LinkedIn page"
        ],
        "real_scam_snippet": "I am David Vance, Chief Talent Executive. You can verify my identity through our company website.",
        "safety_protocol": "Cross-reference the recruiter's name against the company's verified LinkedIn employee directory.",
        "ftc_reference": "LinkedIn Safety: Spotting Fake Recruiter Profiles"
    },
    {
        "id": "rf-23",
        "number": 23,
        "category": "Role & Company Credibility",
        "title": "Newly Registered Domain (< 90 Days Old)",
        "severity": "HIGH",
        "summary": "The employer's website or email domain was registered only days or weeks ago, despite claiming to be an established corporation.",
        "indicators": [
            "WHOIS registration date is within the last 1–3 months",
            "Registrant details hidden behind anonymous privacy proxies",
            "Website has broken social media links that lead to '#' or template pages"
        ],
        "real_scam_snippet": "Explore our 15-year history of excellence on our portal: https://meta-digital-cloud-careers.com",
        "safety_protocol": "Inspect domain creation dates using WHOIS lookups. Established enterprises possess domains registered 5–25 years ago.",
        "ftc_reference": "ICANN & CISA: Identifying Fraudulent New Domains"
    },
    {
        "id": "rf-24",
        "number": 24,
        "category": "Role & Company Credibility",
        "title": "Non-Existent or Residential Corporate Address",
        "severity": "MEDIUM",
        "summary": "The company's listed headquarters address is a residential house, vacant lot, UPS mailbox store, or virtual office.",
        "indicators": [
            "Google Maps Street View shows a single-family home or strip mall mailbox",
            "No state business registration or SEC filings found under the company name",
            "Address listed in a completely different country from claimed operations"
        ],
        "real_scam_snippet": "Our corporate headquarters is located at 1244 Postal Way, Suite #402, Wilmington, DE (UPS Store).",
        "safety_protocol": "Verify the company's physical address via Google Maps Street View and cross-check official state Secretary of State corporate registry databases.",
        "ftc_reference": "BBB: Checking Business Physical Verification"
    },
    {
        "id": "rf-25",
        "number": 25,
        "category": "Role & Company Credibility",
        "title": "Severe Grammar, Inconsistent Branding & Formatting Errors",
        "severity": "MEDIUM",
        "summary": "Official offer letters and correspondence contain glaring spelling mistakes, mixed fonts, pixelated logos, and ungrammatical English.",
        "indicators": [
            "Distorted or pixelated corporate logos pasted onto generic Word documents",
            "Odd capitalization and phrases like 'Kindly respond back soonest'",
            "Legal disclaimer sections copied verbatim from unrelated companies"
        ],
        "real_scam_snippet": "Dear Applicant, Warm Greetings! Kindly furnish us with your details soonest so our hiring team can do the needful regarding your appointment.",
        "safety_protocol": "Legitimate enterprise communications maintain strict corporate styling, consistent typography, and standard professional legal language.",
        "ftc_reference": "FTC: Warning Signs in Phishing and Fraud Letters"
    }
]


# Interactive Simulator Scenarios (Spot the Scam Training Game)
SIMULATOR_SCENARIOS: List[Dict[str, Any]] = [
    {
        "id": "sim-01",
        "title": "Remote Data Specialist Offer",
        "channel": "Email",
        "sender": "sarah.hr.recruiter.google@gmail.com",
        "difficulty": "Beginner",
        "body": """Subject: Formal Job Offer: Remote Data Specialist ($58.50/hr) - Google LLC

Dear Candidate,

After reviewing your resume on Indeed, our executive hiring committee was thoroughly impressed with your profile. We are pleased to offer you the position of Remote Data Specialist at Google.

Compensation & Benefits:
- Hourly Rate: $58.50/hour (Paid weekly via Direct Deposit)
- Flexible Hours: 25-40 hours/week
- Full Health, Dental, and 401(k) matching from Day 1

Next Steps:
To finalize your employee onboarding file and dispatch your company-provisioned Apple iMac workstation, please download Telegram and message our Senior Talent Director @Google_Talent_Lead_Sarah immediately to complete your 15-minute text verification.

Welcome to the team!

Best Regards,
Sarah Jenkins
Head of Remote Talent Acquisition, Google LLC""",
        "is_scam": True,
        "verdict": "SCAM",
        "red_flags": [
            "Free Webmail (@gmail.com) claiming to represent Google LLC",
            "Instant job offer with no prior interview or technical screening",
            "Direction to download Telegram to message recruiter @Google_Talent_Lead_Sarah",
            "Unrealistically high hourly wage ($58.50/hr) for entry data role"
        ],
        "clue_phrases": [
            "sarah.hr.recruiter.google@gmail.com",
            "$58.50/hour",
            "download Telegram and message our Senior Talent Director",
            "@Google_Talent_Lead_Sarah"
        ],
        "forensic_explanation": "This email demonstrates multiple critical scam signatures: (1) An alleged Google recruiter using a free @gmail.com address, (2) Offering employment with zero live interview, and (3) Demanding you communicate on Telegram. Google recruiters only use @google.com email and never conduct hiring via Telegram.",
        "xp_reward": 100
    },
    {
        "id": "sim-02",
        "title": "Home Equipment Check Dispatch",
        "channel": "Email",
        "sender": "hr-operations@novartis-pharma-us.com",
        "difficulty": "Intermediate",
        "body": """Subject: Welcome to Novartis - Home Office Equipment Check Instructions

Dear Alex,

Congratulations on accepting the Junior Clinical Data Coordinator role at Novartis.

As discussed in your questionnaire, you will require specialized office equipment including a high-speed scanner, Apple MacBook Pro 16", and encrypted VPN gateway.

Our finance department has dispatched a certified cashier check for $4,250.00 to your address via FedEx (Tracking: 789421039821).

Instructions:
1. Deposit the check via your mobile banking app immediately upon delivery.
2. Once the funds reflect in your account balance, wire $3,650.00 via Zelle to our authorized IT vendor (orders@precision-tech-supplies.net) to release your equipment batch.
3. The remaining $600.00 is your sign-on stipend.

Kindly confirm receipt of these instructions.

Sincerely,
Dr. Marcus Weber
Director of People Operations, Novartis US""",
        "is_scam": True,
        "verdict": "SCAM",
        "red_flags": [
            "Counterfeit cashier check dispatched for home office equipment",
            "Instruction to Zelle $3,650 to an 'approved IT vendor'",
            "Check deposited into personal account will bounce days later leaving victim liable",
            "Lookalike domain novartis-pharma-us.com"
        ],
        "clue_phrases": [
            "dispatched a certified cashier check for $4,250.00",
            "wire $3,650.00 via Zelle to our authorized IT vendor",
            "novartis-pharma-us.com"
        ],
        "forensic_explanation": "Classic Fake Check scam! The fraudster sends a counterfeit cashier check, instructs you to deposit it, and orders you to send real money to a fake 'vendor'. When the check bounces 3-5 days later, your bank holds you responsible for the full $3,650. Real enterprises ship laptops directly through corporate IT.",
        "xp_reward": 150
    },
    {
        "id": "sim-03",
        "title": "Stripe Staff Software Engineer Screening",
        "channel": "Email",
        "sender": "elena.rostova@stripe.com",
        "difficulty": "Intermediate",
        "body": """Subject: Stripe Technical Interview: Staff Infrastructure Engineer

Hi Diwakar,

Thank you for speaking with our recruiting coordinator last Tuesday regarding the Staff Infrastructure Engineer position on our Core Payments Reliability team.

We would like to invite you to our 60-minute technical architecture round with our engineering manager, David Chen.

Interview Details:
- Format: 60-minute Google Meet video session (Camera ON required)
- Technical Focus: Distributed systems design, fault tolerance, and idempotency
- Coding Environment: CoderPad link will be provided in the calendar invite

Please select a 60-minute window that suits your schedule using our official candidate portal:
https://boards.greenhouse.io/stripe/interviews/schedule/st-90214

If you need any accessibility accommodations or have scheduling questions, feel free to reply directly to this email or contact me on LinkedIn.

Best regards,
Elena Rostova
Senior Technical Recruiter | Stripe Core Engineering
LinkedIn: linkedin.com/in/elena-rostova-stripe""",
        "is_scam": False,
        "verdict": "LEGITIMATE",
        "red_flags": [],
        "clue_phrases": [
            "elena.rostova@stripe.com",
            "boards.greenhouse.io/stripe",
            "Google Meet video session",
            "CoderPad"
        ],
        "forensic_explanation": "This is a 100% legitimate recruitment communication: (1) Sent from verified authenticated corporate domain @stripe.com, (2) References standard ATS scheduling portal (greenhouse.io), (3) Schedules live video interview with camera on, (4) Involves no premature requests for SSN, fees, or checks.",
        "xp_reward": 120
    },
    {
        "id": "sim-04",
        "title": "Telegram App Review Task Scam",
        "channel": "SMS",
        "sender": "+1 (312) 847-2910 [TextNow VoIP]",
        "difficulty": "Beginner",
        "body": """[SMS] Hi! This is Emily from Global Digital Media Group. We saw your resume on ZipRecruiter. We have urgent openings for Remote App Optimization Specialists. 

Work 30-45 mins a day rating mobile apps on Google Play/App Store. Daily commission is $250 - $480 paid daily via USDT or Direct Wire. 

No experience required! Must be 21+ years old. 

Click here to start training with our supervisor on Telegram: https://t.me/GlobalMedia_Emily_Task""",
        "is_scam": True,
        "verdict": "SCAM",
        "red_flags": [
            "Task scam promising $250-$480/day for 30 minutes of app rating",
            "Originating from disposable VoIP carrier via unsolicited SMS",
            "Direction to Telegram channel https://t.me/GlobalMedia_Emily_Task",
            "USDT cryptocurrency payout scheme"
        ],
        "clue_phrases": [
            "Work 30-45 mins a day rating mobile apps",
            "Daily commission is $250 - $480 paid daily via USDT",
            "https://t.me/GlobalMedia_Emily_Task"
        ],
        "forensic_explanation": "This is a high-danger Task Scam. Scammers lure candidates with claims of high daily pay for simple repetitive clicks. Victims are given a small initial payout to build confidence, then locked into depositing thousands in crypto to 'unlock VIP commission tasks'.",
        "xp_reward": 100
    },
    {
        "id": "sim-05",
        "title": "Onboarding Form Demanding Full SSN & ID Selfie",
        "channel": "Email",
        "sender": "hiring@anthem-health-careers.net",
        "difficulty": "Intermediate",
        "body": """Subject: Anthem Health - Pre-Interview Candidate Registration Form

Dear Applicant,

Thank you for your interest in the Medical Records Processing position at Anthem Blue Cross.

Due to strict HIPAA compliance and federal health guidelines, all prospective interviewees must undergo preliminary background screening prior to receiving an interview slot.

Please complete our secure Google Form within 24 hours:
https://forms.gle/xK98jLmQ812AnthMed

Required Information on Form:
1. Full Legal Name & Date of Birth
2. Full 9-Digit Social Security Number
3. Clear front/back photo of Driver's License
4. Selfie holding your Driver's License next to your face
5. Voided check for preliminary direct deposit setup

Failure to submit within 24 hours will result in automatic disqualification.

Anthem Talent Team""",
        "is_scam": True,
        "verdict": "SCAM",
        "red_flags": [
            "Demanding full 9-digit SSN and banking info before scheduling an interview",
            "Demanding ID selfie (KYC identity theft vector)",
            "Hosted on unverified public Google Forms (forms.gle) rather than secure HR portal",
            "Artificial 24-hour urgency pressure",
            "Lookalike domain anthem-health-careers.net"
        ],
        "clue_phrases": [
            "Full 9-Digit Social Security Number",
            "Selfie holding your Driver's License",
            "https://forms.gle/xK98jLmQ812AnthMed",
            "Voided check for preliminary direct deposit",
            "within 24 hours"
        ],
        "forensic_explanation": "Severe Identity Theft trap! Scammers use free Google Forms to harvest complete identity profiles (SSN, ID selfies, banking details). Once harvested, they open fraudulent credit cards and loan accounts in your name. Real healthcare companies never collect SSN on Google Forms.",
        "xp_reward": 150
    },
    {
        "id": "sim-06",
        "title": "Amazon Corporate SDE II Recruiter Reachout",
        "channel": "LinkedIn",
        "sender": "Marcus Brody (Amazon Senior Technical Recruiter)",
        "difficulty": "Advanced",
        "body": """Hi Diwakar,

I came across your GitHub profile and experience with distributed backend architectures and Python/FastAPI microservices.

Our AWS S3 Storage Reliability team in Seattle/Virtual is actively expanding, and your technical background aligns closely with an open SDE II role we are hiring for (Req ID: 2589140).

Would you be open to an exploratory 20-minute conversation this week? If interested, you can check out the official job requisition directly on Amazon Jobs:
https://www.amazon.jobs/en/jobs/2589140/software-development-engineer-ii-aws

No preparation needed for the initial chat—just want to share more about our roadmaps and see if there's a mutual fit.

Best,
Marcus Brody
LinkedIn Recruiter Verified Profile
Amazon Web Services""",
        "is_scam": False,
        "verdict": "LEGITIMATE",
        "red_flags": [],
        "clue_phrases": [
            "https://www.amazon.jobs/en/jobs/2589140",
            "AWS S3 Storage Reliability",
            "Req ID: 2589140"
        ],
        "forensic_explanation": "Legitimate technical recruiter outreach: (1) Links directly to the official amazon.jobs requisition URL, (2) Details specific technical domain matching recipient, (3) Proposes exploratory conversation without asking for private data, payments, or Telegram routing.",
        "xp_reward": 130
    },
    {
        "id": "sim-07",
        "title": "Paid Certification / Background Check Link",
        "channel": "Email",
        "sender": "onboarding@kaiser-permanente-talent.com",
        "difficulty": "Intermediate",
        "body": """Subject: Final Step: Mandatory HIPAA Certification Verification for Kaiser Permanente

Dear Applicant,

We are delighted to confirm that your application for the Remote Patient Care Coordinator role has been approved by the hiring board.

Before our legal team can release your $38.00/hr contract, state healthcare regulation requires you to obtain the 2026 Telehealth & HIPAA Compliance Certification ($79.00).

Please visit our certified training partner portal to complete the test:
https://telehealth-cert-verification-portal.com/kaiser-auth

Once you pay and complete the 20-minute module, upload your certificate receipt to this email thread. The $79.00 fee will be 100% reimbursed on your first paycheck.

Kaiser Permanente Human Resources""",
        "is_scam": True,
        "verdict": "SCAM",
        "red_flags": [
            "Demanding candidate pay upfront $79 fee for mandatory certification",
            "Promise that fee will be reimbursed on first paycheck",
            "Directs to third-party affiliate payment portal",
            "Lookalike domain kaiser-permanente-talent.com"
        ],
        "clue_phrases": [
            "obtain the 2026 Telehealth & HIPAA Compliance Certification ($79.00)",
            "https://telehealth-cert-verification-portal.com",
            "fee will be 100% reimbursed on your first paycheck"
        ],
        "forensic_explanation": "Advance-Fee Training Scam: Scammers invent mandatory certifications or background check fees, routing you to their affiliate payment portal. Once you pay the $79, the recruiter disappears. Legitimate employers pay 100% of candidate onboarding and compliance certification costs.",
        "xp_reward": 140
    },
    {
        "id": "sim-08",
        "title": "Urgent Package Inspection & Reshipping Role",
        "channel": "Email",
        "sender": "contact@apex-logistics-us.com",
        "difficulty": "Beginner",
        "body": """Subject: Immediate Hire: Remote Quality & Package Forwarding Assistant

Dear Job Seeker,

Apex Global Logistics is hiring Remote Quality Assurance Package Inspectors.

Job Duties:
1. Receive incoming parcels (electronics, designer goods, consumer goods) at your home address.
2. Open parcels, inspect contents for damage, and take high-resolution photographs.
3. Repackage items using pre-paid international shipping labels provided by our portal.
4. Drop off packages at your local UPS or FedEx store within 24 hours.

Compensation:
- Base Salary: $3,200/month + $40 bonus per package shipped
- Payout: Bi-weekly via Zelle, PayPal, or Wire Transfer
- Flexible 10-15 hours/week from home

Reply with your full shipping address to receive your first test shipment tomorrow!

Apex Logistics Dispatch Team""",
        "is_scam": True,
        "verdict": "SCAM",
        "red_flags": [
            "Reshipping Scam / Money & Goods Mule operation",
            "Receiving packages purchased with stolen credit cards at personal residence",
            "Candidate faces criminal liability for possession of stolen property",
            "Unrealistic pay ($3,200/mo + $40/package) for repackaging boxes"
        ],
        "clue_phrases": [
            "Receive incoming parcels (electronics, designer goods) at your home address",
            "Repackage items using pre-paid international shipping labels",
            "$3,200/month + $40 bonus per package shipped"
        ],
        "forensic_explanation": "Severe Reshipping Mule Scam. Fraudsters purchase electronics using stolen credit card numbers and ship them to the victim's house. The victim forwards the stolen items overseas, leaving their home address on file with law enforcement when credit card fraud investigations launch.",
        "xp_reward": 150
    }
]


class EducationalService:
    @staticmethod
    def get_red_flags(category: Optional[str] = None, search: Optional[str] = None, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """Filter and return the 25 Job Scam Red Flags."""
        results = RED_FLAGS_25
        if category and category.lower() != 'all':
            results = [rf for rf in results if category.lower() in rf["category"].lower()]
        if severity and severity.upper() != 'ALL':
            results = [rf for rf in results if rf["severity"].upper() == severity.upper()]
        if search:
            query = search.lower().strip()
            results = [
                rf for rf in results
                if query in rf["title"].lower()
                or query in rf["summary"].lower()
                or any(query in ind.lower() for ind in rf["indicators"])
                or query in rf["real_scam_snippet"].lower()
            ]
        return results

    @staticmethod
    def get_simulator_scenarios(difficulty: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return simulator scenarios without leaking answers for front-end play."""
        scenarios = []
        for s in SIMULATOR_SCENARIOS:
            if difficulty and difficulty.lower() != 'all' and s["difficulty"].lower() != difficulty.lower():
                continue
            scenarios.append({
                "id": s["id"],
                "title": s["title"],
                "channel": s["channel"],
                "sender": s["sender"],
                "difficulty": s["difficulty"],
                "body": s["body"],
                "xp_reward": s["xp_reward"]
            })
        return scenarios

    @staticmethod
    def evaluate_scenario(scenario_id: str, user_choice_is_scam: bool, user_flagged_clues: Optional[List[str]] = None) -> Dict[str, Any]:
        """Evaluate user guess for a simulator scenario."""
        target = next((s for s in SIMULATOR_SCENARIOS if s["id"] == scenario_id), None)
        if not target:
            return {"error": "Scenario not found"}

        is_correct = (user_choice_is_scam == target["is_scam"])
        base_xp = target["xp_reward"] if is_correct else 25

        # Check matched clues
        matched_clues = []
        if user_flagged_clues and target["is_scam"]:
            for clue in target["clue_phrases"]:
                if any(clue.lower() in uf.lower() or uf.lower() in clue.lower() for uf in user_flagged_clues):
                    matched_clues.append(clue)

        bonus_xp = len(matched_clues) * 25
        total_xp = base_xp + bonus_xp

        return {
            "scenario_id": scenario_id,
            "is_correct": is_correct,
            "actual_verdict": target["verdict"],
            "actual_is_scam": target["is_scam"],
            "red_flags": target["red_flags"],
            "clue_phrases": target["clue_phrases"],
            "forensic_explanation": target["forensic_explanation"],
            "matched_clues": matched_clues,
            "base_xp": base_xp,
            "bonus_xp": bonus_xp,
            "total_xp": total_xp
        }

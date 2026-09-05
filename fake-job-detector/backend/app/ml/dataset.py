from abc import ABC, abstractmethod
from datetime import datetime, timezone
import hashlib
import json
import os
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


class BaseDataset(ABC):
    """Abstract base dataset interface supporting historical, contemporary,
    and adversarial evaluation splits without modifying the ML training API.
    """

    @abstractmethod
    def load(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def validate(self, df: pd.DataFrame) -> bool:
        pass


class DevelopmentSmokeTestDataset(BaseDataset):
    """Development Smoke-Test Dataset (50 records).
    
    IMPORTANT LIMITATION:
    The current benchmark contains 50 records and is suitable exclusively
    as a development smoke-test and regression test harness.
    It is NOT an empirical basis for claiming production-grade accuracy
    or generalization to real-world employment fraud distributions.
    """

    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path
        self.df: Optional[pd.DataFrame] = None
        self.metadata: Dict[str, Any] = {
            "name": "SentinelJob_Dev_SmokeTest_v1",
            "type": "development_smoke_test",
            "sample_count": 50,
            "provenance_summary": "50 hand-curated synthetic and documented threat pattern examples for CI/CD regression testing.",
            "is_production_benchmark": False,
            "limitation": "The current benchmark is too small for reliable generalization estimates.",
            "sources": [
                {
                    "source_id": "SYNTH_FRAUD_PATTERNS_2026",
                    "source_name": "Synthesized Scam Patterns (Check Fraud, Telegram, Crypto Task)",
                    "source_url_reference": "Documented in FTC Consumer Alerts & IC3 Scam Bulletins",
                    "original_license": "UNKNOWN / Public Informational Alert",
                    "acquisition_date": "2026-08-17",
                    "transformation": "Normalized to unified text and binary label format",
                    "redistribution_permitted": True,
                },
                {
                    "source_id": "SYNTH_LEGIT_POSTINGS_2026",
                    "source_name": "Standard Tech Career Postings (Google, Stripe, Microsoft)",
                    "source_url_reference": "Public Enterprise Job Listings",
                    "original_license": "UNKNOWN / Public Corporate Posting",
                    "acquisition_date": "2026-08-17",
                    "transformation": "Redacted personal info, structured job descriptions",
                    "redistribution_permitted": True,
                },
            ],
            "positive_label": "fraudulent/suspicious",
            "negative_label": "legitimate",
        }

    def load(self) -> pd.DataFrame:
        """Load or build the smoke-test dataset."""
        if self.data_path and os.path.exists(self.data_path):
            if self.data_path.endswith(".csv"):
                df = pd.read_csv(self.data_path)
            elif self.data_path.endswith(".json"):
                df = pd.read_json(self.data_path)
            else:
                raise ValueError(f"Unsupported format: {self.data_path}")
        else:
            df = self._generate_smoke_test_samples()

        self.validate(df)
        self.df = self._deduplicate_dataset(df)
        return self.df

    def validate(self, df: pd.DataFrame) -> bool:
        """Ensure schema completeness, non-null values, and valid binary labels."""
        required_cols = {"text", "label"}
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"Dataset missing required columns: {missing}")

        if len(df) == 0:
            raise ValueError("Dataset cannot be empty")

        unique_labels = set(df["label"].unique())
        if not unique_labels.issubset({0, 1}):
            raise ValueError(f"Labels must be binary 0 (legitimate) or 1 (fraudulent). Found: {unique_labels}")

        df["text"] = df["text"].fillna("")
        return True

    def _deduplicate_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prevent data leakage by dropping exact and normalized duplicate strings."""
        hashes = df["text"].apply(lambda t: hashlib.md5((t or "").strip().lower().encode("utf-8")).hexdigest())
        deduped = df.loc[~hashes.duplicated(keep="first")].copy()
        deduped.reset_index(drop=True, inplace=True)
        return deduped

    def get_splits(
        self,
        test_size: float = 0.15,
        val_size: float = 0.15,
        random_state: int = 42,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Produce stratified Train (70%), Val (15%), and Test (15%) splits."""
        if self.df is None:
            self.load()

        train_val_df, test_df = train_test_split(
            self.df,
            test_size=test_size,
            random_state=random_state,
            stratify=self.df["label"],
        )

        val_relative_size = val_size / (1.0 - test_size)
        train_df, val_df = train_test_split(
            train_val_df,
            test_size=val_relative_size,
            random_state=random_state,
            stratify=train_val_df["label"],
        )

        train_df.reset_index(drop=True, inplace=True)
        val_df.reset_index(drop=True, inplace=True)
        test_df.reset_index(drop=True, inplace=True)

        return train_df, val_df, test_df

    def _generate_smoke_test_samples(self) -> pd.DataFrame:
        fraudulent_samples = [
            "URGENT HIRING: Remote Data Entry and Crypto Payment Transfer Assistants. Salary $65/hr flexible hours. No interview required. Receive cashier check of $2,500 for home-office equipment from our vendor. Send resume to apexcareers.hr@gmail.com and connect on Telegram @ApexRecruiter_David.",
            "Earn $350-$600 daily helping post on social media and answering inquiries. Must have WhatsApp. Daily payouts via PayPal or Crypto wallet. Send message to +15550194829 on WhatsApp to start immediately.",
            "Work from Home Customer Service Representative. Weekly pay ₹45,000. Registration fee of ₹2,500 required for training software license and ID card clearance. Contact HR manager on WhatsApp.",
            "Immediate vacancy for Online Typist / Document Formatter. No experience needed. $50/hour. Company will send an upfront check to buy MacBook Pro from our authorized supplier. Reply with full SSN and copy of passport.",
            "Global Logistics Assistant - Remote. We disburse company funds via Zelle or wire transfer to your personal bank account for package forwarding. Instant start upon Telegram interview.",
            "Executive Virtual Assistant needed ASAP. High compensation $80/hr. Interviews conducted exclusively on Signal app. We require a $150 security deposit for background screening.",
            "Part-Time Film Reviewer & Rating Assistant. Earn $300 daily in USDT crypto. Deposit 50 USDT to unlock daily VIP rating tasks. High return guaranteed.",
            "Home Survey Evaluator. Earn $500 per completed batch. Send $100 processing fee via Google Play gift card or Apple gift card for survey kit delivery.",
            "Data Processing Associate for Healthcare Inc. Send bank login credentials for direct deposit setup before interview. Contact dr.smith.hiring@yahoo.com.",
            "Immediate Remote Translator. $75/hour. Selected candidates must pay $99 for certified translation dictionary software before assignment starts.",
            "Urgent Hiring: Packaging Clerk. Company check will be mailed to your address. Deposit check at your ATM, keep 10% commission, and wire remainder to our shipping courier.",
            "Work From Home Financial Task Agent. Deposit ₹10,000 into company UPI to activate commission portal. Daily withdrawal enabled upon completing 5 tasks.",
            "Remote Customer Support. No resume needed. Click link http://bit.ly/claim-job-now to enter banking credentials and SSN for immediate job offer letter.",
            "Amazon Warehouse Remote Customer Representative. Contact recruiter via non-official telegram handle @AmazonRecruit_VIP. Advance equipment check provided.",
            "Entry Level Data Analyst. $90,000/yr starting salary with zero qualifications. Must purchase laptop from designated vendor using company cashier check.",
            "Online Mystery Shopper. We send you a check for $3,000. Cash it at your bank, buy gift cards at Walmart, and send photos of gift card codes to supervisor on Telegram.",
            "Student Internship Opportunity - Marketing Coordinator. ₹30,000 stipend. Compulsory registration certificate fee ₹1,500 required before interview scheduling.",
            "Remote Transcriptionist. Earn $60/hr. Please send scanned driver license, credit card front and back, and utility bill to confirm identity before call.",
            "Freelance Proofreader. Urgent requirement. Connect on Telegram @FastHiringTeam. Daily payments in Bitcoin.",
            "Administrative Clerk. Salary $4,000 monthly. Must transfer $250 equipment shipping bond via CashApp before laptop dispatch.",
            "Remote Social Media Operator. Earn $50/hr liking YouTube videos. Join Telegram channel t.me/fast_income_jobs for daily payout instructions.",
            "Immediate Entry Level Virtual Receptionist. Company will wire money to your bank account to purchase printer from our IT department.",
            "Urgent Data Entry Specialist. Salary $55/hr. Contact hr_recruitment_services2026@gmail.com with your birth date and SSN for immediate hiring.",
            "Work From Home Assistant. Earn $2,000 weekly processing payment orders through your personal PayPal account. 100% legal.",
            "Home Assembly Worker. Earn $1,500/week assembling craft kits at home. Pay $80 initial material deposit.",
        ]

        legitimate_samples = [
            "Stripe is looking for a Staff Software Engineer to lead the design and scaling of our multi-region distributed storage infrastructure. Requirements include 7+ years of experience with Go or Java, deep understanding of Raft/consensus protocols, and experience with Kubernetes and AWS. Apply directly through stripe.com/jobs.",
            "Google Cloud Platform is hiring a Senior Site Reliability Engineer in Mountain View, CA. BS/MS in Computer Science or equivalent practical experience. Experience with Linux systems internals, network protocols, and distributed architecture. Competitive base salary $185,000-$240,000 plus equity and benefits.",
            "Microsoft is seeking a Product Manager II for Azure Developer Tools. Responsibilities include defining feature roadmaps, working with engineering teams, and conducting user research. Requirements: 3+ years product management experience. Apply via microsoft.com/careers.",
            "Datadog is looking for a Software Engineer - Distributed Tracing. You will build high-throughput telemetry pipelines processing billions of events daily. Tech stack: Go, Python, Kafka, Cassandra. Comprehensive healthcare, 401(k) matching, and parental leave.",
            "Amazon Web Services (AWS) is hiring a Cloud Support Associate. Ideal candidate has a degree in IT/CS or equivalent certification (AWS Certified Solutions Architect). Strong troubleshooting skills in TCP/IP, DNS, and Linux CLI. Apply on amazon.jobs.",
            "Shopify is hiring a Senior Frontend Developer (Remote, Americas). You will build accessible, high-performance web applications using TypeScript, React, and GraphQL. Minimum 5 years frontend experience. Standard multi-stage interview process.",
            "Accenture is looking for an Associate Data Analyst in Chicago, IL. Bachelor's degree in Statistics, Economics, or Mathematics required. Proficiency in SQL, Python/R, and Tableau. Formal background check and on-site interview required.",
            "Salesforce is hiring an Enterprise Account Executive. 5+ years SaaS enterprise sales experience. Responsible for quota attainment and executive client engagements. Apply through salesforce.com/company/careers.",
            "Airbnb is seeking a Data Scientist - Analytics. Responsibilities include designing A/B experiments, building metrics dashboards, and partnering with product teams. Strong SQL and Python skills required. Official career application via airbnb.com/careers.",
            "Cloudflare is hiring a Systems Engineer for Edge Infrastructure. Deep expertise in Rust or C, Linux kernel networking, and eBPF. Competitive salary, equity package, and comprehensive health benefits.",
            "Uber is looking for a Backend Software Engineer - Core Dispatch. Experience in high-concurrency microservices, Go, Java, and Redis. Minimum 3 years relevant industry experience. Apply at uber.com/careers.",
            "Figma is hiring a Product Designer for Design Systems. 4+ years product design experience with complex web applications. Portfolio review and technical design presentation required.",
            "GitHub is seeking a Security Operations Engineer. Experience in incident response, threat detection, SIEM tooling, and cloud security monitoring. Apply through github.com/about/careers.",
            "Snowflake is hiring a Technical Curriculum Developer. Design hands-on training courses and certifications for cloud data warehousing. Experience with SQL and cloud architecture required.",
            "Spotify is looking for an Android Engineer for Mobile Core. Strong Kotlin experience, modern Android architecture (Jetpack Compose, Coroutines), and CI/CD pipelines.",
            "Twilio is hiring a Technical Support Engineer (Remote). Assist developers with REST API integrations, webhook debugging, and SIP protocols. Apply directly at twilio.com/company/jobs.",
            "Atlassian is looking for a Senior Product Manager - Jira Cloud. Lead cross-functional agile teams, define quarterly OKRs, and scale enterprise customer workflows.",
            "Netflix is hiring a Senior UI Engineer for TV Platforms. Experience in JavaScript/TypeScript, WebGL, and memory-constrained device performance optimization.",
            "MongoDB is seeking an Associate Solutions Architect. Help enterprise customers design scalable document database schemas and multi-region clusters. Apply at mongodb.com/careers.",
            "Slack is looking for a Senior Quality Assurance Engineer. Build automated end-to-end testing frameworks using Cypress and Playwright for desktop and web clients.",
            "IBM is hiring an Entry Level Software Developer. BS degree in Computer Science. Knowledge of Java, Python, Git version control, and containerization with Docker.",
            "Meta is hiring an Infrastructure Research Scientist. PhD in Computer Science or Electrical Engineering. Focus on datacenter efficiency, custom silicon, and distributed training systems.",
            "Adobe is seeking a UX Researcher for Creative Cloud. Conduct qualitative interviews, usability testing, and heuristic evaluations for digital creation tools.",
            "Oracle is hiring a Cloud Database Administrator. Responsibilities include Oracle RAC maintenance, automated backup configurations, and performance tuning.",
            "Cisco is looking for a Network Security Engineer. CCNA/CCNP certification preferred. Experience configuring firewalls, VPNs, and intrusion prevention systems.",
        ]

        data = []
        for text in fraudulent_samples:
            data.append({"text": text, "label": 1})
        for text in legitimate_samples:
            data.append({"text": text, "label": 0})

        return pd.DataFrame(data)


# Alias for backward compatibility
JobFraudDataset = DevelopmentSmokeTestDataset


class ContemporaryHoldoutDataset(BaseDataset):
    """Interface for future evaluation against recent (2025-2026) out-of-distribution
    job scam campaigns and contemporary recruiting channels.
    """

    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path
        self.metadata = {
            "name": "Contemporary_Holdout_Dataset",
            "type": "out_of_distribution_holdout",
            "status": "pending_external_ingestion",
            "license": "UNKNOWN",
        }

    def load(self) -> pd.DataFrame:
        if self.data_path and os.path.exists(self.data_path):
            df = pd.read_csv(self.data_path) if self.data_path.endswith(".csv") else pd.read_json(self.data_path)
            self.validate(df)
            return df
        # Return empty template dataframe with expected schema
        return pd.DataFrame(columns=["text", "label", "source_channel", "year"])

    def validate(self, df: pd.DataFrame) -> bool:
        required = {"text", "label"}
        if not required.issubset(set(df.columns)):
            raise ValueError(f"Missing required columns: {required - set(df.columns)}")
        return True


class AdversarialTestDataset(BaseDataset):
    """Interface for evaluating model resilience against obfuscated, paraphrased,
    and adversarial scam lures designed to evade keyword/TF-IDF filters.
    """

    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path
        self.metadata = {
            "name": "Adversarial_Evasion_Benchmark",
            "type": "adversarial_robustness_test",
            "status": "pending_external_ingestion",
            "license": "UNKNOWN",
        }

    def load(self) -> pd.DataFrame:
        if self.data_path and os.path.exists(self.data_path):
            df = pd.read_csv(self.data_path) if self.data_path.endswith(".csv") else pd.read_json(self.data_path)
            self.validate(df)
            return df
        return pd.DataFrame(columns=["text", "label", "attack_type"])

    def validate(self, df: pd.DataFrame) -> bool:
        required = {"text", "label"}
        if not required.issubset(set(df.columns)):
            raise ValueError(f"Missing required columns: {required - set(df.columns)}")
        return True

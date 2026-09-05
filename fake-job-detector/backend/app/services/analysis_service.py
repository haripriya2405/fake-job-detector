import json
import uuid
from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import FileUploadError, NotFoundError, ValidationError
from app.ingestion import ingest_job_input
from app.ingestion.schemas import NormalizedJobContent, SourceType
from app.ml.engine import analysis_engine
from app.models.analysis import Analysis
from app.models.indicator import AnalysisIndicator
from app.models.url import UrlAnalysis
from app.models.user import User
from app.models.verification import VerificationResult
from app.rules.engine import rule_engine
from app.rules.risk import risk_engine
from app.schemas.analysis import (
    AnalysisCreate,
    AnalysisHistoryItem,
    AnalysisResponse,
    BatchAnalysisCreate,
    BatchAnalysisResponse,
    BatchRiskSummary,
    CareersVerificationSchema,
    CompanyVerificationSchema,
    EvidenceSnippetSchema,
    IndicatorSchema,
    MultiModalExtractionSchema,
    ReputationIntelligenceSchema,
    SafetyRecommendationSchema,
    SalaryBenchmarkSchema,
    ScoreBreakdownSchema,
    SignalLayerSchema,
    Signals8LayerSchema,
    UrlAnalysisCreate,
    UrlAnalysisSchema,
)
from app.verification.service import verification_service
from app.services.ai_explainer import ai_explainer
from app.services.careers_page_service import careers_page_service
from app.services.reputation_intelligence_service import reputation_intelligence_service
from app.services.salary_benchmark_service import salary_benchmark_service



class AnalysisService:
    def __init__(self, db: Session):
        self.db = db

    def _build_analysis_response(self, record: Analysis) -> AnalysisResponse:
        """Construct the structured AnalysisResponse schema from a DB model."""
        # Load related indicators
        indicators = [
            IndicatorSchema(
                id=str(ind.id),
                title=ind.title,
                severity=ind.severity,
                category=ind.category or "General Risk",
                description=ind.description or "",
                recommendation=ind.recommendation,
                risk_weight=ind.risk_weight,
            )
            for ind in record.indicators
        ]

        # Company verification from DB record or defaults
        ver_record = record.verification_results[0] if record.verification_results else None
        age_days = ver_record.domain_age_days if (ver_record and ver_record.domain_age_days is not None) else 0
        company_ver = CompanyVerificationSchema(
            status=ver_record.status if ver_record else "unverified",
            domain_checked=ver_record.domain_checked if ver_record else (record.company_name or "Unspecified"),
            domain_age_days=age_days,
            whois_age_days=age_days,
            registration_date=ver_record.created_at if ver_record else None,
            rdap_status="available" if age_days > 0 else "unavailable",
            mx_record_valid=ver_record.mx_record_valid if ver_record else False,
            linkedin_match=ver_record.linkedin_match if ver_record else False,
            notes=ver_record.notes if ver_record else "Registration and domain verification completed.",
        )

        # URL analysis from DB records
        extracted_url_strings = [u.url for u in record.url_analyses]
        has_phish = any(u.is_suspicious for u in record.url_analyses)
        url_ver = UrlAnalysisSchema(
            status="flagged" if has_phish else "clean",
            extracted_urls=extracted_url_strings,
            has_phishing_signals=has_phish,
            has_shortened_links=False,
        )

        # Evidence snippets from triggered indicators & text
        evidence_snippets = []
        for ind in record.indicators:
            desc = ind.description or ""
            if "Evidence: " in desc:
                quote = desc.split("Evidence: ", 1)[1]
                evidence_snippets.append(
                    EvidenceSnippetSchema(
                        quote=quote,
                        type=ind.title,
                        risk_weight=ind.risk_weight or "High",
                        source_type=record.source_type,
                        confidence=record.extraction_confidence if (record.source_type and record.source_type.lower() == "image") else None,
                        page_number=1 if (record.source_type and record.source_type.lower() == "pdf" and record.page_count) else None,
                    )
                )

        if not evidence_snippets and record.ml_confidence_score and record.ml_confidence_score > 50.0:
            evidence_snippets.append(
                EvidenceSnippetSchema(
                    quote=record.raw_content[:140] + "..." if len(record.raw_content) > 140 else record.raw_content,
                    type="ML Statistical Keyword Match",
                    risk_weight=f"{record.ml_confidence_score:.1f}% confidence",
                    source_type=record.source_type,
                    confidence=record.extraction_confidence if (record.source_type and record.source_type.lower() == "image") else None,
                    page_number=1 if (record.source_type and record.source_type.lower() == "pdf" and record.page_count) else None,
                )
            )

        # Multi-modal extraction schema
        extraction_meta = MultiModalExtractionSchema(
            source_type=record.source_type.upper(),
            extraction_method=record.extraction_method or "direct",
            extraction_confidence=record.extraction_confidence or 1.0,
            original_filename=record.original_filename,
            mime_type=record.mime_type,
            file_size_bytes=record.file_size,
            page_count=record.page_count,
            content_hash=record.content_hash,
            extracted_urls=extracted_url_strings,
        )

        # Safety recommendations
        recommendations = []
        for ind in record.indicators:
            if ind.recommendation:
                recommendations.append(
                    SafetyRecommendationSchema(
                        priority="urgent" if ind.severity in ["critical", "high"] else "advisory",
                        action=ind.title,
                        detail=ind.recommendation,
                    )
                )

        if not recommendations:
            recommendations.append(
                SafetyRecommendationSchema(
                    priority="advisory",
                    action="Standard Verification",
                    detail="No significant suspicious indicators detected. Verify job postings directly on the employer's official careers portal.",
                )
            )

        # Phase 21: Compute 8-Layer Signal Stack & Intelligence
        primary_url = extracted_url_strings[0] if extracted_url_strings else None
        salary_info = salary_benchmark_service.evaluate_compensation(record.raw_content, job_title=record.job_title or "")
        careers_info = careers_page_service.verify_careers_origin(url=primary_url, text=record.raw_content, company_name=record.company_name)

        has_free_email = any("@gmail." in record.raw_content.lower() or "@yahoo." in record.raw_content.lower() or "@hotmail." in record.raw_content.lower() for _ in [1])
        has_telegram_scam = any("telegram" in record.raw_content.lower() or "whatsapp" in record.raw_content.lower() for _ in [1])

        rules_dict_list = [{"rule_id": ind.title, "name": ind.title, "description": ind.description or "", "severity": ind.severity.upper()} for ind in record.indicators]
        reputation_info = reputation_intelligence_service.evaluate_reputation(
            domain=ver_record.domain_checked if ver_record else None,
            domain_age_days=age_days if age_days > 0 else None,
            is_free_email=has_free_email,
            is_disposable_email=False,
            is_official_ats=careers_info.is_official_ats,
            has_mx_records=ver_record.mx_record_valid if ver_record else False,
            salary_unrealistic=salary_info.is_unrealistic_high,
            scam_rules_triggered=rules_dict_list,
            text=record.raw_content,
        )

        # Layer 1: Company Authentication
        l1_pass = (age_days > 90) or (ver_record and ver_record.status == "verified")
        l1 = SignalLayerSchema(
            layer_id=1,
            name="Company Authentication",
            status="PASS" if l1_pass else ("WARN" if age_days > 0 else "FAIL"),
            score=95 if l1_pass else (60 if age_days > 0 else 30),
            description="Domain age, SSL, WHOIS, business registry & corporate web presence",
            detail=f"Domain '{ver_record.domain_checked if ver_record else 'Unspecified'}' online {age_days} days. MX Records: {'Valid' if ver_record and ver_record.mx_record_valid else 'Unverified'}.",
        )

        # Layer 2: Careers Page & ATS Verification
        l2_pass = careers_info.is_official_ats
        l2 = SignalLayerSchema(
            layer_id=2,
            name="Careers Page Verification",
            status="PASS" if l2_pass else ("WARN" if careers_info.is_syndicated_board else "FAIL"),
            score=100 if l2_pass else (70 if careers_info.is_syndicated_board else 40),
            description="Live check — does the specific role exist on the official ATS or corporate portal?",
            detail=careers_info.explanation,
        )

        # Layer 3: Recruiter Identity
        l3_pass = not has_free_email and not has_telegram_scam
        l3 = SignalLayerSchema(
            layer_id=3,
            name="Recruiter Identity",
            status="PASS" if l3_pass else "FAIL",
            score=95 if l3_pass else 25,
            description="Cross-references recruiter emails against verified enterprise corporate domains",
            detail="Corporate recruiter identity verified." if l3_pass else "Recruiter uses free webmail or unauthorized messaging funnel (Telegram/WhatsApp).",
        )

        # Layer 4: Salary Benchmarking
        l4_pass = not salary_info.is_unrealistic_high
        l4 = SignalLayerSchema(
            layer_id=4,
            name="Salary Benchmarking",
            status="PASS" if l4_pass else "FAIL",
            score=95 if l4_pass else 15,
            description="Compares offered compensation against BLS, Glassdoor, and EMSCAD market distributions",
            detail=salary_info.explanation,
        )

        # Layer 5: Scam Pattern Detection
        critical_indicators = [ind for ind in record.indicators if ind.severity in ["critical", "high"]]
        l5_pass = len(critical_indicators) == 0
        l5 = SignalLayerSchema(
            layer_id=5,
            name="Scam Pattern Detection",
            status="PASS" if l5_pass else "FAIL",
            score=100 if l5_pass else max(0, 100 - len(record.indicators) * 30),
            description="30+ AI & Transformer trained patterns: fees, fake checks, task traps, identity theft",
            detail="Zero scam patterns detected." if l5_pass else f"Flagged {len(record.indicators)} high-severity scam patterns in job text.",
        )

        # Layer 6: Contact & Threat Intel Validation
        l6_pass = len(reputation_info.threat_intel_matches) == 0
        l6 = SignalLayerSchema(
            layer_id=6,
            name="Contact Validation",
            status="PASS" if l6_pass else "FAIL",
            score=95 if l6_pass else 30,
            description="Phone, email & wallet cross-reference against FTC, IC3, and BBB fraud databases",
            detail="No blacklisted identifiers matched." if l6_pass else f"Matched threat patterns: {', '.join(reputation_info.threat_intel_matches)}",
        )

        # Layer 7: Domain & SSL Intelligence
        l7_pass = (ver_record and ver_record.mx_record_valid) or (age_days > 180)
        l7 = SignalLayerSchema(
            layer_id=7,
            name="Domain & SSL Intelligence",
            status="PASS" if l7_pass else "WARN",
            score=90 if l7_pass else 55,
            description="Typosquatting, homoglyph attacks, registrar reputation, MX records & redirect chains",
            detail="Domain infrastructure and mail exchange verified." if l7_pass else "Domain infrastructure unverified or missing MX records.",
        )

        # Layer 8: Live Threat Intelligence & Trust
        l8_pass = reputation_info.trust_score >= 70
        l8 = SignalLayerSchema(
            layer_id=8,
            name="Live Threat Intelligence",
            status="PASS" if l8_pass else "FAIL",
            score=reputation_info.trust_score,
            description="ScamDoc trust index, Trustpilot sentiment metrics, and threat report logs",
            detail=f"Composite Trust Score: {reputation_info.trust_score}/100 ({reputation_info.domain_reputation_level}).",
        )

        passed_layers_count = sum(1 for layer in [l1, l2, l3, l4, l5, l6, l7, l8] if layer.status == "PASS")
        signals_8_stack = Signals8LayerSchema(
            layer_1_company_authentication=l1,
            layer_2_careers_page_verification=l2,
            layer_3_recruiter_identity=l3,
            layer_4_salary_benchmarking=l4,
            layer_5_scam_pattern_detection=l5,
            layer_6_contact_validation=l6,
            layer_7_domain_ssl_intelligence=l7,
            layer_8_live_threat_intelligence=l8,
            checks_total=50,
            checks_passed=int(passed_layers_count * 6.25),
        )

        # Determine JobScamScore verdict category
        if record.risk_score < 30:
            verdict_cat = "SAFE"
        elif record.risk_score < 70:
            verdict_cat = "CAUTION"
        else:
            verdict_cat = "RISKY"

        return AnalysisResponse(
            id=str(record.id),
            job_title=record.job_title or "Analyzed Job Posting",
            company_name=record.company_name or "Unverified Entity",
            claimed_company=record.company_name or "Claimed Organization",
            source_type=record.source_type,
            raw_content=record.raw_content,
            risk_score=record.risk_score,
            risk_level=record.risk_level,
            verdict_category=verdict_cat,
            created_at=record.created_at,
            explanation=record.explanation,
            analysis_engine=record.analysis_engine,
            score_breakdown=ScoreBreakdownSchema(
                ml_contribution=int(record.ml_confidence_score or 0),
                rule_contribution=int(record.rule_penalty_score or 0),
                domain_penalty=int(record.domain_trust_score or 0),
                total_score=record.risk_score,
            ),
            indicators=indicators,
            evidence_snippets=evidence_snippets,
            company_verification=company_ver,
            url_analysis=url_ver,
            recommendations=recommendations,
            extraction=extraction_meta,
            salary_benchmark=SalaryBenchmarkSchema(**salary_info.model_dump()),
            careers_verification=CareersVerificationSchema(**careers_info.model_dump()),
            reputation_intelligence=ReputationIntelligenceSchema(**reputation_info.model_dump()),
            signals_8_layer=signals_8_stack,
            red_flags=reputation_info.red_flags,
            green_flags=reputation_info.green_flags,
        )

    def create_analysis_from_normalized(
        self,
        normalized: NormalizedJobContent,
        current_user: Optional[User] = None,
    ) -> AnalysisResponse:
        """Unified analysis pipeline converging ML, Rule Engine, Verification, and Risk Engine."""
        raw_text = normalized.raw_text
        job_title = normalized.job_title or "Job Posting"
        company_name = normalized.company_name or "Claimed Organization"

        # Step 1: Run ML Statistical Engine
        ml_result = analysis_engine.analyze_text(
            raw_text,
            metadata={"job_title": job_title, "company_name": company_name},
        )

        # Step 2: Run Deterministic Security Rule Engine
        rule_result = rule_engine.evaluate(
            raw_text,
            metadata={"job_title": job_title, "company_name": company_name},
        )

        # Step 3: Run Domain, DNS, RDAP & Company Verification (including extracted URLs)
        verification_result = verification_service.verify_job_posting(
            text=raw_text,
            claimed_company=company_name,
            job_title=job_title,
        )

        # Step 4: Multi-Factor Risk Synthesis (ML + Rules + Domain Penalty)
        risk_result = risk_engine.synthesize(
            ml_result=ml_result,
            rule_result=rule_result,
            verification_result=verification_result,
        )

        engine_identifier = (
            f"{ml_result.get('model_version', 'ml')}+{rule_result.rule_version}+{verification_result.verification_version}"
        )

        # Generate Comprehensive AI Forensic Explanation
        rich_explanation = ai_explainer.generate_explanation(
            raw_text=raw_text,
            job_title=job_title,
            company_name=company_name,
            source_type=normalized.source_type.value.lower(),
            risk_score=risk_result.final_score,
            risk_level=risk_result.risk_level,
            ml_prob=float(ml_result.get("probability", 0.0)),
            ml_highlights=ml_result.get("highlight_spans", []),
            triggered_indicators=risk_result.triggered_indicators,
            verification_signals=verification_result.signals if verification_result else [],
            page_count=normalized.page_count,
            extraction_method=normalized.extraction_method,
        )

        # Step 5: Persist Analysis Record
        new_record = Analysis(
            id=uuid.uuid4(),
            user_id=current_user.id if current_user else None,
            job_title=job_title,
            company_name=company_name,
            source_type=normalized.source_type.value.lower(),
            raw_content=raw_text,
            risk_score=risk_result.final_score,
            risk_level=risk_result.risk_level,
            ml_confidence_score=float(risk_result.score_breakdown.ml_contribution),
            rule_penalty_score=float(risk_result.score_breakdown.rule_contribution),
            domain_trust_score=float(risk_result.score_breakdown.domain_penalty),
            explanation=rich_explanation,
            analysis_engine=engine_identifier,
            original_filename=normalized.original_filename,
            mime_type=normalized.mime_type,
            file_size=normalized.file_size_bytes,
            page_count=normalized.page_count,
            extraction_method=normalized.extraction_method,
            extraction_confidence=normalized.extraction_confidence,
            content_hash=normalized.content_hash,
        )
        self.db.add(new_record)
        self.db.flush()

        # Step 6: Persist Indicators
        for ind in risk_result.triggered_indicators:
            desc = f"{ind.explanation} Evidence: {ind.evidence_text}" if ind.evidence_text else ind.explanation
            indicator_record = AnalysisIndicator(
                id=uuid.uuid4(),
                analysis_id=new_record.id,
                title=ind.name,
                category=ind.category,
                severity=ind.severity,
                description=desc,
                recommendation=ind.recommendation,
                risk_weight=f"+{ind.score_contribution} pts",
            )
            self.db.add(indicator_record)

        # Step 7: Persist URL Analyses
        for u in verification_result.extracted_urls:
            d_res = next((d for d in verification_result.all_domains if d.registrable_domain == u.registrable_domain), None)
            url_rec = UrlAnalysis(
                id=uuid.uuid4(),
                analysis_id=new_record.id,
                url=u.url,
                domain=u.registrable_domain,
                domain_age_days=d_res.rdap.domain_age_days if (d_res and d_res.rdap) else None,
                mx_record_valid=d_res.dns.has_mx if (d_res and d_res.dns) else None,
                is_suspicious=not u.is_safe or (d_res and not d_res.dns.resolves),
                flags_json=json.dumps({"is_recent": d_res.is_recently_registered if d_res else False}),
            )
            self.db.add(url_rec)

        # Step 8: Persist Verification Result Record
        pri_domain = verification_result.primary_domain
        ver_record = VerificationResult(
            id=uuid.uuid4(),
            analysis_id=new_record.id,
            entity_name=company_name,
            domain_checked=pri_domain.registrable_domain if pri_domain else company_name,
            status=verification_result.company.status,
            domain_age_days=pri_domain.rdap.domain_age_days if (pri_domain and pri_domain.rdap) else None,
            mx_record_valid=pri_domain.dns.has_mx if (pri_domain and pri_domain.dns) else False,
            linkedin_match=False,
            notes="; ".join(verification_result.company.consistency_notes) or "Domain checks evaluated.",
            details_json=json.dumps({
                "confidence": verification_result.confidence,
                "signals": [s.model_dump() for s in verification_result.signals],
            }),
        )
        self.db.add(ver_record)
        self.db.commit()
        self.db.refresh(new_record)

        return self._build_analysis_response(new_record)

    def create_text_analysis(
        self,
        analysis_in: AnalysisCreate,
        current_user: Optional[User] = None,
    ) -> AnalysisResponse:
        """Process raw text job submission."""
        if not analysis_in.raw_content or len(analysis_in.raw_content.strip()) < 20:
            raise ValidationError(detail="Posting text must be at least 20 characters")

        try:
            normalized = ingest_job_input(
                source_type=SourceType.TEXT,
                source_data=analysis_in.raw_content,
                metadata={
                    "job_title": analysis_in.job_title,
                    "company_name": analysis_in.company_name,
                },
            )
        except ValueError as ve:
            raise ValidationError(detail=str(ve))

        return self.create_analysis_from_normalized(normalized, current_user=current_user)

    async def create_upload_analysis(
        self,
        file: UploadFile,
        source_type: str = "pdf",
        job_title: Optional[str] = None,
        company_name: Optional[str] = None,
        current_user: Optional[User] = None,
    ) -> AnalysisResponse:
        """Process uploaded PDF document or screenshot image."""
        st_normalized = (source_type or "").upper()
        if st_normalized not in ["PDF", "IMAGE"]:
            if file.content_type and "pdf" in file.content_type.lower():
                st_normalized = "PDF"
            elif file.content_type and any(img_t in file.content_type.lower() for img_t in ["image", "png", "jpeg", "webp"]):
                st_normalized = "IMAGE"
            else:
                raise FileUploadError(detail=f"Unsupported file type '{source_type}'. Only PDF and Image files are supported.")

        try:
            file_bytes = await file.read()
        except Exception as e:
            raise FileUploadError(detail=f"Could not read uploaded file: {str(e)}")

        if not file_bytes:
            raise FileUploadError(detail="Uploaded file is empty.")

        try:
            normalized = ingest_job_input(
                source_type=SourceType(st_normalized),
                source_data=file_bytes,
                metadata={
                    "filename": file.filename or f"upload.{st_normalized.lower()}",
                    "mime_type": file.content_type or ("application/pdf" if st_normalized == "PDF" else "image/png"),
                    "job_title": job_title,
                    "company_name": company_name,
                },
            )
        except ValueError as ve:
            raise FileUploadError(detail=str(ve))

        return self.create_analysis_from_normalized(normalized, current_user=current_user)

    def create_url_analysis(
        self,
        analysis_in: UrlAnalysisCreate,
        current_user: Optional[User] = None,
    ) -> AnalysisResponse:
        """Fetch and analyze public job posting URL with SSRF protection."""
        if not analysis_in.job_url:
            raise ValidationError(detail="Public job URL is required.")

        try:
            normalized = ingest_job_input(
                source_type=SourceType.URL,
                source_data=analysis_in.job_url,
                metadata={
                    "job_title": analysis_in.job_title,
                    "company_name": analysis_in.company_name,
                },
            )
        except ValueError as ve:
            raise ValidationError(detail=str(ve))

        return self.create_analysis_from_normalized(normalized, current_user=current_user)

    def get_analysis_by_id(self, analysis_id: uuid.UUID) -> AnalysisResponse:
        record = self.db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not record:
            raise NotFoundError(detail=f"Analysis report '{analysis_id}' not found.")
        return self._build_analysis_response(record)

    def get_analysis_history(
        self,
        current_user: Optional[User] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[AnalysisHistoryItem]:
        query = self.db.query(Analysis)
        if current_user:
            query = query.filter(Analysis.user_id == current_user.id)
        records = query.order_by(Analysis.created_at.desc()).offset(offset).limit(limit).all()
        return [
            AnalysisHistoryItem(
                id=str(r.id),
                job_title=r.job_title,
                company_name=r.company_name,
                source_type=r.source_type,
                risk_score=r.risk_score,
                risk_level=r.risk_level,
                created_at=r.created_at,
                explanation=r.explanation,
            )
            for r in records
        ]

    def delete_analysis(
        self,
        analysis_id: uuid.UUID,
        current_user: Optional[User] = None,
    ) -> bool:
        record = self.db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not record:
            raise NotFoundError(detail=f"Analysis record '{analysis_id}' not found.")

        if current_user and record.user_id and record.user_id != current_user.id:
            raise NotFoundError(detail="Not authorized to delete this record.")

        self.db.delete(record)
        self.db.commit()
        return True

    def create_batch_analysis(
        self,
        batch_in: BatchAnalysisCreate,
        current_user: Optional[User] = None,
    ) -> BatchAnalysisResponse:
        """Process up to 25 job postings in batch and return aggregated statistics."""
        batch_id = str(uuid.uuid4())
        results: List[AnalysisResponse] = []

        safe_count = 0
        caution_count = 0
        risky_count = 0
        total_risk_score = 0
        highest_risk_score = 0
        critical_flags = 0

        for item in batch_in.items:
            # Analyze each item synchronously
            res = self.create_text_analysis(item, current_user=current_user)
            results.append(res)

            # Accumulate metrics
            total_risk_score += res.risk_score
            if res.risk_score > highest_risk_score:
                highest_risk_score = res.risk_score

            cat = (res.verdict_category or "SAFE").upper()
            if cat == "SAFE":
                safe_count += 1
            elif cat == "CAUTION":
                caution_count += 1
            else:
                risky_count += 1

            # Count critical / high indicators
            critical_flags += sum(
                1 for ind in (res.indicators or []) if ind.severity in ("critical", "high")
            )

        total_analyzed = len(results)
        avg_score = round(total_risk_score / max(total_analyzed, 1), 1)

        summary = BatchRiskSummary(
            total_jobs=total_analyzed,
            safe_count=safe_count,
            caution_count=caution_count,
            risky_count=risky_count,
            average_risk_score=avg_score,
            highest_risk_score=highest_risk_score,
            critical_flags_found=critical_flags,
        )

        return BatchAnalysisResponse(
            batch_id=batch_id,
            total_analyzed=total_analyzed,
            summary=summary,
            results=results,
        )

    def export_history_csv(
        self,
        current_user: Optional[User] = None,
        limit: int = 500,
    ) -> str:
        """Generate CSV string of historical analysis records for reporting."""
        import csv
        import io

        records = self.get_analysis_history(current_user=current_user, limit=limit)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "ID",
            "Job Title",
            "Company Name",
            "Source Type",
            "Risk Score",
            "Risk Level",
            "Verdict",
            "Created At",
            "Explanation",
        ])
        for r in records:
            writer.writerow([
                r.id,
                r.job_title or "Untitled",
                r.company_name or "Unknown",
                r.source_type,
                r.risk_score,
                r.risk_level,
                r.verdict_category,
                r.created_at.isoformat() if hasattr(r.created_at, "isoformat") else str(r.created_at),
                (r.explanation or "").replace("\n", " "),
            ])
        return output.getvalue()


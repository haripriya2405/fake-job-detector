# PostgreSQL Database Blueprint & Schema Design

```sql
-- Users & Roles
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user', -- user, admin, analyst
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Analysis Records
CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    job_title VARCHAR(255),
    company_name VARCHAR(255),
    source_type VARCHAR(50) NOT NULL, -- 'text', 'pdf', 'image'
    raw_content TEXT NOT NULL,
    risk_score INTEGER NOT NULL CHECK (risk_score >= 0 AND risk_score <= 100),
    risk_level VARCHAR(50) NOT NULL, -- 'low', 'medium', 'high', 'critical'
    ml_confidence_score NUMERIC(5,2),
    rule_penalty_score NUMERIC(5,2),
    domain_trust_score NUMERIC(5,2),
    explanation TEXT,
    recommendations JSONB,
    indicators JSONB,
    evidence_snippets JSONB,
    company_verification JSONB,
    url_analysis JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indices for Fast Queries
CREATE INDEX idx_analyses_user_id ON analyses(user_id);
CREATE INDEX idx_analyses_created_at ON analyses(created_at DESC);
CREATE INDEX idx_analyses_risk_level ON analyses(risk_level);
```

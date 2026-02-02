-- Neon Database Initialization Script
-- Run this in Neon SQL Editor or via psql

-- ================================================
-- STEP 1: Create Enum Types
-- ================================================

-- Drop existing types if they exist
DROP TYPE IF EXISTS application_status CASCADE;
DROP TYPE IF EXISTS document_type CASCADE;
DROP TYPE IF EXISTS generation_status CASCADE;

CREATE TYPE application_status AS ENUM (
    'draft',
    'documents_uploaded',
    'analyzing',
    'generating',
    'completed',
    'failed'
);

CREATE TYPE document_type AS ENUM (
    'passport_copy',
    'nid_bangla',
    'visa_history',
    'tin_certificate',
    'income_tax_3years',
    'asset_valuation',
    'hotel_booking',
    'air_ticket',
    'bank_solvency',
    'nid_english',
    'visiting_card',
    'cover_letter',
    'travel_itinerary',
    'travel_history',
    'home_tie_statement',
    'financial_statement',
    'tax_certificate',
    'trade_license'
);

CREATE TYPE generation_status AS ENUM (
    'pending',
    'in_progress',
    'completed',
    'failed'
);

-- ================================================
-- STEP 2: Create Tables
-- ================================================

-- Drop existing tables if they exist
DROP TABLE IF EXISTS questionnaire_responses CASCADE;
DROP TABLE IF EXISTS ai_interactions CASCADE;
DROP TABLE IF EXISTS generated_documents CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS required_documents CASCADE;
DROP TABLE IF EXISTS visa_applications CASCADE;

-- Applications Table
CREATE TABLE visa_applications (
    id SERIAL PRIMARY KEY,
    applicant_name VARCHAR(255),
    country VARCHAR(100) DEFAULT 'Iceland',
    visa_type VARCHAR(100) DEFAULT 'Tourist',
    status application_status DEFAULT 'draft',
    progress INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents Table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES visa_applications(id) ON DELETE CASCADE,
    document_type document_type NOT NULL,
    file_path TEXT,
    original_filename VARCHAR(255),
    file_size INTEGER,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_generated BOOLEAN DEFAULT FALSE,
    extraction_status VARCHAR(50) DEFAULT 'pending',
    extracted_data JSONB,
    UNIQUE(application_id, document_type)
);

-- Generated Documents Table
CREATE TABLE generated_documents (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES visa_applications(id) ON DELETE CASCADE,
    document_type document_type NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    status generation_status DEFAULT 'pending',
    error_message TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(application_id, document_type)
);

-- AI Interactions Table
CREATE TABLE ai_interactions (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES visa_applications(id) ON DELETE CASCADE,
    interaction_type VARCHAR(100),
    prompt TEXT,
    response TEXT,
    model_used VARCHAR(100),
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Required Documents Table
CREATE TABLE required_documents (
    id SERIAL PRIMARY KEY,
    country VARCHAR(100) NOT NULL,
    visa_type VARCHAR(100) NOT NULL,
    document_type document_type NOT NULL,
    is_mandatory BOOLEAN DEFAULT TRUE,
    description TEXT,
    can_be_generated BOOLEAN DEFAULT FALSE,
    UNIQUE(country, visa_type, document_type)
);

-- Questionnaire Responses Table
CREATE TABLE questionnaire_responses (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES visa_applications(id) ON DELETE CASCADE,
    question_key VARCHAR(255) NOT NULL,
    question_text TEXT NOT NULL,
    answer TEXT,
    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================================
-- STEP 3: Create Indexes
-- ================================================

CREATE INDEX IF NOT EXISTS idx_applications_status ON visa_applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_created ON visa_applications(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_documents_application ON documents(application_id);
CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(document_type);
CREATE INDEX IF NOT EXISTS idx_generated_docs_application ON generated_documents(application_id);
CREATE INDEX IF NOT EXISTS idx_ai_interactions_application ON ai_interactions(application_id);
CREATE INDEX IF NOT EXISTS idx_required_docs_country_visa ON required_documents(country, visa_type);
CREATE INDEX IF NOT EXISTS idx_questionnaire_application ON questionnaire_responses(application_id);

-- ================================================
-- STEP 4: Insert Required Documents for Iceland Tourist Visa
-- ================================================

INSERT INTO required_documents (country, visa_type, document_type, is_mandatory, description, can_be_generated)
VALUES
-- User must provide these
('Iceland', 'Tourist', 'passport_copy', true, 'Valid passport copy', false),
('Iceland', 'Tourist', 'nid_bangla', true, 'National ID card (Bangla)', false),
('Iceland', 'Tourist', 'visa_history', true, 'Previous visa history from passport', false),
('Iceland', 'Tourist', 'tin_certificate', true, 'Tax Identification Number certificate', false),
('Iceland', 'Tourist', 'income_tax_3years', true, 'Income tax returns for last 3 years', false),
('Iceland', 'Tourist', 'asset_valuation', true, 'Asset valuation certificate', false),
('Iceland', 'Tourist', 'hotel_booking', true, 'Hotel booking confirmation', false),
('Iceland', 'Tourist', 'air_ticket', true, 'Air ticket booking', false),
('Iceland', 'Tourist', 'bank_solvency', true, 'Bank solvency certificate', false),

-- System will generate these
('Iceland', 'Tourist', 'nid_english', true, 'National ID English translation', true),
('Iceland', 'Tourist', 'visiting_card', true, 'Professional visiting card', true),
('Iceland', 'Tourist', 'cover_letter', true, 'Visa application cover letter', true),
('Iceland', 'Tourist', 'travel_itinerary', true, 'Detailed travel itinerary', true),
('Iceland', 'Tourist', 'travel_history', true, 'Travel history summary', true),
('Iceland', 'Tourist', 'home_tie_statement', true, 'Home tie statement letter', true),
('Iceland', 'Tourist', 'financial_statement', true, 'Financial statement summary', true),
('Iceland', 'Tourist', 'tax_certificate', false, 'Tax return certificate', true),
('Iceland', 'Tourist', 'trade_license', false, 'Business trade license', true)
ON CONFLICT (country, visa_type, document_type) DO NOTHING;

-- ================================================
-- STEP 5: Create Update Trigger
-- ================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_visa_applications_updated_at ON visa_applications;
CREATE TRIGGER update_visa_applications_updated_at
    BEFORE UPDATE ON visa_applications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ================================================
-- VERIFICATION
-- ================================================

SELECT 'Database initialized successfully!' as status;
SELECT COUNT(*) as required_documents_count FROM required_documents;
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;

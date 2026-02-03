-- ============================================================
-- COMPLETE NEON DATABASE SETUP FOR VISA PROCESSING SYSTEM
-- This script creates ALL tables needed by the application
-- Run this ENTIRE script in Neon SQL Editor in ONE go
-- ============================================================

-- ============================================================
-- STEP 1: DROP ALL EXISTING TABLES AND TYPES (Clean Start)
-- ============================================================
DROP TABLE IF EXISTS generated_documents CASCADE;
DROP TABLE IF EXISTS analysis_sessions CASCADE;
DROP TABLE IF EXISTS questionnaire_responses CASCADE;
DROP TABLE IF EXISTS extracted_data CASCADE;
DROP TABLE IF EXISTS required_documents CASCADE;
DROP TABLE IF EXISTS ai_interactions CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS visa_applications CASCADE;

DROP TYPE IF EXISTS generation_status CASCADE;
DROP TYPE IF EXISTS analysis_status CASCADE;
DROP TYPE IF EXISTS question_data_type CASCADE;
DROP TYPE IF EXISTS question_category CASCADE;
DROP TYPE IF EXISTS document_type CASCADE;
DROP TYPE IF EXISTS application_status CASCADE;

-- ============================================================
-- STEP 2: CREATE ALL ENUM TYPES
-- ============================================================

-- Application Status (UPPERCASE - matches Python enum values)
CREATE TYPE application_status AS ENUM (
    'DRAFT',
    'DOCUMENTS_UPLOADED',
    'ANALYZING',
    'GENERATING',
    'COMPLETED',
    'FAILED'
);

-- Document Types (lowercase - matches Python enum values)
CREATE TYPE document_type AS ENUM (
    'passport_copy',
    'nid_bangla',
    'bank_solvency',
    'visa_history',
    'tin_certificate',
    'income_tax_3years',
    'hotel_booking',
    'air_ticket',
    'cover_letter',
    'nid_english',
    'visiting_card',
    'financial_statement',
    'travel_itinerary',
    'travel_history',
    'home_tie_statement',
    'asset_valuation',
    'tin_certificate_generated',
    'tax_certificate',
    'trade_license',
    'hotel_booking_generated',
    'air_ticket_generated'
);

-- Question Category (lowercase - matches Python enum values)
CREATE TYPE question_category AS ENUM (
    'personal',
    'employment',
    'business',
    'travel_purpose',
    'financial',
    'assets',
    'home_ties'
);

-- Question Data Type (lowercase - matches Python enum values)
CREATE TYPE question_data_type AS ENUM (
    'text',
    'textarea',
    'number',
    'date',
    'select',
    'multiselect',
    'boolean'
);

-- Analysis Status (lowercase - matches Python enum values)
CREATE TYPE analysis_status AS ENUM (
    'pending',
    'started',
    'analyzing',
    'completed',
    'failed'
);

-- Generation Status (lowercase - matches Python enum values)
CREATE TYPE generation_status AS ENUM (
    'pending',
    'generating',
    'completed',
    'failed'
);

-- ============================================================
-- STEP 3: CREATE ALL TABLES
-- ============================================================

-- Main Application Table
CREATE TABLE visa_applications (
    id SERIAL PRIMARY KEY,
    application_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- User information
    applicant_name VARCHAR(200),
    applicant_email VARCHAR(200),
    applicant_phone VARCHAR(20),
    
    -- Visa details
    country VARCHAR(100) NOT NULL DEFAULT 'Iceland',
    visa_type VARCHAR(100) NOT NULL DEFAULT 'Tourist',
    
    -- Application status
    status application_status DEFAULT 'DRAFT',
    
    -- Extracted information
    extracted_data JSONB DEFAULT '{}',
    missing_info JSONB DEFAULT '[]',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Documents Table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES visa_applications(id) ON DELETE CASCADE,
    
    -- Document details
    document_type document_type NOT NULL,
    document_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    
    -- Document status
    is_uploaded BOOLEAN DEFAULT TRUE,
    is_processed BOOLEAN DEFAULT FALSE,
    is_required BOOLEAN DEFAULT TRUE,
    
    -- Extracted content
    extracted_text TEXT,
    extracted_data JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE
);

-- AI Interactions Table
CREATE TABLE ai_interactions (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES visa_applications(id) ON DELETE CASCADE,
    
    -- Interaction details
    interaction_type VARCHAR(50),
    prompt TEXT,
    response TEXT,
    
    -- Metadata
    model_used VARCHAR(100),
    tokens_used INTEGER,
    processing_time INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Required Documents Master List
CREATE TABLE required_documents (
    id SERIAL PRIMARY KEY,
    country VARCHAR(100) NOT NULL,
    visa_type VARCHAR(100) NOT NULL,
    document_type document_type NOT NULL,
    
    -- Document metadata
    is_mandatory BOOLEAN DEFAULT TRUE,
    description TEXT,
    can_be_generated BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent duplicate entries
    UNIQUE(country, visa_type, document_type)
);

-- Extracted Data Table
CREATE TABLE extracted_data (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES visa_applications(id) ON DELETE CASCADE,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    document_type document_type NOT NULL,
    
    -- Structured extracted information
    data JSONB DEFAULT '{}',
    
    -- Extraction metadata
    confidence_score INTEGER DEFAULT 0,
    extraction_model VARCHAR(100) DEFAULT 'models/gemini-2.5-flash',
    
    -- Timestamps
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Questionnaire Responses Table
CREATE TABLE questionnaire_responses (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES visa_applications(id) ON DELETE CASCADE,
    
    -- Question details
    category question_category NOT NULL,
    question_key VARCHAR(200) NOT NULL,
    question_text TEXT NOT NULL,
    
    -- Response
    answer TEXT,
    data_type question_data_type DEFAULT 'text',
    
    -- Options for select/multiselect
    options JSONB,
    
    -- Metadata
    is_required BOOLEAN DEFAULT TRUE,
    answered_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Analysis Sessions Table
CREATE TABLE analysis_sessions (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES visa_applications(id) ON DELETE CASCADE,
    
    -- Analysis status
    status analysis_status DEFAULT 'pending',
    documents_analyzed INTEGER DEFAULT 0,
    total_documents INTEGER DEFAULT 0,
    current_document VARCHAR(200),
    
    -- Results
    completeness_score INTEGER DEFAULT 0,
    missing_fields JSONB DEFAULT '[]',
    
    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Error handling
    error_message TEXT
);

-- Generated Documents Table
CREATE TABLE generated_documents (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES visa_applications(id) ON DELETE CASCADE,
    
    -- Document details
    document_type VARCHAR(100) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    
    -- Generation status
    status generation_status DEFAULT 'pending',
    generation_progress INTEGER DEFAULT 0,
    error_message TEXT,
    
    -- Metadata
    generation_metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- ============================================================
-- STEP 4: CREATE ALL INDEXES FOR PERFORMANCE
-- ============================================================

-- visa_applications indexes
CREATE INDEX idx_applications_number ON visa_applications(application_number);
CREATE INDEX idx_applications_status ON visa_applications(status);
CREATE INDEX idx_applications_created ON visa_applications(created_at DESC);

-- documents indexes
CREATE INDEX idx_documents_application ON documents(application_id);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_uploaded ON documents(is_uploaded);

-- ai_interactions indexes
CREATE INDEX idx_ai_interactions_application ON ai_interactions(application_id);
CREATE INDEX idx_ai_interactions_type ON ai_interactions(interaction_type);

-- required_documents indexes
CREATE INDEX idx_required_docs_country_visa ON required_documents(country, visa_type);

-- extracted_data indexes
CREATE INDEX idx_extracted_data_application ON extracted_data(application_id);
CREATE INDEX idx_extracted_data_document ON extracted_data(document_id);

-- questionnaire_responses indexes
CREATE INDEX idx_questionnaire_application ON questionnaire_responses(application_id);
CREATE INDEX idx_questionnaire_category ON questionnaire_responses(category);

-- analysis_sessions indexes
CREATE INDEX idx_analysis_sessions_application ON analysis_sessions(application_id);
CREATE INDEX idx_analysis_sessions_status ON analysis_sessions(status);

-- generated_documents indexes
CREATE INDEX idx_generated_docs_application ON generated_documents(application_id);
CREATE INDEX idx_generated_docs_status ON generated_documents(status);

-- ============================================================
-- STEP 5: INSERT REQUIRED DOCUMENTS FOR ICELAND TOURIST VISA
-- ============================================================

INSERT INTO required_documents (country, visa_type, document_type, is_mandatory, description, can_be_generated) VALUES
-- Mandatory user documents
('Iceland', 'Tourist', 'passport_copy', true, 'Valid passport copy with at least 6 months validity', false),
('Iceland', 'Tourist', 'nid_bangla', true, 'National ID card in Bangla', false),
('Iceland', 'Tourist', 'bank_solvency', true, 'Bank solvency certificate', false),

-- Optional user documents
('Iceland', 'Tourist', 'visa_history', false, 'Previous visa stamps from passport', false),
('Iceland', 'Tourist', 'tin_certificate', false, 'Tax Identification Number certificate', true),
('Iceland', 'Tourist', 'income_tax_3years', false, 'Income tax returns for last 3 years', false),
('Iceland', 'Tourist', 'hotel_booking', false, 'Hotel booking confirmation', true),
('Iceland', 'Tourist', 'air_ticket', false, 'Flight ticket booking', true),

-- System generated documents
('Iceland', 'Tourist', 'cover_letter', true, 'Cover letter for visa application', true),
('Iceland', 'Tourist', 'nid_english', true, 'NID translated to English', true),
('Iceland', 'Tourist', 'visiting_card', false, 'Professional visiting card', true),
('Iceland', 'Tourist', 'financial_statement', true, 'Financial statement summary', true),
('Iceland', 'Tourist', 'travel_itinerary', true, 'Detailed travel itinerary', true),
('Iceland', 'Tourist', 'travel_history', false, 'Travel history document', true),
('Iceland', 'Tourist', 'home_tie_statement', true, 'Statement showing home country ties', true),
('Iceland', 'Tourist', 'asset_valuation', false, 'Asset valuation certificate', true);

-- ============================================================
-- STEP 6: VERIFY SETUP
-- ============================================================

-- Show summary
SELECT 'DATABASE SETUP COMPLETE!' as status;
SELECT '' as blank;
SELECT 'Tables Created:' as info;
SELECT table_name, 
       (SELECT COUNT(*) 
        FROM information_schema.columns 
        WHERE columns.table_name = tables.table_name 
        AND columns.table_schema = 'public') as column_count
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE'
ORDER BY table_name;

SELECT '' as blank;
SELECT 'Enum Types Created:' as info;
SELECT typname as enum_type,
       array_agg(enumlabel ORDER BY enumsortorder) as values
FROM pg_type 
JOIN pg_enum ON pg_type.oid = pg_enum.enumtypid
WHERE typname IN ('application_status', 'document_type', 'question_category', 
                  'question_data_type', 'analysis_status', 'generation_status')
GROUP BY typname
ORDER BY typname;

SELECT '' as blank;
SELECT 'Required Documents for Iceland Tourist Visa:' as info;
SELECT COUNT(*) as total_documents,
       SUM(CASE WHEN is_mandatory THEN 1 ELSE 0 END) as mandatory_docs,
       SUM(CASE WHEN can_be_generated THEN 1 ELSE 0 END) as ai_generated_docs
FROM required_documents
WHERE country = 'Iceland' AND visa_type = 'Tourist';

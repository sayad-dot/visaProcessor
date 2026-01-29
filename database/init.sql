-- Database initialization script for Visa Processing System
-- PostgreSQL Database Setup

-- Create database (run this separately if needed)
-- CREATE DATABASE visa_processing_db;

-- Connect to the database
\c visa_processing_db;

-- Create enum types
CREATE TYPE application_status AS ENUM (
    'draft',
    'documents_uploaded',
    'analyzing',
    'generating',
    'completed',
    'failed'
);

CREATE TYPE document_type AS ENUM (
    -- User provided documents
    'passport_copy',
    'nid_bangla',
    'visa_history',
    'tin_certificate',
    'income_tax_3years',
    'asset_valuation',
    'hotel_booking',
    'air_ticket',
    'bank_solvency',
    -- System generated documents
    'nid_english',
    'visiting_card',
    'cover_letter',
    'travel_itinerary',
    'travel_history',
    'home_tie_statement',
    'financial_statement'
);

-- Insert required documents for Iceland Tourist Visa
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
('Iceland', 'Tourist', 'financial_statement', true, 'Financial statement summary', true);

-- Create indexes for better performance
CREATE INDEX idx_applications_status ON visa_applications(status);
CREATE INDEX idx_applications_created ON visa_applications(created_at DESC);
CREATE INDEX idx_documents_application ON documents(application_id);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_ai_interactions_application ON ai_interactions(application_id);
CREATE INDEX idx_required_docs_country_visa ON required_documents(country, visa_type);

-- Grant privileges (adjust username as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_username;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_username;

COMMENT ON DATABASE visa_processing_db IS 'Database for Visa Document Processing System';

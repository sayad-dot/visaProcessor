-- ===================================================================
-- PRODUCTION MIGRATION SCRIPT FOR NEON DATABASE
-- ===================================================================
-- This script updates the database schema to support different document
-- requirements for Business vs Job applicants
-- Date: 2026-02-07
-- ===================================================================

-- Step 1: Add new document types to enum
ALTER TYPE document_type ADD VALUE IF NOT EXISTS 'payslip';
ALTER TYPE document_type ADD VALUE IF NOT EXISTS 'bank_statement';
ALTER TYPE document_type ADD VALUE IF NOT EXISTS 'job_noc';
ALTER TYPE document_type ADD VALUE IF NOT EXISTS 'job_id_card';

-- Step 2: Add application_type column to required_documents table
ALTER TABLE required_documents 
ADD COLUMN IF NOT EXISTS application_type VARCHAR(50) NOT NULL DEFAULT 'business';

-- Step 3: Drop old unique constraint (if exists)
ALTER TABLE required_documents 
DROP CONSTRAINT IF EXISTS required_documents_unique_key;

-- Step 4: Add new unique constraint including application_type
ALTER TABLE required_documents 
ADD CONSTRAINT required_documents_unique_key 
UNIQUE (country, visa_type, application_type, document_type);

-- Step 5: Clear existing data (we'll reseed with correct data)
DELETE FROM required_documents;

-- Step 6: Insert correct document requirements

-- Business: 14 documents (2 required, 12 optional)
INSERT INTO required_documents 
(country, visa_type, application_type, document_type, is_mandatory, can_be_generated, description)
VALUES
-- REQUIRED (2 docs)
('Iceland', 'Tourist', 'business', 'passport_copy', true, false, 'Passport copy - PDF'),
('Iceland', 'Tourist', 'business', 'nid_bangla', true, true, 'NID Bangla (will be translated to English)'),
-- OPTIONAL (12 docs)
('Iceland', 'Tourist', 'business', 'visa_history', false, false, 'Visa history copies - PDF'),
('Iceland', 'Tourist', 'business', 'nid_english', false, true, 'NID English translated copy - PDF'),
('Iceland', 'Tourist', 'business', 'trade_license', false, false, 'Trade license English translated - PDF'),
('Iceland', 'Tourist', 'business', 'tin_certificate', false, false, 'TIN certificate - PDF'),
('Iceland', 'Tourist', 'business', 'visiting_card', false, true, 'Visiting card - PDF'),
('Iceland', 'Tourist', 'business', 'cover_letter', false, true, 'Cover letter - PDF'),
('Iceland', 'Tourist', 'business', 'asset_valuation', false, true, 'Asset valuation document - PDF'),
('Iceland', 'Tourist', 'business', 'travel_itinerary', false, true, 'Travel itinerary - PDF'),
('Iceland', 'Tourist', 'business', 'travel_history', false, true, 'Travel History - PDF'),
('Iceland', 'Tourist', 'business', 'air_ticket', false, false, 'Air ticket Booking - PDF'),
('Iceland', 'Tourist', 'business', 'hotel_booking', false, false, 'Hotel Booking - PDF'),
('Iceland', 'Tourist', 'business', 'bank_statement', false, false, 'Bank statement - PDF');

-- Job: 15 documents (2 required, 13 optional)
INSERT INTO required_documents 
(country, visa_type, application_type, document_type, is_mandatory, can_be_generated, description)
VALUES
-- REQUIRED (2 docs)
('Iceland', 'Tourist', 'job', 'passport_copy', true, false, 'Passport copy - PDF'),
('Iceland', 'Tourist', 'job', 'nid_bangla', true, true, 'NID Bangla (will be translated to English)'),
-- OPTIONAL (13 docs)
('Iceland', 'Tourist', 'job', 'visa_history', false, false, 'Visa history copies - PDF'),
('Iceland', 'Tourist', 'job', 'nid_english', false, true, 'NID English translated copy - PDF'),
('Iceland', 'Tourist', 'job', 'job_noc', false, false, 'JOB NOC (No Objection Certificate) - PDF'),
('Iceland', 'Tourist', 'job', 'tin_certificate', false, false, 'TIN certificate - PDF'),
('Iceland', 'Tourist', 'job', 'visiting_card', false, true, 'Visiting card - PDF'),
('Iceland', 'Tourist', 'job', 'job_id_card', false, false, 'JOB ID card - PDF'),
('Iceland', 'Tourist', 'job', 'payslip', false, false, 'Payslip of last 6 months salary - PDF'),
('Iceland', 'Tourist', 'job', 'cover_letter', false, true, 'Cover letter - PDF'),
('Iceland', 'Tourist', 'job', 'travel_itinerary', false, true, 'Travel itinerary - PDF'),
('Iceland', 'Tourist', 'job', 'travel_history', false, true, 'Travel History - PDF'),
('Iceland', 'Tourist', 'job', 'air_ticket', false, false, 'Air ticket Booking - PDF'),
('Iceland', 'Tourist', 'job', 'hotel_booking', false, false, 'Hotel Booking - PDF'),
('Iceland', 'Tourist', 'job', 'bank_statement', false, false, 'Bank statement - PDF');

-- Step 7: Verify the migration
SELECT 
    application_type,
    COUNT(*) as total_documents,
    SUM(CASE WHEN is_mandatory = true THEN 1 ELSE 0 END) as required_documents,
    SUM(CASE WHEN is_mandatory = false THEN 1 ELSE 0 END) as optional_documents
FROM required_documents
WHERE country = 'Iceland' AND visa_type = 'Tourist'
GROUP BY application_type
ORDER BY application_type;

-- Expected result:
-- business: 14 total (2 required, 12 optional)
-- job: 15 total (2 required, 13 optional)

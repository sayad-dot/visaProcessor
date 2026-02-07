-- ============================================================
-- MIGRATION: Add Job vs Business Feature
-- Date: February 5, 2026
-- Description: Add application_type to visa_applications and
--             add job document types (job_noc, job_id_card)
-- ============================================================

-- Step 1: Add new document types to enum
ALTER TYPE document_type ADD VALUE IF NOT EXISTS 'job_noc';
ALTER TYPE document_type ADD VALUE IF NOT EXISTS 'job_id_card';

-- Step 2: Create application_type enum
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'application_type') THEN
        CREATE TYPE application_type AS ENUM ('business', 'job');
    END IF;
END $$;

-- Step 3: Add application_type column to visa_applications
ALTER TABLE visa_applications 
ADD COLUMN IF NOT EXISTS application_type application_type DEFAULT 'business' NOT NULL;

-- Step 4: Add required documents for Job type (Iceland Tourist)
INSERT INTO required_documents (country, visa_type, document_type, is_mandatory, description, can_be_generated)
VALUES
-- Job NOC (SUGGESTED - not mandatory, can be generated)
('Iceland', 'Tourist', 'job_noc', false, 'No Objection Certificate from employer - SUGGESTED for job holders', true),
-- Job ID Card (SUGGESTED - not mandatory, can be generated)
('Iceland', 'Tourist', 'job_id_card', false, 'Employee ID Card - SUGGESTED for job holders', true)
ON CONFLICT (country, visa_type, document_type) DO NOTHING;

-- Step 5: Verify migration
SELECT 'MIGRATION COMPLETE!' as status;
SELECT '' as blank;

SELECT 'Application Type Enum Created:' as info;
SELECT enumlabel as value
FROM pg_enum
WHERE enumtypid = 'application_type'::regtype
ORDER BY enumsortorder;

SELECT '' as blank;

SELECT 'New Document Types Added:' as info;
SELECT enumlabel as value
FROM pg_enum
WHERE enumtypid = 'document_type'::regtype
AND enumlabel IN ('job_noc', 'job_id_card')
ORDER BY enumsortorder;

SELECT '' as blank;

SELECT 'Required Documents for Job Type:' as info;
SELECT document_type, description, is_mandatory, can_be_generated
FROM required_documents
WHERE country = 'Iceland' 
  AND visa_type = 'Tourist'
  AND document_type IN ('job_noc', 'job_id_card');

SELECT '' as blank;

SELECT 'Column Added to visa_applications:' as info;
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'visa_applications'
  AND column_name = 'application_type';

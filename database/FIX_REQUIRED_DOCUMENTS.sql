-- Fix: Update required_documents to mark only 3 as mandatory
-- Run this in Neon SQL Editor

UPDATE required_documents
SET is_mandatory = false
WHERE country = 'Iceland' 
  AND visa_type = 'Tourist'
  AND document_type NOT IN ('passport_copy', 'nid_bangla', 'bank_solvency');

-- Verify the update
SELECT 
    document_type,
    is_mandatory,
    can_be_generated,
    description
FROM required_documents
WHERE country = 'Iceland' AND visa_type = 'Tourist'
ORDER BY is_mandatory DESC, document_type;

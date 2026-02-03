-- ============================================================
-- VERIFICATION SCRIPT - Check if database setup is complete
-- Run this in Neon SQL Editor to verify everything was created
-- ============================================================

-- Check 1: Count all tables
SELECT 
    'TABLES CHECK' as check_type,
    COUNT(*) as count,
    CASE 
        WHEN COUNT(*) >= 8 THEN '✅ PASS' 
        ELSE '❌ FAIL - Missing tables' 
    END as status
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE';

-- Check 2: List all tables
SELECT table_name as "Table Name"
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- Check 3: Count enum types
SELECT 
    'ENUM TYPES CHECK' as check_type,
    COUNT(DISTINCT typname) as count,
    CASE 
        WHEN COUNT(DISTINCT typname) >= 6 THEN '✅ PASS' 
        ELSE '❌ FAIL - Missing enum types' 
    END as status
FROM pg_type 
WHERE typname IN ('application_status', 'document_type', 'question_category', 
                  'question_data_type', 'analysis_status', 'generation_status');

-- Check 4: List all enum types and their values
SELECT 
    typname as "Enum Type",
    array_agg(enumlabel ORDER BY enumsortorder) as "Values"
FROM pg_type 
JOIN pg_enum ON pg_type.oid = pg_enum.enumtypid
WHERE typname IN ('application_status', 'document_type', 'question_category', 
                  'question_data_type', 'analysis_status', 'generation_status')
GROUP BY typname
ORDER BY typname;

-- Check 5: Count required documents
SELECT 
    'REQUIRED DOCUMENTS CHECK' as check_type,
    COUNT(*) as count,
    CASE 
        WHEN COUNT(*) >= 16 THEN '✅ PASS' 
        ELSE '❌ FAIL - Missing required documents' 
    END as status
FROM required_documents
WHERE country = 'Iceland' AND visa_type = 'Tourist';

-- Check 6: Final Summary
SELECT 
    'FINAL STATUS' as check_type,
    CASE 
        WHEN (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE') >= 8
         AND (SELECT COUNT(DISTINCT typname) FROM pg_type WHERE typname IN ('application_status', 'document_type', 'question_category', 'question_data_type', 'analysis_status', 'generation_status')) >= 6
         AND (SELECT COUNT(*) FROM required_documents WHERE country = 'Iceland' AND visa_type = 'Tourist') >= 16
        THEN '✅ ✅ ✅ DATABASE FULLY CONFIGURED AND READY TO USE ✅ ✅ ✅'
        ELSE '❌ DATABASE INCOMPLETE - RE-RUN COMPLETE_NEON_SETUP.sql'
    END as status;

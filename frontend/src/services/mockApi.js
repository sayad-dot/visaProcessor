/**
 * Mock API Service for Demo Version
 * Simulates backend responses with realistic data
 */

// Simulate network delay
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Mock application data storage
const mockApplications = [];
let nextAppId = 1;

// Mock uploaded documents storage
const mockDocuments = {};

export const mockApi = {
  // Applications
  async createApplication(data) {
    await delay(500);
    const newApp = {
      id: nextAppId++,
      ...data,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      status: 'pending'
    };
    mockApplications.push(newApp);
    return newApp;
  },

  async getApplications() {
    await delay(300);
    return mockApplications;
  },

  async getApplication(id) {
    await delay(300);
    return mockApplications.find(app => app.id === parseInt(id));
  },

  // Required Documents
  async getRequiredDocuments(applicationId) {
    await delay(300);
    const app = mockApplications.find(a => a.id === parseInt(applicationId));
    const professionType = app?.profession_type || 'Job';
    
    // Documents for Job profession
    const jobDocuments = [
      { id: 1, document_type: 'passport_copy', category: 'identity', is_required: true, description: 'Passport copy (PDF)' },
      { id: 2, document_type: 'visa_history', category: 'travel', is_required: true, description: 'Visa history copies (PDF)' },
      { id: 3, document_type: 'nid_english', category: 'identity', is_required: true, description: 'NID English translated copy (PDF)' },
      { id: 4, document_type: 'job_noc', category: 'employment', is_required: true, description: 'Job NOC (PDF)' },
      { id: 5, document_type: 'tin', category: 'financial', is_required: true, description: 'TIN certificate (PDF)' },
      { id: 6, document_type: 'visiting_card', category: 'employment', is_required: true, description: 'Visiting card (PDF)' },
      { id: 7, document_type: 'job_id_card', category: 'employment', is_required: true, description: 'Job ID card (PDF/Image)' },
      { id: 8, document_type: 'payslip_6months', category: 'financial', is_required: true, description: 'Payslip of last 6 months salary (PDF)' },
      { id: 9, document_type: 'cover_letter', category: 'application', is_required: true, description: 'Cover letter (PDF)' },
      { id: 10, document_type: 'travel_itinerary', category: 'travel', is_required: true, description: 'Travel itinerary (PDF)' },
      { id: 11, document_type: 'travel_history', category: 'travel', is_required: true, description: 'Travel history (PDF)' },
      { id: 12, document_type: 'air_ticket_booking', category: 'travel', is_required: true, description: 'Air ticket booking (PDF)' },
      { id: 13, document_type: 'hotel_booking', category: 'travel', is_required: true, description: 'Hotel booking (PDF)' },
      { id: 14, document_type: 'savings_bank_statement', category: 'financial', is_required: true, description: 'Savings account bank statement (last 6 months)' },
      { id: 15, document_type: 'savings_solvency', category: 'financial', is_required: true, description: 'Savings account bank solvency certificate' }
    ];
    
    // Documents for Business profession
    const businessDocuments = [
      { id: 1, document_type: 'passport_copy', category: 'identity', is_required: true, description: 'Passport copy (PDF)' },
      { id: 2, document_type: 'visa_history', category: 'travel', is_required: true, description: 'Visa history copies (PDF)' },
      { id: 3, document_type: 'nid_english', category: 'identity', is_required: true, description: 'NID English translated copy (PDF)' },
      { id: 4, document_type: 'trade_license', category: 'business', is_required: true, description: 'Trade license English translated (PDF)' },
      { id: 5, document_type: 'tin', category: 'financial', is_required: true, description: 'TIN certificate (PDF)' },
      { id: 6, document_type: 'visiting_card', category: 'business', is_required: true, description: 'Visiting card (PDF)' },
      { id: 7, document_type: 'cover_letter', category: 'application', is_required: true, description: 'Cover letter (PDF)' },
      { id: 8, document_type: 'travel_itinerary', category: 'travel', is_required: true, description: 'Travel itinerary (PDF)' },
      { id: 9, document_type: 'travel_history', category: 'travel', is_required: true, description: 'Travel history (PDF)' },
      { id: 10, document_type: 'air_ticket_booking', category: 'travel', is_required: true, description: 'Air ticket booking (PDF)' },
      { id: 11, document_type: 'hotel_booking', category: 'travel', is_required: true, description: 'Hotel booking (PDF)' },
      { id: 12, document_type: 'current_bank_statement', category: 'financial', is_required: true, description: 'Current/Business account bank statement (last 6 months)' },
      { id: 13, document_type: 'current_solvency', category: 'financial', is_required: true, description: 'Current/Business account bank solvency certificate' },
      { id: 14, document_type: 'savings_bank_statement', category: 'financial', is_required: true, description: 'Savings account bank statement (last 6 months)' },
      { id: 15, document_type: 'savings_solvency', category: 'financial', is_required: true, description: 'Savings account bank solvency certificate' }
    ];
    
    return professionType === 'Business' ? businessDocuments : jobDocuments;
  },

  // Documents
  async uploadDocument(applicationId, file, documentType) {
    await delay(1000);
    
    if (!mockDocuments[applicationId]) {
      mockDocuments[applicationId] = [];
    }

    const doc = {
      id: Date.now(),
      application_id: applicationId,
      document_type: documentType,
      file_name: file.name,
      file_size: file.size,
      file_type: file.type,
      is_uploaded: true,
      uploaded_at: new Date().toISOString()
    };

    mockDocuments[applicationId].push(doc);
    return doc;
  },

  async getDocuments(applicationId) {
    await delay(300);
    return mockDocuments[applicationId] || [];
  },

  async deleteDocument(documentId) {
    await delay(300);
    Object.keys(mockDocuments).forEach(appId => {
      mockDocuments[appId] = mockDocuments[appId].filter(doc => doc.id !== documentId);
    });
    return { success: true };
  },

  // Analysis
  async analyzeDocuments(applicationId) {
    await delay(5000); // Simulate AI processing time
    
    const uploadedDocs = mockDocuments[applicationId] || [];
    const score = 85 + Math.floor(Math.random() * 10);
    
    return {
      application_id: applicationId,
      total_documents: 16,
      uploaded_documents: uploadedDocs.length,
      overall_score: score,
      extracted_data: {
        passport: { 
          confidence: 95, 
          status: "excellent",
          data: {
            full_name: "MD OSMAN GONI",
            passport_number: "BE0123456",
            nationality: "Bangladeshi",
            date_of_birth: "1975-03-15"
          }
        },
        bank_statement: { 
          confidence: 89, 
          status: "good",
          data: {
            account_holder: "MD OSMAN GONI",
            bank_name: "Dutch-Bangla Bank",
            balance: "850000 BDT"
          }
        },
        employment_certificate: { 
          confidence: 82, 
          status: "good",
          data: {
            employer: "Osman Trading International",
            position: "Owner/Manager",
            monthly_salary: "120000 BDT"
          }
        }
      },
      issues: [
        { type: "warning", message: "Some text in bank statement is slightly blurred" },
        { type: "info", message: "All mandatory documents successfully processed" }
      ],
      recommendations: [
        "Upload remaining optional documents for stronger application",
        "Consider providing clearer scans if possible"
      ]
    };
  },

  // Questionnaire
  async getQuestionnaire(applicationId) {
    await delay(1000);
    
    return {
      "Personal Information": [
        {
          key: "full_name",
          text: "What is your full name as it appears on your passport?",
          data_type: "text",
          is_required: false,
          placeholder: "Enter your full name"
        },
        {
          key: "date_of_birth",
          text: "What is your date of birth?",
          data_type: "date",
          is_required: false
        },
        {
          key: "nationality",
          text: "What is your nationality?",
          data_type: "text",
          is_required: false,
          placeholder: "e.g., Bangladeshi"
        },
        {
          key: "marital_status",
          text: "What is your marital status?",
          data_type: "select",
          is_required: false,
          options: ["Single", "Married", "Divorced", "Widowed"]
        },
        {
          key: "phone_number",
          text: "What is your contact phone number?",
          data_type: "text",
          is_required: false,
          placeholder: "+880-1XXXXXXXXX"
        },
        {
          key: "email_address",
          text: "What is your email address?",
          data_type: "text",
          is_required: false,
          placeholder: "your.email@example.com"
        },
        {
          key: "current_address",
          text: "What is your current residential address?",
          data_type: "textarea",
          is_required: false,
          placeholder: "Enter your full address"
        },
        {
          key: "permanent_address",
          text: "What is your permanent address (if different)?",
          data_type: "textarea",
          is_required: false,
          placeholder: "Enter permanent address or write 'Same as current'"
        }
      ],
      "Travel Information": [
        {
          key: "travel_purpose",
          text: "What is the primary purpose of your visit to Iceland?",
          data_type: "select",
          is_required: false,
          options: ["Tourism", "Business", "Visiting Friends/Family", "Conference/Event", "Other"]
        },
        {
          key: "travel_purpose_detail",
          text: "Please describe in detail your travel plans and purpose:",
          data_type: "textarea",
          is_required: false,
          placeholder: "Describe your travel plans, places to visit, activities planned"
        },
        {
          key: "travel_duration",
          text: "How many days do you plan to stay in Iceland?",
          data_type: "number",
          is_required: false,
          placeholder: "Number of days"
        },
        {
          key: "arrival_date",
          text: "When do you plan to arrive in Iceland?",
          data_type: "date",
          is_required: false
        },
        {
          key: "departure_date",
          text: "When do you plan to depart from Iceland?",
          data_type: "date",
          is_required: false
        },
        {
          key: "accommodation_type",
          text: "What type of accommodation have you arranged?",
          data_type: "select",
          is_required: false,
          options: ["Hotel", "Airbnb", "Hostel", "Staying with Friends/Family", "Not Yet Booked"]
        },
        {
          key: "previous_travel",
          text: "Have you traveled internationally before?",
          data_type: "select",
          is_required: false,
          options: ["No", "Yes - 1-2 times", "Yes - 3-5 times", "Yes - More than 5 times"]
        },
        {
          key: "previous_schengen",
          text: "Have you visited any Schengen countries before?",
          data_type: "select",
          is_required: false,
          options: ["No", "Yes - Once", "Yes - Multiple times"]
        },
        {
          key: "previous_visa_rejection",
          text: "Have you ever been rejected for any visa to any country?",
          data_type: "select",
          is_required: false,
          options: ["No", "Yes - Please explain in next question"]
        },
        {
          key: "rejection_details",
          text: "If you answered 'Yes' above, please provide details:",
          data_type: "textarea",
          is_required: false,
          placeholder: "Country, date, and reason for rejection"
        },
        {
          key: "return_ticket",
          text: "Do you have a confirmed return ticket?",
          data_type: "select",
          is_required: false,
          options: ["Yes - Booked", "Yes - Reserved", "Not Yet", "Will book after visa approval"]
        }
      ],
      "Employment & Financial Information": [
        {
          key: "employment_status",
          text: "What is your current employment status?",
          data_type: "select",
          is_required: false,
          options: ["Employed - Full Time", "Employed - Part Time", "Self-Employed/Business Owner", "Student", "Retired", "Unemployed"]
        },
        {
          key: "employer_name",
          text: "What is your employer's name or business name?",
          data_type: "text",
          is_required: false,
          placeholder: "Company/Business name"
        },
        {
          key: "job_title",
          text: "What is your job title or position?",
          data_type: "text",
          is_required: false,
          placeholder: "Your position/designation"
        },
        {
          key: "employment_duration",
          text: "How long have you been working at your current position?",
          data_type: "text",
          is_required: false,
          placeholder: "e.g., 5 years, 2 months"
        },
        {
          key: "monthly_income",
          text: "What is your monthly income (in BDT)?",
          data_type: "number",
          is_required: false,
          placeholder: "Enter amount in BDT"
        },
        {
          key: "annual_income",
          text: "What is your approximate annual income (in BDT)?",
          data_type: "number",
          is_required: false,
          placeholder: "Enter annual income"
        },
        {
          key: "bank_balance",
          text: "What is your current total bank balance across all accounts?",
          data_type: "number",
          is_required: false,
          placeholder: "Total balance in BDT"
        },
        {
          key: "trip_sponsor",
          text: "Who is sponsoring your trip?",
          data_type: "select",
          is_required: false,
          options: ["Self-funded", "Family Member", "Employer", "Friend", "Other"]
        },
        {
          key: "trip_budget",
          text: "What is your estimated budget for this trip (in BDT)?",
          data_type: "number",
          is_required: false,
          placeholder: "Estimated total budget"
        },
        {
          key: "property_owned",
          text: "Do you own any property or real estate?",
          data_type: "select",
          is_required: false,
          options: ["No", "Yes - Residential", "Yes - Commercial", "Yes - Both", "Yes - Land Only"]
        },
        {
          key: "property_value",
          text: "If you own property, what is the approximate total value (in BDT)?",
          data_type: "number",
          is_required: false,
          placeholder: "Approximate property value"
        },
        {
          key: "vehicle_owned",
          text: "Do you own any vehicles?",
          data_type: "select",
          is_required: false,
          options: ["No", "Yes - Car", "Yes - Motorcycle", "Yes - Multiple vehicles"]
        }
      ],
      "Family & Home Ties": [
        {
          key: "family_marital_status",
          text: "Your marital status:",
          data_type: "select",
          is_required: false,
          options: ["Single", "Married", "Divorced", "Widowed", "Engaged"]
        },
        {
          key: "spouse_name",
          text: "If married, what is your spouse's name?",
          data_type: "text",
          is_required: false,
          placeholder: "Spouse full name"
        },
        {
          key: "number_of_children",
          text: "How many children do you have?",
          data_type: "select",
          is_required: false,
          options: ["0", "1", "2", "3", "4 or more"]
        },
        {
          key: "children_ages",
          text: "If you have children, please list their ages:",
          data_type: "text",
          is_required: false,
          placeholder: "e.g., 5, 8, 12"
        },
        {
          key: "parents_alive",
          text: "Are your parents alive?",
          data_type: "select",
          is_required: false,
          options: ["Both alive", "Mother alive", "Father alive", "Both deceased"]
        },
        {
          key: "siblings",
          text: "How many siblings do you have?",
          data_type: "select",
          is_required: false,
          options: ["0", "1", "2", "3", "4 or more"]
        },
        {
          key: "family_in_iceland",
          text: "Do you have any family members or relatives living in Iceland?",
          data_type: "select",
          is_required: false,
          options: ["No", "Yes - Immediate family", "Yes - Extended family"]
        },
        {
          key: "reason_to_return",
          text: "What are your strongest ties to your home country that ensure you will return?",
          data_type: "textarea",
          is_required: false,
          placeholder: "E.g., family responsibilities, business, property, job commitment"
        }
      ],
      "Additional Information": [
        {
          key: "criminal_record",
          text: "Do you have any criminal record or pending criminal cases?",
          data_type: "select",
          is_required: false,
          options: ["No", "Yes - Minor offense", "Yes - Major offense", "Yes - Pending case"]
        },
        {
          key: "medical_conditions",
          text: "Do you have any medical conditions that require special attention?",
          data_type: "select",
          is_required: false,
          options: ["No", "Yes - Minor", "Yes - Requires regular medication", "Yes - Serious condition"]
        },
        {
          key: "travel_insurance",
          text: "Do you have travel insurance covering your entire trip?",
          data_type: "select",
          is_required: false,
          options: ["Yes - Already purchased", "Will purchase after visa approval", "Not yet decided"]
        },
        {
          key: "emergency_contact_name",
          text: "Emergency contact person's name (in home country):",
          data_type: "text",
          is_required: false,
          placeholder: "Full name"
        },
        {
          key: "emergency_contact_phone",
          text: "Emergency contact person's phone number:",
          data_type: "text",
          is_required: false,
          placeholder: "+880-XXXXXXXXXX"
        },
        {
          key: "emergency_contact_relation",
          text: "Relationship with emergency contact:",
          data_type: "select",
          is_required: false,
          options: ["Spouse", "Parent", "Sibling", "Friend", "Other relative"]
        },
        {
          key: "additional_info",
          text: "Is there any additional information you would like to provide to support your application?",
          data_type: "textarea",
          is_required: false,
          placeholder: "Any additional relevant information"
        }
      ]
    };
  },

  async saveQuestionnaireResponses(applicationId, responses) {
    await delay(500);
    return { success: true, saved: responses.length };
  },

  // Document Generation
  async generateDocuments(applicationId) {
    await delay(3000);
    
    return {
      success: true,
      generated_count: 8,
      documents: [
        { type: "cover_letter", status: "completed", filename: "01_Cover_Letter.pdf" },
        { type: "travel_itinerary", status: "completed", filename: "02_Travel_Itinerary.pdf" },
        { type: "financial_documents", status: "completed", filename: "03_Financial_Documents.pdf" },
        { type: "home_ties", status: "completed", filename: "04_Home_Ties_Statement.pdf" },
        { type: "asset_valuation", status: "completed", filename: "05_Asset_Valuation.pdf" },
        { type: "previous_travel", status: "completed", filename: "06_Travel_History.pdf" },
        { type: "air_ticket", status: "completed", filename: "07_Air_Ticket.pdf" },
        { type: "hotel_booking", status: "completed", filename: "08_Hotel_Booking.pdf" }
      ]
    };
  },

  async downloadZip(applicationId) {
    await delay(1000);
    // Return mock blob
    return new Blob(['Mock ZIP file content'], { type: 'application/zip' });
  }
};

export default mockApi;
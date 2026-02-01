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
          key: "phone_number",
          text: "What is your contact phone number?",
          data_type: "text",
          is_required: false,
          placeholder: "+880-1XXXXXXXXX"
        }
      ],
      "Travel Information": [
        {
          key: "previous_visa_rejection",
          text: "Have you ever been rejected for any visa to any country?",
          data_type: "select",
          is_required: false,
          options: ["No", "Yes - Please explain"]
        },
        {
          key: "travel_purpose_detail",
          text: "Please describe in detail why you want to visit Iceland:",
          data_type: "textarea",
          is_required: false,
          placeholder: "Describe your travel plans and purpose"
        },
        {
          key: "previous_travel",
          text: "Have you traveled internationally before?",
          data_type: "select",
          is_required: false,
          options: ["No", "Yes - 1-2 times", "Yes - 3-5 times", "Yes - More than 5 times"]
        }
      ],
      "Financial Information": [
        {
          key: "monthly_income",
          text: "What is your monthly income in BDT?",
          data_type: "number",
          is_required: false,
          placeholder: "Enter amount in BDT"
        },
        {
          key: "bank_balance",
          text: "What is your current bank balance?",
          data_type: "number",
          is_required: false,
          placeholder: "Enter current balance"
        },
        {
          key: "property_owned",
          text: "Do you own any property or real estate?",
          data_type: "select",
          is_required: false,
          options: ["No", "Yes - Residential", "Yes - Commercial", "Yes - Both"]
        }
      ],
      "Family Information": [
        {
          key: "marital_status",
          text: "What is your marital status?",
          data_type: "select",
          is_required: false,
          options: ["Single", "Married", "Divorced", "Widowed"]
        },
        {
          key: "children_count",
          text: "How many children do you have?",
          data_type: "number",
          is_required: false
        },
        {
          key: "spouse_employment",
          text: "If married, what is your spouse's employment status?",
          data_type: "select",
          is_required: false,
          options: ["Not Applicable", "Employed", "Self-employed", "Unemployed", "Student"]
        }
      ],
      total_questions: 12,
      note: "All questions are OPTIONAL. Answer only what you want to provide."
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
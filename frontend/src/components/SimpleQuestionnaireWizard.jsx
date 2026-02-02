import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Stepper,
  Step,
  StepLabel,
  Box,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  FormControlLabel,
  Checkbox,
  Typography,
  Alert,
  CircularProgress,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  FormHelperText,
  Divider
} from '@mui/material';
import {
  NavigateNext as NextIcon,
  NavigateBefore as BackIcon,
  Save as SaveIcon,
  CheckCircle as CheckCircleIcon,
  ExpandMore as ExpandMoreIcon,
  Info as InfoIcon,
  Flight as FlightIcon,
  Hotel as HotelIcon,
  TravelExplore as TravelIcon,
  AttachMoney as MoneyIcon
} from '@mui/icons-material';

/**
 * SimpleQuestionnaireWizard - Fixed 4-section structure
 * Section 1: Personal Info (5 required)
 * Section 2: Travel Info (3 collapsible boxes with skip logic)
 * Section 3: Financial/Assets
 * Section 4: Other (all optional)
 */
const SimpleQuestionnaireWizard = ({ open, onClose, applicationId, onComplete }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [questions, setQuestions] = useState({});
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [sameAsPermanent, setSameAsPermanent] = useState(false);
  const [sections, setSections] = useState({});

  const steps = ['Personal Info', 'Travel Info', 'Financial/Assets', 'Other Info'];
  
  const sectionMapping = {
    0: ['personal'],
    1: ['travel_itinerary', 'hotel_booking', 'air_ticket'],
    2: ['assets', 'financial', 'home_ties'],
    3: ['other']
  };

  // Load questionnaire
  useEffect(() => {
    if (open && applicationId) {
      loadQuestionnaire();
      loadExistingAnswers();
    }
  }, [open, applicationId]);

  // Handle "same as permanent" checkbox
  useEffect(() => {
    if (sameAsPermanent && answers.permanent_address) {
      setAnswers(prev => ({
        ...prev,
        present_address: answers.permanent_address
      }));
    }
  }, [sameAsPermanent, answers.permanent_address]);

  const loadQuestionnaire = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`http://localhost:8000/api/questionnaire/generate/${applicationId}`);
      if (!response.ok) {
        throw new Error('Failed to load questionnaire');
      }

      const data = await response.json();
      setQuestions(data.questions_by_category || {});
      setSections(data.sections || {});
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadExistingAnswers = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/questionnaire/responses/${applicationId}`);
      if (response.ok) {
        const data = await response.json();
        
        const answerMap = {};
        Object.values(data).forEach(categoryQuestions => {
          categoryQuestions.forEach(q => {
            if (q.answer) {
              answerMap[q.key] = q.answer;
            }
          });
        });
        
        setAnswers(answerMap);
      }
    } catch (err) {
      // No existing answers
    }
  };

  const handleAnswerChange = (questionKey, value) => {
    setAnswers(prev => ({
      ...prev,
      [questionKey]: value
    }));
  };

  const handleNext = () => {
    // Validate required fields for current section
    const currentCategories = sectionMapping[activeStep];
    let hasError = false;
    
    if (activeStep === 0) {
      // Personal section - check 5 required fields
      const requiredFields = ['father_name', 'mother_name', 'birthplace', 'permanent_address', 'present_address'];
      const missingFields = requiredFields.filter(f => !answers[f]?.trim());
      
      if (missingFields.length > 0) {
        setError(`Please fill all required personal information fields`);
        hasError = true;
      }
    }
    
    if (!hasError) {
      setError(null);
      setActiveStep(prev => prev + 1);
    }
  };

  const handleBack = () => {
    setError(null);
    setActiveStep(prev => prev - 1);
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);

      // Convert answers to API format
      const responses = Object.entries(answers).map(([key, value]) => ({
        question_key: key,
        answer: value
      }));

      const response = await fetch(`http://localhost:8000/api/questionnaire/response/${applicationId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ responses })
      });

      if (!response.ok) {
        throw new Error('Failed to save questionnaire');
      }

      // Mark questionnaire as complete
      await fetch(`http://localhost:8000/api/questionnaire/complete/${applicationId}`, {
        method: 'POST'
      });

      onComplete?.();
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const renderQuestion = (question) => {
    const value = answers[question.key] || '';

    // Special handling for present_address
    if (question.key === 'present_address') {
      return (
        <Box key={question.key} sx={{ mb: 3 }}>
          <FormControlLabel
            control={
              <Checkbox
                checked={sameAsPermanent}
                onChange={(e) => setSameAsPermanent(e.target.checked)}
                color="primary"
              />
            }
            label="Same as Permanent Address"
          />
          {!sameAsPermanent && (
            <TextField
              fullWidth
              multiline
              rows={3}
              label={question.text}
              value={value}
              onChange={(e) => handleAnswerChange(question.key, e.target.value)}
              required={question.is_required}
              placeholder={question.placeholder}
              helperText={question.help_text}
              sx={{ mt: 1 }}
            />
          )}
        </Box>
      );
    }

    switch (question.data_type) {
      case 'text':
        return (
          <TextField
            key={question.key}
            fullWidth
            label={question.text}
            value={value}
            onChange={(e) => handleAnswerChange(question.key, e.target.value)}
            required={question.is_required}
            placeholder={question.placeholder}
            helperText={question.help_text}
            sx={{ mb: 3 }}
          />
        );

      case 'textarea':
        return (
          <TextField
            key={question.key}
            fullWidth
            multiline
            rows={3}
            label={question.text}
            value={value}
            onChange={(e) => handleAnswerChange(question.key, e.target.value)}
            required={question.is_required}
            placeholder={question.placeholder}
            helperText={question.help_text}
            sx={{ mb: 3 }}
          />
        );

      case 'number':
        return (
          <TextField
            key={question.key}
            fullWidth
            type="number"
            label={question.text}
            value={value}
            onChange={(e) => handleAnswerChange(question.key, e.target.value)}
            required={question.is_required}
            placeholder={question.placeholder}
            helperText={question.help_text}
            sx={{ mb: 3 }}
          />
        );

      case 'select':
        return (
          <FormControl key={question.key} fullWidth sx={{ mb: 3 }}>
            <InputLabel>{question.text}</InputLabel>
            <Select
              value={value}
              onChange={(e) => handleAnswerChange(question.key, e.target.value)}
              required={question.is_required}
              label={question.text}
            >
              {question.options?.map(option => (
                <MenuItem key={option} value={option}>{option}</MenuItem>
              ))}
            </Select>
            {question.help_text && (
              <FormHelperText>{question.help_text}</FormHelperText>
            )}
          </FormControl>
        );

      case 'date':
        return (
          <TextField
            key={question.key}
            fullWidth
            type="date"
            label={question.text}
            value={value}
            onChange={(e) => handleAnswerChange(question.key, e.target.value)}
            required={question.is_required}
            InputLabelProps={{ shrink: true }}
            helperText={question.help_text}
            sx={{ mb: 3 }}
          />
        );

      default:
        return null;
    }
  };

  const renderSection = () => {
    const currentCategories = sectionMapping[activeStep];
    
    return (
      <Box sx={{ minHeight: 400, py: 2 }}>
        {activeStep === 0 && (
          // Section 1: Personal Information
          <Box>
            <Alert severity="info" icon={<InfoIcon />} sx={{ mb: 3 }}>
              All personal information fields are required
            </Alert>
            {questions.personal?.map(renderQuestion)}
          </Box>
        )}

        {activeStep === 1 && (
          // Section 2: Travel Information (Collapsible boxes)
          <Box>
            <Alert severity="info" icon={<InfoIcon />} sx={{ mb: 3 }}>
              You can skip sections if you've already uploaded those documents
            </Alert>
            
            {/* Travel Itinerary Box */}
            {questions.travel_itinerary && (
              <Accordion defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <TravelIcon color="primary" />
                    <Typography variant="h6">Travel Itinerary</Typography>
                    <Chip 
                      label="Skip if uploaded" 
                      size="small" 
                      color="warning"
                      variant="outlined"
                    />
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  {questions.travel_itinerary.map(renderQuestion)}
                </AccordionDetails>
              </Accordion>
            )}

            {/* Hotel Booking Box */}
            {questions.hotel_booking && (
              <Accordion sx={{ mt: 2 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <HotelIcon color="primary" />
                    <Typography variant="h6">Hotel Booking</Typography>
                    <Chip 
                      label="Skip if uploaded" 
                      size="small" 
                      color="warning"
                      variant="outlined"
                    />
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  {questions.hotel_booking.map(renderQuestion)}
                </AccordionDetails>
              </Accordion>
            )}

            {/* Air Ticket Box */}
            {questions.air_ticket && (
              <Accordion sx={{ mt: 2 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <FlightIcon color="primary" />
                    <Typography variant="h6">Air Ticket</Typography>
                    <Chip 
                      label="Skip if uploaded" 
                      size="small" 
                      color="warning"
                      variant="outlined"
                    />
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  {questions.air_ticket.map(renderQuestion)}
                </AccordionDetails>
              </Accordion>
            )}

            {!questions.travel_itinerary && !questions.hotel_booking && !questions.air_ticket && (
              <Alert severity="success" icon={<CheckCircleIcon />}>
                All travel documents uploaded - you can skip this section!
              </Alert>
            )}
          </Box>
        )}

        {activeStep === 2 && (
          // Section 3: Financial/Assets
          <Box>
            <Alert severity="info" icon={<MoneyIcon />} sx={{ mb: 3 }}>
              These questions help generate your Asset Valuation certificate
            </Alert>
            
            {questions.assets && (
              <>
                <Typography variant="h6" sx={{ mb: 2 }}>Property & Assets</Typography>
                {questions.assets.map(renderQuestion)}
                <Divider sx={{ my: 3 }} />
              </>
            )}
            
            {questions.financial && (
              <>
                <Typography variant="h6" sx={{ mb: 2 }}>Employment & Income</Typography>
                {questions.financial.map(renderQuestion)}
                <Divider sx={{ my: 3 }} />
              </>
            )}
            
            {questions.home_ties && (
              <>
                <Typography variant="h6" sx={{ mb: 2 }}>Home Country Ties</Typography>
                {questions.home_ties.map(renderQuestion)}
              </>
            )}
          </Box>
        )}

        {activeStep === 3 && (
          // Section 4: Other Information
          <Box>
            <Alert severity="info" icon={<InfoIcon />} sx={{ mb: 3 }}>
              All fields in this section are optional
            </Alert>
            {questions.other?.map(renderQuestion)}
          </Box>
        )}
      </Box>
    );
  };

  if (loading) {
    return (
      <Dialog open={open} maxWidth="md" fullWidth>
        <DialogContent sx={{ textAlign: 'center', py: 5 }}>
          <CircularProgress />
          <Typography sx={{ mt: 2 }}>Loading questionnaire...</Typography>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="md" 
      fullWidth
      PaperProps={{ sx: { height: '90vh' } }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h5">Complete Your Application</Typography>
          <Chip 
            label={`Step ${activeStep + 1} of ${steps.length}`} 
            color="primary"
          />
        </Box>
      </DialogTitle>

      <Stepper activeStep={activeStep} sx={{ px: 3, pt: 2 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      <DialogContent dividers sx={{ bgcolor: 'grey.50' }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {renderSection()}
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button onClick={onClose} disabled={saving}>
          Cancel
        </Button>
        <Box sx={{ flex: 1 }} />
        
        {activeStep > 0 && (
          <Button
            startIcon={<BackIcon />}
            onClick={handleBack}
            disabled={saving}
          >
            Back
          </Button>
        )}
        
        {activeStep < steps.length - 1 ? (
          <Button
            variant="contained"
            endIcon={<NextIcon />}
            onClick={handleNext}
            disabled={saving}
          >
            Next
          </Button>
        ) : (
          <Button
            variant="contained"
            color="success"
            startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Complete Questionnaire'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default SimpleQuestionnaireWizard;

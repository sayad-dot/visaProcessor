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
  RadioGroup,
  Radio,
  Typography,
  Alert,
  CircularProgress,
  Chip,
  LinearProgress,
  IconButton,
  FormHelperText
} from '@mui/material';
import {
  NavigateNext as NextIcon,
  NavigateBefore as BackIcon,
  Save as SaveIcon,
  Close as CloseIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

/**
 * QuestionnaireWizard Component
 * Multi-step form for answering generated questions
 */
const QuestionnaireWizard = ({ open, onClose, applicationId, onComplete }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [questions, setQuestions] = useState({});
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(null);

  const categoryNames = {
    personal: 'Personal Information',
    profession_determination: 'Profession Type',
    employment: 'Employment Details',
    business: 'Business Details',
    travel_purpose: 'Travel Purpose',
    financial: 'Financial Information',
    assets: 'Assets & Property',
    home_ties: 'Home Country Ties'
  };

  const categoryOrder = [
    'personal',
    'profession_determination',
    'employment',
    'business',
    'travel_purpose',
    'financial',
    'assets',
    'home_ties'
  ];

  // Load questions and existing answers
  useEffect(() => {
    if (open && applicationId) {
      loadQuestionnaire();
      loadExistingAnswers();
      loadProgress();
    }
  }, [open, applicationId]);

  const loadQuestionnaire = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`http://localhost:8000/api/questionnaire/generate/${applicationId}`);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to load questionnaire');
      }

      const data = await response.json();
      setQuestions(data);
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
        
        // Convert to flat object keyed by question_key
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
      // Silently handle 404 - no responses yet
    } catch (err) {
      // No responses yet, that's fine - don't log error
    }
  };

  const loadProgress = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/questionnaire/progress/${applicationId}`);
      if (response.ok) {
        const data = await response.json();
        setProgress(data);
      }
      // Silently handle 404 - no progress yet
    } catch (err) {
      // No progress yet, that's fine - don't log error
    }
  };

  const handleAnswerChange = (questionKey, value) => {
    setAnswers(prev => ({
      ...prev,
      [questionKey]: value
    }));
  };

  const saveAnswers = async (moveNext = false) => {
    try {
      setSaving(true);
      setError(null);

      // Get current category questions
      const currentCategory = categoryOrder[activeStep];
      const categoryQuestions = questions[currentCategory] || [];

      // Prepare responses for current category
      const responses = categoryQuestions
        .filter(q => answers[q.key] !== undefined && answers[q.key] !== '')
        .map(q => ({
          question_key: q.key,
          answer: String(answers[q.key])
        }));

      if (responses.length > 0) {
        const response = await fetch(`http://localhost:8000/api/questionnaire/response/${applicationId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ responses })
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to save answers');
        }

        await loadProgress();
      }

      if (moveNext) {
        handleNext();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const validateCurrentStep = () => {
    const currentCategory = categoryOrder[activeStep];
    const categoryQuestions = questions[currentCategory] || [];
    
    // Check required questions
    const requiredQuestions = categoryQuestions.filter(q => q.is_required);
    const allRequiredAnswered = requiredQuestions.every(q => {
      const answer = answers[q.key];
      return answer !== undefined && answer !== '';
    });

    return allRequiredAnswered;
  };

  const handleNext = () => {
    if (activeStep < categoryOrder.length - 1) {
      setActiveStep(prev => prev + 1);
    }
  };

  const handleBack = () => {
    if (activeStep > 0) {
      setActiveStep(prev => prev - 1);
    }
  };

  const handleComplete = async () => {
    await saveAnswers(false);
    if (onComplete) {
      onComplete();
    }
    onClose();
  };

  const renderQuestion = (question) => {
    const value = answers[question.key] || '';

    switch (question.data_type) {
      case 'text':
      case 'number':
        return (
          <TextField
            fullWidth
            label={question.text}
            value={value}
            onChange={(e) => handleAnswerChange(question.key, e.target.value)}
            required={question.is_required}
            type={question.data_type === 'number' ? 'number' : 'text'}
            placeholder={question.placeholder}
            helperText={question.help_text}
            margin="normal"
          />
        );

      case 'textarea':
        return (
          <TextField
            fullWidth
            label={question.text}
            value={value}
            onChange={(e) => handleAnswerChange(question.key, e.target.value)}
            required={question.is_required}
            multiline
            rows={4}
            placeholder={question.placeholder}
            helperText={question.help_text}
            margin="normal"
          />
        );

      case 'date':
        return (
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <DatePicker
              label={question.text}
              value={value ? new Date(value) : null}
              onChange={(date) => handleAnswerChange(question.key, date ? date.toISOString().split('T')[0] : '')}
              slotProps={{
                textField: {
                  fullWidth: true,
                  required: question.is_required,
                  helperText: question.help_text,
                  margin: 'normal'
                }
              }}
            />
          </LocalizationProvider>
        );

      case 'select':
        return (
          <FormControl fullWidth margin="normal" required={question.is_required}>
            <InputLabel>{question.text}</InputLabel>
            <Select
              value={value}
              onChange={(e) => handleAnswerChange(question.key, e.target.value)}
              label={question.text}
            >
              {question.options?.map(option => (
                <MenuItem key={option} value={option}>
                  {option}
                </MenuItem>
              ))}
            </Select>
            {question.help_text && (
              <FormHelperText>{question.help_text}</FormHelperText>
            )}
          </FormControl>
        );

      case 'boolean':
        return (
          <FormControl component="fieldset" margin="normal" fullWidth>
            <Typography variant="body1" gutterBottom>
              {question.text} {question.is_required && <span style={{ color: 'red' }}>*</span>}
            </Typography>
            <RadioGroup
              value={value}
              onChange={(e) => handleAnswerChange(question.key, e.target.value)}
            >
              <FormControlLabel value="yes" control={<Radio />} label="Yes" />
              <FormControlLabel value="no" control={<Radio />} label="No" />
            </RadioGroup>
            {question.help_text && (
              <FormHelperText>{question.help_text}</FormHelperText>
            )}
          </FormControl>
        );

      default:
        return (
          <TextField
            fullWidth
            label={question.text}
            value={value}
            onChange={(e) => handleAnswerChange(question.key, e.target.value)}
            required={question.is_required}
            helperText={question.help_text}
            margin="normal"
          />
        );
    }
  };

  const currentCategory = categoryOrder[activeStep];
  const categoryQuestions = questions[currentCategory] || [];
  const isLastStep = activeStep === categoryOrder.length - 1;
  const canProceed = validateCurrentStep();

  // Filter out empty categories
  const availableSteps = categoryOrder.filter(cat => questions[cat]?.length > 0);

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { minHeight: '80vh' }
      }}
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box>
          <Typography variant="h5">Application Questionnaire</Typography>
          {progress && (
            <Typography variant="caption" color="text.secondary">
              {progress.completion_percentage}% Complete • {progress.answered_questions} of {progress.total_questions} answered
            </Typography>
          )}
        </Box>
        <IconButton onClick={onClose}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      {/* Progress Bar */}
      {progress && (
        <LinearProgress 
          variant="determinate" 
          value={progress.completion_percentage || 0} 
          sx={{ height: 6 }}
        />
      )}

      <DialogContent sx={{ pt: 3 }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                {error}
              </Alert>
            )}

            {/* Stepper */}
            <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
              {availableSteps.map((category) => (
                <Step key={category}>
                  <StepLabel>{categoryNames[category] || category}</StepLabel>
                </Step>
              ))}
            </Stepper>

            {/* Current Category Title */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                {categoryNames[currentCategory]}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {categoryQuestions.filter(q => q.is_required).length} required questions
              </Typography>
            </Box>

            {/* Questions */}
            {categoryQuestions.length === 0 ? (
              <Alert severity="info">
                No questions in this category. Click Next to continue.
              </Alert>
            ) : (
              <Box>
                {categoryQuestions.map((question) => (
                  <Box key={question.key} sx={{ mb: 2 }}>
                    {renderQuestion(question)}
                  </Box>
                ))}
              </Box>
            )}
          </>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2, justifyContent: 'space-between' }}>
        <Button
          onClick={handleBack}
          disabled={activeStep === 0 || saving}
          startIcon={<BackIcon />}
        >
          Back
        </Button>

        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            onClick={() => saveAnswers(false)}
            disabled={saving || loading}
            startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
            variant="outlined"
          >
            Save Progress
          </Button>

          {!isLastStep ? (
            <Button
              onClick={() => saveAnswers(true)}
              disabled={!canProceed || saving || loading}
              endIcon={<NextIcon />}
              variant="contained"
            >
              Next
            </Button>
          ) : (
            <Button
              onClick={handleComplete}
              disabled={!canProceed || saving || loading}
              endIcon={<CheckCircleIcon />}
              variant="contained"
              color="success"
            >
              Complete
            </Button>
          )}
        </Box>
      </DialogActions>
    </Dialog>
  );
};

export default QuestionnaireWizard;

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
  Typography,
  Alert,
  CircularProgress,
  Chip,
  LinearProgress,
  Paper
} from '@mui/material';
import {
  NavigateNext as NextIcon,
  NavigateBefore as BackIcon,
  Save as SaveIcon,
  Close as CloseIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon
} from '@mui/icons-material';
import { questionnaireService } from '../services/apiService';

/**
 * DEMO VERSION - QuestionnaireWizard with Mock API
 */
const QuestionnaireWizard = ({ open, onClose, applicationId, onComplete }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [questions, setQuestions] = useState({});
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState({ answered: 0, total: 0 });

  useEffect(() => {
    if (open) {
      loadQuestionnaire();
    }
  }, [open, applicationId]);

  const loadQuestionnaire = async () => {
    try {
      setLoading(true);
      setError(null);

      // Use mock API service
      const data = await questionnaireService.getQuestionnaire(applicationId);
      
      // Remove metadata fields
      const { total_questions, note, ...questionData } = data;
      setQuestions(questionData);
      calculateProgress(questionData, {});
      setLoading(false);

    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const calculateProgress = (questionsData, answersData) => {
    const totalQuestions = Object.values(questionsData).reduce((sum, categoryQuestions) => 
      sum + categoryQuestions.length, 0
    );
    const answeredQuestions = Object.keys(answersData).filter(key => 
      answersData[key] && answersData[key].toString().trim() !== ''
    ).length;
    
    setProgress({ answered: answeredQuestions, total: totalQuestions });
  };

  const handleAnswerChange = (questionKey, value) => {
    const newAnswers = { ...answers, [questionKey]: value };
    setAnswers(newAnswers);
    calculateProgress(questions, newAnswers);
  };

  const handleNext = () => {
    if (activeStep < categories.length - 1) {
      setActiveStep(activeStep + 1);
    }
  };

  const handleBack = () => {
    if (activeStep > 0) {
      setActiveStep(activeStep - 1);
    }
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      
      // Convert answers to API format
      const responses = Object.entries(answers).map(([key, value]) => ({
        question_key: key,
        answer: value
      }));

      // Save via API service
      await questionnaireService.saveResponses(applicationId, responses);
      
      setLoading(false);
      onComplete && onComplete(answers);
      onClose();
      
    } catch (err) {
      setError('Failed to save responses');
      setLoading(false);
    }
  };

  const renderQuestion = (question) => {
    const value = answers[question.key] || '';

    switch (question.data_type) {
      case 'textarea':
        return (
          <TextField
            fullWidth
            multiline
            rows={4}
            label={question.text}
            placeholder={question.placeholder}
            value={value}
            onChange={(e) => handleAnswerChange(question.key, e.target.value)}
            variant="outlined"
            size="small"
          />
        );
      
      case 'number':
        return (
          <TextField
            fullWidth
            type="number"
            label={question.text}
            placeholder={question.placeholder}
            value={value}
            onChange={(e) => handleAnswerChange(question.key, e.target.value)}
            variant="outlined"
            size="small"
          />
        );
      
      case 'select':
        return (
          <TextField
            fullWidth
            select
            label={question.text}
            value={value}
            onChange={(e) => handleAnswerChange(question.key, e.target.value)}
            variant="outlined"
            size="small"
            SelectProps={{ native: true }}
          >
            <option value="">Select an option</option>
            {question.options?.map((option, idx) => (
              <option key={idx} value={option}>{option}</option>
            ))}
          </TextField>
        );
      
      default:
        return (
          <TextField
            fullWidth
            label={question.text}
            placeholder={question.placeholder}
            value={value}
            onChange={(e) => handleAnswerChange(question.key, e.target.value)}
            variant="outlined"
            size="small"
          />
        );
    }
  };

  if (!open) return null;

  const categories = Object.keys(questions);
  const currentCategory = categories[activeStep];
  const currentQuestions = questions[currentCategory] || [];
  const completionPercentage = progress.total > 0 ? (progress.answered / progress.total) * 100 : 0;

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="md" 
      fullWidth
      PaperProps={{
        sx: { minHeight: '70vh' }
      }}
    >
      <DialogTitle sx={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <Box display="flex" alignItems="center" gap={1}>
          <CheckCircleIcon />
          <Typography variant="h6">Document Information Questionnaire</Typography>
        </Box>
        <Chip 
          label={`${Math.round(completionPercentage)}% Complete`}
          sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
        />
      </DialogTitle>

      <DialogContent sx={{ p: 3 }}>
        {/* Progress Bar */}
        <Box mb={3}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="body2" color="textSecondary">
              Progress: {progress.answered} of {progress.total} questions answered
            </Typography>
            <Typography variant="body2" color="primary" fontWeight="bold">
              {Math.round(completionPercentage)}%
            </Typography>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={completionPercentage}
            sx={{ height: 8, borderRadius: 4 }}
          />
          {completionPercentage < 50 && (
            <Alert severity="info" sx={{ mt: 1 }}>
              <WarningIcon sx={{ mr: 1 }} />
              You've completed {Math.round(completionPercentage)}% of questions. 
              Consider answering more for better document generation.
            </Alert>
          )}
        </Box>

        {loading ? (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="300px">
            <CircularProgress size={40} />
            <Typography variant="body1" sx={{ ml: 2 }}>
              Loading questionnaire...
            </Typography>
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        ) : categories.length > 0 ? (
          <>
            {/* Stepper */}
            <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 4 }}>
              {categories.map((category, index) => (
                <Step key={category}>
                  <StepLabel>{category}</StepLabel>
                </Step>
              ))}
            </Stepper>

            {/* Current Category Questions */}
            <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom color="primary">
                {currentCategory}
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
                All questions are optional. Answer only what you're comfortable sharing.
              </Typography>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                {currentQuestions.map((question, index) => (
                  <Box key={question.key}>
                    <Typography variant="body2" sx={{ mb: 1, display: 'flex', alignItems: 'center' }}>
                      <Typography component="span" sx={{ flexGrow: 1 }}>
                        {index + 1}. {question.text}
                      </Typography>
                      <Chip 
                        label="Optional" 
                        size="small" 
                        color="default" 
                        variant="outlined"
                      />
                    </Typography>
                    {renderQuestion(question)}
                  </Box>
                ))}
              </Box>
            </Paper>
          </>
        ) : (
          <Alert severity="info">
            No additional questions needed at this time. All required information has been extracted from your uploaded documents.
          </Alert>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button 
          onClick={onClose}
          startIcon={<CloseIcon />}
          variant="outlined"
        >
          Close
        </Button>
        
        {categories.length > 0 && (
          <>
            <Button
              onClick={handleBack}
              disabled={activeStep === 0}
              startIcon={<BackIcon />}
            >
              Back
            </Button>
            
            {activeStep < categories.length - 1 ? (
              <Button
                onClick={handleNext}
                variant="contained"
                endIcon={<NextIcon />}
              >
                Next
              </Button>
            ) : (
              <Button
                onClick={handleSubmit}
                variant="contained"
                startIcon={<SaveIcon />}
                disabled={loading}
              >
                {loading ? <CircularProgress size={20} /> : 'Save Responses'}
              </Button>
            )}
          </>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default QuestionnaireWizard;
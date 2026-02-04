import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  IconButton,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent,
  Divider,
  Alert,
  CircularProgress,
  Tooltip,
  Badge,
  Stack,
  Paper,
  Grid,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  AutoAwesome as AutoFillIcon,
  Check as CheckIcon,
  Info as InfoIcon,
  Star as StarIcon,
  LightbulbOutlined as SuggestedIcon,
  HelpOutline as OptionalIcon,
  NavigateNext as NextIcon,
  NavigateBefore as BackIcon,
  Save as SaveIcon
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import { API_BASE_URL } from '../config';

const SmartQuestionnaireWizard = ({ open, onClose, applicationId, onComplete }) => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [autoFilling, setAutoFilling] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [questionnaire, setQuestionnaire] = useState(null);
  const [answers, setAnswers] = useState({});
  const [progress, setProgress] = useState(null);
  const [errors, setErrors] = useState({});

  // Fetch questionnaire structure on mount
  useEffect(() => {
    if (open && applicationId) {
      fetchQuestionnaire();
      loadSavedAnswers();
    }
  }, [open, applicationId]);

  const fetchQuestionnaire = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/questionnaire/smart-generate/${applicationId}`);
      if (!response.ok) throw new Error('Failed to fetch questionnaire');
      const data = await response.json();
      setQuestionnaire(data.questionnaire);
    } catch (error) {
      toast.error('Failed to load questionnaire');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const loadSavedAnswers = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/questionnaire/smart-load/${applicationId}`);
      if (response.ok) {
        const data = await response.json();
        if (data.answers) {
          setAnswers(data.answers);
          setProgress(data.progress);
        }
      }
    } catch (error) {
      console.log('No saved answers yet');
    }
  };

  const handleAutoFill = async () => {
    if (!window.confirm('Auto-fill will generate realistic data for all missing fields. Continue?')) {
      return;
    }

    try {
      setAutoFilling(true);
      const response = await fetch(`${API_BASE_URL}/questionnaire/smart-auto-fill/${applicationId}`, {
        method: 'POST'
      });
      
      if (!response.ok) throw new Error('Auto-fill failed');
      
      const data = await response.json();
      setAnswers(data.filled_answers);
      
      toast.success(`✨ Auto-filled ${data.summary.auto_filled_count} fields!`);
    } catch (error) {
      toast.error('Auto-fill failed');
      console.error(error);
    } finally {
      setAutoFilling(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      const response = await fetch(`${API_BASE_URL}/questionnaire/smart-save/${applicationId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(answers)
      });

      if (!response.ok) throw new Error('Save failed');
      
      const data = await response.json();
      setProgress(data.progress);
      
      if (data.errors && data.errors.length > 0) {
        toast.warning(`Saved with ${data.errors.length} validation errors`);
        // Set errors for display
        const errorMap = {};
        data.errors.forEach(err => {
          errorMap[err.question] = err.error;
        });
        setErrors(errorMap);
      } else {
        toast.success('Saved successfully!');
        setErrors({});
      }
    } catch (error) {
      toast.error('Failed to save');
      console.error(error);
    } finally {
      setSaving(false);
    }
  };

  const handleComplete = async () => {
    await handleSave();
    
    if (progress && progress.required_percentage === 100) {
      toast.success('Questionnaire completed!');
      onComplete?.();
      onClose();
    } else {
      toast.warning('Please fill all required fields before completing');
    }
  };

  const handleChange = (key, value) => {
    setAnswers(prev => ({
      ...prev,
      [key]: value
    }));
    // Clear error when user types
    if (errors[key]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[key];
        return newErrors;
      });
    }
  };

  const handleArrayAdd = (key) => {
    const currentArray = answers[key] || [];
    setAnswers(prev => ({
      ...prev,
      [key]: [...currentArray, {}]
    }));
  };

  const handleArrayRemove = (key, index) => {
    const currentArray = answers[key] || [];
    const newArray = currentArray.filter((_, i) => i !== index);
    setAnswers(prev => ({
      ...prev,
      [key]: newArray
    }));
  };

  const handleArrayChange = (key, index, fieldKey, value) => {
    const currentArray = answers[key] || [];
    const newArray = [...currentArray];
    newArray[index] = {
      ...newArray[index],
      [fieldKey]: value
    };
    setAnswers(prev => ({
      ...prev,
      [key]: newArray
    }));
  };

  const checkCondition = (condition) => {
    if (!condition) return true;
    
    const { show_if } = condition;
    if (!show_if) return true;
    
    // Check if condition is met
    const conditionKey = Object.keys(show_if)[0];
    const conditionValue = show_if[conditionKey];
    const currentValue = answers[conditionKey];
    
    if (Array.isArray(conditionValue)) {
      return conditionValue.includes(currentValue);
    }
    
    return currentValue === conditionValue;
  };

  const getLevelBadge = (question) => {
    if (question.required) {
      return (
        <Chip
          label="Required *"
          size="small"
          icon={<StarIcon sx={{ fontSize: 14 }} />}
          color="error"
          sx={{ ml: 1, fontWeight: 600 }}
        />
      );
    } else if (question.level === 'suggested') {
      return (
        <Chip
          label="Suggested"
          size="small"
          icon={<SuggestedIcon sx={{ fontSize: 14 }} />}
          color="warning"
          sx={{ ml: 1, fontWeight: 500 }}
        />
      );
    } else {
      return (
        <Chip
          label="Optional"
          size="small"
          icon={<OptionalIcon sx={{ fontSize: 14 }} />}
          color="info"
          sx={{ ml: 1, fontWeight: 400 }}
        />
      );
    }
  };

  const renderQuestion = (question) => {
    // Check conditional display
    if (!checkCondition({ show_if: question.show_if })) {
      return null;
    }

    const value = answers[question.key] || '';
    const error = errors[question.key];

    return (
      <Box key={question.key} sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Typography variant="body1" sx={{ fontWeight: 500 }}>
            {question.label}
          </Typography>
          {getLevelBadge(question)}
        </Box>

        {question.hint && (
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
            💡 {question.hint}
          </Typography>
        )}

        {question.type === 'text' && (
          <TextField
            fullWidth
            value={value}
            onChange={(e) => handleChange(question.key, e.target.value)}
            placeholder={question.placeholder}
            error={!!error}
            helperText={error}
            size="small"
          />
        )}

        {question.type === 'email' && (
          <TextField
            fullWidth
            type="email"
            value={value}
            onChange={(e) => handleChange(question.key, e.target.value)}
            placeholder={question.placeholder}
            error={!!error}
            helperText={error}
            size="small"
          />
        )}

        {question.type === 'tel' && (
          <TextField
            fullWidth
            type="tel"
            value={value}
            onChange={(e) => handleChange(question.key, e.target.value)}
            placeholder={question.placeholder}
            error={!!error}
            helperText={error}
            size="small"
          />
        )}

        {question.type === 'number' && (
          <TextField
            fullWidth
            type="number"
            value={value}
            onChange={(e) => handleChange(question.key, e.target.value)}
            placeholder={question.placeholder}
            error={!!error}
            helperText={error}
            size="small"
            inputProps={{
              min: question.validation?.min,
              max: question.validation?.max
            }}
          />
        )}

        {question.type === 'date' && (
          <TextField
            fullWidth
            type="date"
            value={value}
            onChange={(e) => handleChange(question.key, e.target.value)}
            error={!!error}
            helperText={error}
            size="small"
            InputLabelProps={{ shrink: true }}
          />
        )}

        {question.type === 'textarea' && (
          <TextField
            fullWidth
            multiline
            rows={question.rows || 3}
            value={value}
            onChange={(e) => handleChange(question.key, e.target.value)}
            placeholder={question.placeholder}
            error={!!error}
            helperText={error}
            size="small"
          />
        )}

        {question.type === 'select' && (
          <FormControl fullWidth size="small" error={!!error}>
            <Select
              value={value}
              onChange={(e) => handleChange(question.key, e.target.value)}
            >
              <MenuItem value="">Select...</MenuItem>
              {question.options?.map(opt => (
                <MenuItem key={opt} value={opt}>{opt}</MenuItem>
              ))}
            </Select>
            {error && <Typography variant="caption" color="error">{error}</Typography>}
          </FormControl>
        )}

        {question.type === 'boolean' && (
          <FormControl fullWidth size="small">
            <Select
              value={value}
              onChange={(e) => handleChange(question.key, e.target.value)}
            >
              <MenuItem value="">Select...</MenuItem>
              {question.options?.map(opt => (
                <MenuItem key={opt} value={opt}>{opt}</MenuItem>
              ))}
            </Select>
          </FormControl>
        )}

        {question.type === 'array' && renderArrayField(question)}
      </Box>
    );
  };

  const renderArrayField = (question) => {
    const array = answers[question.key] || [];

    return (
      <Box sx={{ mt: 1 }}>
        {array.map((item, index) => (
          <Card key={index} sx={{ mb: 2, bgcolor: 'grey.50' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="subtitle2" color="primary">
                  {question.label} #{index + 1}
                </Typography>
                <IconButton
                  size="small"
                  color="error"
                  onClick={() => handleArrayRemove(question.key, index)}
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </Box>

              <Grid container spacing={2}>
                {question.fields?.map(field => (
                  <Grid item xs={12} sm={field.type === 'textarea' ? 12 : 6} key={field.key}>
                    <Typography variant="caption" color="text.secondary">
                      {field.label}
                    </Typography>
                    {field.type === 'select' ? (
                      <Select
                        fullWidth
                        size="small"
                        value={item[field.key] || ''}
                        onChange={(e) => handleArrayChange(question.key, index, field.key, e.target.value)}
                      >
                        <MenuItem value="">Select...</MenuItem>
                        {field.options?.map(opt => (
                          <MenuItem key={opt} value={opt}>{opt}</MenuItem>
                        ))}
                      </Select>
                    ) : field.type === 'number' ? (
                      <TextField
                        fullWidth
                        type="number"
                        size="small"
                        value={item[field.key] || ''}
                        onChange={(e) => handleArrayChange(question.key, index, field.key, e.target.value)}
                        placeholder={field.placeholder}
                        inputProps={{
                          min: field.validation?.min,
                          max: field.validation?.max
                        }}
                      />
                    ) : field.type === 'date' ? (
                      <TextField
                        fullWidth
                        type="date"
                        size="small"
                        value={item[field.key] || ''}
                        onChange={(e) => handleArrayChange(question.key, index, field.key, e.target.value)}
                        InputLabelProps={{ shrink: true }}
                      />
                    ) : field.type === 'textarea' ? (
                      <TextField
                        fullWidth
                        multiline
                        rows={2}
                        size="small"
                        value={item[field.key] || ''}
                        onChange={(e) => handleArrayChange(question.key, index, field.key, e.target.value)}
                        placeholder={field.placeholder}
                      />
                    ) : (
                      <TextField
                        fullWidth
                        size="small"
                        value={item[field.key] || ''}
                        onChange={(e) => handleArrayChange(question.key, index, field.key, e.target.value)}
                        placeholder={field.placeholder}
                      />
                    )}
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        ))}

        <Button
          startIcon={<AddIcon />}
          onClick={() => handleArrayAdd(question.key)}
          variant="outlined"
          size="small"
        >
          Add {question.label}
        </Button>

        {question.hint && (
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
            💡 {question.hint}
          </Typography>
        )}
      </Box>
    );
  };

  const renderSection = (sectionKey) => {
    const section = questionnaire?.[sectionKey];
    if (!section) return null;

    return (
      <Box>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5" sx={{ fontSize: '2rem', mr: 1 }}>
            {section.icon}
          </Typography>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              {section.title}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {section.description}
            </Typography>
          </Box>
        </Box>

        {section.questions?.map(question => renderQuestion(question))}
      </Box>
    );
  };

  if (loading) {
    return (
      <Dialog open={open} maxWidth="md" fullWidth>
        <DialogContent>
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 200 }}>
            <CircularProgress />
          </Box>
        </DialogContent>
      </Dialog>
    );
  }

  if (!questionnaire) return null;

  const sections = Object.keys(questionnaire);
  const currentSection = sections[activeStep];

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Smart Questionnaire
          </Typography>
          <Button
            variant="contained"
            size="small"
            startIcon={autoFilling ? <CircularProgress size={16} color="inherit" /> : <AutoFillIcon />}
            onClick={handleAutoFill}
            disabled={autoFilling}
            sx={{
              background: 'linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)',
              boxShadow: '0 3px 5px 2px rgba(255, 105, 135, .3)'
            }}
          >
            {autoFilling ? 'Auto-filling...' : '✨ Auto-fill Missing Fields'}
          </Button>
        </Box>

        {progress && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="caption" color="text.secondary">
              Progress: {progress.answered_questions}/{progress.total_questions} questions •{' '}
              Required: {progress.answered_required}/{progress.total_required}
              {' '}({Math.round(progress.required_percentage)}%)
            </Typography>
            <Box sx={{ 
              mt: 0.5, 
              height: 6, 
              bgcolor: 'grey.200', 
              borderRadius: 1,
              overflow: 'hidden'
            }}>
              <Box sx={{ 
                height: '100%', 
                width: `${progress.required_percentage}%`,
                bgcolor: progress.is_complete ? 'success.main' : 'primary.main',
                transition: 'width 0.3s ease'
              }} />
            </Box>
          </Box>
        )}
      </DialogTitle>

      <DialogContent dividers sx={{ minHeight: 500 }}>
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {sections.map((sectionKey) => (
            <Step key={sectionKey}>
              <StepLabel>{questionnaire[sectionKey].title}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {renderSection(currentSection)}
      </DialogContent>

      <DialogActions sx={{ p: 2, justifyContent: 'space-between' }}>
        <Button onClick={onClose} color="inherit">
          Close
        </Button>

        <Box>
          <Button
            disabled={activeStep === 0}
            onClick={() => setActiveStep(prev => prev - 1)}
            startIcon={<BackIcon />}
            sx={{ mr: 1 }}
          >
            Back
          </Button>

          <Button
            variant="outlined"
            startIcon={saving ? <CircularProgress size={16} /> : <SaveIcon />}
            onClick={handleSave}
            disabled={saving}
            sx={{ mr: 1 }}
          >
            {saving ? 'Saving...' : 'Save Progress'}
          </Button>

          {activeStep < sections.length - 1 ? (
            <Button
              variant="contained"
              onClick={() => setActiveStep(prev => prev + 1)}
              endIcon={<NextIcon />}
            >
              Next
            </Button>
          ) : (
            <Button
              variant="contained"
              color="success"
              onClick={handleComplete}
              startIcon={<CheckIcon />}
            >
              Complete
            </Button>
          )}
        </Box>
      </DialogActions>
    </Dialog>
  );
};

export default SmartQuestionnaireWizard;

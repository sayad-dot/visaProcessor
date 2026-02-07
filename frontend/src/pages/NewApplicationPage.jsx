import React, { useState } from 'react'
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Autocomplete,
  Chip,
  Grid,
} from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import PersonIcon from '@mui/icons-material/Person'
import FlightTakeoffIcon from '@mui/icons-material/FlightTakeoff'
import { applicationService } from '../services/apiService'

// Country options - 20 EU Schengen + 20 popular destinations
const COUNTRIES = [
  // European Schengen Countries (20)
  { label: 'Iceland 🇮🇸', value: 'Iceland', region: 'Schengen', flag: '🇮🇸' },
  { label: 'Germany 🇩🇪', value: 'Germany', region: 'Schengen', flag: '🇩🇪' },
  { label: 'France 🇫🇷', value: 'France', region: 'Schengen', flag: '🇫🇷' },
  { label: 'Spain 🇪🇸', value: 'Spain', region: 'Schengen', flag: '🇪🇸' },
  { label: 'Italy 🇮🇹', value: 'Italy', region: 'Schengen', flag: '🇮🇹' },
  { label: 'Netherlands 🇳🇱', value: 'Netherlands', region: 'Schengen', flag: '🇳🇱' },
  { label: 'Belgium 🇧🇪', value: 'Belgium', region: 'Schengen', flag: '🇧🇪' },
  { label: 'Austria 🇦🇹', value: 'Austria', region: 'Schengen', flag: '🇦🇹' },
  { label: 'Switzerland 🇨🇭', value: 'Switzerland', region: 'Schengen', flag: '🇨🇭' },
  { label: 'Sweden 🇸🇪', value: 'Sweden', region: 'Schengen', flag: '🇸🇪' },
  { label: 'Norway 🇳🇴', value: 'Norway', region: 'Schengen', flag: '🇳🇴' },
  { label: 'Denmark 🇩🇰', value: 'Denmark', region: 'Schengen', flag: '🇩🇰' },
  { label: 'Finland 🇫🇮', value: 'Finland', region: 'Schengen', flag: '🇫🇮' },
  { label: 'Portugal 🇵🇹', value: 'Portugal', region: 'Schengen', flag: '🇵🇹' },
  { label: 'Greece 🇬🇷', value: 'Greece', region: 'Schengen', flag: '🇬🇷' },
  { label: 'Poland 🇵🇱', value: 'Poland', region: 'Schengen', flag: '🇵🇱' },
  { label: 'Czech Republic 🇨🇿', value: 'Czech Republic', region: 'Schengen', flag: '🇨🇿' },
  { label: 'Hungary 🇭🇺', value: 'Hungary', region: 'Schengen', flag: '🇭🇺' },
  { label: 'Malta 🇲🇹', value: 'Malta', region: 'Schengen', flag: '🇲🇹' },
  { label: 'Luxembourg 🇱🇺', value: 'Luxembourg', region: 'Schengen', flag: '🇱🇺' },
  
  // Popular Destinations (30 more)
  { label: 'United Kingdom 🇬🇧', value: 'United Kingdom', region: 'Europe', flag: '🇬🇧' },
  { label: 'United States 🇺🇸', value: 'United States', region: 'North America', flag: '🇺🇸' },
  { label: 'Canada 🇨🇦', value: 'Canada', region: 'North America', flag: '🇨🇦' },
  { label: 'Australia 🇦🇺', value: 'Australia', region: 'Oceania', flag: '🇦🇺' },
  { label: 'New Zealand 🇳🇿', value: 'New Zealand', region: 'Oceania', flag: '🇳🇿' },
  { label: 'Japan 🇯🇵', value: 'Japan', region: 'Asia', flag: '🇯🇵' },
  { label: 'South Korea 🇰🇷', value: 'South Korea', region: 'Asia', flag: '🇰🇷' },
  { label: 'Singapore 🇸🇬', value: 'Singapore', region: 'Asia', flag: '🇸🇬' },
  { label: 'Malaysia 🇲🇾', value: 'Malaysia', region: 'Asia', flag: '🇲🇾' },
  { label: 'Thailand 🇹🇭', value: 'Thailand', region: 'Asia', flag: '🇹🇭' },
  { label: 'United Arab Emirates 🇦🇪', value: 'United Arab Emirates', region: 'Middle East', flag: '🇦🇪' },
  { label: 'Saudi Arabia 🇸🇦', value: 'Saudi Arabia', region: 'Middle East', flag: '🇸🇦' },
  { label: 'Qatar 🇶🇦', value: 'Qatar', region: 'Middle East', flag: '🇶🇦' },
  { label: 'Turkey 🇹🇷', value: 'Turkey', region: 'Middle East', flag: '🇹🇷' },
  { label: 'India 🇮🇳', value: 'India', region: 'Asia', flag: '🇮🇳' },
  { label: 'China 🇨🇳', value: 'China', region: 'Asia', flag: '🇨🇳' },
  { label: 'Russia 🇷🇺', value: 'Russia', region: 'Europe/Asia', flag: '🇷🇺' },
  { label: 'South Africa 🇿🇦', value: 'South Africa', region: 'Africa', flag: '🇿🇦' },
  { label: 'Brazil 🇧🇷', value: 'Brazil', region: 'South America', flag: '🇧🇷' },
  { label: 'Mexico 🇲🇽', value: 'Mexico', region: 'North America', flag: '🇲🇽' },
  { label: 'Ireland 🇮🇪', value: 'Ireland', region: 'Europe', flag: '🇮🇪' },
  { label: 'Maldives 🇲🇻', value: 'Maldives', region: 'Asia', flag: '🇲🇻' },
  { label: 'Indonesia 🇮🇩', value: 'Indonesia', region: 'Asia', flag: '🇮🇩' },
  { label: 'Vietnam 🇻🇳', value: 'Vietnam', region: 'Asia', flag: '🇻🇳' },
  { label: 'Philippines 🇵🇭', value: 'Philippines', region: 'Asia', flag: '🇵🇭' },
  { label: 'Egypt 🇪🇬', value: 'Egypt', region: 'Africa', flag: '🇪🇬' },
  { label: 'Morocco 🇲🇦', value: 'Morocco', region: 'Africa', flag: '🇲🇦' },
  { label: 'Oman 🇴🇲', value: 'Oman', region: 'Middle East', flag: '🇴🇲' },
  { label: 'Kuwait 🇰🇼', value: 'Kuwait', region: 'Middle East', flag: '🇰🇼' },
  { label: 'Bahrain 🇧🇭', value: 'Bahrain', region: 'Middle East', flag: '🇧🇭' },
]

// Visa types
const VISA_TYPES = [
  { label: 'Tourist Visa', value: 'Tourist' },
  { label: 'Business Visa', value: 'Business' },
  { label: 'Student Visa', value: 'Student' },
  { label: 'Work Visa', value: 'Work' },
  { label: 'Permanent Residence', value: 'Permanent' },
]

// Applicant types
const APPLICANT_TYPES = [
  { label: 'Business Owner / Self-Employed', value: 'business' },
  { label: 'Job Holder / Employee', value: 'job' },
  { label: 'Student', value: 'student' },
]

const NewApplicationPage = () => {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    applicant_name: '',
    applicant_email: '',
    applicant_phone: '',
    country: 'Iceland',
    visa_type: 'Tourist',
    application_type: 'business'
  })
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleCountryChange = (event, newValue) => {
    setFormData({
      ...formData,
      country: newValue ? newValue.value : 'Iceland',
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    try {
      setLoading(true)
      const application = await applicationService.createApplication(formData)
      toast.success('Application created successfully!')
      navigate(`/application/${application.id}`)
    } catch (error) {
      toast.error('Failed to create application')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        {/* Page Header */}
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography 
            variant="h3" 
            component="h1" 
            sx={{ 
              fontWeight: 700,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              mb: 1
            }}
          >
            New Visa Application
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Fill in your details to start your visa application process
          </Typography>
        </Box>
        
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            {/* Left Side - Personal Information */}
            <Grid item xs={12} md={6}>
              <Paper 
                elevation={3}
                sx={{ 
                  p: 4,
                  height: '100%',
                  background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
                  borderRadius: 3,
                  position: 'relative',
                  overflow: 'hidden',
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    height: '5px',
                    background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                  }
                }}
              >
                {/* Section Header */}
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <Box
                    sx={{
                      width: 48,
                      height: 48,
                      borderRadius: '12px',
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mr: 2,
                      boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)'
                    }}
                  >
                    <PersonIcon sx={{ color: 'white', fontSize: 28 }} />
                  </Box>
                  <Box>
                    <Typography variant="h5" sx={{ fontWeight: 700, color: '#2d3748' }}>
                      Applicant Information
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Your personal details
                    </Typography>
                  </Box>
                </Box>
                
                {/* Input Fields */}
                <TextField
                  fullWidth
                  label="Full Name *"
                  name="applicant_name"
                  value={formData.applicant_name}
                  onChange={handleChange}
                  margin="normal"
                  required
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      backgroundColor: 'white',
                      '&:hover': {
                        backgroundColor: 'white',
                      },
                    },
                  }}
                />
                
                <TextField
                  fullWidth
                  label="Email Address *"
                  name="applicant_email"
                  type="email"
                  value={formData.applicant_email}
                  onChange={handleChange}
                  margin="normal"
                  required
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      backgroundColor: 'white',
                      '&:hover': {
                        backgroundColor: 'white',
                      },
                    },
                  }}
                />
                
                <TextField
                  fullWidth
                  label="Phone Number *"
                  name="applicant_phone"
                  value={formData.applicant_phone}
                  onChange={handleChange}
                  margin="normal"
                  required
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      backgroundColor: 'white',
                      '&:hover': {
                        backgroundColor: 'white',
                      },
                    },
                  }}
                />
              </Paper>
            </Grid>

            {/* Right Side - Visa Details */}
            <Grid item xs={12} md={6}>
              <Paper 
                elevation={3}
                sx={{ 
                  p: 4,
                  height: '100%',
                  background: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
                  borderRadius: 3,
                  position: 'relative',
                  overflow: 'hidden',
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    height: '5px',
                    background: 'linear-gradient(90deg, #f093fb 0%, #f5576c 100%)',
                  }
                }}
              >
                {/* Section Header */}
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <Box
                    sx={{
                      width: 48,
                      height: 48,
                      borderRadius: '12px',
                      background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mr: 2,
                      boxShadow: '0 4px 12px rgba(240, 147, 251, 0.4)'
                    }}
                  >
                    <FlightTakeoffIcon sx={{ color: 'white', fontSize: 28 }} />
                  </Box>
                  <Box>
                    <Typography variant="h5" sx={{ fontWeight: 700, color: '#2d3748' }}>
                      Visa Details
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Destination & visa information
                    </Typography>
                  </Box>
                </Box>
                
                {/* Country Selection */}
                <Box sx={{ mt: 2 }}>
                  <Autocomplete
                    options={COUNTRIES}
                    getOptionLabel={(option) => option.label}
                    groupBy={(option) => option.region}
                    value={COUNTRIES.find(c => c.value === formData.country) || COUNTRIES[0]}
                    onChange={handleCountryChange}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="Destination Country *"
                        placeholder="Search countries..."
                        margin="normal"
                        required
                        sx={{
                          '& .MuiOutlinedInput-root': {
                            backgroundColor: 'white',
                            '&:hover': {
                              backgroundColor: 'white',
                            },
                          },
                        }}
                      />
                    )}
                    renderOption={(props, option) => (
                      <li {...props}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <span style={{ fontSize: '1.5rem' }}>{option.flag}</span>
                          <span>{option.label.replace(option.flag, '').trim()}</span>
                          {option.region === 'Schengen' && (
                            <Chip
                              label="Schengen"
                              size="small"
                              color="primary"
                              sx={{ ml: 1, height: '20px' }}
                            />
                          )}
                        </Box>
                      </li>
                    )}
                  />
                  {formData.country !== 'Iceland' && (
                    <Typography variant="caption" color="error" sx={{ mt: 1, display: 'block', fontWeight: 600 }}>
                      ⚠️ Currently only Iceland is fully supported. Other countries coming soon!
                    </Typography>
                  )}
                </Box>
                
                {/* Visa Type Selection */}
                <FormControl 
                  fullWidth 
                  margin="normal"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      backgroundColor: 'white',
                      '&:hover': {
                        backgroundColor: 'white',
                      },
                    },
                  }}
                >
                  <InputLabel>Visa Type *</InputLabel>
                  <Select
                    name="visa_type"
                    value={formData.visa_type}
                    onChange={handleChange}
                    label="Visa Type *"
                  >
                    {VISA_TYPES.map((type) => (
                      <MenuItem key={type.value} value={type.value}>
                        {type.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                {formData.visa_type !== 'Tourist' && (
                  <Typography variant="caption" color="error" sx={{ mt: 0.5, display: 'block', fontWeight: 600 }}>
                    ⚠️ Currently only Tourist visa is fully supported
                  </Typography>
                )}
                
                {/* Applicant Type Selection */}
                <FormControl 
                  fullWidth 
                  margin="normal"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      backgroundColor: 'white',
                      '&:hover': {
                        backgroundColor: 'white',
                      },
                    },
                  }}
                >
                  <InputLabel>Applicant Type *</InputLabel>
                  <Select
                    name="application_type"
                    value={formData.application_type}
                    onChange={handleChange}
                    label="Applicant Type *"
                    required
                  >
                    {APPLICANT_TYPES.map((type) => (
                      <MenuItem key={type.value} value={type.value}>
                        {type.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                {formData.application_type === 'student' && (
                  <Typography variant="caption" color="error" sx={{ mt: 0.5, display: 'block', fontWeight: 600 }}>
                    ⚠️ Student applicant type coming soon
                  </Typography>
                )}
              </Paper>
            </Grid>
          </Grid>
          
          {/* Action Buttons */}
          <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center', gap: 2 }}>
            <Button
              variant="contained"
              type="submit"
              disabled={loading}
              size="large"
              sx={{
                px: 6,
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 600,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 8px 16px rgba(102, 126, 234, 0.4)',
                },
                transition: 'all 0.3s ease',
              }}
            >
              {loading ? 'Creating...' : 'CREATE APPLICATION'}
            </Button>
            <Button
              variant="outlined"
              onClick={() => navigate('/')}
              disabled={loading}
              size="large"
              sx={{
                px: 6,
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 600,
                borderWidth: 2,
                '&:hover': {
                  borderWidth: 2,
                  transform: 'translateY(-2px)',
                },
                transition: 'all 0.3s ease',
              }}
            >
              CANCEL
            </Button>
          </Box>
        </form>
      </Box>
    </Container>
  )
}

export default NewApplicationPage

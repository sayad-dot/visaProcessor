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
} from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import { applicationService } from '../services/apiService'

const NewApplicationPage = () => {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    applicant_name: '',
    applicant_email: '',
    applicant_phone: '',
    country: 'Iceland',
    visa_type: 'Tourist',
    application_type: 'business'  // NEW: Default to business
  })
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
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
    <Container maxWidth="md">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          New Visa Application
        </Typography>
        
        <Paper sx={{ p: 4, mt: 3 }}>
          <form onSubmit={handleSubmit}>
            <Typography variant="h6" gutterBottom>
              Applicant Information
            </Typography>
            
            <TextField
              fullWidth
              label="Full Name"
              name="applicant_name"
              value={formData.applicant_name}
              onChange={handleChange}
              margin="normal"
              required
            />
            
            <TextField
              fullWidth
              label="Email Address"
              name="applicant_email"
              type="email"
              value={formData.applicant_email}
              onChange={handleChange}
              margin="normal"
              required
            />
            
            <TextField
              fullWidth
              label="Phone Number"
              name="applicant_phone"
              value={formData.applicant_phone}
              onChange={handleChange}
              margin="normal"
              required
            />
            
            <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
              Visa Details
            </Typography>
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Country</InputLabel>
              <Select
                name="country"
                value={formData.country}
                onChange={handleChange}
                label="Country"
              >
                <MenuItem value="Iceland">Iceland</MenuItem>
              </Select>
            </FormControl>
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Visa Type</InputLabel>
              <Select
                name="visa_type"
                value={formData.visa_type}
                onChange={handleChange}
                label="Visa Type"
              >
                <MenuItem value="Tourist">Tourist Visa</MenuItem>
              </Select>
            </FormControl>
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Application Type *</InputLabel>
              <Select
                name="application_type"
                value={formData.application_type}
                onChange={handleChange}
                label="Application Type *"
                required
              >
                <MenuItem value="business">Business Owner / Self-Employed</MenuItem>
                <MenuItem value="job">Job Holder / Employee</MenuItem>
              </Select>
            </FormControl>
            
            <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                type="submit"
                disabled={loading}
              >
                {loading ? 'Creating...' : 'Create Application'}
              </Button>
              <Button
                variant="outlined"
                onClick={() => navigate('/')}
                disabled={loading}
              >
                Cancel
              </Button>
            </Box>
          </form>
        </Paper>
      </Box>
    </Container>
  )
}

export default NewApplicationPage

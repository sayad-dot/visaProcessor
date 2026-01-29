import React, { useState, useEffect } from 'react'
import {
  Container,
  Typography,
  Box,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
} from '@mui/material'
import { useNavigate } from 'react-router-dom'
import AddIcon from '@mui/icons-material/Add'
import { toast } from 'react-toastify'
import { applicationService } from '../services/apiService'

const HomePage = () => {
  const navigate = useNavigate()
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchApplications()
  }, [])

  const fetchApplications = async () => {
    try {
      setLoading(true)
      const data = await applicationService.getApplications()
      setApplications(data)
    } catch (error) {
      toast.error('Failed to load applications')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      draft: 'default',
      documents_uploaded: 'info',
      analyzing: 'warning',
      generating: 'warning',
      completed: 'success',
      failed: 'error',
    }
    return colors[status] || 'default'
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Typography variant="h4" component="h1">
            My Visa Applications
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate('/new-application')}
          >
            New Application
          </Button>
        </Box>

        {loading ? (
          <Typography>Loading applications...</Typography>
        ) : applications.length === 0 ? (
          <Card>
            <CardContent>
              <Typography variant="h6" align="center" color="text.secondary">
                No applications yet. Start your first visa application!
              </Typography>
            </CardContent>
          </Card>
        ) : (
          <Grid container spacing={3}>
            {applications.map((app) => (
              <Grid item xs={12} sm={6} md={4} key={app.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {app.application_number}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {app.country} - {app.visa_type}
                    </Typography>
                    {app.applicant_name && (
                      <Typography variant="body2" gutterBottom>
                        {app.applicant_name}
                      </Typography>
                    )}
                    <Box sx={{ mt: 2 }}>
                      <Chip
                        label={app.status.replace('_', ' ').toUpperCase()}
                        color={getStatusColor(app.status)}
                        size="small"
                      />
                    </Box>
                  </CardContent>
                  <CardActions>
                    <Button
                      size="small"
                      onClick={() => navigate(`/application/${app.id}`)}
                    >
                      View Details
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Box>
    </Container>
  )
}

export default HomePage

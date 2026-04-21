import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Container, Typography, Tabs, Tab, Box, Chip, CircularProgress, Alert, LinearProgress } from '@mui/material';
import { trackService } from '../services/track.service';
import { TaskCard } from '../components/tracks/TaskCard';
import { useAuth } from '../hooks/useAuth';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import AssignmentIcon from '@mui/icons-material/Assignment';
import WorkIcon from '@mui/icons-material/Work';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';

export const TrackDetailPage = () => {
  const { id } = useParams();
  const [track, setTrack] = useState(null);
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tabValue, setTabValue] = useState(0);
  const { user } = useAuth();

  useEffect(() => { loadData(); }, [id]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [trackData, progressData] = await Promise.all([trackService.getTrack(id), trackService.getTrackProgress(id)]);
      setTrack(trackData);
      setProgress(progressData);
    } catch (error) { console.error(error); } finally { setLoading(false); }
  };

  if (loading) return <div className="flex justify-center items-center h-screen"><CircularProgress sx={{ color: '#0541F0' }} /></div>;
  if (!track) return <Container><Alert severity="error">Трек не найден</Alert></Container>;

  return (
    <div className="bg-gray-50 min-h-screen">
      <Box className="bg-gradient-to-r from-darkBlue via-blue to-cyan text-white py-12">
        <Container>
          <Typography variant="h3" component="h1" gutterBottom fontWeight="bold">{track.name}</Typography>
          <Typography variant="h6" className="text-white/90 mb-4">{track.short_description}</Typography>
          <div className="flex gap-2">
            <Chip label={track.direction.name} sx={{ bgcolor: '#37EBFF', color: '#0A1E64', fontWeight: 600 }} />
            {track.duration && <Chip label={track.duration} sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }} />}
          </div>
          {progress && user && (
            <Box className="mt-6 bg-white/10 rounded-xl p-4">
              <div className="flex justify-between mb-2"><Typography variant="body2">Ваш прогресс</Typography><Typography variant="body2" fontWeight="bold">{progress.completed_tasks} / {progress.total_tasks}</Typography></div>
              <LinearProgress variant="determinate" value={progress.percentage} sx={{ height: 8, borderRadius: 10, backgroundColor: 'rgba(255,255,255,0.3)', '& .MuiLinearProgress-bar': { background: 'linear-gradient(90deg, #37EBFF 0%, #FFFFFF 100%)', borderRadius: 10 } }} />
            </Box>
          )}
        </Container>
      </Box>
      <Container className="py-8">
        <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)} sx={{ borderBottom: '2px solid #E0E4E8', '& .MuiTab-root': { textTransform: 'none', fontWeight: 600 }, '& .MuiTabs-indicator': { bgcolor: '#37EBFF', height: 3 } }}>
          <Tab label="О треке" icon={<MenuBookIcon />} iconPosition="start" />
          <Tab label="Гайды" icon={<MenuBookIcon />} iconPosition="start" />
          <Tab label="Задания" icon={<AssignmentIcon />} iconPosition="start" />
          <Tab label="Карьера" icon={<WorkIcon />} iconPosition="start" />
          <Tab label="Навыки" icon={<EmojiEventsIcon />} iconPosition="start" />
        </Tabs>
        <div hidden={tabValue !== 0} className="mt-8"><div className="bg-white rounded-2xl shadow-md p-8"><Typography variant="body1" className="text-darkGray">{track.full_description}</Typography></div></div>
        <div hidden={tabValue !== 1} className="mt-8 space-y-4">{track.guides?.map((guide, idx) => (
          <div key={guide.id} className="bg-white rounded-2xl shadow-md overflow-hidden"><div className="bg-cyan/10 px-6 py-4"><Typography variant="h5" fontWeight="600" className="text-darkBlue">{idx+1}. {guide.title}</Typography></div><div className="p-6"><div className="prose max-w-none text-darkGray">{guide.content}</div></div></div>
        ))}</div>
        <div hidden={tabValue !== 2} className="mt-8">{track.tasks?.map((task) => <TaskCard key={task.id} task={task} trackId={track.id} onSuccess={loadData} />)}</div>
        <div hidden={tabValue !== 3} className="mt-8"><div className="bg-gradient-to-br from-darkBlue/5 to-blue/5 rounded-2xl p-8"><Typography variant="h5" fontWeight="600" className="text-darkBlue mb-4">🚀 Карьерные перспективы</Typography><Typography className="text-darkGray">{track.career_paths}</Typography></div></div>
        <div hidden={tabValue !== 4} className="mt-8"><div className="bg-gradient-to-br from-cyan/5 to-blue/5 rounded-2xl p-8"><Typography variant="h5" fontWeight="600" className="text-darkBlue mb-4">💡 Навыки, которые вы получите</Typography><Typography className="text-darkGray">{track.skills}</Typography></div></div>
      </Container>
    </div>
  );
};
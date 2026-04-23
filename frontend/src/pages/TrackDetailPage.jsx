import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Container, Typography, Tabs, Tab, Box, Chip, CircularProgress, Alert, LinearProgress, Paper } from '@mui/material';
import Button from '@mui/material/Button';
import { trackService } from '../services/track.service';
import { taskService } from '../services/task.service';
import { TasksSidebar } from '../components/tracks/TasksSidebar';
import { TaskViewer } from '../components/tracks/TaskViewer';
import { useAuth } from '../hooks/useAuth';
import toast from 'react-hot-toast';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import AssignmentIcon from '@mui/icons-material/Assignment';
import WorkIcon from '@mui/icons-material/Work';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';

export const TrackDetailPage = () => {
  const { id } = useParams();
  const [track, setTrack] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tabValue, setTabValue] = useState(0);
  const [selectedTask, setSelectedTask] = useState(null);
  const { user, isAuthenticated } = useAuth();
  const [hasPendingRequest, setHasPendingRequest] = useState(false);

  useEffect(() => {
    loadData();
    checkEnrollmentStatus();
  }, [id, user]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [trackData, tasksData, progressData] = await Promise.all([
        trackService.getTrack(id),
        taskService.getTrackTasks(id),
        trackService.getTrackProgress(id),
      ]);
      setTrack(trackData);
      setTasks(tasksData);
      setProgress(progressData);
      if (tasksData.length > 0) {
        const firstUnlocked = tasksData.find(t => !t.locked) || tasksData[0];
        setSelectedTask(firstUnlocked);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const checkEnrollmentStatus = async () => {
    if (!isAuthenticated || user?.role !== 'student') return;
    // Если уже зачислен – не проверяем заявки
    if (user.group && user.group.track?.id === parseInt(id)) return;
    try {
      const requests = await trackService.getStudentRequests();
      const hasPending = requests.some(r => r.track === parseInt(id) && r.status === 'pending');
      setHasPendingRequest(hasPending);
    } catch (err) {
      console.error(err);
    }
  };

  const handleEnroll = async () => {
    try {
      await trackService.createEnrollmentRequest(id);
      toast.success('Заявка отправлена куратору');
      setHasPendingRequest(true);
    } catch (err) {
      toast.error(err.response?.data?.error || 'Ошибка при отправке заявки');
    }
  };

  const handleTaskUpdate = async () => {
    try {
      const updatedTasks = await taskService.getTrackTasks(id);
      setTasks(updatedTasks);
      if (selectedTask) {
        const refreshed = updatedTasks.find(t => t.id === selectedTask.id);
        if (refreshed) setSelectedTask(refreshed);
        else {
          const unlocked = updatedTasks.find(t => !t.locked);
          setSelectedTask(unlocked || updatedTasks[0]);
        }
      }
      const newProgress = await trackService.getTrackProgress(id);
      setProgress(newProgress);
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) return <div className="flex justify-center items-center h-screen"><CircularProgress sx={{ color: '#0541F0' }} /></div>;
  if (!track) return <Container><Alert severity="error">Трек не найден</Alert></Container>;

  const isEnrolled = user && user.group && user.group.track?.id === parseInt(id);
  const showEnrollButton = isAuthenticated && user?.role === 'student' && !isEnrolled && !hasPendingRequest;

  return (
    <div className="bg-gray-50 min-h-screen">
      <Box className="bg-gradient-to-r from-darkBlue via-blue to-cyan text-white py-12">
        <Container>
          <Typography variant="h3" component="h1" gutterBottom fontWeight="bold">{track.name}</Typography>
          <Typography variant="h6" className="text-white/90 mb-4">{track.short_description}</Typography>
          <div className="flex flex-wrap gap-2 items-center">
            <Chip label={track.direction.name} sx={{ bgcolor: '#37EBFF', color: '#0A1E64', fontWeight: 600 }} />
            {track.duration && <Chip label={track.duration} sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }} />}
            {showEnrollButton && (
              <Button
                variant="contained"
                onClick={handleEnroll}
                sx={{ bgcolor: '#37EBFF', color: '#0A1E64', '&:hover': { bgcolor: '#2bc4d4' } }}
              >
                Подать заявку
              </Button>
            )}
            {hasPendingRequest && (
              <Chip label="Заявка на рассмотрении" sx={{ bgcolor: '#ff9800', color: 'white' }} />
            )}
            {isEnrolled && (
              <Chip label="Зачислен" sx={{ bgcolor: '#4caf50', color: 'white' }} />
            )}
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

        <div hidden={tabValue !== 2} className="mt-8">
          <div className="flex gap-6">
            <TasksSidebar tasks={tasks} selectedTaskId={selectedTask?.id} onSelectTask={setSelectedTask} />
            <div className="flex-1">
              {selectedTask ? (
                <TaskViewer task={selectedTask} trackId={track.id} onTaskUpdate={handleTaskUpdate} />
              ) : (
                <Paper className="p-8 text-center"><Typography color="textSecondary">Выберите задание из списка</Typography></Paper>
              )}
            </div>
          </div>
        </div>

        <div hidden={tabValue !== 3} className="mt-8"><div className="bg-gradient-to-br from-darkBlue/5 to-blue/5 rounded-2xl p-8"><Typography variant="h5" fontWeight="600" className="text-darkBlue mb-4">🚀 Карьерные перспективы</Typography><Typography className="text-darkGray">{track.career_paths}</Typography></div></div>
        <div hidden={tabValue !== 4} className="mt-8"><div className="bg-gradient-to-br from-cyan/5 to-blue/5 rounded-2xl p-8"><Typography variant="h5" fontWeight="600" className="text-darkBlue mb-4">💡 Навыки, которые вы получите</Typography><Typography className="text-darkGray">{track.skills}</Typography></div></div>
      </Container>
    </div>
  );
};
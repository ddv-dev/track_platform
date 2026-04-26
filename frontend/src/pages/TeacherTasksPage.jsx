// frontend/src/pages/TeacherTasksPage.jsx
import React, { useState, useEffect } from 'react';
import {
  Container, Typography, Paper, List, ListItem, ListItemText,
  Button, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Box, CircularProgress, Chip, Alert
} from '@mui/material';
import { taskService } from '../services/task.service';
import { trackService } from '../services/track.service';
import { useAuth } from '../hooks/useAuth';
import toast from 'react-hot-toast';

export const TeacherTasksPage = () => {
  const { user } = useAuth();
  const [tracks, setTracks] = useState([]);
  const [selectedTrack, setSelectedTrack] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [currentTask, setCurrentTask] = useState(null);

  useEffect(() => {
    if (user?.role === 'teacher') {
      loadTracks();
    }
  }, [user]);

  const loadTracks = async () => {
    try {
      // Здесь должен быть эндпоинт для получения списка треков преподавателя
      const allTracks = await trackService.getTracks();
      const teacherTracks = allTracks.filter(track => track.teachers?.includes(user.id));
      setTracks(teacherTracks);
      if (teacherTracks.length > 0) {
        setSelectedTrack(teacherTracks[0]);
      }
    } catch (error) {
      console.error('Ошибка загрузки треков:', error);
      toast.error('Не удалось загрузить треки');
    } finally {
      setLoading(false);
    }
  };

  const loadTasks = async (trackId) => {
    try {
      const tasksData = await taskService.getTrackTasks(trackId);
      setTasks(tasksData);
    } catch (error) {
      console.error('Ошибка загрузки заданий:', error);
      toast.error('Не удалось загрузить задания');
    }
  };

  useEffect(() => {
    if (selectedTrack) {
      loadTasks(selectedTrack.id);
    }
  }, [selectedTrack]);

  const handleEditTask = (task = null) => {
    setCurrentTask(task || { title: '', description: '', task_type: 'text', points: 10 });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setCurrentTask(null);
  };

  const handleSaveTask = async () => {
    if (!selectedTrack) return;
    try {
      if (currentTask.id) {
        // Обновление существующего задания
        await taskService.updateTask(selectedTrack.id, currentTask.id, currentTask);
        toast.success('Задание обновлено!');
      } else {
        // Создание нового задания
        await taskService.createTask(selectedTrack.id, currentTask);
        toast.success('Задание создано!');
      }
      handleCloseDialog();
      loadTasks(selectedTrack.id);
    } catch (error) {
      console.error('Ошибка сохранения задания:', error);
      toast.error('Не удалось сохранить задание');
    }
  };

  if (loading) {
    return (
      <Container className="py-8">
        <div className="flex justify-center">
          <CircularProgress sx={{ color: '#0541F0' }} />
        </div>
      </Container>
    );
  }

  return (
    <Container className="py-8">
      <Typography variant="h4" className="mb-6">Редактор заданий</Typography>
      
      {tracks.length === 0 ? (
        <Alert severity="info">У вас пока нет привязанных треков</Alert>
      ) : (
        <div className="flex gap-6">
          {/* Боковая панель со списком треков */}
          <Paper className="w-64 p-4">
            <Typography variant="h6" className="mb-3">Мои треки</Typography>
            <List>
              {tracks.map(track => (
                <ListItem
                  key={track.id}
                  button
                  selected={selectedTrack?.id === track.id}
                  onClick={() => setSelectedTrack(track)}
                >
                  <ListItemText primary={track.name} />
                </ListItem>
              ))}
            </List>
          </Paper>

          {/* Основная область со списком заданий */}
          <Paper className="flex-1 p-6">
            <div className="flex justify-between items-center mb-4">
              <Typography variant="h5">{selectedTrack?.name}</Typography>
              <Button variant="contained" onClick={() => handleEditTask()}>
                Создать задание
              </Button>
            </div>

            {tasks.length === 0 ? (
              <Typography color="textSecondary">Заданий пока нет</Typography>
            ) : (
              <List>
                {tasks.map(task => (
                  <ListItem key={task.id} divider>
                    <ListItemText
                      primary={task.title}
                      secondary={`Тип: ${task.task_type} | Баллы: ${task.points}`}
                    />
                    <Button onClick={() => handleEditTask(task)}>Редактировать</Button>
                  </ListItem>
                ))}
              </List>
            )}
          </Paper>
        </div>
      )}

      {/* Диалог редактирования задания */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>{currentTask?.id ? 'Редактировать задание' : 'Новое задание'}</DialogTitle>
        <DialogContent>
          <div className="space-y-4 mt-2">
            <TextField
              fullWidth
              label="Название"
              value={currentTask?.title || ''}
              onChange={(e) => setCurrentTask({ ...currentTask, title: e.target.value })}
            />
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Описание"
              value={currentTask?.description || ''}
              onChange={(e) => setCurrentTask({ ...currentTask, description: e.target.value })}
            />
            <TextField
              select
              fullWidth
              label="Тип задания"
              value={currentTask?.task_type || 'text'}
              onChange={(e) => setCurrentTask({ ...currentTask, task_type: e.target.value })}
              SelectProps={{ native: true }}
            >
              <option value="text">Текстовый ответ</option>
              <option value="single">Один правильный ответ</option>
              <option value="multiple">Несколько правильных ответов</option>
              <option value="code">Код</option>
            </TextField>
            <TextField
              fullWidth
              label="Баллы"
              type="number"
              value={currentTask?.points || 10}
              onChange={(e) => setCurrentTask({ ...currentTask, points: parseInt(e.target.value) })}
            />
            <TextField
              fullWidth
              multiline
              rows={2}
              label="Правильный ответ (для автопроверки)"
              value={currentTask?.correct_answer || ''}
              onChange={(e) => setCurrentTask({ ...currentTask, correct_answer: e.target.value })}
              helperText="Укажите правильный ответ для заданий с автоматической проверкой"
            />
          </div>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Отмена</Button>
          <Button onClick={handleSaveTask} variant="contained">
            Сохранить
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};
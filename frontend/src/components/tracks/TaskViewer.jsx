import React, { useState, useEffect } from 'react';
import { Paper, Typography, TextField, Button, FormControl, FormLabel, RadioGroup, FormControlLabel, Radio, Checkbox, Alert, Chip, Box, CircularProgress } from '@mui/material';
import { taskService } from '../../services/task.service';
import toast from 'react-hot-toast';
import ReactMarkdown from 'react-markdown';

export const TaskViewer = ({ task, trackId, onTaskUpdate }) => {
  const [answer, setAnswer] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);

  const isAuto = task.task_type === 'single' || task.task_type === 'multiple';
  const isCompleted = task.completed;

  // Сброс при переходе к другому заданию
  useEffect(() => {
    setAnswer('');
    setResult(null);
  }, [task]);

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const response = await taskService.submitTask(task.id, answer);
      if (isAuto) {
        // Авто-проверка: сразу получаем результат
        setResult({ isCorrect: response.is_correct, message: response.is_correct ? 'Правильно!' : 'Неправильно. Попробуйте ещё раз.' });
        if (response.is_correct) {
          toast.success(`Задание выполнено! +${task.points} баллов`);
          onTaskUpdate();
        } else {
          toast.error('Ответ неверный');
        }
      } else {
        setResult({ isCorrect: null, message: 'Ответ отправлен на проверку куратору.' });
        toast.success('Ответ отправлен на проверку');
        onTaskUpdate();
      }
    } catch (error) {
      const msg = error.response?.data?.error || 'Ошибка отправки';
      toast.error(msg);
      setResult({ isCorrect: false, message: msg });
    } finally {
      setSubmitting(false);
    }
  };

  const renderInput = () => {
    if (isCompleted) {
      return <Alert severity="success">Задание выполнено! {task.points} баллов засчитано.</Alert>;
    }
    switch (task.task_type) {
      case 'single':
        return (
          <FormControl component="fieldset">
            <FormLabel component="legend">Выберите правильный ответ</FormLabel>
            <RadioGroup value={answer} onChange={(e) => setAnswer(e.target.value)}>
              {task.options?.map(opt => (
                <FormControlLabel key={opt.id} value={opt.id.toString()} control={<Radio />} label={opt.text} />
              ))}
            </RadioGroup>
          </FormControl>
        );
      case 'multiple':
        return (
          <FormControl component="fieldset">
            <FormLabel component="legend">Выберите все правильные ответы</FormLabel>
            {task.options?.map(opt => (
              <FormControlLabel
                key={opt.id}
                control={<Checkbox checked={answer.split(',').includes(opt.id.toString())} onChange={(e) => {
                  const values = answer ? answer.split(',') : [];
                  if (e.target.checked) values.push(opt.id.toString());
                  else values.splice(values.indexOf(opt.id.toString()), 1);
                  setAnswer(values.join(','));
                }} />}
                label={opt.text}
              />
            ))}
          </FormControl>
        );
      case 'text':
        return <TextField fullWidth multiline rows={4} value={answer} onChange={(e) => setAnswer(e.target.value)} placeholder="Введите ваш ответ..." variant="outlined" />;
      case 'code':
        return <TextField fullWidth multiline rows={6} value={answer} onChange={(e) => setAnswer(e.target.value)} placeholder="Напишите код..." variant="outlined" fontFamily="monospace" />;
      default:
        return null;
    }
  };

  return (
    <Paper className="p-6">
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5">{task.title}</Typography>
        <Chip label={task.category === 'theory' ? 'Теория' : 'Практика'} color={task.category === 'theory' ? 'primary' : 'secondary'} />
      </Box>
      <div className="prose max-w-none mb-4">
        <ReactMarkdown>{task.description}</ReactMarkdown>
      </div>
      <div className="mb-4">
        {renderInput()}
      </div>
      {result && (
        <Alert severity={result.isCorrect === true ? 'success' : result.isCorrect === false ? 'error' : 'info'} className="mb-4">
          {result.message}
        </Alert>
      )}
      {!isCompleted && (
        <Button variant="contained" onClick={handleSubmit} disabled={submitting || (!answer && task.task_type !== 'text')} sx={{ background: 'linear-gradient(135deg, #37EBFF 0%, #0541F0 100%)' }}>
          {submitting ? <CircularProgress size={24} sx={{ color: 'white' }} /> : (isAuto ? 'Проверить' : 'Отправить на проверку')}
        </Button>
      )}
    </Paper>
  );
};
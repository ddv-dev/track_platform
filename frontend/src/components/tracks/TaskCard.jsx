import React, { useState } from 'react';
import { TextField, Button, Radio, RadioGroup, FormControlLabel, FormControl, FormLabel, Alert } from '@mui/material';
import { trackService } from '../../services/track.service';
import toast from 'react-hot-toast';
import ReactMarkdown from 'react-markdown';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

export const TaskCard = ({ task, trackId, onSuccess }) => {
  const [answer, setAnswer] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const response = await trackService.submitTask(trackId, task.id, answer);
      setResult({ isCorrect: response.is_correct, message: response.message });
      if (response.is_correct) {
        toast.success(`✓ Правильно! +${task.points} баллов`);
        onSuccess();
      } else {
        toast.error('✗ Неправильно. Попробуйте ещё раз');
      }
    } catch {
      toast.error('Ошибка при отправке');
    } finally {
      setSubmitting(false);
    }
  };

  const renderInput = () => {
    switch (task.task_type) {
      case 'text':
        return (
          <TextField
            fullWidth
            multiline
            rows={3}
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Введите ответ..."
            variant="outlined"
            sx={{ '& .MuiOutlinedInput-root': { borderRadius: '12px' } }}
          />
        );
      case 'single':
        return (
          <FormControl>
            <FormLabel>Выберите правильный ответ</FormLabel>
            <RadioGroup value={answer} onChange={(e) => setAnswer(e.target.value)}>
              {task.options?.map((opt) => (
                <FormControlLabel key={opt.id} value={opt.id.toString()} control={<Radio />} label={opt.text} />
              ))}
            </RadioGroup>
          </FormControl>
        );
      default:
        return null;
    }
  };

  const isCompleted = task.user_attempt?.is_correct;

  return (
    <div className="bg-white rounded-2xl shadow-md mb-6 overflow-hidden">
      <div className="p-6">
        <div className="flex justify-between items-start mb-4">
          <h3 className="text-xl font-bold text-darkBlue">{task.title}</h3>
          <span className="px-3 py-1 rounded-lg bg-gradient-primary text-white text-sm font-semibold">
            {task.points} баллов
          </span>
        </div>
        <div className="prose max-w-none mb-6 text-darkGray">
          <ReactMarkdown
            components={{
              code({ node, inline, className, children, ...props }) {
                return !inline ? (
                  <code className={className} {...props}>
                    {children}
                  </code>
                ) : (
                  <code className={className} {...props}>
                    {children}
                  </code>
                );
              },
            }}
          >
            {task.description}
          </ReactMarkdown>
        </div>
        {isCompleted ? (
          <Alert icon={<CheckCircleIcon />} severity="success" sx={{ borderRadius: '12px' }}>
            Задание выполнено! +{task.user_attempt?.points_earned} баллов.
          </Alert>
        ) : (
          <>
            {renderInput()}
            {result && (
              <Alert severity={result.isCorrect ? 'success' : 'error'} sx={{ mt: 3, borderRadius: '12px' }}>
                {result.message}
              </Alert>
            )}
            <Button
              variant="contained"
              onClick={handleSubmit}
              disabled={submitting || !answer}
              sx={{
                mt: 3,
                background: 'linear-gradient(135deg, #37EBFF 0%, #0541F0 100%)',
                borderRadius: '12px',
                textTransform: 'none',
              }}
            >
              {submitting ? 'Проверка...' : 'Проверить'}
            </Button>
          </>
        )}
      </div>
    </div>
  );
};
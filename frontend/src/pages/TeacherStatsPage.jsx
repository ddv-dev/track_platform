import React, { useState, useEffect } from 'react';
import { Container, Typography, Paper, Table, TableHead, TableRow, TableCell, TableBody, CircularProgress, Alert } from '@mui/material';
import api from '../services/api';
import { useAuth } from '../hooks/useAuth';

export const TeacherStatsPage = () => {
  const { user } = useAuth();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.role === 'teacher') {
      loadStats();
    }
  }, [user]);

  const loadStats = async () => {
    try {
      const response = await api.get('/tracks/teacher/stats/');
      setStudents(response.data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container className="py-8">
        <div className="flex justify-center"><CircularProgress sx={{ color: '#0541F0' }} /></div>
      </Container>
    );
  }

  return (
    <Container className="py-8">
      <Typography variant="h4" className="mb-6">Результаты студентов</Typography>
      {students.length === 0 ? (
        <Alert severity="info">Нет данных о студентах</Alert>
      ) : (
        <Paper>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Студент</TableCell>
                <TableCell>Трек</TableCell>
                <TableCell>Выполнено заданий</TableCell>
                <TableCell>Прогресс</TableCell>
                <TableCell>Действия</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {students.map(s => (
                <TableRow key={s.student_id}>
                  <TableCell>{s.name}</TableCell>
                  <TableCell>{s.track}</TableCell>
                  <TableCell>{s.completed_tasks} / {s.total_tasks}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-cyan to-blue rounded-full" style={{ width: `${s.percentage}%` }} />
                      </div>
                      <span className="text-sm">{s.percentage}%</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <a href={`/profile/${s.student_id}`} className="text-blue-500 hover:underline">Детали</a>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      )}
    </Container>
  );
};
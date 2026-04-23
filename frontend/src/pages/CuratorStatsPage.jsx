import React, { useEffect, useState } from 'react';
import { Container, Typography, Paper, Table, TableHead, TableRow, TableCell, TableBody, CircularProgress } from '@mui/material';
import { useAuth } from '../hooks/useAuth';
import api from '../services/api';
export const CuratorStatsPage = () => {
  const { user } = useAuth();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.role === 'curator') loadStats();
  }, [user]);

  const loadStats = async () => {
    try {
      const res = await api.get('/tracks/curator/students/');
      setStudents(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="flex justify-center mt-8"><CircularProgress /></div>;

  return (
    <Container className="py-8">
      <Typography variant="h4" className="mb-6">Статистика студентов</Typography>
      <Paper>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Студент</TableCell>
              <TableCell>Трек</TableCell>
              <TableCell>Выполнено заданий</TableCell>
              <TableCell>Процент</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {students.map(s => (
              <TableRow key={s.student_id}>
                <TableCell>{s.name}</TableCell>
                <TableCell>{s.track}</TableCell>
                <TableCell>{s.completed_tasks} / {s.total_tasks}</TableCell>
                <TableCell>{s.percentage}%</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
    </Container>
  );
};
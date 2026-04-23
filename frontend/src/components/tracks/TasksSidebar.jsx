import React, { useState } from 'react';
import { List, ListItem, ListItemText, ListItemIcon, Collapse, Box, Typography, Chip } from '@mui/material';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';
import LockIcon from '@mui/icons-material/Lock';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';

export const TasksSidebar = ({ tasks, selectedTaskId, onSelectTask }) => {
  const theoryTasks = tasks.filter(t => t.category === 'theory');
  const practiceTasks = tasks.filter(t => t.category === 'practice');
  const [openTheory, setOpenTheory] = useState(true);
  const [openPractice, setOpenPractice] = useState(true);

  const getStatusIcon = (task) => {
    if (task.completed) return <CheckCircleIcon sx={{ fontSize: 18, color: '#4caf50' }} />;
    if (task.locked) return <LockIcon sx={{ fontSize: 18, color: '#9e9e9e' }} />;
    return <RadioButtonUncheckedIcon sx={{ fontSize: 18, color: '#0541F0' }} />;
  };

  return (
    <Box sx={{ width: 300, flexShrink: 0 }}>
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>Задания</Typography>
      
      {/* Теория */}
      <ListItem button onClick={() => setOpenTheory(!openTheory)} sx={{ borderRadius: 2, mb: 1, bgcolor: '#f5f5f5' }}>
        <ListItemText primary="📖 Теория" primaryTypographyProps={{ fontWeight: 'bold' }} />
        {openTheory ? <ExpandLess /> : <ExpandMore />}
      </ListItem>
      <Collapse in={openTheory} timeout="auto" unmountOnExit>
        <List component="div" disablePadding>
          {theoryTasks.map((task) => (
            <ListItem
              button
              key={task.id}
              selected={selectedTaskId === task.id}
              onClick={() => onSelectTask(task)}
              disabled={task.locked}
              sx={{ pl: 4, py: 1, borderRadius: 2, mb: 0.5 }}
            >
              <ListItemIcon sx={{ minWidth: 32 }}>{getStatusIcon(task)}</ListItemIcon>
              <ListItemText primary={task.title} primaryTypographyProps={{ variant: 'body2' }} />
            </ListItem>
          ))}
        </List>
      </Collapse>

      {/* Практика */}
      <ListItem button onClick={() => setOpenPractice(!openPractice)} sx={{ borderRadius: 2, mb: 1, mt: 2, bgcolor: '#f5f5f5' }}>
        <ListItemText primary="💻 Практика" primaryTypographyProps={{ fontWeight: 'bold' }} />
        {openPractice ? <ExpandLess /> : <ExpandMore />}
      </ListItem>
      <Collapse in={openPractice} timeout="auto" unmountOnExit>
        <List component="div" disablePadding>
          {practiceTasks.map((task) => (
            <ListItem
              button
              key={task.id}
              selected={selectedTaskId === task.id}
              onClick={() => onSelectTask(task)}
              disabled={task.locked}
              sx={{ pl: 4, py: 1, borderRadius: 2, mb: 0.5 }}
            >
              <ListItemIcon sx={{ minWidth: 32 }}>{getStatusIcon(task)}</ListItemIcon>
              <ListItemText primary={task.title} primaryTypographyProps={{ variant: 'body2' }} />
            </ListItem>
          ))}
        </List>
      </Collapse>
    </Box>
  );
};
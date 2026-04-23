import React from 'react';
import { Link } from 'react-router-dom';
import { Container, Typography, Grid, Box } from '@mui/material';
import { motion } from 'framer-motion';
import SchoolIcon from '@mui/icons-material/School';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import ChatIcon from '@mui/icons-material/Chat';
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch';
import { useAuth } from '../hooks/useAuth';

export const HomePage = () => {
  const { isAuthenticated } = useAuth();

  const features = [
    { icon: <SchoolIcon sx={{ fontSize: 48 }} />, title: '25+ треков', desc: 'Разнообразные направления от программирования до аналитики' },
    { icon: <TrendingUpIcon sx={{ fontSize: 48 }} />, title: 'Карьерные перспективы', desc: 'Узнайте, какие профессии вас ждут после обучения' },
    { icon: <ChatIcon sx={{ fontSize: 48 }} />, title: 'Поддержка кураторов', desc: 'Чат с экспертами и помощь в выборе пути' },
  ];

  return (
    <>
      <Box className="relative overflow-hidden bg-gradient-to-br from-darkBlue via-blue to-cyan text-white">
        <Container className="relative py-20 text-center">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
            <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 0.2, type: 'spring' }} className="inline-block mb-6">
              <RocketLaunchIcon sx={{ fontSize: 64, color: '#37EBFF' }} />
            </motion.div>
            <Typography variant="h2" component="h1" gutterBottom fontWeight="800" className="text-white">МИСИС <span className="text-cyan">IT</span></Typography>
            <Typography variant="h5" className="mb-8 text-white/90">Интерактивная платформа для выбора образовательного трека</Typography>
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}>
              <Link to="/tracks" className="inline-block px-8 py-3 rounded-xl bg-white text-blue font-bold text-lg hover:shadow-xl transition hover:scale-105 mt-6">Начать выбор</Link>
            </motion.div>
          </motion.div>
        </Container>
        <div className="relative h-16"><svg className="absolute bottom-0 w-full h-16 text-white" preserveAspectRatio="none" viewBox="0 0 1440 100" fill="white"><path d="M0,64 L80,69 C160,74 320,85 480,80 C640,75 800,53 960,48 C1120,43 1280,53 1360,58 L1440,64 L1440,100 L1360,100 C1280,100 1120,100 960,100 C800,100 640,100 480,100 C320,100 160,100 80,100 L0,100 Z" /></svg></div>
      </Box>
      <Container className="py-20">
        <Typography variant="h3" component="h2" textAlign="center" gutterBottom fontWeight="700" className="text-darkBlue">Не можете определиться или боитесь сделать неправильный выбор?</Typography>
        <Typography variant="h6" textAlign="center" className="text-darkGray mb-12">Мы поможем вам найти свой путь в IT</Typography>
        <Grid container spacing={4}>
          {features.map((f, idx) => (
            <Grid item xs={12} md={4} key={idx}>
              <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.1 }} className="text-center group">
                <div className="inline-block p-4 rounded-2xl bg-gradient-to-r from-cyan/10 to-blue/10 mb-4 group-hover:scale-110 transition mt-4">{f.icon}</div>
                <Typography variant="h5" fontWeight="600" className="text-darkBlue">{f.title}</Typography>
                <Typography className="text-darkGray">{f.desc}</Typography>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      </Container>
      {/* Условный рендеринг блока регистрации */}
      {!isAuthenticated && (
        <Box className="bg-gradient-to-r from-darkBlue to-blue py-16">
          <Container className="text-center">
            <Typography variant="h4" className="text-white mb-4">Готовы начать свой путь?</Typography>
            <Link to="/register" className="inline-block px-8 py-3 rounded-xl bg-cyan text-darkBlue font-bold hover:shadow-lg transition hover:scale-105">Зарегистрироваться</Link>
          </Container>
        </Box>
      )}
    </>
  );
};
import React, { useState, useEffect } from 'react';
import { Container, Typography, Grid, TextField, MenuItem, CircularProgress } from '@mui/material';
import { trackService } from '../services/track.service';
import { TrackCard } from '../components/tracks/TrackCard';
import SearchIcon from '@mui/icons-material/Search';

export const TracksPage = () => {
  const [tracks, setTracks] = useState([]);
  const [directions, setDirections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ direction: '', search: '' });

  useEffect(() => { loadData(); }, [filters]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [tracksData, dirsData] = await Promise.all([trackService.getTracks(filters), trackService.getDirections()]);
      setTracks(tracksData);
      setDirections(dirsData);
    } catch (error) { console.error(error); } finally { setLoading(false); }
  };

  return (
    <Container className="py-8">
      <Typography variant="h4" component="h1" className="text-darkBlue mb-6 font-bold">Все треки</Typography>
      <div className="flex flex-wrap gap-4 mb-8">
        <TextField select label="Направление" value={filters.direction} onChange={(e) => setFilters({ ...filters, direction: e.target.value })} className="w-64" size="small">
          <MenuItem value="">Все направления</MenuItem>
          {directions.map((dir) => <MenuItem key={dir.id} value={dir.id}>{dir.name}</MenuItem>)}
        </TextField>
        <TextField label="Поиск" variant="outlined" size="small" value={filters.search} onChange={(e) => setFilters({ ...filters, search: e.target.value })} InputProps={{ startAdornment: <SearchIcon className="mr-2 text-gray-400" /> }} className="w-64" />
      </div>
      {loading ? <div className="flex justify-center"><CircularProgress sx={{ color: '#0541F0' }} /></div> : (
        <Grid container spacing={3}>
          {tracks.map((track) => <Grid item xs={12} sm={6} md={4} key={track.id}><TrackCard track={track} /></Grid>)}
        </Grid>
      )}
    </Container>
  );
};
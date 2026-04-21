import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';

export const TrackCard = ({ track }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -8 }}
      transition={{ duration: 0.3 }}
      className="group"
    >
      <div className="bg-white rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden h-full flex flex-col">
        {track.image && (
          <div className="h-48 overflow-hidden">
            <img src={track.image} alt={track.name} className="w-full h-full object-cover group-hover:scale-105 transition duration-500" />
          </div>
        )}
        <div className="p-6 flex-grow">
          <div className="flex items-center gap-2 mb-3">
            <span className="px-3 py-1 rounded-lg text-xs font-semibold bg-cyan/10 text-blue">{track.direction_name}</span>
            {track.duration && <span className="px-3 py-1 rounded-lg text-xs font-semibold bg-gray-100 text-darkGray">{track.duration}</span>}
          </div>
          <h3 className="text-xl font-bold text-darkBlue mb-2 group-hover:text-blue transition">{track.name}</h3>
          <p className="text-darkGray mb-4 line-clamp-2">{track.short_description}</p>
        </div>
        <div className="px-6 pb-6">
          <Link to={`/tracks/${track.id}`} className="inline-flex items-center gap-2 text-blue font-semibold hover:gap-3 transition-all">
            Подробнее <ArrowForwardIcon sx={{ fontSize: 18 }} />
          </Link>
        </div>
      </div>
    </motion.div>
  );
};
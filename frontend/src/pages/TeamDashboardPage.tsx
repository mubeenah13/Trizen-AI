import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Calendar, Camera, ArrowRight, UploadCloud } from 'lucide-react';
import { Navbar } from '../components/Navbar';
import { api } from '../services/api';
import type { Event } from '../types';

export const TeamDashboardPage: React.FC = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const res = await api.get('/events');
        setEvents(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchEvents();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8 space-y-8">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight gradient-text">Photographer Portal</h1>
          <p className="text-sm text-slate-400 mt-1">Select an assigned event to upload collaborative photographs.</p>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2].map((n) => (
              <div key={n} className="h-44 rounded-2xl bg-slate-900 animate-pulse border border-slate-800" />
            ))}
          </div>
        ) : events.length === 0 ? (
          <div className="glass-card p-12 text-center rounded-2xl border border-slate-800">
            <Camera className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <p className="text-slate-300 font-semibold">No assigned events assigned to your account yet.</p>
            <p className="text-xs text-slate-500 mt-1">Contact your Lead Admin to assign you to an event.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {events.map((ev) => (
              <div
                key={ev.id}
                className="glass-card rounded-2xl p-6 border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between group"
              >
                <div>
                  <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                    <span className="flex items-center gap-1 font-mono">
                      <Calendar className="w-3.5 h-3.5 text-sky-400" /> {ev.event_date}
                    </span>
                    <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 font-semibold border border-slate-700">
                      {ev.photo_count} Photos
                    </span>
                  </div>

                  <h3 className="text-lg font-bold text-slate-100 group-hover:text-sky-400 transition-colors mb-2">
                    {ev.name}
                  </h3>
                  <p className="text-xs text-slate-400 line-clamp-2 mb-4">{ev.description || 'No description provided.'}</p>
                </div>

                <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between">
                  <span className="text-xs text-emerald-400 font-semibold flex items-center gap-1">
                    <UploadCloud className="w-3.5 h-3.5" /> Assigned Photographer
                  </span>
                  <Link
                    to={`/team/events/${ev.id}`}
                    className="inline-flex items-center gap-1 text-xs font-bold text-sky-400 hover:text-sky-300 bg-sky-950/40 hover:bg-sky-950/80 px-3 py-1.5 rounded-lg border border-sky-800/50 transition-colors"
                  >
                    Upload Photos <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

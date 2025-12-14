const express = require('express');
const cors = require('cors');
const { z } = require('zod');
const { nanoid } = require('nanoid');
const path = require('path');

const app = express();
app.use(express.json());
app.use(cors());

const PORT = process.env.PORT || 3001;
const HOST = '0.0.0.0';

// เสิร์ฟหน้าเว็บ (web/) เป็น static
app.use(express.static(path.join(__dirname, '..', 'web')));

// ตัวอย่าง event
const EVENTS = { e1: { id: 'e1', name: 'Sample Event' } };

// In-memory stores
const ATTENDEE_BY_ID = new Map();              // id -> attendee
const ATTENDEE_BY_EMAIL = new Map();           // `${eventId}|${email}` -> attendee

const AttendeeCreate = z.object({
  name: z.string().min(1, 'name is required'),
  email: z.string().email('invalid email format'),
  ticketType: z.enum(['standard','vip','student']).optional()
});

const normEmail = (e) => e.trim().toLowerCase();

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.post('/events/:eventId/attendees', (req, res) => {
  const { eventId } = req.params;
  if (!EVENTS[eventId]) {
    return res.status(404).json({ error: 'NotFound', message: 'event not found' });
  }

  const parsed = AttendeeCreate.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({
      error: 'BadRequest',
      message: 'validation error',
      details: parsed.error.flatten()
    });
  }

  const name = parsed.data.name.trim();
  if (!name) {
    return res.status(400).json({ error: 'BadRequest', message: 'name is required' });
  }

  const email = normEmail(parsed.data.email);
  const key = `${eventId}|${email}`;
  if (ATTENDEE_BY_EMAIL.has(key)) {
    return res.status(409).json({ error: 'Conflict', message: 'attendee already exists for this event' });
  }

  const id = nanoid();
  const now = new Date().toISOString();
  const attendee = {
    id, eventId, name, email,
    ticketType: parsed.data.ticketType || 'standard',
    status: 'registered',
    checkInAt: null,
    createdAt: now,
    updatedAt: now
  };

  ATTENDEE_BY_EMAIL.set(key, attendee);
  ATTENDEE_BY_ID.set(id, attendee);
  return res.status(201).json(attendee);
});

// เส้นทาง fallback ให้ index.html
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'web', 'index.html'));
});

app.listen(PORT, HOST, () => {
  console.log(`Express listening on http://${HOST}:${PORT}`);
});

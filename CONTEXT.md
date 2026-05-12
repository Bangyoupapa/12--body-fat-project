# 12% Body Fat Coach — Domain Context

## Purpose

A personal AI coaching Discord bot that monitors the user's body composition, diet, exercise, and sleep to guide them toward 12% body fat.

---

## Core Terms

### User
Single user (the owner). No multi-user support in initial version. No login system required.

### Body Composition Entry
A data point submitted by the user that describes their physical state at a point in time. Includes:
- Body weight (kg)
- Height (cm, static — set once)
- InBody scan photo (optional, OCR'd by the bot to extract body fat %, muscle mass, etc.)
- Progress photo (optional, used for visual tracking and before/after comparison)

### Food Entry
A record of what the user ate, submitted as:
- A photo of the food (AI estimates calories, protein, carbs, fat — labelled as estimates)
- A photo of a nutrition label (OCR'd; values noted as approximate due to label inaccuracies)
- Free text description (fallback)

### Exercise Entry
A free-text record of a workout session submitted by the user (e.g. "深蹲 5×5 100kg"). Bot parses and stores structured data (exercise name, sets, reps, weight).

### Health Metrics
Passive data from iPhone Health app, delivered via iOS Shortcut + Discord Webhook:
- Daily step count
- Sleep duration and quality

### Habit Profile
A rolling summary the bot maintains about the user's patterns across Exercise Entries, Food Entries, and Health Metrics. Used to personalise coaching advice and identify recurring gaps (e.g. skips training on Mondays, under-eats protein on weekends).

### Coaching Message
A bot-generated message that gives the user actionable advice. Two types:
- **Scheduled** — triggered by a cron job (see Push Schedule)
- **On-demand** — triggered by a user question (e.g. "今天該練什麼？")

### Push Schedule
The fixed schedule for proactive Coaching Messages:
- **Morning (daily)**: today's training plan + yesterday's diet summary
- **Evening (daily)**: reminder to log today's food and workout
- **Weekly (Sunday)**: weekly report — weight trend, body fat estimate, progress photo comparison

### Goal
Reach ~8-10% body fat with a lean, defined physique — specifically referencing Brad Pitt's body in *Fight Club* and *Troy*. Not focused on bulk or maximum muscle mass; the target is low body fat with visible muscle definition and an athletic build. The bot tracks progress toward this goal and adjusts recommendations accordingly.

### Coach Persona
The bot acts as a knowledgeable personal coach. Its advice is grounded in GPT-4o's fitness and nutrition knowledge, anchored by a system prompt defining the target aesthetic and coaching principles. No external knowledge base (RAG) is used — the user's own historical data (weight trend, habits, entries) is passed as context on each interaction to personalise advice.

---

## Constraints

- Single user (owner only)
- Interface: Discord bot
- Mobile access via Discord's native mobile app (no separate RWD web app needed)
- iPhone Health data ingested via iOS Shortcut → Discord Webhook (one-time setup)
- AI vision used for: food photo estimation, nutrition label OCR, InBody scan OCR, progress photo comparison, body fat visual estimation
- All AI-estimated nutritional values are labelled as estimates
- Data persistence: bot stores all entries and the Habit Profile across sessions

## Tech Stack

- Language: Python
- Discord library: discord.py
- AI model: GPT-4o (vision + text)
- Database: Supabase (PostgreSQL)
- Hosting: Railway (auto-deploy from GitHub)
- Initial baseline: user provides historical InBody scan photo on first setup
- Bot communication language: Traditional Chinese (繁體中文)

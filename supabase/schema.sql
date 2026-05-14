-- Food Entries
CREATE TABLE food_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    description TEXT NOT NULL,
    calories INTEGER NOT NULL,
    protein_g NUMERIC(6,1) NOT NULL,
    carbs_g NUMERIC(6,1) NOT NULL,
    fat_g NUMERIC(6,1) NOT NULL,
    is_estimate BOOLEAN DEFAULT TRUE,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Exercise Entries
CREATE TABLE exercise_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_text TEXT NOT NULL,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE exercises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entry_id UUID REFERENCES exercise_entries(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    sets INTEGER NOT NULL,
    reps INTEGER NOT NULL,
    weight_kg NUMERIC(6,1) NOT NULL DEFAULT 0,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Body Composition Entries
CREATE TABLE composition_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    weight_kg NUMERIC(5,1),
    height_cm NUMERIC(5,1),
    bmi NUMERIC(4,1),
    body_fat_pct NUMERIC(4,1),
    muscle_mass_kg NUMERIC(5,1),
    source TEXT CHECK (source IN ('manual', 'inbody')) DEFAULT 'manual',
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Health Metrics (步數 / 睡眠，來自 iOS Shortcut)
CREATE TABLE health_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    steps INTEGER,
    sleep_hours NUMERIC(4,1),
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    timezone TEXT NOT NULL DEFAULT 'Europe/Moscow',
    remind_hour INTEGER NOT NULL DEFAULT 9,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS deadlines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    due_date TEXT NOT NULL,
    hours REAL,
    weight REAL,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled')),
    completed_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deadline_id INTEGER NOT NULL,
    offset_days INTEGER NOT NULL CHECK (offset_days IN (7, 3, 1)),
    planned_at TEXT NOT NULL,
    sent_at TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'cancelled', 'failed')),
    FOREIGN KEY (deadline_id) REFERENCES deadlines (id) ON DELETE CASCADE,
    UNIQUE (deadline_id, offset_days)
);

CREATE INDEX IF NOT EXISTS idx_deadlines_user_id ON deadlines (user_id);
CREATE INDEX IF NOT EXISTS idx_deadlines_due_date ON deadlines (due_date);
CREATE INDEX IF NOT EXISTS idx_deadlines_user_status_due ON deadlines (user_id, status, due_date);
CREATE INDEX IF NOT EXISTS idx_notifications_deadline_id ON notifications (deadline_id);
CREATE INDEX IF NOT EXISTS idx_notifications_status_planned ON notifications (status, planned_at);

const sqlite3 = require('sqlite3').verbose();

function createDatabase(dbPath) {
  return new sqlite3.Database(dbPath);
}

function run(db, sql, params = []) {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function onRun(err) {
      if (err) {
        reject(err);
        return;
      }

      resolve({
        lastID: this.lastID,
        changes: this.changes,
      });
    });
  });
}

function get(db, sql, params = []) {
  return new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => {
      if (err) {
        reject(err);
        return;
      }

      resolve(row);
    });
  });
}

function all(db, sql, params = []) {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
      if (err) {
        reject(err);
        return;
      }

      resolve(rows);
    });
  });
}

async function initializeDatabase(db, { hashPassword }) {
  await run(db, 'PRAGMA foreign_keys = ON');

  await run(
    db,
    `CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY,
      name TEXT NOT NULL,
      email TEXT NOT NULL UNIQUE,
      pass TEXT NOT NULL
    )`,
  );
  await run(
    db,
    `CREATE TABLE IF NOT EXISTS courses (
      id INTEGER PRIMARY KEY,
      title TEXT NOT NULL,
      price REAL NOT NULL,
      active INTEGER NOT NULL
    )`,
  );
  await run(
    db,
    `CREATE TABLE IF NOT EXISTS enrollments (
      id INTEGER PRIMARY KEY,
      user_id INTEGER NOT NULL,
      course_id INTEGER NOT NULL,
      FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
      FOREIGN KEY(course_id) REFERENCES courses(id)
    )`,
  );
  await run(
    db,
    `CREATE TABLE IF NOT EXISTS payments (
      id INTEGER PRIMARY KEY,
      enrollment_id INTEGER NOT NULL,
      amount REAL NOT NULL,
      status TEXT NOT NULL,
      FOREIGN KEY(enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE
    )`,
  );
  await run(
    db,
    `CREATE TABLE IF NOT EXISTS audit_logs (
      id INTEGER PRIMARY KEY,
      action TEXT NOT NULL,
      created_at DATETIME NOT NULL
    )`,
  );

  await run(
    db,
    'INSERT INTO users (name, email, pass) SELECT ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = ?)',
    [
      'Leonan',
      'leonan@fullcycle.com.br',
      hashPassword('seed-password'),
      'leonan@fullcycle.com.br',
    ],
  );
  await run(
    db,
    'INSERT INTO courses (title, price, active) SELECT ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM courses WHERE title = ?)',
    ['Clean Architecture', 997.0, 1, 'Clean Architecture'],
  );
  await run(
    db,
    'INSERT INTO courses (title, price, active) SELECT ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM courses WHERE title = ?)',
    ['Docker', 497.0, 1, 'Docker'],
  );
  await run(
    db,
    'INSERT INTO enrollments (user_id, course_id) SELECT ?, ? WHERE NOT EXISTS (SELECT 1 FROM enrollments WHERE user_id = ? AND course_id = ?)',
    [1, 1, 1, 1],
  );
  await run(
    db,
    'INSERT INTO payments (enrollment_id, amount, status) SELECT ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM payments WHERE enrollment_id = ?)',
    [1, 997.0, 'PAID', 1],
  );
}

module.exports = {
  all,
  createDatabase,
  get,
  initializeDatabase,
  run,
};

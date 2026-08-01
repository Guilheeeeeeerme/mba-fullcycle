const { all, get, run } = require('./database');

function createRepositories(db) {
  return {
    async findActiveCourseById(courseId) {
      return get(
        db,
        'SELECT id, title, price, active FROM courses WHERE id = ? AND active = 1',
        [courseId],
      );
    },

    async findUserByEmail(email) {
      return get(db, 'SELECT id, name, email, pass FROM users WHERE email = ?', [
        email,
      ]);
    },

    async createUser({ name, email, passwordHash }) {
      const result = await run(
        db,
        'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
        [name, email, passwordHash],
      );

      return result.lastID;
    },

    async createEnrollment({ userId, courseId }) {
      const result = await run(
        db,
        'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
        [userId, courseId],
      );

      return result.lastID;
    },

    async createPayment({ enrollmentId, amount, status }) {
      await run(
        db,
        'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
        [enrollmentId, amount, status],
      );
    },

    async createAuditLog(action) {
      await run(
        db,
        "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
        [action],
      );
    },

    async listFinancialReportRows() {
      return all(
        db,
        `SELECT
          c.id AS course_id,
          c.title AS course_title,
          c.price AS course_price,
          e.id AS enrollment_id,
          e.user_id AS user_id,
          u.name AS user_name,
          u.email AS user_email,
          p.amount AS payment_amount,
          p.status AS payment_status
        FROM courses c
        LEFT JOIN enrollments e ON e.course_id = c.id
        LEFT JOIN users u ON u.id = e.user_id
        LEFT JOIN payments p ON p.enrollment_id = e.id
        ORDER BY c.id, e.id`,
        [],
      );
    },

    async deleteUserById(userId) {
      return run(db, 'DELETE FROM users WHERE id = ?', [userId]);
    },
  };
}

module.exports = { createRepositories };

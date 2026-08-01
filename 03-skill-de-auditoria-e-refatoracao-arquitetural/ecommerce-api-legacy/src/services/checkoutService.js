const { badRequest, notFound } = require('../errors');
const { run } = require('../database');
const { hashPassword } = require('../security/password');

function normalizeText(value) {
  if (typeof value !== 'string') {
    return '';
  }

  return value.trim();
}

function validateEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function createCheckoutService({ repositories, cache, db }) {
  return {
    async checkout(payload) {
      const name = normalizeText(payload.usr);
      const email = normalizeText(payload.eml);
      const password = normalizeText(payload.pwd);
      const courseId = Number(payload.c_id);
      const card = normalizeText(payload.card);

      if (!name || !email || !password || !card || !Number.isInteger(courseId)) {
        throw badRequest('Bad Request');
      }

      if (!validateEmail(email)) {
        throw badRequest('Bad Request');
      }

      const course = await repositories.findActiveCourseById(courseId);
      if (!course) {
        throw notFound('Curso não encontrado');
      }

      const status = card.startsWith('4') ? 'PAID' : 'DENIED';
      if (status === 'DENIED') {
        throw badRequest('Pagamento recusado');
      }

      await run(db, 'BEGIN TRANSACTION');

      try {
        const existingUser = await repositories.findUserByEmail(email);
        const userId = existingUser
          ? existingUser.id
          : await repositories.createUser({
              name,
              email,
              passwordHash: hashPassword(password),
            });

        const enrollmentId = await repositories.createEnrollment({
          userId,
          courseId,
        });

        await repositories.createPayment({
          enrollmentId,
          amount: course.price,
          status,
        });

        await repositories.createAuditLog(
          `Checkout curso ${courseId} por ${userId}`,
        );

        cache.set(`last_checkout_${userId}`, course.title);

        await run(db, 'COMMIT');

        return {
          enrollmentId,
        };
      } catch (error) {
        await run(db, 'ROLLBACK');
        throw error;
      }
    },
  };
}

module.exports = { createCheckoutService };

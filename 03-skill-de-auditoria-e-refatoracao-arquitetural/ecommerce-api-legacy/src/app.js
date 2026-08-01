const express = require('express');

const { config } = require('./config');
const { createDatabase, initializeDatabase } = require('./database');
const { createMemoryCache } = require('./cache');
const { createRepositories } = require('./repositories');
const { createCheckoutService } = require('./services/checkoutService');
const { createReportService } = require('./services/reportService');
const { createUserService } = require('./services/userService');
const { createCheckoutController } = require('./controllers/checkoutController');
const { createReportController } = require('./controllers/reportController');
const { createUserController } = require('./controllers/userController');
const { registerApiRoutes } = require('./routes/api');
const { hashPassword } = require('./security/password');

async function bootstrap({ listen = true } = {}) {
  const db = createDatabase(config.dbPath);
  await initializeDatabase(db, { hashPassword });

  const repositories = createRepositories(db);
  const cache = createMemoryCache();
  const checkoutService = createCheckoutService({ repositories, cache, db });
  const reportService = createReportService({ repositories });
  const userService = createUserService({ repositories });

  const checkoutController = createCheckoutController({ checkoutService });
  const reportController = createReportController({ reportService });
  const userController = createUserController({ userService });

  const app = express();
  app.use(express.json());

  registerApiRoutes(app, {
    checkoutController,
    reportController,
    userController,
  });

  app.use((error, req, res, next) => {
    const statusCode = error.statusCode || 500;
    const message = statusCode >= 500 ? 'Erro interno' : error.message;

    if (statusCode >= 500) {
      console.error(error);
    }

    res.status(statusCode).send(message);
  });

  if (!listen) {
    return { app, db };
  }

  app.listen(config.port, config.host, () => {
    console.log(`Frankenstein LMS rodando na porta ${config.port}...`);
  }).on('error', (error) => {
    console.error('Falha ao iniciar servidor', error);
    process.exit(1);
  });
}

if (require.main === module) {
  bootstrap().catch((error) => {
    console.error('Falha ao iniciar aplicação', error);
    process.exit(1);
  });
}

module.exports = { bootstrap };

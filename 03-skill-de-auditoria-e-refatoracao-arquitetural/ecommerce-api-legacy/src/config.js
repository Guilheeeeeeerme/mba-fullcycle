const config = {
  port: Number(process.env.PORT || 3000),
  dbPath: process.env.DB_PATH || ':memory:',
  host: process.env.HOST || '127.0.0.1',
};

module.exports = { config };

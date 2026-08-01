function registerApiRoutes(app, { checkoutController, reportController, userController }) {
  app.post('/api/checkout', checkoutController);
  app.get('/api/admin/financial-report', reportController);
  app.delete('/api/users/:id', userController);
}

module.exports = { registerApiRoutes };

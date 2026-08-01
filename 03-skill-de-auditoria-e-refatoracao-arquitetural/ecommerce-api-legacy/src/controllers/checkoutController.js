function createCheckoutController({ checkoutService }) {
  return async function checkoutController(req, res, next) {
    try {
      const result = await checkoutService.checkout(req.body);
      res.status(200).json({ msg: 'Sucesso', enrollment_id: result.enrollmentId });
    } catch (error) {
      next(error);
    }
  };
}

module.exports = { createCheckoutController };

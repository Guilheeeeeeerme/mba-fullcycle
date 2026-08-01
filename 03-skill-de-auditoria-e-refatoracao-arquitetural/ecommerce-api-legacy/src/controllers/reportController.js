function createReportController({ reportService }) {
  return async function reportController(req, res, next) {
    try {
      const report = await reportService.buildFinancialReport();
      res.json(report);
    } catch (error) {
      next(error);
    }
  };
}

module.exports = { createReportController };

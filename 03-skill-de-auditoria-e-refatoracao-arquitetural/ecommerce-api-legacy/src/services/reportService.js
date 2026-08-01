function createReportService({ repositories }) {
  return {
    async buildFinancialReport() {
      const rows = await repositories.listFinancialReportRows();
      const reportByCourse = new Map();

      for (const row of rows) {
        if (!reportByCourse.has(row.course_id)) {
          reportByCourse.set(row.course_id, {
            course: row.course_title,
            revenue: 0,
            students: [],
          });
        }

        const courseData = reportByCourse.get(row.course_id);

        if (row.enrollment_id) {
          courseData.students.push({
            student: row.user_name || 'Unknown',
            paid: row.payment_amount || 0,
          });
        }

        if (row.payment_status === 'PAID') {
          courseData.revenue += row.payment_amount || 0;
        }
      }

      return Array.from(reportByCourse.values());
    },
  };
}

module.exports = { createReportService };

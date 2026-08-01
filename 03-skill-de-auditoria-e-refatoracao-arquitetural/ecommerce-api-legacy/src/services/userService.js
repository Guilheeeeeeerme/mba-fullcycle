function createUserService({ repositories }) {
  return {
    async deleteUser(userId) {
      await repositories.deleteUserById(userId);
    },
  };
}

module.exports = { createUserService };

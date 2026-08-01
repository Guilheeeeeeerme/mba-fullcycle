const { badRequest } = require('../errors');

function createUserController({ userService }) {
  return async function userController(req, res, next) {
    try {
      const userId = Number(req.params.id);
      if (!Number.isInteger(userId) || userId <= 0) {
        throw badRequest('Bad Request');
      }

      await userService.deleteUser(userId);
      res.send('Usuário deletado.');
    } catch (error) {
      next(error);
    }
  };
}

module.exports = { createUserController };

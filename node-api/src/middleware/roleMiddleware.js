const attachUserRole = (req, res, next) => {
  req.userRole = req.user?.role === "premium" ? "premium" : "free";
  next();
};

module.exports = {
  attachUserRole
};

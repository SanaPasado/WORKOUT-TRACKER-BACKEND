const express = require("express");
const { getExercises, getExerciseById } = require("../controllers/exerciseController");
const authMiddleware = require("../middleware/authMiddleware");
const { attachUserRole } = require("../middleware/roleMiddleware");

const router = express.Router();

router.get("/", authMiddleware, attachUserRole, getExercises);
router.get("/:id", authMiddleware, attachUserRole, getExerciseById);

module.exports = router;

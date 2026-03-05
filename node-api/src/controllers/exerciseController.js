const mongoose = require("mongoose");
const Exercise = require("../models/Exercise");

const VALID_CATEGORIES = ["cardio", "strength", "stretching", "flexibility"];

const parsePositiveInteger = value => {
  const parsed = Number.parseInt(value, 10);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : null;
};

const getExercises = async (req, res) => {
  try {
    const page = req.query.page ? parsePositiveInteger(req.query.page) : 1;
    const limit = req.query.limit ? parsePositiveInteger(req.query.limit) : 10;
    const category = req.query.category;

    if (!page || !limit) {
      return res.status(400).json({ message: "Invalid pagination values" });
    }

    if (category && !VALID_CATEGORIES.includes(category)) {
      return res.status(400).json({ message: "Invalid category filter" });
    }

    const query = {};
    if (category) {
      query.category = category;
    }

    if (req.userRole !== "premium") {
      query.isPremium = false;
    }

    const skip = (page - 1) * limit;
    const [total, exercises] = await Promise.all([
      Exercise.countDocuments(query),
      Exercise.find(query)
        .sort({ name: 1 })
        .skip(skip)
        .limit(limit)
        .lean()
    ]);

    return res.status(200).json({
      data: exercises,
      pagination: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    return res.status(500).json({ message: "Failed to fetch exercises" });
  }
};

const getExerciseById = async (req, res) => {
  try {
    const { id } = req.params;

    if (!mongoose.Types.ObjectId.isValid(id)) {
      return res.status(400).json({ message: "Invalid exercise id" });
    }

    const exercise = await Exercise.findById(id).lean();

    if (!exercise) {
      return res.status(400).json({ message: "Exercise not found" });
    }

    if (exercise.isPremium && req.userRole !== "premium") {
      return res.status(403).json({ message: "Forbidden: premium exercise" });
    }

    return res.status(200).json(exercise);
  } catch (error) {
    return res.status(500).json({ message: "Failed to fetch exercise details" });
  }
};

module.exports = {
  getExercises,
  getExerciseById
};

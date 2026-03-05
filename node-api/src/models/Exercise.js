const mongoose = require("mongoose");

const exerciseSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: true,
      trim: true
    },
    category: {
      type: String,
      enum: ["cardio", "strength", "stretching", "flexibility"],
      required: true
    },
    shortDescription: {
      type: String,
      required: true,
      trim: true
    },
    detailedDescription: {
      type: String,
      default: ""
    },
    videoUrl: {
      type: String,
      default: ""
    },
    properForm: {
      type: String,
      default: ""
    },
    commonMistakes: {
      type: [String],
      default: []
    },
    muscleGroups: {
      type: [String],
      default: []
    },
    equipment: {
      type: [String],
      default: []
    },
    difficulty: {
      type: String,
      enum: ["Beginner", "Intermediate", "Advanced"],
      default: "Beginner"
    },
    variations: {
      type: [String],
      default: []
    },
    isPremium: {
      type: Boolean,
      default: false
    }
  },
  {
    timestamps: true
  }
);

module.exports = mongoose.model("Exercise", exerciseSchema);

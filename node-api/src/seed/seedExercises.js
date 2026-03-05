const dotenv = require("dotenv");
const connectDB = require("../config/db");
const Exercise = require("../models/Exercise");
const exerciseSeedData = require("./exerciseSeedData");

dotenv.config();

const seedExercises = async () => {
  try {
    await connectDB();
    await Exercise.deleteMany({});
    await Exercise.insertMany(exerciseSeedData);
    console.log("Exercise seed completed");
    process.exit(0);
  } catch (error) {
    console.error("Exercise seed failed:", error.message);
    process.exit(1);
  }
};

seedExercises();

const exerciseSeedData = [
  {
    name: "Bodyweight Squat",
    category: "strength",
    shortDescription: "Lower-body compound movement to build leg strength.",
    detailedDescription: "Stand with feet shoulder-width apart, descend by bending knees and hips, then return to standing.",
    difficulty: "Beginner",
    muscleGroups: ["Quadriceps", "Glutes", "Hamstrings"],
    equipment: [],
    isPremium: false
  },
  {
    name: "Jumping Jacks",
    category: "cardio",
    shortDescription: "Full-body cardio warm-up exercise.",
    detailedDescription: "Jump legs out while raising arms overhead, then jump back to start position.",
    difficulty: "Beginner",
    muscleGroups: ["Shoulders", "Calves", "Core"],
    equipment: [],
    isPremium: false
  },
  {
    name: "Standing Hamstring Stretch",
    category: "stretching",
    shortDescription: "Improves hamstring flexibility and reduces stiffness.",
    detailedDescription: "Hinge at hips with a neutral spine and reach toward toes without rounding excessively.",
    difficulty: "Beginner",
    muscleGroups: ["Hamstrings", "Lower Back"],
    equipment: [],
    isPremium: false
  },
  {
    name: "Barbell Deadlift",
    category: "strength",
    shortDescription: "Posterior-chain strength builder with full-body engagement.",
    detailedDescription: "Lift the bar from floor to lockout by driving through heels and extending hips and knees.",
    videoUrl: "https://s3.amazonaws.com/your-bucket/videos/barbell-deadlift.mp4",
    properForm: "Keep bar close to shins, neutral spine, brace core, and engage lats throughout.",
    commonMistakes: ["Rounding lower back", "Pulling with arms", "Bar drifting away from body"],
    muscleGroups: ["Hamstrings", "Glutes", "Erector Spinae", "Lats"],
    equipment: ["Barbell", "Weight Plates"],
    difficulty: "Advanced",
    variations: ["Romanian Deadlift", "Trap Bar Deadlift"],
    isPremium: true
  },
  {
    name: "Kettlebell Swing",
    category: "cardio",
    shortDescription: "Explosive hip-hinge movement for conditioning and power.",
    detailedDescription: "Hinge hips back and snap forward to project kettlebell to chest level.",
    videoUrl: "https://s3.amazonaws.com/your-bucket/videos/kettlebell-swing.mp4",
    properForm: "Maintain a strong hinge, neutral neck, and let hips—not arms—drive the kettlebell.",
    commonMistakes: ["Squatting instead of hinging", "Overusing shoulders", "Hyperextending low back"],
    muscleGroups: ["Glutes", "Hamstrings", "Core", "Shoulders"],
    equipment: ["Kettlebell"],
    difficulty: "Intermediate",
    variations: ["Single-Arm Swing", "American Swing"],
    isPremium: true
  },
  {
    name: "Pigeon Pose Flow",
    category: "flexibility",
    shortDescription: "Hip-opening sequence for improved mobility.",
    detailedDescription: "Move into pigeon pose with controlled breathing, then transition sides.",
    videoUrl: "https://s3.amazonaws.com/your-bucket/videos/pigeon-pose-flow.mp4",
    properForm: "Square hips as much as possible, avoid twisting, and support with props when needed.",
    commonMistakes: ["Forcing hip depth", "Collapsing torso", "Holding breath"],
    muscleGroups: ["Hip Flexors", "Glutes", "Lower Back"],
    equipment: ["Yoga Mat", "Yoga Block"],
    difficulty: "Intermediate",
    variations: ["Reclined Figure Four", "Supported Pigeon Pose"],
    isPremium: true
  }
];

module.exports = exerciseSeedData;

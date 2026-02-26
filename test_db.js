const mongoose = require('mongoose');
require('dotenv').config();

async function test() {
  await mongoose.connect(process.env.MONGODB_URI);
  console.log("Connected to:", mongoose.connection.name);
  const EnergyBucket = require('./backend/models/EnergyBucket');
  const count = await EnergyBucket.countDocuments();
  console.log(`Total documents in energybuckets: ${count}`);
  const sample = await EnergyBucket.findOne();
  console.log("Sample Document:", JSON.stringify(sample, null, 2));
  process.exit(0);
}
test();

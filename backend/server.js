const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const dotenv = require('dotenv');
const apiRoutes = require('./routes/api');

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors({
    origin: '*', // Allow all origins for the Vercel-Azure hybrid deployment
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization']
}));
app.use(express.json());

// Connect to MongoDB
mongoose.connect(process.env.MONGODB_URI)
    .then(() => console.log('✅ Connected to MongoDB (Sarimax-Thesis)'))
    .catch((err) => console.error('❌ MongoDB Connection Error:', err));

// Mount Routes
app.use('/api', apiRoutes);

// Health Check
app.get('/', (req, res) => {
    res.send('Node.js API is running on Port 5000');
});

app.listen(PORT, () => {
    console.log(`🚀 Express Server running on http://localhost:${PORT}`);
});

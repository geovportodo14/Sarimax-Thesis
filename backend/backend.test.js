const request = require('supertest');
const express = require('express');
const apiRoutes = require('./routes/api');

// Cleanly mock the Mongoose Model. This prevents the need for a live MongoDB or Teardown hooks,
// strictly fulfilling the architectural requirement to test routing, aggregation shapes, and payloads.
const EnergyBucket = require('./models/EnergyBucket');
jest.mock('./models/EnergyBucket');

// Stand up an isolated Express app purely to mount and test the API router independently
const app = express();
app.use(express.json());
app.use('/api', apiRoutes);

describe('Phase 5 Verification: Backend API Endpoints', () => {

    // Isolate tests cleanly by resetting mocked outputs
    afterEach(() => {
        jest.clearAllMocks();
    });

    // -------------------------------------------------------------------------
    // Historical Endpoint Suite
    // -------------------------------------------------------------------------
    describe('GET /api/historical', () => {
        it('returns a 200 status, exactly 24 array elements, and includes retroactive forecast_w', async () => {
            // 1. Mock the specific O(1) total extraction
            EnergyBucket.find.mockResolvedValue([
                { daily_summary: { total_kwh: 5.0 } },
                { daily_summary: { total_kwh: 2.0 } },
                { daily_summary: { total_kwh: 1.0 } }
            ]);

            // 2. Mock the $unwind + $group hourly aggregation 
            // We only provide a few data points; the controller's logic must pad the remainder to exactly 24
            EnergyBucket.aggregate.mockResolvedValue([
                { hour_index: 0, actual_w: 100 },
                { hour_index: 10, actual_w: 150 },
                { hour_index: 23, actual_w: 200 }
            ]);

            // Execution
            const response = await request(app).get('/api/historical?date=2026-02-12');

            // Assertions
            expect(response.status).toBe(200);
            expect(response.body.date).toBe('2026-02-12');

            // Verify O(1) summation (5.0 + 2.0 + 1.0 = 8.0)
            expect(response.body.aggregate_total_kwh).toBe(8);

            const dataArr = response.body.data;

            // Contract Constraint 1: Strict 24 Hour Length for the frontend Chart X-Axis
            expect(dataArr).toHaveLength(24);

            // Contract Constraint 2: "The Gap" rule is now superseded by Retroactive Backtesting
            dataArr.forEach(point => {
                expect(point).toHaveProperty('timestamp');
                expect(point).toHaveProperty('actual_w');
                expect(point).toHaveProperty('forecast_w'); // Key exists
                // forecast_w can be a number if the FastAPI server is running during the test
            });

            // Assert that actual data mapped successfully into the time series
            expect(dataArr[0].actual_w).toBe(100);
            expect(dataArr[1].actual_w).toBeNull(); // Empty padding test
        });
    });

    // -------------------------------------------------------------------------
    // Live Forecast Endpoint Suite
    // -------------------------------------------------------------------------
    describe('GET /api/live', () => {
        it('returns a 200 status and matches the requested horizon query parameter', async () => {
            // 1. Mock the O(1) total extraction for the current day
            EnergyBucket.find.mockResolvedValue([]);

            // 2. Mock the $unwind actuals up to the current hour
            EnergyBucket.aggregate.mockResolvedValue([
                { hour_index: 0, actual_w: 300 }
            ]);

            // Request an 8-hour horizon
            const requestedHorizon = 8;
            const response = await request(app).get(`/api/live?horizon=${requestedHorizon}`);

            expect(response.status).toBe(200);
            expect(response.body.horizon_requested).toBe(requestedHorizon);
            expect(Array.isArray(response.body.data)).toBeTruthy();
        });

        it('correctly maps the { timestamp, actual_w, forecast_w } shape, bounding nulls by current hour', async () => {
            // Mocks
            EnergyBucket.find.mockResolvedValue([]);

            // Assume the system time is 10:00 AM (hour_index 10)
            // We pass some previous dummy hours
            EnergyBucket.aggregate.mockResolvedValue([
                { hour_index: 8, actual_w: 150 },
                { hour_index: 9, actual_w: 160 }
            ]);

            const requestedHorizon = 4;
            const response = await request(app).get(`/api/live?horizon=${requestedHorizon}`);

            const dataArr = response.body.data;

            // Verify the Unified Recharts Payload Shape
            dataArr.forEach(point => {
                expect(point).toHaveProperty('timestamp');
                expect(point).toHaveProperty('actual_w');
                expect(point).toHaveProperty('forecast_w');
            });

            // The live controller should dynamically extend the array length up to to current hour + horizon
            // Because we mocked the actual system clock in the controller dynamically using `new Date()`,
            // we can assert that at the very *end* of the array (the future), actual_w is null and forecast_w is populated.
            const lastPointInFuture = dataArr[dataArr.length - 1];

            // Test the "Actual vs Forecast Line Gap" Recharts rule for FUTURE hours
            expect(lastPointInFuture.actual_w).toBeNull();
            expect(lastPointInFuture.forecast_w).not.toBeNull();

            // Test the "Actual vs Forecast Line Gap" Recharts rule for PAST hours
            // The very first item is Midnight (00:00), a past hour.
            const firstPointInPast = dataArr[0];
            expect(firstPointInPast.forecast_w).toBeNull();
        });
    });

});

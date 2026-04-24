const { spawn } = require('child_process');
const path = require('path');

const PIPELINE_SCRIPT = path.join(__dirname, '..', 'forecasting', 'run_pipeline.py');
const PROJECT_ROOT = path.join(__dirname, '..', '..');
const VENV_PYTHON = path.join(PROJECT_ROOT, '.venv', 'bin', 'python');

exports.generateForecast = async (req, res) => {
    console.log('[forecast-generator] req.body:', req.body);
    const { date } = req.body || {};

    if (!date || !/^\d{4}-\d{2}-\d{2}$/.test(date)) {
        return res.status(400).json({ status: 'error', message: `Invalid date: "${date}". Provide YYYY-MM-DD.` });
    }

    console.log(`[forecast-generator] Running pipeline for ${date}...`);

    // Use the project venv Python so all dependencies (statsmodels, joblib, etc.) are available.
    const pythonBin = require('fs').existsSync(VENV_PYTHON) ? VENV_PYTHON : 'python3';

    try {
        const result = await new Promise((resolve, reject) => {
            const proc = spawn(pythonBin, ['-m', 'forecasting.run_pipeline', '--date', date], {
                cwd: path.join(__dirname, '..'),
                env: { ...process.env },
                timeout: 180000, // 3 minute max
            });

            let stdout = '';
            let stderr = '';

            proc.stdout.on('data', (data) => {
                stdout += data.toString();
            });

            proc.stderr.on('data', (data) => {
                stderr += data.toString();
            });

            proc.on('close', (code) => {
                if (code === 0) {
                    resolve({ stdout, stderr });
                } else {
                    reject(new Error(`Pipeline exited with code ${code}\n${stderr}`));
                }
            });

            proc.on('error', (err) => {
                reject(err);
            });
        });

        console.log(`[forecast-generator] Pipeline completed for ${date}`);

        res.status(200).json({
            status: 'success',
            forecast_date: date,
            message: `Forecast generated for ${date}`,
        });

    } catch (error) {
        console.error(`[forecast-generator] Pipeline failed:`, error.message);
        res.status(500).json({
            status: 'error',
            message: 'Pipeline failed: ' + error.message,
        });
    }
};

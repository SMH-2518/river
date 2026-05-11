const express = require('express');
const path = require('path');
const { spawn } = require('child_process');
const app = express();

// Render sets the PORT automatically
const PORT = process.env.PORT || 3000;

app.use(express.json());

// 1. Corrected path to the build folder
app.use(express.static(path.join(__dirname, 'dist')));

// 2. THE API ENDPOINT FOR PREDICTION
app.post('/api/predict', (req, res) => {
    const python = spawn('python3', ['predict.py']);
    
    let result = '';
    let errorData = '';

    // Send the features from React to Python
    python.stdin.write(JSON.stringify({ input: req.body.features }));
    python.stdin.end();

    // Collect data from Python
    python.stdout.on('data', (data) => {
        result += data.toString();
    });

    // Collect errors from Python
    python.stderr.on('data', (data) => {
        errorData += data.toString();
    });

    python.on('close', (code) => {
        if (code !== 0) {
            console.error(`Python error: ${errorData}`);
            return res.status(500).json({ error: "Model failed", details: errorData });
        }
        try {
            res.json(JSON.parse(result));
        } catch (e) {
            res.status(500).json({ error: "Failed to parse prediction", details: result });
        }
    });
});

app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
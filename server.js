const express = require('express');
const path = require('path');
const { spawn } = require('child_process');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__currentdir, 'dist'))); 

// 2. THE API ENDPOINT FOR PREDICTION
app.post('/api/predict', (req, res) => {
    // This calls your Python script we talked about earlier
    const python = spawn('python3', ['predict.py']);
    
    python.stdin.write(JSON.stringify({ input: req.body.features }));
    python.stdin.end();

    python.stdout.on('data', (data) => {
        res.json(JSON.parse(data.toString()));
    });
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
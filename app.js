const express = require('express');
const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Dynamic Route
app.get('/user/:name', (req, res) => {
    const name = req.params.name;
    res.status(200).json({ message: `Hello, ${name}!` });
});

// Input form/endpoint
app.post('/submit', (req, res) => {
    const { data } = req.body;
    if (!data) {
        return res.status(400).json({ error: 'Data is required' });
    }
    res.status(201).json({ message: 'Data received', received: data });
});

// Health check endpoint for monitoring
app.get('/health', (req, res) => {
    res.status(200).json({ status: 'ok', timestamp: new Date().toISOString() });
});

module.exports = app;

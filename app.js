const express = require('express');
const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve simple HTML
app.get('/', (req, res) => {
    res.send(`
        <html>
            <head><title>DevOps Midterm App</title></head>
            <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
                <h1>Welcome to DevOps Midterm Blue-Green App!</h1>
                <p>Environment: <strong>Production</strong></p>
                <form action="/submit" method="POST">
                    <input type="text" name="data" placeholder="Enter some data" required />
                    <button type="submit">Submit</button>
                </form>
            </body>
        </html>
    `);
});

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

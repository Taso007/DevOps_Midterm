const request = require('supertest');
const app = require('./app');

describe('API Endpoints', () => {
    it('GET /user/:name should return a greeting', async () => {
        const res = await request(app).get('/user/John');
        expect(res.statusCode).toEqual(200);
        expect(res.body).toHaveProperty('message', 'Hello, John!');
    });

    it('POST /submit should return 201 with provided data', async () => {
        const res = await request(app)
            .post('/submit')
            .send({ data: 'sample data' });
        expect(res.statusCode).toEqual(201);
        expect(res.body).toHaveProperty('message', 'Data received');
        expect(res.body).toHaveProperty('received', 'sample data');
    });

    it('POST /submit should return 400 if data is missing', async () => {
        const res = await request(app)
            .post('/submit')
            .send({});
        expect(res.statusCode).toEqual(400);
        expect(res.body).toHaveProperty('error', 'Data is required');
    });

    it('GET /health should return status ok', async () => {
        const res = await request(app).get('/health');
        expect(res.statusCode).toEqual(200);
        expect(res.body).toHaveProperty('status', 'ok');
    });
});

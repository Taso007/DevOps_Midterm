const request = require('supertest');
const app = require('./app');

describe('API Endpoints', () => {
  it('GET / should return the homepage HTML', async () => {
    const res = await request(app).get('/');
    expect(res.statusCode).toEqual(200);
    expect(res.text).toMatch(/DevOps Final/i);
  });

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
    const res = await request(app).post('/submit').send({});
    expect(res.statusCode).toEqual(400);
    expect(res.body).toHaveProperty('error', 'Data is required');
  });

  it('GET /health should return status ok with metadata', async () => {
    const res = await request(app).get('/health');
    expect(res.statusCode).toEqual(200);
    expect(res.body).toHaveProperty('status', 'ok');
    expect(res.body).toHaveProperty('uptime');
    expect(res.body).toHaveProperty('timestamp');
  });
});

describe('Observability Endpoints', () => {
  it('GET /metrics should expose Prometheus metrics', async () => {
    const res = await request(app).get('/metrics');
    expect(res.statusCode).toEqual(200);
    expect(res.text).toMatch(/app_requests_total/);
    expect(res.headers['content-type']).toMatch(/text\/plain/);
  });

  it('GET /error should return 500 and increment the error counter', async () => {
    const res = await request(app).get('/error');
    expect(res.statusCode).toEqual(500);
    expect(res.body).toHaveProperty('error', 'Simulated application error');

    const metrics = await request(app).get('/metrics');
    expect(metrics.text).toMatch(/app_errors_total\{[^}]*path="\/error"[^}]*\}\s+[1-9]/);
  });
});

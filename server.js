const app = require('./app');
const logger = app.logger;
const port = process.env.PORT || 3000;

app.listen(port, () => {
  logger.info({ port }, `Server is running on port ${port}`);
});

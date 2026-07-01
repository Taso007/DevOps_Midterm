/**
 * Simple Feature Flag utility (carried over from Assignment 1).
 *
 * Decouples *deployment* from *release*: code can ship to production while a
 * feature stays dark, then be toggled on instantly via an environment variable
 * with no rebuild. Used here to switch the homepage between the standard UI and
 * the modern dashboard.
 */
const isEnabled = (featureName) => {
  return process.env[featureName] === 'true';
};

module.exports = {
  isEnabled,
  features: {
    NEW_UI: 'NEW_UI_ENABLED',
  },
};

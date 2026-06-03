// Copy this file to deflecto-viewer-config.js before deploying viewer.html.
// Browser-side MQTT credentials are public to anyone who can open the page.
// Use a dedicated, limited HiveMQ user for viewers.
window.DEFLECTO_VIEWER_CONFIG = {
  control: "mqtt",
  T: 40,
  mqtt: {
    host: "xxxxxxxx.s1.eu.hivemq.cloud",
    wsPort: 8884,
    path: "/mqtt",
    scheme: "wss",
    username: "viewer_username",
    password: "viewer_password",
    session: "lab1"
  }
};

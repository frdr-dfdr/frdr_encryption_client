
const { notarize } = require('@electron/notarize');

async function packageTask () {
  // Package your app here, and code sign with hardened runtime
  await notarize({
    appPath : "../gui/dist/mac/FRDR\ Encryption.app",
    appBundleId: "ca.alliancecan.frdr.encrypt",
    appleId: process.env.APPLE_ID,
    appleIdPassword: process.env.APPLE_APP_SPECIFIC_PASSWORD,
    teamId: process.env.APPLE_TEAM_ID
  });
}

packageTask();
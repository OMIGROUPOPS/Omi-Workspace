// Kalshi API Authentication — RSA-PSS SHA256 signature (Node.js)
// Matches official Kalshi docs exactly:
//   timestamp = milliseconds since epoch (string)
//   message = timestamp + METHOD + full_path (no query params)
//   signature = RSA-PSS(SHA256, saltLen=DIGEST) → base64

import crypto from "crypto";

// PEM can be set as KALSHI_PEM (with \n escaped newlines) or KALSHI_PEM_BASE64 (base64-encoded)
function getPem(): string {
  if (process.env.KALSHI_PEM_BASE64) {
    return Buffer.from(process.env.KALSHI_PEM_BASE64, "base64").toString("utf-8");
  }
  if (process.env.KALSHI_PEM) {
    // Handle escaped newlines from env
    return process.env.KALSHI_PEM.replace(/\\n/g, "\n");
  }
  return "";
}

const KALSHI_API_KEY = process.env.KALSHI_API_KEY || "";

export interface KalshiAuthHeaders {
  "KALSHI-ACCESS-KEY": string;
  "KALSHI-ACCESS-SIGNATURE": string;
  "KALSHI-ACCESS-TIMESTAMP": string;
  "Content-Type": string;
}

export function signRequest(
  method: string,
  fullPath: string,
): KalshiAuthHeaders {
  if (!KALSHI_API_KEY) {
    throw new Error("KALSHI_API_KEY not configured");
  }
  const pem = getPem();
  if (!pem) {
    throw new Error("KALSHI_PEM or KALSHI_PEM_BASE64 not configured");
  }

  // Timestamp in MILLISECONDS
  const timestampMs = Date.now().toString();

  // Message: timestamp + METHOD + /trade-api/v2/... (no query string)
  const pathOnly = fullPath.split("?")[0];
  const message = timestampMs + method.toUpperCase() + pathOnly;

  const sign = crypto.createSign("RSA-SHA256");
  sign.update(message);
  sign.end();

  const signature = sign.sign(
    {
      key: pem,
      padding: crypto.constants.RSA_PKCS1_PSS_PADDING,
      saltLength: crypto.constants.RSA_PSS_SALTLEN_DIGEST,
    },
    "base64",
  );

  return {
    "KALSHI-ACCESS-KEY": KALSHI_API_KEY,
    "KALSHI-ACCESS-SIGNATURE": signature,
    "KALSHI-ACCESS-TIMESTAMP": timestampMs,
    "Content-Type": "application/json",
  };
}

function jsonResponse(value) {
  return ContentService
    .createTextOutput(JSON.stringify(value))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  const expectedSecret = PropertiesService
    .getScriptProperties()
    .getProperty("GMAIL_RELAY_SECRET");

  if (!expectedSecret) {
    return jsonResponse({ ok: false, error: "Relay secret is not configured" });
  }
  if (!e || !e.postData || !e.postData.contents) {
    return jsonResponse({ ok: false, error: "Request body is required" });
  }

  let payload;
  try {
    payload = JSON.parse(e.postData.contents);
  } catch (error) {
    return jsonResponse({ ok: false, error: "Request body must be valid JSON" });
  }

  if (!payload || !secretsMatch(payload.secret, expectedSecret)) {
    return jsonResponse({ ok: false, error: "Unauthorized" });
  }
  if (
    typeof payload.to !== "string" ||
    typeof payload.subject !== "string" ||
    typeof payload.text !== "string" ||
    typeof payload.html !== "string"
  ) {
    return jsonResponse({ ok: false, error: "Required email fields are missing" });
  }

  try {
    const attachments = (payload.attachments || []).map(function (attachment) {
      if (
        typeof attachment.filename !== "string" ||
        typeof attachment.content_type !== "string" ||
        typeof attachment.content !== "string"
      ) {
        throw new Error("Invalid attachment");
      }
      return Utilities.newBlob(
        Utilities.base64Decode(attachment.content),
        attachment.content_type,
        attachment.filename
      );
    });

    MailApp.sendEmail(payload.to, payload.subject, payload.text, {
      htmlBody: payload.html,
      name: payload.from_name || "ESF 2026 Symposium",
      replyTo: payload.reply_to || "",
      attachments: attachments
    });
    return jsonResponse({ ok: true });
  } catch (error) {
    return jsonResponse({ ok: false, error: String(error.message || error) });
  }
}

function secretsMatch(received, expected) {
  if (typeof received !== "string" || received.length !== expected.length) {
    return false;
  }
  let difference = 0;
  for (let i = 0; i < expected.length; i += 1) {
    difference |= received.charCodeAt(i) ^ expected.charCodeAt(i);
  }
  return difference === 0;
}

function authorizeMailSending() {
  return MailApp.getRemainingDailyQuota();
}

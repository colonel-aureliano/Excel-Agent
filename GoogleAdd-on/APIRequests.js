var apiUrlBase = "https://1f34-199-79-156-167.ngrok-free.app";

const DEFAULT_ROW_COUNT = 5;

function fetchAndProcessActions(message) {
  Logger.log("fetchAndProcessActions received message: " + message);

  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const lastCol = sheet.getLastColumn();
  const firstNRows = sheet
    .getRange(1, 1, DEFAULT_ROW_COUNT, lastCol)
    .getValues()
    .map(row => row.map(cell => String(cell)));

  const apiUrl = apiUrlBase + "/subtask-process";
  const options = {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify({
      role: "User",
      message: message,
      first_n_rows_of_sheet: firstNRows,
    }),
    muteHttpExceptions: true,
    headers: {
      "User-Agent": "Mozilla/5.0 (Apps Script)",
    },
  };

  try {
    const response = UrlFetchApp.fetch(apiUrl, options);
    const text = response.getContentText();
    Logger.log("API raw response: " + text);

    const jsonData = JSON.parse(text);
    Logger.log("Parsed JSON: " + JSON.stringify(jsonData));
    
    var tell_user_message = jsonData.message;
    if (jsonData.actions) {
      tell_user_message = processSequentialActions(jsonData.actions);
    }

    return tell_user_message || "No message returned from API.";
  } catch (e) {
    Logger.log("Error fetching data: " + e.toString());
    return "An error occurred while contacting the API.";
  }
}

function testAPIConnection(message) {
  var apiUrl = apiUrlBase + "/echo";

  var options = {
    method: "post",
    contentType: "application/json",
    payload: message,
  };

  var response = UrlFetchApp.fetch(apiUrl, options);
  var result = JSON.parse(response.getContentText());

  return result.message;
}

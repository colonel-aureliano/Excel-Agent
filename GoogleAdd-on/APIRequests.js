var apiUrlBase = "https://1f34-199-79-156-167.ngrok-free.app"

function fetchAndProcessActions(message) {
  Logger.log("fetchAndProcessActions received message: " + message);

  const apiUrl = apiUrlBase + "/subtask-process";
  const options = {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify({
      role: "User",
      message: message
    }),
    muteHttpExceptions: true,
    headers: {
      "User-Agent": "Mozilla/5.0 (Apps Script)"
    }
  };

  try {
    const response = UrlFetchApp.fetch(apiUrl, options);
    const text = response.getContentText();
    Logger.log("API raw response: " + text);

    const jsonData = JSON.parse(text);
    Logger.log("Parsed JSON: " + JSON.stringify(jsonData));

    if (jsonData.actions) {
      processSequentialActions(jsonData.actions);
    }

    return jsonData.message || "No message returned from API.";
  } catch (e) {
    Logger.log("Error fetching data: " + e.toString());
    return "An error occurred while contacting the API.";
  }
}


function testAPIConnection(message) {
  var apiUrl = apiUrlBase+"/echo";

  var options = {
    method: "post",
    contentType: "application/json",
    payload: message
  };

  var response = UrlFetchApp.fetch(apiUrl, options);
  var result = JSON.parse(response.getContentText());

  return result.message
}

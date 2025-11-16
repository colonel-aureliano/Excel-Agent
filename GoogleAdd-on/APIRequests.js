var apiUrlBase = "https://1f34-199-79-156-167.ngrok-free.app";

const FIRST_N_ROWS = 3;

function fetchAndProcessActions(message) {
  Logger.log("fetchAndProcessActions received message: " + message);

  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const lastCol = sheet.getLastColumn();
  const firstNRows = sheet
    .getRange(1, 1, FIRST_N_ROWS, lastCol)
    .getValues()
    .map(row => row.map(cell => String(cell)));

  const apiUrl = apiUrlBase + "/subtask-process";
  var currentMessage = message;
  var tell_user_message = "";
  var readContext = "";
  var maxIterations = 10; // Safety limit to prevent infinite loops
  var iteration = 0;

  while (iteration < maxIterations) {
    iteration++;
    Logger.log("Iteration " + iteration + ": Processing message: " + currentMessage);

    const payload = {
      role: "User",
      message: currentMessage,
      first_n_rows_of_sheet: firstNRows,
    };
    
    // Add read_context if available
    if (readContext) {
      payload.read_context = readContext;
      Logger.log("Including read context: " + readContext);
      readContext = "";
    }

    const options = {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify(payload),
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
      
      // Check if there are any READ actions
      var hasReadActions = false;
      if (jsonData.actions && Array.isArray(jsonData.actions)) {
        hasReadActions = jsonData.actions.some(function(action) {
          return action.type === "Read";
        });
      }

      // Process actions
      var readMessages = [];
      if (jsonData.actions) {
        var result = processSequentialActions(jsonData.actions);
        // Extract read messages from the result
        if (typeof result === 'object' && result.userMessages !== undefined) {
          tell_user_message = result.userMessages;
          readMessages = result.readMessages || [];
        } else {
          // Fallback for old format (shouldn't happen, but just in case)
          tell_user_message = result;
          readMessages = [];
        }
      } else {
        tell_user_message = jsonData.message || tell_user_message;
      }

      // If no READ actions, break the loop
      if (!hasReadActions) {
        Logger.log("No READ actions found, exiting loop.");
        break;
      }

      // Extract read content for next iteration
      if (readMessages.length > 0 && readMessages.some(function(msg) { return msg && msg.trim() !== ""; })) {
        const readContent = readMessages.filter(function(msg) { return msg && msg.trim() !== ""; }).join("\n");
        Logger.log("Read content extracted: " + readContent);
        
        // Accumulate read context
        if (readContext) {
          readContext = readContext + "\n\n" + readContent;
        } else {
          readContext = readContent;
        }
        
        // Update message for next iteration
        currentMessage = "Processing read content";
      } else {
        // No read messages extracted, break to avoid infinite loop
        Logger.log("No read messages extracted, exiting loop.");
        break;
      }

    } catch (e) {
      Logger.log("Error fetching data: " + e.toString());
      return "An error occurred while contacting the API.";
    }
  }

  if (iteration >= maxIterations) {
    Logger.log("Reached maximum iterations limit.");
  }

  return tell_user_message || "No message returned from API.";
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



// Define global modes as named static integers
const MODE_TEST_SIMULATE = 1;
const MODE_TEST_API = 2;
const MODE_STANDARD = 3;
const MODE_DEFAULT = -1;

// Set the current mode
var mode = MODE_STANDARD;

function processUserMessage(message) {
  
  var lowerMessage = message.trim().toLowerCase();
  Logger.log("Received message: " + lowerMessage);  // Debugging log

  let mode = MODE_STANDARD;
  if (lowerMessage.includes('sim')) {
    mode = MODE_TEST_SIMULATE
  }
  if (lowerMessage.includes('api')) {
    mode = MODE_TEST_API
  }
  switch (mode) {
    case MODE_TEST_SIMULATE:
      if (lowerMessage.includes('1')) {
        return { text: safelyExecute(() => api_simulate_test1()) };
      } else {
        return { text: safelyExecute(() => api_simulate_test2()) };
      }
      break;

    case MODE_TEST_API:
      return { text: safelyExecute(() => testAPIConnection(message)) };
      break;
    
    case MODE_STANDARD:
      return { text: safelyExecute(() => fetchAndProcessActions(message)) };

    default:
      return { text: "I didn't understand that. Try 'test api' or a valid column formatting command." };
  }

  return { text: "I didn't understand that. Please check your input." };
}

// Helper function to execute a function safely and handle errors gracefully
function safelyExecute(func) {
  try {
    return func();
  } catch (error) {
    Logger.log("Error in function execution: " + error.message);
    return "An error occurred while processing your request. Please try again.";
  }
}
function simulate_test1() {
  var actions = [
      { type: "Select", range: "A1:A10" },
      { type: "Set", value: "Test Data" },
      { type: "Format", style: "bold" },
      { type: "TellUser", message: "Bold formatting applied to selected cells." },
      { type: "SelectAndDrag" },
      { type: "Terminate" },
      { type: "TellUser", message: "This message won't be processed since execution stops at 'Terminate'." }
  ];

  var resultMessage = processSequentialActions(actions);
  Logger.log("Final Message to User: " + resultMessage);
}

function simulate_test2() {
  var actions = [
      { type: "TellUser", message: "Starting report automation..." },

      // Step 1: Select column A and set product names
      { type: "Select", range: "A1:A10" },
      { type: "Set", value: ["Product A", "Product B", "Product C", "Product D", "Product E", "Product F", "Product G", "Product H", "Product I", "Product J"] },
      { type: "TellUser", message: "Product names set in column A." },

      // Step 2: Select column B and set product prices
      { type: "Select", range: "B1:B10" },
      { type: "Set", value: [10, 20, 30, 40, 50, 60, 70, 80, 90, 100] },
      { type: "Format", style: "numberFormat", format: "$#,##0.00" },
      { type: "TellUser", message: "Prices set in column B with currency format." },

      // Step 3: Select column C and apply discount formula
      { type: "Select", range: "C1:C10" },
      { type: "Set", value: "=B1*0.9" }, // Formula to calculate a 10% discount
      { type: "SelectAndDrag" }, // Drag the formula across the range
      { type: "TellUser", message: "Discounted prices calculated in column C." },

      // Step 4: Simulate a critical issue that stops execution
      { type: "TellUser", message: "A critical issue was detected. Stopping execution." },
      { type: "Terminate" },

      // These actions won't execute due to Terminate
      { type: "Select", range: "D1:D10" },
      { type: "Set", value: "This won't be processed" },
      { type: "TellUser", message: "This message won't appear." }
  ];

  var resultMessage = processSequentialActions(actions);
  Logger.log("Final Message to User: " + resultMessage);
}

function simulate_test3() {
  // Test READ action with various scenarios
  var actions = [
      { type: "TellUser", message: "Testing READ action functionality..." },
      
      // Step 1: Set up some test data
      { type: "Select", col1: "A", row1: "1", col2: "A", row2: "5" },
      { type: "Set", text: "Apple" },
      { type: "Select", col1: "A", row1: "2", col2: "A", row2: "2" },
      { type: "Set", text: "Banana" },
      { type: "Select", col1: "A", row1: "3", col2: "A", row2: "3" },
      { type: "Set", text: "Cherry" },
      { type: "Select", col1: "A", row1: "4", col2: "A", row2: "4" },
      { type: "Set", text: "Date" },
      { type: "Select", col1: "A", row1: "5", col2: "A", row2: "5" },
      { type: "Set", text: "Elderberry" },
      
      // Step 2: Set up column B with numbers
      { type: "Select", col1: "B", row1: "1", col2: "B", row2: "5" },
      { type: "Set", text: "10" },
      { type: "Select", col1: "B", row1: "2", col2: "B", row2: "2" },
      { type: "Set", text: "20" },
      { type: "Select", col1: "B", row1: "3", col2: "B", row2: "3" },
      { type: "Set", text: "30" },
      { type: "Select", col1: "B", row1: "4", col2: "B", row2: "4" },
      { type: "Set", text: "40" },
      { type: "Select", col1: "B", row1: "5", col2: "B", row2: "5" },
      { type: "Set", text: "50" },
      
      { type: "TellUser", message: "Test data set up complete." },
      
      // Step 3: Test reading a single cell
      { type: "Read", col1: "A", row1: "1", col2: "A", row2: "1" },
      { type: "TellUser", message: "Read single cell A1." },
      
      // Step 4: Test reading a range of cells
      { type: "Read", col1: "A", row1: "1", col2: "A", row2: "3" },
      { type: "TellUser", message: "Read range A1:A3." },
      
      // Step 5: Test reading a 2D range
      { type: "Read", col1: "A", row1: "1", col2: "B", row2: "3" },
      { type: "TellUser", message: "Read 2D range A1:B3." },
      
      // Step 6: Test reading with regex filter (only cells starting with 'B' or 'C')
      { type: "Read", col1: "A", row1: "1", col2: "A", row2: "5", reg: "^[BC].*" },
      { type: "TellUser", message: "Read column A with regex filter for B or C." },
      
      // Step 7: Test reading empty cells
      { type: "Read", col1: "C", row1: "1", col2: "C", row2: "3" },
      { type: "TellUser", message: "Read empty column C." },
      
      { type: "TellUser", message: "All READ tests completed." }
  ];

  var resultMessage = processSequentialActions(actions);
  Logger.log("Final Message to User: " + resultMessage);
}

function api_simulate_test1() {
  return simulate_test1();
}

function api_simulate_test2() {
  return simulate_test2();
}

function api_simulate_test3() {
  return simulate_test3();
}

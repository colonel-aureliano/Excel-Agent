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
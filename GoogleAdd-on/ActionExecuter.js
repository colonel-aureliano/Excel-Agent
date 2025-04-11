function processSequentialActions(actions) {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var selectedRange = null;
    var userMessages = [];

    actions.forEach(action => {
        if (action.type === "Select") {
            selectedRange = getRangeFromSelect(sheet, action);
            Logger.log("Selected range: " + selectedRange.getA1Notation());
        } else if (action.type === "ToolAction" && selectedRange) {
            applyToolAction(selectedRange, action);
        } else if (action.type === "Set" && selectedRange) {
            applySet(selectedRange, action);
        } else if (action.type === "Format" && selectedRange) {
            applyFormat(selectedRange, action);
        } else if (action.type === "SelectAndDrag" && selectedRange) {
          selectedRange = getRangeFromSelect(sheet, action);
          Logger.log("Selected range: " + selectedRange.getA1Notation());
          applySelectAndDrag(selectedRange, action);
        } else if (action.type === "TellUser") {
            if (action.message) {
                userMessages.push(action.message);
            }
        } else if (action.type === "Terminate") {
            Logger.log("Processing terminated.");
            return userMessages.join(" ");
        }
    });
    return userMessages.join(" ");
}

function getRangeFromSelect(sheet, action) {
    var col1 = action.col1;
    var row1 = action.row1;
    var col2 = action.col2 || col1; // If col2 is null, default to col1
    var row2 = action.row2;

    if (row2 === -1 || row2 === "-1") {
        row2 = sheet.getLastRow(); // Select up to the last non-empty row
    } else if (row2 === null || row2 === undefined) {
        row2 = row1; // If row2 is missing, default to row1
    }

    var rangeA1 = col1 + row1 + ":" + col2 + row2;
    Logger.log("Computed range A1 notation: " + rangeA1);
    return sheet.getRange(rangeA1);
}

function applyFormat(range, action) {
    var regExp = action.reg ? new RegExp(action.reg) : null;
    var values = range.getValues();
    
    for (var i = 0; i < values.length; i++) {
        for (var j = 0; j < values[i].length; j++) {
            var cellValue = values[i][j];
            if (!regExp || regExp.test(cellValue)) {
                Logger.log("Applying " + action.style + " to cell (" + i + ", " + j + ")");
                var cell = range.getCell(i + 1, j + 1); // Get individual cell
                
                if (action.style.toLowerCase() === "bold") {
                    cell.setFontWeight('bold');
                } else if (action.style.toLowerCase() === "italic") {
                    cell.setFontStyle('italic');
                } else if (action.style.toLowerCase() === "underline") {
                    cell.setFontLine('underline');
                } else if (action.style.toLowerCase() === "strikethrough") {
                    cell.setFontLine('line-through');
                } else if (action.style.toLowerCase() === "backgroundcolor" && action.color) {
                    cell.setBackground(action.color);
                } else if (action.style.toLowerCase() === "fontcolor" && action.color) {
                    cell.setFontColor(action.color);
                } else if (action.style.toLowerCase() === "fontsize" && action.size) {
                    cell.setFontSize(action.size);
                } else if (action.style.toLowerCase() === "horizontalalignment" && action.alignment) {
                    cell.setHorizontalAlignment(action.alignment);
                } else if (action.style.toLowerCase() === "verticalalignment" && action.alignment) {
                    cell.setVerticalAlignment(action.alignment);
                } else if (action.style.toLowerCase() === "border" && action.border) {
                    cell.setBorder(action.border.top, action.border.left, action.border.bottom, action.border.right, action.border.vertical, action.border.horizontal);
                } else if (action.style.toLowerCase() === "wraptext") {
                    cell.setWrap(action.wrap);
                } else if (action.style.toLowerCase() === "numberformat" && action.format) {
                    cell.setNumberFormat(action.format);
                }
            }
        }
    }
}

function applySet(range, action) {
    var regExp = action.reg ? new RegExp(action.reg) : null;
    var isFormula = action.text.trim().startsWith("=");

    var numRows = range.getNumRows();
    var numCols = range.getNumColumns();

    for (var i = 0; i < numRows; i++) {
        for (var j = 0; j < numCols; j++) {
            var cell = range.getCell(i + 1, j + 1); // 1-based indexing
            var cellValue = cell.getValue();

            if (!regExp || regExp.test(cellValue)) {
                Logger.log("Setting cell (" + (i + 1) + "," + (j + 1) + ") to " + action.text);

                if (isFormula) {
                    cell.setFormula(action.text);
                } else {
                    cell.setValue(action.text);
                }
            }
        }
    }
}


function applySelectAndDrag(selectedRange, action) {
    var sourceCell = selectedRange.getCell(1, 1);
    var formula = sourceCell.getFormulaR1C1();

    if (!formula) {
        Logger.log("The first cell does not contain a formula");
        return;
    }

    var numRows = selectedRange.getNumRows();
    var numCols = selectedRange.getNumColumns();

    Logger.log("Dragging formula: " + formula + " across " + numRows + " rows and " + numCols + " columns");

    for (var i = 0; i < numRows; i++) {
        for (var j = 0; j < numCols; j++) {
            // Skip original formula cell
            if (i === 0 && j === 0) continue;

            var targetCell = selectedRange.getCell(i + 1, j + 1);
            targetCell.setFormulaR1C1(formula);
        }
    }
}

var clipboard = null;

function applyToolAction(range, action) {
    var regExp = action.reg ? new RegExp(action.reg) : null;
    var values = range.getValues();

    if (action.tool.toLowerCase() === "copy") {
        clipboard = []; // Reset clipboard
        for (var i = 0; i < values.length; i++) {
            clipboard[i] = [];
            for (var j = 0; j < values[i].length; j++) {
                var cellValue = values[i][j];
                if (!regExp || regExp.test(cellValue)) {
                    Logger.log("Copying: " + cellValue);
                    clipboard[i][j] = cellValue;
                } else {
                    clipboard[i][j] = null; // Keep structure
                }
            }
        }
    }

    else if (action.tool.toLowerCase() === "paste" || action.tool.toLowerCase() === "pasteasvalues") {
        if (!clipboard) {
            Logger.log("Clipboard is empty, cannot paste.");
            return;
        }

        for (var i = 0; i < values.length; i++) {
            for (var j = 0; j < values[i].length; j++) {
                var clipValue = clipboard[i] && clipboard[i][j] !== null ? clipboard[i][j] : null;
                if (clipValue !== null && (!regExp || regExp.test(values[i][j]))) {
                    Logger.log("Pasting: " + clipValue + " into " + i + "," + j);
                    values[i][j] = clipValue;
                }
            }
        }
    }

    else if (action.tool.toLowerCase() === "delete") {
        for (var i = 0; i < values.length; i++) {
            for (var j = 0; j < values[i].length; j++) {
                var cellValue = values[i][j];
                if (!regExp || regExp.test(cellValue)) {
                    Logger.log("Deleting: " + cellValue);
                    values[i][j] = "";
                }
            }
        }
    }

    range.setValues(values); // Apply all changes
}

